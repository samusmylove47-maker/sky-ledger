#!/usr/bin/env python3
"""conditions.py -- which of this engine's behaviours are NOT visible in its patterns.

WHY THIS EXISTS. Session C audited my engine by transliterating it: it preserved "the four
patterns and the SPL->HIT->DOT match order verbatim" and reported that my SPELL branch
counts a player's own Cannibalize damage as output. It does not. The guard is
`if m.group(1).lower() in SELF_TARGETS` on line 208 -- AFTER the match, outside every
pattern. C preserved faithfully what it set out to preserve, and the guard was not in that
set.

    TRANSLITERATING AN IMPLEMENTATION PRESERVES ITS PATTERNS AND LOSES EVERYTHING
    THAT IS NOT ONE.

So this file answers the obvious next question -- WHAT ELSE? -- by MEASUREMENT rather than
by reading, because reading is the instrument that failed. It mutates each non-regex
condition in turn and reports which published fields move. Anything that moves is a
behaviour an auditor cannot see by reading my regexes, and therefore a behaviour I owe
anyone comparing against me.

Every mutation is restored in a `finally`, and the restore is verified before the report
prints -- a tool that patches the live engine is only safe if the patch cannot escape.

    python3 conditions.py [--log PATH]
    python3 conditions.py --selftest
"""
import copy, io, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import gapengine as G

DEFAULT_LOG = os.path.join(ROOT, "corpus", "amp",
                           "eqlog_Shara_rivervale_20260829_full.txt")

# Every non-regex constant, with a mutation that should change behaviour if the constant
# is load-bearing. The mutation is deliberately CRUDE -- emptying or inverting -- because
# the question is "does this condition do anything at all", not "is its value right".
MUTATIONS = {
    "SELF_TARGETS":               lambda v: set(),
    "GAP":                        lambda v: 600,
    "MIN_ENGAGEMENT":             lambda v: 0,
    "AUTO_VERBS":                 lambda v: set(),
    "LANE_VERBS":                 lambda v: set(),
    "UNCLASSIFIED_VERBS":         lambda v: set(),
    "LANE_CEILING":               lambda v: {},
    "STANCE_EVEN_SHARE_OFFENSIVE": lambda v: 0.5,
    "STANCE_EVEN_SHARE_BALANCED": lambda v: 0.993,
    "STANCE_OFFENSIVE_MULT":      lambda v: 1.0,
}


def flatten(d, prefix=""):
    """Published fields as a flat {path: value}, so a diff names the field."""
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(d, list):
        out[prefix] = json.dumps(d, sort_keys=True, default=str)[:200]
    else:
        out[prefix] = d
    return out


# THE VERB SETS ARE BOTH A PATTERN INPUT AND A RUNTIME CONDITION, which the first
# version of this file got wrong. `MELEE` is compiled from
# LANE_VERBS | AUTO_VERBS | UNCLASSIFIED_VERBS at IMPORT, so mutating a set afterwards
# left the pattern still matching verbs the set no longer contained -- and the audit
# reported UNCLASSIFIED_VERBS as moving ONE field when it actually governs whether the
# damage is seen at all. An audit that understates the thing it is auditing is worse than
# no audit, because it reads as a clean bill.
# Rebuilding the pattern is also the honest finding for anyone comparing against me:
# changing one without the other produces a third behaviour that is neither.
VERB_SETS = ("LANE_VERBS", "AUTO_VERBS", "UNCLASSIFIED_VERBS")


def _rebuild_melee():
    import re
    verbs = "|".join(sorted(G.LANE_VERBS | G.AUTO_VERBS | G.UNCLASSIFIED_VERBS))
    if not verbs:
        verbs = "\\b\\B"          # matches nothing, rather than an empty alternation
    G.MELEE = re.compile(r"^You (" + verbs + r")(?:es)? (?:on )?(.+?) for (\d+) "
                         r"points of damage\.(\s*\(Critical\))?$")


def run(lines):
    return flatten(G.gap_engine(list(lines)))


def moved(base, other):
    keys = set(base) | set(other)
    return sorted(k for k in keys if base.get(k) != other.get(k))


def audit(lines):
    """[(constant, [fields that moved])], plus a restore verification."""
    base = run(lines)
    rows = []
    for name, mutate in MUTATIONS.items():
        original = getattr(G, name)
        snapshot = copy.deepcopy(original)
        saved_melee = G.MELEE
        try:
            setattr(G, name, mutate(original))
            if name in VERB_SETS:
                _rebuild_melee()
            rows.append((name, moved(base, run(lines))))
        finally:
            G.MELEE = saved_melee
            setattr(G, name, original)
            # An in-place mutation would survive reassignment; restore contents too.
            if isinstance(original, (set, dict)):
                original.clear()
                original.update(snapshot)
        assert getattr(G, name) == snapshot, f"{name} NOT RESTORED"
    return base, rows


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("SELFTEST -- the audit must find movement, and must not leak")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        S = "[Mon Aug 31 12:00:%02d 2026] "
        body = [S % i + "You slash a gnoll for 10 points of damage." for i in range(0, 40, 2)]
        body += [S % i + "You kick a gnoll for 90 points of damage." for i in (5, 15, 25)]
        body += [S % 9 + "You hit yourself for 500 points of damage."]
        body += [S % 11 + "You cleave a gnoll for 40 points of damage."]

        before = {k: copy.deepcopy(getattr(G, k)) for k in MUTATIONS}
        base, rows = audit(body)
        d = dict(rows)

        # POSITIVE CONTROL FIRST: an audit where nothing moves proves nothing.
        chk("at least one condition moves a published field",
            any(v for _, v in rows), "every mutation was inert -- the audit is dead")
        chk("SELF_TARGETS is load-bearing", bool(d["SELF_TARGETS"]),
            "emptying it changed nothing, so the guard C reported missing does nothing")
        chk("GAP is load-bearing", bool(d["GAP"]), "")
        chk("AUTO_VERBS is load-bearing", bool(d["AUTO_VERBS"]), "")
        chk("UNCLASSIFIED_VERBS is load-bearing", bool(d["UNCLASSIFIED_VERBS"]), "")
        # THE ONE THIS FILE MUST NOT GET WRONG.
        leaked = [k for k, v in before.items() if getattr(G, k) != v]
        chk("every constant restored -- the audit did not leak into the engine",
            not leaked, f"LEAKED: {leaked}")
        # ...and prove the leak check can fail, or it proves nothing.
        _keep = copy.deepcopy(G.SELF_TARGETS)
        G.SELF_TARGETS.clear()
        chk("...and that leak check CAN fail",
            [k for k, v in before.items() if getattr(G, k) != v] == ["SELF_TARGETS"],
            "the leak detector is blind")
        G.SELF_TARGETS.clear(); G.SELF_TARGETS.update(_keep)
        chk("a nonsense field name is not reported as moved",
            "no.such.field" not in d["GAP"], "")
        # THE FIX THIS FILE NEEDED: without rebuilding MELEE, clearing the verb set
        # left the pattern still matching and the audit understated its own subject.
        chk("clearing UNCLASSIFIED_VERBS moves DAMAGE, not just a coverage list",
            any(f.startswith("measured.") for f in d["UNCLASSIFIED_VERBS"]),
            f"only moved {d['UNCLASSIFIED_VERBS']} -- MELEE was not rebuilt, so the "
            f"audit is measuring less than it claims")
        chk("MELEE restored after a verb-set mutation",
            "cleave" in G.MELEE.pattern, "the rebuilt pattern leaked")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    log = DEFAULT_LOG
    if "--log" in sys.argv:
        log = sys.argv[sys.argv.index("--log") + 1]
    lines = io.open(log, encoding="utf-8", errors="replace").read().splitlines()
    print(f"read 1 log: {os.path.basename(log)} ({len(lines):,} lines)")
    print("Each row: what moves in the PUBLISHED report when that condition is disabled.")
    print("A row with movement is a behaviour NOBODY CAN SEE BY READING THE PATTERNS.\n")
    base, rows = audit(lines)
    for name, fields in sorted(rows, key=lambda r: -len(r[1])):
        if not fields:
            print(f"  {name:<28} inert on this log")
            continue
        print(f"  {name:<28} {len(fields)} field(s) move")
        for f in fields[:6]:
            print(f"      {f}")
        if len(fields) > 6:
            print(f"      ... and {len(fields) - 6} more")
    live = sum(1 for _, f in rows if f)
    print(f"\n  {live} of {len(rows)} conditions are load-bearing on this log.")
