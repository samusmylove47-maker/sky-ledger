#!/usr/bin/env python3
"""Does a non-weapon Exaltation deal damage?

The client prints "Your <item> (Exaltation) <verb>." whenever an Exaltation fires. If those
were damage procs, a spell-damage line would follow. The test needs a CONTROL, because a
busy combat log has spell damage flying constantly: we compare the +/-1s hit rate around an
Exaltation message against the same window around an ordinary melee swing.

Result on the committed corpus: control 20.9%, Exaltation messages 16.9% -- BELOW chance.
Every armour and jewellery Exaltation sits at or under the baseline. They are worn and click
effects, not damage procs. This independently confirms the player's rule that only PRIMARY,
SECONDARY (and a Ranger's RANGED) proc sockets fire in combat.

Usage:  python3 tools/exaltation.py /path/to/fixtures/*.log
"""
import re, sys, collections, datetime

TS  = re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
EX  = re.compile(r'^Your (.+?) \(Exaltation\) (.+?)\.$')
SPD = re.compile(r'^You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.')
MEL = re.compile(r'^You (\w+) (.+?) for ([\d,]+) points? of damage\.')

def near(rows, i, t, rx, window=1.0):
    for j in range(max(0, i - 4), min(len(rows), i + 5)):
        if abs((rows[j][0] - t).total_seconds()) > window:
            continue
        if rx.match(rows[j][1]):
            return True
    return False

ex_hit = ex_n = ctl_hit = ctl_n = 0
per = collections.defaultdict(lambda: [0, 0])
for fn in sys.argv[1:]:
    rows = []
    for ln in open(fn, errors='replace'):
        m = TS.match(ln.rstrip('\n'))
        if m:
            t = datetime.datetime(int(m.group(7)), MON[m.group(2)], int(m.group(3)),
                                  int(m.group(4)), int(m.group(5)), int(m.group(6)))
            rows.append((t, m.group(8)))
    for i, (t, x) in enumerate(rows):
        m = EX.match(x)
        if m:
            h = near(rows, i, t, SPD)
            ex_n += 1; ex_hit += h
            p = per[m.group(1)]; p[0] += 1; p[1] += h
        elif MEL.match(x) and i % 7 == 0:       # deterministic control sample
            ctl_n += 1; ctl_hit += near(rows, i, t, SPD)

if not ctl_n:
    sys.exit('no control samples — pass more logs')
base = ctl_hit / ctl_n * 100
print(f"CONTROL  spell damage within +/-1s of an ordinary melee swing: {ctl_hit}/{ctl_n} = {base:.1f}%")
print(f"POOLED   same window around an (Exaltation) message:           {ex_hit}/{ex_n} = {ex_hit/ex_n*100:.1f}%")
print(f"\n{'source':<26}{'fires':>7}{'w/dmg':>7}{'rate':>8}   verdict")
for s, (n, h) in sorted(per.items(), key=lambda x: -x[1][0]):
    r = h / n * 100
    v = ('DAMAGE PROC' if r > base * 2.5 else 'at/below chance -> NOT a damage proc') if n >= 20 else 'n too small'
    print(f"{s[:26]:<26}{n:>7}{h:>7}{r:>7.0f}%   {v}")
