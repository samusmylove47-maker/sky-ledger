#!/usr/bin/env python3
# PARSER-ROLE: NOT-THE-ENGINE  the engine is gapengine.py
# This file builds its own damage-line pattern for a local purpose and is NOT
# authoritative. Enforced by check_oneengine.py.
"""Support test: does the melee damage roll live on a 20-point lattice?

A quantised roll `W * (D20/10) + B` admits at most 20 distinct damage values per
(weapon, verb, target). Counting distinct values against the observed span settles
it without needing to know the weapon.

Usage:  python3 tools/lattice.py /path/to/fixtures/*.log
"""
import re, sys, collections
HIT = re.compile(r'^\[.*?\] You (slash|pierce|punch|bash|kick|strike|crush|claw) (.+?) for (\d+) points of damage\.\s*$')
by = collections.defaultdict(list)
for fn in sys.argv[1:]:
    for ln in open(fn, errors='replace'):
        m = HIT.match(ln)
        if m: by[(fn.split('/')[-1], m.group(1), m.group(2))].append(int(m.group(3)))
print(f"{'file':<34}{'verb':<8}{'target':<24}{'n':>5}{'distinct':>9}{'span':>6}{'cover':>8}")
bad = 0
for k, v in sorted(by.items(), key=lambda x: -len(x[1]))[:12]:
    if len(v) < 60: continue
    u = len(set(v)); span = max(v) - min(v) + 1
    if u > 20: bad += 1
    print(f"{k[0][:34]:<34}{k[1]:<8}{k[2][:24]:<24}{len(v):>5}{u:>9}{span:>6}{u/span*100:>7.1f}%")
print(f"\n{bad} group(s) exceed 20 distinct values. Any one of them refutes the lattice.")
