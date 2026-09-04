#!/usr/bin/env python3
# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# This file builds its own damage-line pattern for a local purpose and is NOT
# authoritative. Enforced by check_oneengine.py.
"""Offensive Stance parity test.

If Offensive Stance multiplies FinalDamage by exactly 2, then every damage number
logged while it is up must be even. Nothing else produces that signature, so the
parity rate is a direct, assumption-free test of the multiplier.

Usage:  python3 tools/stance.py /path/to/fixtures/*.log
"""
import re, sys, collections
STANCE = re.compile(r'^\[.*?\] .*?\b(offensive|balanced|defensive|berserker|evasive|striker) stance', re.I)
HIT    = re.compile(r'^\[.*?\] You (slash|pierce|punch|bash|kick|strike|crush|claw) (.+?) for (\d+) points of damage\.\s*$')
MISS   = re.compile(r'^\[.*?\] You try to (\w+) (.+?), but ')

dmg  = collections.defaultdict(lambda: [0, 0])   # stance -> [hits, even]
land = collections.defaultdict(lambda: [0, 0])   # stance -> [attempts, hits]
for fn in sys.argv[1:]:
    cur = 'start'
    for ln in open(fn, errors='replace'):
        m = STANCE.match(ln)
        if m:
            cur = m.group(1).lower(); continue
        m = HIT.match(ln)
        if m:
            d = dmg[cur]; d[0] += 1; d[1] += (int(m.group(3)) % 2 == 0)
            l = land[cur]; l[0] += 1; l[1] += 1; continue
        if MISS.match(ln):
            land[cur][0] += 1

print(f"{'stance':<12}{'hits':>7}{'% even dmg':>13}{'attempts':>10}{'land%':>8}")
for k in sorted(dmg, key=lambda x: -dmg[x][0]):
    n, e = dmg[k]; at, h = land[k]
    print(f"{k:<12}{n:>7}{e/n*100:>12.1f}%{at:>10}{h/at*100:>7.1f}%")
print("\nA stance at ~99% even against ~55% for the others is a x2 multiplier applied last.")
