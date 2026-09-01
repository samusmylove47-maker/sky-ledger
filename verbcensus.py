#!/usr/bin/env python3
"""verbcensus.py -- what first-person damage verbs actually occur, over every EQ log
on this machine, deduplicated by content.

WHY THIS FILE EXISTS. I published "117 logs, 282,615 stamped lines" as the population
behind the biggest accuracy finding in this tree (six damage verbs the meter cannot
see). That measurement was run by hand and left no script, so it was not reproducible
from this repository -- the same defect as a fixture nothing produces. Worse, 117 was
a SUBTREE. There are 416 log-shaped files here across seven trees, and three of those
trees vendor the same sample files, so a naive count triple-counts them.

A verb share is only a share against the population its numerator came from. This
file names that population, dedupes it by sha256, and states the count it opened
(R73).

    python3 verbcensus.py [--root DIR] [--json]
    python3 verbcensus.py --selftest
"""
import argparse, hashlib, io, json, os, re, sys

# The EQ log stamp. Day is [ 0-9][0-9] because a single-digit day is space-padded --
# refuted on this corpus, but the pattern stays wide because the cost of being wrong
# is silent and the cost of being wide is nothing.
STAMP = re.compile(r"^\[[A-Z][a-z]{2} [A-Z][a-z]{2} [ \d]\d \d{2}:\d{2}:\d{2} \d{4}\]")

# First-person damage. The verb is left OPEN on purpose: the whole point is to find
# verbs no hand-written list contains. `for N points of damage.` with no qualifier is
# the melee form; `points of <adjective> damage` is a spell and is counted apart.
DMG = re.compile(
    r"^\[[^\]]+\] You ([a-z]+) (.+?) for (\d+) points of ([a-z]+ )?damage\.")

SELF = {"yourself"}

# What gapengine.py's MELEE pattern reads today. Kept as a literal rather than
# imported so this census stays a measurement of the LOGS and does not silently
# change meaning when the engine changes. Cross-checked against the engine below.
# UPDATED when the Tuesday bundle landed: nine verbs became nineteen. Kept as a
# LITERAL rather than imported, deliberately, so this file stays a measurement of the
# LOGS and does not silently change meaning when the engine changes -- but the
# self-test below compares it against the engine's live sets, so drift fails loudly.
ENGINE_VERBS = {"backstab", "bash", "bite", "claw", "cleave", "crush", "frenzy",
                "hit", "kick", "pierce", "punch", "reave", "shoot", "slash", "slice",
                "smash", "smite", "sting", "strike"}


def census(paths):
    """Returns (per-verb rows, files opened, files unique, stamped lines)."""
    seen, stamped, files_open = set(), 0, 0
    verbs = {}          # verb -> [lines, damage, files-containing]
    for p in paths:
        files_open += 1
        try:
            raw = io.open(p, "rb").read()
        except OSError:
            continue
        h = hashlib.sha256(raw).hexdigest()
        if h in seen:
            continue        # the same log vendored into three trees is ONE log
        seen.add(h)
        here = set()
        for line in raw.decode("utf-8", "replace").splitlines():
            line = line.rstrip("\r")
            if not STAMP.match(line):
                continue
            stamped += 1
            m = DMG.match(line)
            if not m:
                continue
            verb, target, amt, qual = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            if qual:                       # `points of magic damage` -- a spell
                continue
            if target.strip().lower() in SELF:
                continue                   # a self-hit is not an attack on a mob
            row = verbs.setdefault(verb, [0, 0, 0])
            row[0] += 1
            row[1] += amt
            here.add(verb)
        for v in here:
            verbs[v][2] += 1
    rows = sorted(((v, n, d, f) for v, (n, d, f) in verbs.items()),
                  key=lambda r: -r[1])
    return rows, files_open, len(seen), stamped


def perlog(paths):
    """Invisible-damage share PER LOG. The corpus-wide share is an average over a
    population no player is; what a player sees is one log. A 12% corpus average and
    a log where every melee line is invisible are both true and only one of them is
    the user's experience."""
    seen, out = set(), []
    for p in paths:
        try:
            raw = io.open(p, "rb").read()
        except OSError:
            continue
        h = hashlib.sha256(raw).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        vis = inv = 0
        for line in raw.decode("utf-8", "replace").splitlines():
            m = DMG.match(line.rstrip("\r"))
            if not m or m.group(4) or m.group(2).strip().lower() in SELF:
                continue
            if m.group(1) in ENGINE_VERBS:
                vis += int(m.group(3))
            else:
                inv += int(m.group(3))
        if vis + inv:
            out.append((os.path.basename(p), inv, vis + inv, 100.0 * inv / (vis + inv)))
    return sorted(out, key=lambda r: -r[3])


def find(root):
    out = []
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for n in names:
            if n.endswith((".txt", ".log")):
                out.append(os.path.join(dirpath, n))
    return sorted(out)


def is_log(p):
    try:
        with io.open(p, "rb") as f:
            head = f.read(4096).decode("utf-8", "replace")
    except OSError:
        return False
    return any(STAMP.match(l) for l in head.splitlines())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/user")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--perlog", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        import tempfile
        print("SELFTEST -- the census must find a verb no list contains")
        bad = 0
        d = tempfile.mkdtemp()
        S = "[Mon Aug 31 12:00:0%d 2026] "
        body = "\n".join([
            S % 0 + "You slash a gnoll for 10 points of damage.",
            # `gnaw` is the control BECAUSE it is outside every list: it comes from
            # Shara's shipped parser and Session C measures it at ZERO across 5.6M
            # lines, as do I. The control used to be `frenzy`, which the Tuesday
            # bundle ADDED -- so the positive control silently became a negative one
            # and this check failed the moment the engine caught up with it. A control
            # must name something the thing under test genuinely cannot know.
            S % 1 + "You gnaw a gnoll for 40 points of damage.",   # NOT in the engine
            S % 2 + "You hit a gnoll for 7 points of magic damage.",    # a spell, excluded
            S % 3 + "You hit yourself for 500 points of damage.",       # self, excluded
            S % 4 + "a gnoll hits YOU for 9 points of damage.",         # inbound, no stamp match on `You `
        ])
        one = os.path.join(d, "a.txt")
        io.open(one, "w").write(body + "\n")
        two = os.path.join(d, "b.txt")          # a byte-identical copy: must dedupe
        io.open(two, "w").write(body + "\n")

        rows, opened, uniq, stamped = census([one, two])
        got = {v: (n, dd) for v, n, dd, _ in rows}

        def chk(name, ok, detail=""):
            global bad
            print(f"  [{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -- {detail}"))
            bad += 0 if ok else 1

        # POSITIVE CONTROL FIRST: a census that finds nothing passes every exclusion
        # check below it vacuously.
        chk("finds a verb the engine's list does NOT contain",
            "gnaw" in got and "gnaw" not in ENGINE_VERBS, f"got {sorted(got)}")
        chk("finds the verb the engine DOES contain", got.get("slash") == (1, 10),
            f"slash -> {got.get('slash')}")
        chk("a qualified damage line is not counted as melee", "magic" not in got
            and got.get("hit") is None, f"hit -> {got.get('hit')}")
        chk("a self-hit is excluded", sum(n for _, n, _, _ in rows) == 2,
            f"total lines {sum(n for _, n, _, _ in rows)}")
        chk("two byte-identical files count as one log", uniq == 1 and opened == 2,
            f"opened {opened} unique {uniq}")
        chk("stamped lines counted from the unique file only", stamped == 5,
            f"stamped {stamped}")
        # DRIFT CHECK, now against the engine's LIVE SETS rather than a regex over a
        # literal alternation. The old version scraped `^You (a|b|c)` out of the source;
        # the moment MELEE was built from a variable that regex returned None and the
        # check CRASHED instead of failing -- a scraper that reads source text is a
        # measurement of formatting, not of behaviour.
        import gapengine as _G
        live = _G.LANE_VERBS | _G.AUTO_VERBS | _G.UNCLASSIFIED_VERBS
        chk("the engine verb list matches gapengine.py's live sets",
            ENGINE_VERBS == live,
            f"literal-only {sorted(ENGINE_VERBS - live)}, engine-only {sorted(live - ENGINE_VERBS)}")
        print(f"  {bad} self-test checks failed")
        sys.exit(1 if bad else 0)

    cands = find(a.root)
    paths = [p for p in cands if is_log(p)]
    rows, opened, uniq, stamped = census(paths)
    tot_n = sum(r[1] for r in rows)
    tot_d = sum(r[2] for r in rows)
    miss_n = sum(r[1] for r in rows if r[0] not in ENGINE_VERBS)
    miss_d = sum(r[2] for r in rows if r[0] not in ENGINE_VERBS)

    if a.perlog:
        rr = perlog(paths)
        band = [0, 0, 0, 0]
        for _, _, _, pct in rr:
            band[0 if pct == 0 else 1 if pct < 10 else 2 if pct < 50 else 3] += 1
        print(f"{len(rr)} unique logs with at least one first-person melee damage line")
        print(f"  {band[0]:>4}  0%          the meter sees everything")
        print(f"  {band[1]:>4}  0-10%       a rounding-scale error")
        print(f"  {band[2]:>4}  10-50%      the number on screen is wrong")
        print(f"  {band[3]:>4}  50-100%     the meter is measuring a different fight")
        print()
        print("  worst 12 logs by invisible share of first-person melee damage:")
        for n, inv, tot, pct in rr[:12]:
            print(f"    {pct:6.2f}%  {inv:>8,} / {tot:>8,}  {n[:58]}")
        sys.exit(0)

    if a.json:
        print(json.dumps({"root": a.root, "files_named": len(cands),
                          "files_opened": opened, "logs_unique": uniq,
                          "stamped_lines": stamped, "melee_lines": tot_n,
                          "melee_damage": tot_d, "invisible_lines": miss_n,
                          "invisible_damage": miss_d,
                          "verbs": [{"verb": v, "lines": n, "damage": d, "logs": f,
                                     "engine_reads": v in ENGINE_VERBS}
                                    for v, n, d, f in rows]}, indent=2))
        sys.exit(0)

    print(f"root {a.root}")
    print(f"named {len(cands)} .txt/.log files, OPENED {opened} that look like EQ logs, "
          f"{uniq} UNIQUE by sha256 ({opened - uniq} duplicate copies skipped)")
    print(f"{stamped:,} stamped lines")
    print()
    print(f"  {'verb':<10} {'lines':>8} {'damage':>11} {'logs':>5}  engine reads it?")
    for v, n, d, f in rows:
        print(f"  {v:<10} {n:>8,} {d:>11,} {f:>5}  "
              + ("yes" if v in ENGINE_VERBS else "NO  <-- invisible"))
    print()
    print(f"  {'TOTAL':<10} {tot_n:>8,} {tot_d:>11,}")
    print(f"  invisible  {miss_n:>8,} {miss_d:>11,}   "
          f"{100.0*miss_n/tot_n:.2f}% of lines, {100.0*miss_d/tot_d:.2f}% of damage")
