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


def audit(handoff, patches, today=None):
    today = today or datetime.date.today()
    out = []
    decls = DECL.findall(handoff or "")
    # POSITIVE CONTROL FIRST: a pattern that matches nothing passes every check below
    # it vacuously, and this repository has caught two dead sweeps already.
    probe = DECL.search("HELD-PATCH: P-9 [HELD] ground=AWAITING-RULING until=2099-01-01 -- a probe line\n")
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
        # THE EXPIRY ARM.
        try:
            end = datetime.date(*[int(x) for x in until.split("-")])
        except (ValueError, TypeError):
            out.append((f"{pid}: until= is a readable date", False,
                        f"got {until!r} -- an end condition nobody can evaluate is "
                        f"the same as no end condition"))
            continue
        out.append((f"{pid}: its stated end has not passed", 
                    not (state in LIVE_STATES and end < today),
                    f"declared until {end} and today is {today}. The condition that "
                    f"justified this hold is GONE. Ship it, or re-declare it with a "
                    f"ground and an end that are true now -- do not extend the date "
                    f"to make the gate quiet."))
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

    # THE EXPIRY ARMS. Every hold here reads until=2026-09-08, so this arm is DARK
    # against the real tree until September and would sit unproven for a week -- which
    # is exactly how long a hold would have to be wrong before anyone noticed. Run the
    # audit against a LATER clock instead of waiting for one.
    import datetime as _dt
    def mut_at(label, day, expect_sub, want_fire=True):
        global n
        fired = [x for x, ok, _ in audit(h, p, today=day) if not ok]
        hit = any(expect_sub in x for x in fired)
        ok = hit if want_fire else not hit
        print(f"  [{'ok' if ok else 'FAIL'}] {label}"
              + ("" if ok else f"  -- fired {fired[:2]}"))
        n += 0 if ok else 1
    mut_at("a hold whose stated end has PASSED fires",
           _dt.date(2026, 9, 9), "stated end has not passed")
    mut_at("...and does NOT fire the day before it",
           _dt.date(2026, 9, 7), "stated end has not passed", want_fire=False)
    mut_at("...nor on the end date itself",
           _dt.date(2026, 9, 8), "stated end has not passed", want_fire=False)
    mut("an unreadable end condition is caught, not skipped",
        h.replace("until=2026-09-08", "until=soon", 1), p, "is a readable date")
    # SHIPPED is not a hold. A patch that has landed cannot expire.
    shipped = h.replace("HELD-PATCH: P-1 [READY]", "HELD-PATCH: P-1 [SHIPPED]", 1)
    fired = [x for x, ok, _ in audit(shipped, p, today=_dt.date(2026, 9, 9)) if not ok]
    hit = any("P-1: its stated end" in x for x in fired)
    print(f"  [{'ok' if not hit else 'FAIL'}] a SHIPPED patch past its end does NOT "
          f"fire -- it is done, not held")
    n += 0 if not hit else 1
    print(f"  {n} self-test checks failed")
    sys.exit(1 if n else 0)
