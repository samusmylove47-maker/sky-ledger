#!/usr/bin/env python3
"""validate_jos437.py -- re-run the chain against the one fully-pinned character.

jos437-finishing-blow.log: PAL/MNK/ENC at 50, both weapons identified from their
own damage endpoints (U = 2*DMG + 1), provably in Offensive stance (93.6% even
damage), 395 s engaged. Nothing here is fitted to its damage.

Run it rather than trusting the prose. DAMAGE-CHAIN.md carried a sentence saying
this came out at 381 against 381.0 without naming a lane-rate setting; it does
so at one of the two and misses by +23.6% at the other, and even the close one
agrees by cancellation.
"""
import model4 as M

TRIO = {'PAL', 'MNK', 'ENC'}
MODE = 'avg'
MAIN = ('Thelvorn +10', 40, 26, '1H')     # slash
OFF  = ("Wu's Fist +10", 32, 22, '1H')    # punch
MEASURED = {'slash': 148.7, 'punch': 92.5, 'bash': 38.5,
            'kick': 22.8, 'smite': 57.2, 'strike': 21.3}
MEASURED_TOTAL = sum(MEASURED.values())
MEASURED_RATE = {'slash': 1.111, 'punch': 1.132}

off = max(M.OFFENSE[c] for c in TRIO)
wrath = off + M.STR_MOD + M.SPELL_ATK
sm = M.STANCE_DMG
pland = M.P_LAND_BAL * M.ACC_OFF
hm = 1 + (M.HASTE_CAP + M.MNK_ALACRITY_ADD) / 100.0

r_mh = hm / (MAIN[2] / 10.0) * M.MH_CHAIN
r_oh = min(hm / (OFF[2] / 10.0) * M.OH_CHAIN * M.DW_SUCCESS, M.OH_RATE_CAP)
slash = M.lane_dps(2*MAIN[1]+1, M.bonus(MAIN[1], MAIN[2], M.HAND_1H), r_mh,
                   wrath, MODE, sm, pland, M.CRIT_RATE, M.CRIT_MULT, 0.0)
punch = M.lane_dps(2*OFF[1]+1, 0.0, r_oh,
                   wrath, MODE, sm, pland, M.CRIT_RATE, M.CRIT_MULT, 0.0)
scale = M.e_rx(wrath, MODE) * M.MITF[MODE] / (M.E_RX_BASE * M.MITF['avg'])

print(f"wrath {wrath:.0f}   haste {M.HASTE_CAP + M.MNK_ALACRITY_ADD:.0f}"
      f"   stance x{sm:.2f}   mitigation '{MODE}'")
print(f"swing rate  slash {r_mh:.3f}/s vs {MEASURED_RATE['slash']:.3f} measured"
      f"  ({100*(r_mh/MEASURED_RATE['slash']-1):+.1f}%)")
print(f"swing rate  punch {r_oh:.3f}/s vs {MEASURED_RATE['punch']:.3f} measured"
      f"  ({100*(r_oh/MEASURED_RATE['punch']-1):+.1f}%)")
print()

for tag, R in (('max  (abilities on cooldown)', M.LANE_RATE_MAX),
               ('med  (corpus median)',         M.LANE_RATE_MED)):
    pred = {'slash': slash, 'punch': punch}
    for ln in ('bash', 'kick', 'strike', 'smite'):
        v = R[ln] * pland * M.LANE_MEAN[ln] * scale * sm
        if ln == 'smite':
            v += R[ln] * pland * M.SMITE_RIDER
        pred[ln] = v
    tot = sum(pred.values())
    print(f"rates = {tag}")
    print(f"  {'lane':<8} {'pred':>8} {'meas':>8} {'err':>9}")
    for ln in MEASURED:
        print(f"  {ln:<8} {pred[ln]:8.1f} {MEASURED[ln]:8.1f} "
              f"{100*(pred[ln]/MEASURED[ln]-1):+8.1f}%")
    print(f"  {'TOTAL':<8} {tot:8.1f} {MEASURED_TOTAL:8.1f} "
          f"{100*(tot/MEASURED_TOTAL-1):+8.1f}%")
    worst = max(MEASURED, key=lambda k: abs(pred[k]/MEASURED[k]-1))
    print(f"  worst single lane: {worst} at {100*(pred[worst]/MEASURED[worst]-1):+.1f}%"
          f"  -- a total is not a validation while a lane is this far out.")
    print()
