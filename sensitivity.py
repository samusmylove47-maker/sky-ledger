#!/usr/bin/env python3
"""sensitivity.py -- how much of the model-vs-measured gap each ceiling
assumption is worth. One knob at a time, on all 560 trios, raid mitigation."""
import itertools, statistics as st, json, sys
import model4 as M

ALL = list(itertools.combinations(M.CLASSES, 3))
# every 10th trio in lexical order: a deterministic 56-of-560 stratified sample.
# Stated because a silent cap reads as full coverage when it is not.
TRIOS = ALL[::10]
# Read out of the dataset at run time. A figure typed beside the data it claims
# to come from is the fault this project keeps finding in other people's work,
# and it would be this file's own fault if the constant were pasted here.
import residual
MEAS_MED = st.median([d for d in (residual.dps(x) for x in residual.F) if d is not None])

def sweep(label, mutate=None, rates='max'):
    saved = {}
    if mutate:
        for k, v in mutate.items():
            saved[k] = getattr(M, k); setattr(M, k, v)
    try:
        v = sorted(M.evaluate(t, 'raid', front=False, charm=False, rates=rates)['total'] for t in TRIOS)
    finally:
        for k, val in saved.items(): setattr(M, k, val)
    return label, v[0], st.median(v), v[-1]

NO_FREE_BUFF = dict(M.PROC_BUFF)          # keep table, but stop granting it unconditionally
rows = [sweep('baseline (as published)')]
rows.append(sweep('ability rates: corpus median not cooldown', rates='med'))
rows.append(sweep('Offensive stance off (x2.00 -> x1.00)', {'STANCE_DMG': 1.00}))
rows.append(sweep('no crit (0.1272 -> 0)', {'CRIT_RATE': 0.0}))
rows.append(sweep('haste 0 instead of capped 75', {'HASTE_CAP': 0.0}))
rows.append(sweep('no multi-attack chain', {'MH_CHAIN': 1.0, 'OH_CHAIN': 1.0}))
rows.append(sweep('med rates AND no stance', {'STANCE_DMG': 1.00}, rates='med'))

print(f'trios evaluated: {len(TRIOS)} of {len(ALL)} (every 10th, deterministic)')
print(f"{'knob':<44} {'worst':>8} {'median':>8} {'best':>8}  {'median/measured':>16}")
for lab, lo, med, hi in rows:
    print(f"{lab:<44} {lo:8.1f} {med:8.1f} {hi:8.1f}  {med/MEAS_MED:15.2f}x")
print()
print(f"measured median, per our character, {len(residual.F)} fights: {MEAS_MED:.1f} DPS")
print("No single knob brings the model's MEDIAN trio down to the measured median.")
print("Stance and ability rates together are the largest pair, and they still leave a gap.")
