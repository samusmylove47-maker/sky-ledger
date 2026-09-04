#!/usr/bin/env python3
# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# This file builds its own damage-line pattern for a local purpose and is NOT
# authoritative. Enforced by check_oneengine.py.
"""Peak-to-sustained DPS ratios — the conversion between what a model computes and what a
player quotes.

A damage model computes SUSTAINED ENGAGED DPS. A player reading a meter usually quotes the
BEST PARSE — the best 60-second window. On the committed corpus those differ by a stable
factor, so comparing one against the other without converting is an apples-to-oranges error
worth about 25%.

Measured over 30 fights:
    best-60s / engaged = 1.22 median (1.19 mean)
    best-30s / engaged = 1.45 median
    best-10s / engaged = 2.03 median

Usage:  python3 tools/convention.py /path/to/fixtures/*.log
"""
import re, sys, datetime, statistics

TS  = re.compile(r'^\[(\w{3}) (\w{3}) +(\d+) (\d+):(\d+):(\d+) (\d+)\] (.*)$')
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
SPL = re.compile(r'^You (?:hit )?(.+?) for ([\d,]+) points? of (\w+) damage by (.+?)\.')
DOT = re.compile(r'^(.+?) has taken ([\d,]+) damage from your (.+?)\.')
MEL = re.compile(r'^You (\w+) (.+?) for ([\d,]+) points? of damage\.')

def events(fn):
    ev = []
    for ln in open(fn, errors='replace'):
        m = TS.match(ln.rstrip('\n'))
        if not m:
            continue
        t = datetime.datetime(int(m.group(7)), MON[m.group(2)], int(m.group(3)),
                              int(m.group(4)), int(m.group(5)), int(m.group(6)))
        x = m.group(8); d = 0
        a = SPL.match(x)
        if a and ' damage by ' in x:
            d = int(a.group(2).replace(',', ''))
        else:
            a = MEL.match(x)
            if a:
                d = int(a.group(3).replace(',', ''))
            else:
                a = DOT.match(x)
                if a:
                    d = int(a.group(2).replace(',', ''))
        if d:
            ev.append((t, d))
    return ev

def best_window(ev, w):
    b = 0
    for i, (t0, _) in enumerate(ev):
        s = 0
        for t, d in ev[i:]:
            if (t - t0).total_seconds() > w:
                break
            s += d
        b = max(b, s)
    return b / w

r60, r30, r10 = [], [], []
print(f"{'engaged':>8}{'best60':>8}{'best30':>8}{'wall':>8}   {'b60/eng':>8}   file")
for fn in sys.argv[1:]:
    ev = events(fn)
    if len(ev) < 120:
        continue
    wall = (ev[-1][0] - ev[0][0]).total_seconds() or 1
    tot = sum(d for _, d in ev)
    segs, cur = [], [ev[0]]
    for e in ev[1:]:
        if (e[0] - cur[-1][0]).total_seconds() > 6:
            segs.append(cur); cur = [e]
        else:
            cur.append(e)
    segs.append(cur)
    eng = sum(max((s[-1][0] - s[0][0]).total_seconds(), 1) for s in segs)
    e_dps = tot / eng
    if e_dps < 40:
        continue
    b60, b30, b10 = best_window(ev, 60), best_window(ev, 30), best_window(ev, 10)
    r60.append(b60 / e_dps); r30.append(b30 / e_dps); r10.append(b10 / e_dps)
    print(f"{e_dps:>8.0f}{b60:>8.0f}{b30:>8.0f}{tot/wall:>8.0f}   {b60/e_dps:>8.2f}   {fn.split('/')[-1][:34]}")

if r60:
    print(f"\n  n={len(r60)} fights")
    print(f"  best-60s / engaged : median {statistics.median(r60):.2f}")
    print(f"  best-30s / engaged : median {statistics.median(r30):.2f}")
    print(f"  best-10s / engaged : median {statistics.median(r10):.2f}")
    k = statistics.median(r60)
    print("\n  Converting a SUSTAINED model number to the peak a player would quote (x%.2f):" % k)
    for s in (610, 743, 926):
        print(f"     {s:>5} sustained  ->  {s*k:>6.0f} best-60s peak")
