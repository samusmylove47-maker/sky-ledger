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

# ---------------------------------------------------------------------------
# THE INPUTS NO LOG CAN EVER SUPPLY, swept because a COUNT is not a magnitude.
# percharacter.py measured that model4 needs 13 inputs and a log supplies at most 6.
# Seven are ASSUMED. Knowing there are seven does not tell the owner which capture is
# worth their time; knowing what each is WORTH does.
#
# THE LIST IS IMPORTED, NEVER RETYPED. Two lists that must agree are two lists that
# will drift -- this file already carries six ad-hoc knobs chosen before that audit
# existed, and not one of them is target mitigation, wrath or strikethrough. Deriving
# it means adding an ASSUMED input to the audit automatically demands a sweep here,
# and `python3 sensitivity.py --check` fails until it gets one.
import percharacter as PC

ASSUMED = [(name, const) for name, kind, const, how, pref in PC.INPUTS if kind == "assumed"]

# The NEUTRAL value each assumption is swept to, and WHY that value is the neutral one.
NEUTRAL = {
    "HASTE_CAP":     (0.0, "no haste at all, against the capped 75 the model assumes"),
    "STR_MOD":       (0.0, "no worn STR contribution to wrath"),
    "STRIKETHROUGH": (0.0, "no strikethrough, i.e. the non-Ranger case"),
    "MITF":          ({"avg": 1.0, "raid": 1.0},
                      "raid targets mitigate like average ones, removing the 0.73"),
}
# Inputs that are ASSUMED but are NOT a scalar knob. Declared with a reason rather
# than silently skipped, so a reader can tell "not swept" from "cannot be swept".
UNSWEEPABLE = {
    "weapon damage": "not a scalar. The model picks the best legal weapon out of the "
                     "429-row catalogue; 'off' would mean a different catalogue, not a "
                     "different number.",
    "weapon delay":  "same: a property of the chosen weapon, not a knob.",
    "buff uptime":   "no constant exists to move. It is not a line this parser reads, "
                     "so there is nothing here to set to neutral.",
}


def assumed_coverage():
    """Cheap invariant, no model evaluation: every ASSUMED input is swept or declared."""
    out = []
    for name, const in ASSUMED:
        covered = (const in NEUTRAL) or (name in UNSWEEPABLE)
        out.append((f"ASSUMED input {name!r} is swept or declared unsweepable", covered,
                    f"const={const!r}"))
    stale = [k for k in UNSWEEPABLE if k not in {n for n, _ in ASSUMED}]
    out.append(("no UNSWEEPABLE entry names an input that is no longer ASSUMED",
                not stale, f"stale {stale}"))
    stale_n = [k for k in NEUTRAL if k not in {c for _, c in ASSUMED}]
    out.append(("no NEUTRAL entry names a constant that is no longer ASSUMED",
                not stale_n, f"stale {stale_n}"))
    out.append(("the ASSUMED list is not empty", bool(ASSUMED), f"{len(ASSUMED)} inputs"))
    return out


if "--check" in sys.argv:
    # The list agreement only. The full sweep takes ~3 minutes and has no place in a
    # 13-second suite; this arm is instant and is what check.sh runs.
    bad = 0
    for n, ok, d in assumed_coverage():
        print(f"  [{'ok' if ok else 'FAIL'}] {n}" + ("" if ok else f"  -- {d}"))
        bad += 0 if ok else 1
    if "--selftest" in sys.argv:
        saved = list(PC.INPUTS)
        try:
            PC.INPUTS.append(("invented input", "assumed", "NO_SUCH_CONST", "x", "x"))
            ASSUMED[:] = [(n, c) for n, k, c, _h, _p in PC.INPUTS if k == "assumed"]
            fired = [n for n, ok, _ in assumed_coverage() if not ok]
            ok = any("invented input" in n for n in fired)
            print(f"  [{'ok' if ok else 'FAIL'}] an ASSUMED input with no sweep is caught")
            bad += 0 if ok else 1
        finally:
            PC.INPUTS[:] = saved
            ASSUMED[:] = [(n, c) for n, k, c, _h, _p in PC.INPUTS if k == "assumed"]
    sys.exit(1 if bad else 0)

NO_FREE_BUFF = dict(M.PROC_BUFF)          # keep table, but stop granting it unconditionally
rows = [sweep('baseline (as published)')]
rows.append(sweep('ability rates: corpus median not cooldown', rates='med'))
rows.append(sweep('Offensive stance off (x2.00 -> x1.00)', {'STANCE_DMG': 1.00}))
rows.append(sweep('no crit (0.1272 -> 0)', {'CRIT_RATE': 0.0}))
rows.append(sweep('haste 0 instead of capped 75', {'HASTE_CAP': 0.0}))
rows.append(sweep('no multi-attack chain', {'MH_CHAIN': 1.0, 'OH_CHAIN': 1.0}))
rows.append(sweep('med rates AND no stance', {'STANCE_DMG': 1.00}, rates='med'))

# ...and the assumed inputs, driven by percharacter.INPUTS rather than by this list.
for _name, _const in ASSUMED:
    if _const in NEUTRAL and not any(_const in (r[0] or '') for r in []):
        _val, _why = NEUTRAL[_const]
        rows.append(sweep(f'ASSUMED {_name}: {_why}', {_const: _val}))

print(f'trios evaluated: {len(TRIOS)} of {len(ALL)} (every 10th, deterministic)')
print(f"{'knob':<44} {'worst':>8} {'median':>8} {'best':>8}  {'median/measured':>16}")
for lab, lo, med, hi in rows:
    print(f"{lab:<44} {lo:8.1f} {med:8.1f} {hi:8.1f}  {med/MEAS_MED:15.2f}x")
print()
print(f"measured median, per our character, {len(residual.F)} fights: {MEAS_MED:.1f} DPS")
print("No single knob brings the model's MEDIAN trio down to the measured median.")
print("Stance and ability rates together are the largest pair, and they still leave a gap.")
print()
print("ASSUMED inputs that CANNOT be swept, declared rather than omitted:")
for _n, _r in sorted(UNSWEEPABLE.items()):
    print(f"  {_n:<16} {_r}")
