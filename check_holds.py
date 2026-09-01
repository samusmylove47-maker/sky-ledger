#!/usr/bin/env python3
"""check_holds.py -- every WITHHELD patch must be declared in a form an instrument can
read, with a state and a GROUND from closed sets.

WHY. Session 0's finding: "a claim that stops work does not announce itself the way a
claim that starts work does." A withheld fix leaves no trace in any output. I had FOUR
held items in this repository: ONE declared in a machine-checked closed set -- the
re-pin, `REPIN NEEDED: <version> [OPEN|DEFERRED]` -- and THREE as prose in commit
bodies, visible to no instrument and found only because somebody grepped for an
unrelated word.

I built the mechanism at 04:34Z and pointed it at the one case that prompted it. That
is the inverse of the fault this project caught three times today: not three authors
reaching for the wrong mechanism, but one author with the right mechanism, applied
once and not aimed at the neighbouring cases.

THE GROUND IS A CLOSED SET, AND THAT IS THE PART THAT MATTERS. I held three patches
for nine hours on the ground "B is offline", which was false the whole time and which
my own hourly output refuted. A FREE-TEXT GROUND IS ONE NOBODY CAN CHECK -- it is the
same argument as the state, one level down, and a closed set would have made that
claim undeclarable.

AND THE GATE MUST ACCEPT AN HONEST HOLD AS READILY AS AN OPEN ONE. A gate that
punishes a hold teaches its author to hide it. That is why HELD is a legal state and
not a failure.

    python3 check_holds.py
    python3 check_holds.py --selftest
"""
import datetime, io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.path.join(ROOT, "HANDOFF.md")
PATCHES = os.path.join(ROOT, "handover", "TO-SESSION-B-tuesday.md")

STATES = ("HELD", "READY", "SHIPPED")
# WHY a patch is not shipping. Availability is deliberately NOT here: a hold resting
# on somebody being reachable expires the moment they answer, and mine rested on a
# reading that was false for nine hours.
GROUNDS = ("SCHEDULED-REBUILD", "AWAITING-EVIDENCE", "AWAITING-RULING")

# `until=` IS NEW AND IT IS THE DIRECTOR'S POINT TURNED INTO A FIELD. A ground names
# WHY a hold exists; it does not say WHEN it stops being true. All five of mine read
# `ground=SCHEDULED-REBUILD`, and nothing in this file checked whether the rebuild had
# happened -- so on 9 September they would have become holds resting on an event that
# was already past, still declared, still read as live, with nothing red.
#
# That is the shape the Director named after the Sage's hourly timer outlived its
# reason: A STANDING CLAIM THAT ACTS. Everything else stale we found today sat still
# and waited to be read. A hold does not wait -- it keeps work from shipping, on a
# schedule, long after the condition that justified it has gone.
#
# The value is parsed as \S+ rather than a date shape on purpose: a pattern that only
# matches VALID input turns an invalid value into an ABSENT one, which is the defect I
# put into mailbox.py's poll verdict earlier tonight and had to widen back out.
DECL = re.compile(
    r"^HELD-PATCH:\s+(P-\d+)\s+\[(\w+)\]\s+ground=([A-Z-]+)\s+until=(\S+)\s+--\s+(\S.*)$",
    re.M)
# A hold past its own stated end is no longer an honest hold. HELD passes this gate as
# readily as SHIPPED -- that principle stands -- but an EXPIRED hold is not a hold, it
# is a claim nobody retired.
LIVE_STATES = ("HELD", "READY")

# *** A DATE IS NOT A CONDITION. *** I wrote `until=2026-09-08` and thought I had fixed
# this. The Director's correction, which is right: "expires Tuesday" requires a READER
# to know what day it is and to care; a condition is something an INSTRUMENT can
# evaluate. My date was evaluable, but what it evaluated was that a calendar day had
# passed -- NOT that the rebuild had happened. If B rebuilds early the holds are stale
# before the 8th; if B slips to the 15th they expire while still legitimately held, and
# the gate would push me to extend the date -- which is precisely what I told myself not
# to do one commit earlier.
#
# So `until=` now names a CONDITION from a closed set, each with an evaluator. A date is
# no longer a legal value.
#
# UNCHECKABLE IS LEGAL, and that is the Director's rule adopted: anything that cannot be
# phrased as a check is marked UNCHECKABLE rather than given a date. It passes -- for the
# same reason HELD passes -- but it is COUNTED, so a tree where everything is
# unverifiable says so out loud instead of looking green.


def _b_off_140(root):
    """MET when B has moved off the 1.4.0 pin -- the event these holds actually wait on.

    Reads MY VENDORED COPY of B's contract, so it answers 'the last time I vendored B's
    contract, was B off 1.4.0'. The staleness is bounded and visible: the filename
    carries B's commit sha. Returns (met, detail) or (None, why) when it cannot look --
    and CANNOT LOOK IS NOT NOT-MET.
    """
    import glob, json
    hits = sorted(glob.glob(os.path.join(root, "handover", "gap-contract.b-*.json")))
    if not hits:
        return None, "no vendored contract found -- cannot evaluate, so REFUSING"
    try:
        d = json.load(io.open(hits[-1], encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"vendored contract unreadable ({e}) -- REFUSING"
    v = d.get("assertedEngineVersion")
    if v is None:
        return None, "vendored contract has no assertedEngineVersion -- REFUSING"
    return (v != "1.4.0"), f"{os.path.basename(hits[-1])} asserts {v!r}"


CONDITIONS = {
    "B-OFF-1.4.0": _b_off_140,
    # Legal, honest, counted. Not a loophole: a hold marked UNCHECKABLE is one I am
    # saying out loud that nobody can verify, which is strictly better than a date that
    # looks like verification and is not.
    "UNCHECKABLE": None,
}


def audit(handoff, patches, today=None, root=None):
    today = today or datetime.date.today()
    root = root or ROOT
    out = []
    unverifiable = []
    decls = DECL.findall(handoff or "")
    # POSITIVE CONTROL FIRST: a pattern that matches nothing passes every check below
    # it vacuously, and this repository has caught two dead sweeps already.
    probe = DECL.search("HELD-PATCH: P-9 [HELD] ground=AWAITING-RULING until=UNCHECKABLE -- a probe line\n")
    out.append(("the declaration pattern matches a known-good line", bool(probe),
                f"probe -> {probe.group(1) if probe else None}"))
    out.append(("at least one patch is declared", bool(decls), f"{len(decls)} found"))

    ids = [d[0] for d in decls]
    out.append(("no patch id is declared twice", len(ids) == len(set(ids)),
                f"ids {ids}"))
    for pid, state, ground, until, what in decls:
        out.append((f"{pid}: state is one of {list(STATES)}", state in STATES,
                    f"got {state!r}"))
        out.append((f"{pid}: ground is one of {list(GROUNDS)}", ground in GROUNDS,
                    f"got {ground!r} -- a free-text ground is one nobody can check"))
        out.append((f"{pid}: says what it changes", len(what.strip()) >= 20,
                    f"got {what[:40]!r}"))
        # THE END-CONDITION ARM.
        out.append((f"{pid}: until= names a condition, not a date",
                    until in CONDITIONS,
                    f"got {until!r}. Legal: {list(CONDITIONS)}. A DATE IS NOT A "
                    f"CONDITION -- it needs a reader who knows what day it is. If this "
                    f"hold's end genuinely cannot be phrased as a check, say "
                    f"UNCHECKABLE and mean it."))
        if until not in CONDITIONS:
            continue
        fn = CONDITIONS[until]
        if fn is None:
            unverifiable.append(pid)
            continue
        met, why = fn(root)
        out.append((f"{pid}: its end condition is evaluable at all", met is not None,
                    f"{why} -- an instrument that cannot look must REFUSE, not pass"))
        if met is None:
            continue
        out.append((f"{pid}: its end condition has NOT been met",
                    not (state in LIVE_STATES and met),
                    f"{why}. The condition that justified this hold IS NOW TRUE. Ship "
                    f"it, or re-declare with a ground and a condition that are true "
                    f"now -- do not weaken the condition to make the gate quiet."))
    # Every patch written up for the consumer must also be declared here, and the
    # reverse: a declaration for a patch nobody wrote up is a promise with no artifact.
    written = set(re.findall(r"^## (P-\d+)", patches or "", re.M))
    declared = set(ids)
    out.append(("every patch written up for B is declared", written <= declared,
                f"written {sorted(written)} undeclared {sorted(written - declared)}"))
    out.append(("every declared patch is written up for B", declared <= written,
                f"declared {sorted(declared)} unwritten {sorted(declared - written)}"))
    # NOT A FAILURE, BUT NEVER SILENT. A tree where every hold is UNCHECKABLE passes
    # every check above and is worth nothing; saying so is the difference between an
    # honest hold and a hidden one.
    out.append((f"holds with an UNVERIFIABLE end condition: {len(unverifiable)}", True,
                f"{unverifiable}"))
    return out


def read(p):
    try:
        return io.open(p, encoding="utf-8").read()
    except OSError:
        return None


if __name__ == "__main__":
    h, p = read(HANDOFF), read(PATCHES)
    print(f"read 2 files: {os.path.basename(HANDOFF)}, "
          f"handover/{os.path.basename(PATCHES)}")

    if "--selftest" not in sys.argv:
        rows = audit(h, p)
        bad = 0
        for n, ok, d in rows:
            print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1
        print(f"  {len(rows)} checks, {bad} failing")
        sys.exit(1 if bad else 0)

    print("SELFTEST -- each check must fail when its own condition is broken")
    if any(not ok for _, ok, _ in audit(h, p)):
        print("  the real tree does not pass"); sys.exit(1)
    print("  the real tree passes")
    n = 0

    def mut(label, hh, pp, expect_sub):
        global n
        fired = [x for x, ok, _ in audit(hh, pp) if not ok]
        hit = any(expect_sub in x for x in fired)
        print(f"  [{'ok' if hit else 'FAIL'}] {label}"
              + ("" if hit else f"  -- fired {fired[:2]}"))
        n += 0 if hit else 1

    mut("a state outside the closed set",
        h.replace("HELD-PATCH: P-1 [READY]", "HELD-PATCH: P-1 [SOON]", 1), p, "state is one of")
    # THE ONE THIS FILE EXISTS FOR: my own nine-hour false ground would not compile.
    mut("a free-text ground -- the 'B is offline' shape",
        h.replace("ground=SCHEDULED-REBUILD", "ground=B-IS-OFFLINE", 1), p, "ground is one of")
    mut("a declaration that does not say what it changes",
        re.sub(r"(HELD-PATCH: P-1 \[[A-Z]+\] ground=[A-Z-]+ until=\S+ --).*", r"\1 x",
               h, count=1),
        p, "says what it changes")
    mut("a patch written up for B but not declared",
        DECL.sub("", h, count=1), p, "every patch written up for B is declared")
    mut("a declaration for a patch nobody wrote up",
        h, re.sub(r"^## P-3.*$", "## P-9 removed", p, count=1, flags=re.M),
        "every declared patch is written up")
    mut("NO declarations at all is caught, not read as clean",
        DECL.sub("", h), p, "at least one patch is declared")

    # THE END-CONDITION ARMS. The real tree's condition is NOT met (B is still on
    # 1.4.0), so this arm is dark against it -- exactly as the date arm was dark until
    # September. Inject a contract that says otherwise instead of waiting for B.
    import json as _json, tempfile as _tf, os as _os

    def _root_with(version):
        d = _tf.mkdtemp()
        _os.makedirs(_os.path.join(d, "handover"))
        io.open(_os.path.join(d, "handover", "gap-contract.b-test.json"), "w",
                encoding="utf-8").write(_json.dumps({"assertedEngineVersion": version}))
        return d

    def mut_root(label, root, expect_sub, want_fire=True, hh=None):
        global n
        fired = [x for x, ok, _ in audit(hh or h, p, root=root) if not ok]
        hit = any(expect_sub in x for x in fired)
        ok = hit if want_fire else not hit
        print(f"  [{'ok' if ok else 'FAIL'}] {label}"
              + ("" if ok else f"  -- fired {fired[:2]}"))
        n += 0 if ok else 1

    mut_root("the end condition MET fires -- B has moved off 1.4.0",
             _root_with("1.6.0"), "end condition has NOT been met")
    mut_root("...and does NOT fire while B is still on 1.4.0",
             _root_with("1.4.0"), "end condition has NOT been met", want_fire=False)
    # THE FAULT THIS WHOLE FIELD EXISTS TO CORRECT.
    mut("a DATE where a condition belongs is refused",
        h.replace("until=B-OFF-1.4.0", "until=2026-09-08", 1), p,
        "names a condition, not a date")
    # FAIL-CLOSED: an instrument that cannot look must refuse, not pass.
    mut_root("an absent contract REFUSES rather than reading as not-met",
             _tf.mkdtemp(), "end condition is evaluable at all")
    mut_root("an unparseable version REFUSES too",
             _root_with(None), "end condition is evaluable at all")
    # SHIPPED is not a hold; a landed patch cannot be released again.
    mut_root("a SHIPPED patch does NOT fire even when the condition is met",
             _root_with("1.6.0"), "P-1: its end condition has NOT been met",
             want_fire=False,
             hh=h.replace("HELD-PATCH: P-1 [READY]", "HELD-PATCH: P-1 [SHIPPED]", 1))
    # UNCHECKABLE is legal AND counted -- honest, not a loophole.
    unc = h.replace("until=B-OFF-1.4.0", "until=UNCHECKABLE", 1)
    # Root at 1.4.0, NOT 1.6.0: the other four holds keep a condition that is not yet
    # met, so the only thing this arm can be measuring is the UNCHECKABLE one. My first
    # version injected 1.6.0 and the other four fired correctly, which made the test
    # read as a failure of UNCHECKABLE. The test was wrong, not the gate.
    rows = audit(unc, p, root=_root_with("1.4.0"))
    legal = not any(not ok for nm, ok, _ in rows)
    counted = any("UNVERIFIABLE end condition: 1" in nm for nm, _, _ in rows)
    print(f"  [{'ok' if legal and counted else 'FAIL'}] UNCHECKABLE passes AND is "
          f"counted -- an honest 'nobody can verify this' is not punished, and not hidden")
    n += 0 if (legal and counted) else 1

    print(f"  {n} self-test checks failed")
    sys.exit(1 if n else 0)
