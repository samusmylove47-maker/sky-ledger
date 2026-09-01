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
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HANDOFF = os.path.join(ROOT, "HANDOFF.md")
PATCHES = os.path.join(ROOT, "handover", "TO-SESSION-B-tuesday.md")

STATES = ("HELD", "READY", "SHIPPED")
# WHY a patch is not shipping. Availability is deliberately NOT here: a hold resting
# on somebody being reachable expires the moment they answer, and mine rested on a
# reading that was false for nine hours.
GROUNDS = ("SCHEDULED-REBUILD", "AWAITING-EVIDENCE", "AWAITING-RULING")

DECL = re.compile(
    r"^HELD-PATCH:\s+(P-\d+)\s+\[(\w+)\]\s+ground=([A-Z-]+)\s+--\s+(\S.*)$", re.M)


def audit(handoff, patches):
    out = []
    decls = DECL.findall(handoff or "")
    # POSITIVE CONTROL FIRST: a pattern that matches nothing passes every check below
    # it vacuously, and this repository has caught two dead sweeps already.
    probe = DECL.search("HELD-PATCH: P-9 [HELD] ground=AWAITING-RULING -- a probe line\n")
    out.append(("the declaration pattern matches a known-good line", bool(probe),
                f"probe -> {probe.group(1) if probe else None}"))
    out.append(("at least one patch is declared", bool(decls), f"{len(decls)} found"))

    ids = [d[0] for d in decls]
    out.append(("no patch id is declared twice", len(ids) == len(set(ids)),
                f"ids {ids}"))
    for pid, state, ground, what in decls:
        out.append((f"{pid}: state is one of {list(STATES)}", state in STATES,
                    f"got {state!r}"))
        out.append((f"{pid}: ground is one of {list(GROUNDS)}", ground in GROUNDS,
                    f"got {ground!r} -- a free-text ground is one nobody can check"))
        out.append((f"{pid}: says what it changes", len(what.strip()) >= 20,
                    f"got {what[:40]!r}"))
    # Every patch written up for the consumer must also be declared here, and the
    # reverse: a declaration for a patch nobody wrote up is a promise with no artifact.
    written = set(re.findall(r"^## (P-\d+)", patches or "", re.M))
    declared = set(ids)
    out.append(("every patch written up for B is declared", written <= declared,
                f"written {sorted(written)} undeclared {sorted(written - declared)}"))
    out.append(("every declared patch is written up for B", declared <= written,
                f"declared {sorted(declared)} unwritten {sorted(declared - written)}"))
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
        h.replace("HELD-PATCH: P-1 [HELD]", "HELD-PATCH: P-1 [SOON]", 1), p, "state is one of")
    # THE ONE THIS FILE EXISTS FOR: my own nine-hour false ground would not compile.
    mut("a free-text ground -- the 'B is offline' shape",
        h.replace("ground=SCHEDULED-REBUILD", "ground=B-IS-OFFLINE", 1), p, "ground is one of")
    mut("a declaration that does not say what it changes",
        re.sub(r"(HELD-PATCH: P-1 \[HELD\] ground=[A-Z-]+ --).*", r"\1 x", h, count=1),
        p, "says what it changes")
    mut("a patch written up for B but not declared",
        DECL.sub("", h, count=1), p, "every patch written up for B is declared")
    mut("a declaration for a patch nobody wrote up",
        h, re.sub(r"^## P-3.*$", "## P-9 removed", p, count=1, flags=re.M),
        "every declared patch is written up")
    mut("NO declarations at all is caught, not read as clean",
        DECL.sub("", h), p, "at least one patch is declared")
    print(f"  {n} self-test checks failed")
    sys.exit(1 if n else 0)
