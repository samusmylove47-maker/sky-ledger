#!/usr/bin/env python3
"""Multi-attack, measured from the shape of the log rather than from a formula.

Every extra attack prints its own damage line, and the client stamps to the second, so the
number of attempts sharing one timestamp is the multi-attack burst. Measured on the
committed corpus:

    slash    46.8% one · 40.2% two · 9.1% three · 3.5% four · 0.4% five   mean 1.71, max 6
    frenzy   19.8% one · 21.9% two · 26.5% three · 18.5% four · 9.0% five mean 2.89, max 7

The classic chain 1 + DA + DA*TA with DA=.476 / TA=.238 predicts 1.589 -- close to the
measured 1.71 for a main hand, and nowhere near frenzy. Berserker's Frenzy is a burst lane,
not an ordinary autoskill, and modelling it at one hit per activation understates it ~2x.

Also note (Riposte) fires 730 times against (Flurry) 35. A riposte is an EXTRA SWING that
only happens while you are being attacked -- so it is damage that accrues to whoever is
tanking, and is absent for a DPS character standing behind the boss.

Usage:  python3 tools/multiattack.py /path/to/fixtures/*.log
"""
import re, sys, collections, datetime

TS  = re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
ATT = re.compile(r'^You (?:(\w+) .+? for [\d,]+ points? of damage|try to (\w+) .+?, but )')
TAG = re.compile(r'\((Critical|Riposte|Flurry|Rampage|Strikethrough|Slay Undead|Finishing Blow|Riposte Critical|Riposte Strikethrough)\)')
MAIN = {'slash','pierce','crush','punch','claw','hit','bash','kick','strike','frenzy',
        'backstab','smite','slam','cleave','reave'}

persec = collections.defaultdict(collections.Counter)
tags = collections.Counter()
for fn in sys.argv[1:]:
    sec = collections.defaultdict(collections.Counter)
    for ln in open(fn, errors='replace'):
        m = TS.match(ln.rstrip('\n'))
        if not m:
            continue
        t = datetime.datetime(int(m.group(7)), MON[m.group(2)], int(m.group(3)),
                              int(m.group(4)), int(m.group(5)), int(m.group(6)))
        x = m.group(8)
        for g in TAG.findall(x):
            tags[g] += 1
        a = ATT.match(x)
        if not a:
            continue
        v = a.group(1) or a.group(2)
        if v in MAIN:
            sec[v][t] += 1
    for v, c in sec.items():
        for t, n in c.items():
            persec[v][n] += 1

print("ATTEMPTS SHARING ONE TIMESTAMP  (this is the multi-attack burst)")
print(f"{'verb':<10}{'seconds':>9}   " + ''.join(f"{k:>7}" for k in range(1, 9)) + f"{'mean':>8}{'max':>5}")
for v, c in sorted(persec.items(), key=lambda x: -sum(x[1].values())):
    tot = sum(c.values())
    if tot < 80:
        continue
    mean = sum(k * n for k, n in c.items()) / tot
    row = ''.join(f"{c.get(k,0)/tot*100:>6.1f}%" for k in range(1, 9))
    print(f"{v:<10}{tot:>9}   {row}{mean:>8.2f}{max(c):>5}")
print("\nDAMAGE TAGS  (Riposte/Flurry/Rampage/Strikethrough are EXTRA SWINGS):")
for k, v in tags.most_common():
    print(f"   {v:>6}  ({k})")
