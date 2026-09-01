#!/usr/bin/env python3
"""check_timeclaims.py -- no document in this tree may claim a time that has not
happened yet.

WHY. On 1 Sep between 16:01Z and 16:25Z I wrote TWELVE timestamps into this
repository -- into the Director's polled channel, into Session B's handover, and into
two shipped Python files -- dated 16:30Z through 18:05Z. Every one was in the future.
I did not read a clock; I estimated elapsed time from how much work I had done and
typed the result. The instrument was `date`, it costs nothing, and it was sitting
right there.

That is fault shape (8) -- having the measurement and not reading it -- and it landed
in the same four commits whose SUBJECT LINES are about not asserting unsourced values.
A timestamp is a number. "Never invent a number" does not have an exception for the
ones that look like formatting.

Nothing here judges whether a timestamp is CORRECT -- only whether it is POSSIBLE. A
future date is the one error a clock can prove on its own.

    python3 check_timeclaims.py
    python3 check_timeclaims.py --selftest
"""
import datetime, io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}

# The shape this repository writes: `1 Sep 16:16Z`, `31 Aug 17:34Z`.
CLAIM = re.compile(r"\b(\d{1,2}) (" + "|".join(MONTHS) + r") (\d{2}):(\d{2})Z")

# A deliberate future reference declares itself and is counted -- the same convention
# check_timestamps.py uses for its known-bad control.
#
# THIS FILE'S OWN FIXTURES ARE THE ONLY ONES, AND THEY ARE ASSERTED AT AN EXACT COUNT,
# NOT CAPPED. On its first run this gate fired on its own self-test strings: a true
# positive on a false target, which is precisely what check_timestamps.py did the
# first time it ran. The obvious fixes are both holes -- skipping this file blinds the
# scanner to itself, and a cap I raise whenever it binds is not a cap. An EXACT count
# fires in BOTH directions: if a fixture is added or removed without updating this
# number, the gate fails and I have to look.
EXEMPT = "FUTURE-TIME-OK"
SELF = os.path.basename(__file__) if "__file__" in dir() else "check_timeclaims.py"
EXEMPT_HERE = 5       # the self-test fixtures below, exactly
EXEMPT_ELSEWHERE = 0  # no document in this tree has a legitimate future claim yet

SCAN = (".md", ".py", ".sh", ".js")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def claims(text, year):
    """Every parseable time claim in `text`, as (datetime, line, exempt?)."""
    out = []
    for line in text.splitlines():
        for m in CLAIM.finditer(line):
            d, mon, hh, mm = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)), int(m.group(4))
            try:
                t = datetime.datetime(year, mon, d, hh, mm, tzinfo=datetime.timezone.utc)
            except ValueError:
                continue
            out.append((t, line.strip(), EXEMPT in line))
    return out


def audit(files, now):
    """files: list of (path, text). Returns (rows, {path: exempt_count})."""
    rows, exempt = [], {}
    for path, text in files:
        for t, line, ex in claims(text, now.year):
            if t <= now:
                continue
            if ex:
                exempt[path] = exempt.get(path, 0) + 1
                continue
            rows.append((path, t, line))
    return rows, exempt


def tree():
    out = []
    for d, dirs, names in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in names:
            if n.endswith(SCAN):
                p = os.path.join(d, n)
                try:
                    out.append((os.path.relpath(p, ROOT),
                                io.open(p, encoding="utf-8", errors="replace").read()))
                except OSError:
                    pass
    return out


if __name__ == "__main__":
    now = datetime.datetime.now(datetime.timezone.utc)

    if "--selftest" in sys.argv:
        print("SELFTEST -- a future claim must fire, a past one must not")
        bad = 0

        def chk(name, ok, d=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {d}"))
            bad += 0 if ok else 1

        fake = datetime.datetime(2026, 9, 1, 16, 36, tzinfo=datetime.timezone.utc)
        # POSITIVE CONTROL FIRST: a pattern that parses nothing reports a clean tree
        # for every input, and this repository has shipped two dead sweeps already.
        chk("the claim pattern parses a known-good line",
            len(claims("written 1 Sep 16:16Z by me", 2026)) == 1,
            f"parsed {claims('written 1 Sep 16:16Z by me', 2026)}")
        r, _ = audit([("f.md", "landed 1 Sep 18:05Z")], fake)   # FUTURE-TIME-OK fixture
        chk("a FUTURE claim fires", len(r) == 1, f"{r}")
        r, _ = audit([("f.md", "landed 1 Sep 16:16Z")], fake)
        chk("a PAST claim does not fire", not r, f"{r}")
        r, _ = audit([("f.md", "landed 1 Sep 16:36Z")], fake)
        chk("the current minute is not 'future'", not r, f"{r}")
        r, e = audit([("f.md", f"scheduled 2 Sep 09:00Z {EXEMPT}")], fake)  # FUTURE-TIME-OK
        chk("a declared future reference is exempt and COUNTED PER FILE",
            not r and e == {"f.md": 1}, f"rows {r} exempt {e}")
        r, _ = audit([("f.md", "scheduled 2 Sep 09:00Z")], fake)  # FUTURE-TIME-OK fixture
        chk("...but an UNdeclared one still fires", len(r) == 1, f"{r}")
        r, _ = audit([("f.md", "the 12 timestamps: 1 Sep 17:20Z and 1 Sep 17:55Z")], fake)  # FUTURE-TIME-OK x2
        chk("every claim on a line is checked, not just the first", len(r) == 2, f"{r}")
        r, _ = audit([("f.md", "31 Feb 10:00Z is not a date")], fake)
        chk("an impossible date is skipped, not crashed on", not r, f"{r}")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    files = tree()
    rows, exempt = audit(files, now)
    print(f"read {len(files)} files under {os.path.basename(ROOT)}/ "
          f"({', '.join(SCAN)}); clock {now:%Y-%m-%d %H:%M}Z")
    total = sum(len(claims(t, now.year)) for _, t in files)
    here = exempt.pop(SELF, 0)
    other = sum(exempt.values())
    print(f"  {total:,} time claims parsed; {here} declared exemption(s) in {SELF} "
          f"(expect exactly {EXEMPT_HERE}), {other} elsewhere "
          f"(expect exactly {EXEMPT_ELSEWHERE})")
    fail = False
    if here != EXEMPT_HERE:
        print(f"  [FAIL] this file's own fixture count moved: {here} != {EXEMPT_HERE}. "
              f"Update the constant deliberately, or the exemption is drifting.")
        fail = True
    if other != EXEMPT_ELSEWHERE:
        print(f"  [FAIL] {other} {EXEMPT} marker(s) outside this file: "
              f"{sorted(exempt)} -- expected {EXEMPT_ELSEWHERE}")
        fail = True
    if fail:
        sys.exit(1)
    if not rows:
        print("  [ok] no document claims a time that has not happened yet")
        sys.exit(0)
    for p, t, line in rows[:20]:
        print(f"  [FAIL] {p}: claims {t:%d %b %H:%M}Z -- {line[:70]}")
    print(f"  {len(rows)} future-dated claim(s)")
    sys.exit(1)
