#!/usr/bin/env python3
"""verify_upgrade.py -- the item-upgrade rule, and what our evidence actually decides.

Two rules are in play across the project:

    PCT    value(base, N) = base + floor(base * N / 10)          # percentage only
    FLOOR  value(base, N) = base + max(N, floor(base * N / 10))  # +1/tier floor

`EQUIPMENT-TRUTH.md` section 2 grades FLOOR tier M off a client tooltip.
Session B grades PCT tier M off five client captures of weapon damage.
`model4.py`'s up10() shipped FLOOR; B's `upgrade.ts` ships PCT.

This script asks one question of both bodies of evidence: does any capture in
either of them land where the two rules give different answers?

Run:  python3 verify_upgrade.py        (exit 0 = every assertion below holds)
"""
import json, os, sys

REPO = os.path.dirname(os.path.abspath(__file__))

def pct(base, N):   return base + (base * N) // 10
def floorr(base, N): return base + (max(N, (base * N) // 10) if N else 0)

# Rules the captures are graded against, for completeness.
def lin10(base, N): return int(base * (1 + 0.10 * N))
def lin5(base, N):  return int(base * (1 + 0.05 * N))
def cmp10(base, N): return int(base * (1.10 ** N))

def distinguishes(base, N):
    return pct(base, N) != floorr(base, N)

# --------------------------------------------------------------------------
# 1. The two capture sets, verbatim.
# --------------------------------------------------------------------------
# Session B, research/validation/TIER0-VALIDATION.md:10-27 -- weapon damage.
B_CAPTURES = [("Whitened Treant Fists", 14,  0, 14),
              ("Whitened Treant Fists", 14,  1, 15),
              ("Whitened Treant Fists", 14,  2, 16),
              ("Whitened Treant Fists", 14,  3, 18),
              ("Earthshaker",           37, 10, 74)]
# Ours, EQUIPMENT-TRUTH.md:97-107 -- Midnight Clad Straps +6, five stats.
E_CAPTURES = [("Midnight Clad Straps AC",  10, 6, 16),
              ("Midnight Clad Straps STR", 13, 6, 20),
              ("Midnight Clad Straps STA", 13, 6, 20),
              ("Midnight Clad Straps INT", 13, 6, 20),
              ("Midnight Clad Straps WIS", 13, 6, 20)]

def report(title, caps):
    print(f"\n{title}")
    print(f"  {'capture':<28}{'base':>5}{'+N':>4}{'obs':>5} | {'PCT':>5}{'FLOOR':>6}{'lin10':>6}{'lin5':>6}{'cmp10':>6} | decides?")
    sc = dict(PCT=0, FLOOR=0, lin10=0, lin5=0, cmp10=0)
    ndec = 0
    for nm, b, N, obs in caps:
        v = dict(PCT=pct(b, N), FLOOR=floorr(b, N),
                 lin10=lin10(b, N), lin5=lin5(b, N), cmp10=cmp10(b, N))
        for k in sc:
            if v[k] == obs: sc[k] += 1
        d = distinguishes(b, N); ndec += d
        print(f"  {nm:<28}{b:>5}{N:>4}{obs:>5} | {v['PCT']:>5}{v['FLOOR']:>6}{v['lin10']:>6}"
              f"{v['lin5']:>6}{v['cmp10']:>6} | {'YES' if d else 'no'}")
    print(f"  exact matches out of {len(caps)}: " +
          "  ".join(f"{k} {n}" for k, n in sc.items()))
    print(f"  captures that separate PCT from FLOOR: {ndec} of {len(caps)}")
    return sc, ndec

scB, decB = report("Session B's five captures (weapon damage)", B_CAPTURES)
scE, decE = report("Our client tooltip (EQUIPMENT-TRUTH.md section 2, stats)", E_CAPTURES)

# --------------------------------------------------------------------------
# 2. Positive control -- the script CAN report a decisive capture.
# --------------------------------------------------------------------------
CONTROL = [("SYNTHETIC control, base 3 at +5", 3, 5, 8)]
scC, decC = report("POSITIVE CONTROL (invented, not evidence)", CONTROL)
assert decC == 1, "positive control failed: the detector cannot report a decisive capture"

# --------------------------------------------------------------------------
# 3. Where the two rules part company, over the whole integer domain.
# --------------------------------------------------------------------------
binds = sorted({b for b in range(1, 400) for N in range(1, 11) if distinguishes(b, N)})
print(f"\nOver base 1..399 x tier 1..10, PCT and FLOOR differ for base values: {binds}")
assert binds == list(range(1, 10)), binds
print("  -- the floor term is reachable only below base 10, and no capture in either")
print("     repository sits there. Ten captures, zero of them decisive.")

# --------------------------------------------------------------------------
# 4. What it costs in our catalogue, at the tier the model uses.
# --------------------------------------------------------------------------
ONEH = {'1H Blunt','1H Slashing','1H Piercing','Piercing','Hand to Hand'}
TWOH = {'2H Blunt','2H Slashing','2H Piercing'}
DELETED = {'Rheumguls', "Wu's Tranquil Fist", 'Beckon'}
W = {}
for f in ('sh-PRIMARY.json','sh-SECONDARY.json','sh-RANGE.json'):
    for it in json.load(open(os.path.join(REPO, f)))['items']:
        if it.get('wp'): W.setdefault(it['n'], it)
rows = []
for it in W.values():
    w = it['wp']; d, dl, sk = w.get('dmg'), w.get('dly'), w.get('skill')
    if not d or not dl or sk == 'Archery' or it['n'] in DELETED: continue
    if sk not in ONEH and sk not in TWOH: continue
    rows.append((it['n'], d))
diff = [(n, d, floorr(d, 10), pct(d, 10)) for n, d in rows if distinguishes(d, 10)]
print(f"\nCatalogue rows model4.weapon_rows() emits: {len(rows)}")
print(f"  where PCT and FLOOR disagree at +10 : {len(diff)}  ({100*len(diff)/len(rows):.1f}%)")
worst = max(diff, key=lambda r: r[2] / r[3])
print(f"  largest overstatement by FLOOR      : {worst[0]} base {worst[1]} -> "
      f"{worst[2]} vs {worst[3]}  ({worst[2]/worst[3]:.2f}x)")
print(f"  Efreeti Standard                    : base 3 -> "
      f"{floorr(3,10)} (FLOOR) vs {pct(3,10)} (PCT)")
assert 250 <= len(diff) <= 280, len(diff)
# --------------------------------------------------------------------------
# 5. What it costs the RANKINGS -- run model4 under both rules, cap on and off.
# --------------------------------------------------------------------------
print("\nmodel4 under both rules, with OH_RATE_CAP in place and removed:")
src = open(os.path.join(REPO, 'model4.py')).read()
def build(rule, cap):
    s = src
    if rule == 'FLOOR':
        s = s.replace("def up10(v,N=10): return v+(v*N)//10",
                      "def up10(v,N=10): return v+(max(N,(v*N)//10) if N else 0)")
    if not cap:
        s = s.replace("OH_RATE_CAP=1.42", "OH_RATE_CAP=1e9")
    m = {'__name__': 'x'}
    exec(compile(s, f'model4[{rule},cap={cap}]', 'exec'), m)
    return m
# Full run = 4 x 560 trios x ~429 mains x ~200 offhands, about 2 minutes. check.sh
# calls --fast, which evaluates every 10th trio (56 of 560) on the same deterministic
# stride sensitivity.py uses. NOT A SILENT CAP: the mode prints which it ran, and the
# comparison narrows with it, so a --fast pass proves less than a full one.
FAST = '--fast' in sys.argv
STRIDE = 10 if FAST else 1
print("  mode: " + (f"--fast, every {STRIDE}th trio (56 of 560)"
                    "  -- run without --fast for the whole ranking"
                    if FAST else "FULL, all 560 trios"))
grid = {}
import itertools as _it
for rule in ('PCT', 'FLOOR'):
    for cap in (True, False):
        m = build(rule, cap)
        trios = list(_it.combinations(m['CLASSES'], 3))[::STRIDE]
        res = sorted((m['evaluate'](t, 'raid') for t in trios), key=lambda r: -r['total'])
        grid[(rule, cap)] = (round(res[0]['total'], 1),
                             res[0]['oh']['n'] if res[0]['oh'] else '-',
                             tuple('+'.join(r['trio']) for r in res[:12]))
        t, oh, order = grid[(rule, cap)]
        print(f"  rule={rule:<5} cap={'1.42' if cap else 'OFF ':<4}  #1 DPS {t:>7}  "
              f"offhand {oh:<24} top12 head {order[0]}/{order[1]}")
base = grid[('PCT', True)]
assert grid[('PCT', False)] == base, "removing the cap moves the model under PCT"
assert grid[('FLOOR', True)] == base, "the two upgrade rules disagree with the cap in place"
assert grid[('FLOOR', False)] != base, "the cap is not masking anything -- check the harness"
print("  -> PCT/cap-on, PCT/cap-off and FLOOR/cap-on are IDENTICAL in DPS, offhand and top-12.")
print("     Only FLOOR/cap-off differs. OH_RATE_CAP was masking the upgrade rule,")
print("     and under PCT it is inert: removing it today changes nothing.")

print("\nAll assertions hold.")
