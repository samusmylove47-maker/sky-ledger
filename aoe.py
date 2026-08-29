#!/usr/bin/env python3
"""AOE farming — killing large numbers of monsters at once.

The previous model gated on having a tank class, which is wrong: it excluded every kiting
and caster-control trio, i.e. the entire real AOE meta. Rebuilt around three facts measured
from the spell database:

  1. NO AE spell in the game states a target cap. Damage scales linearly with the pull,
     unbounded. Pull size is therefore the dominant term.
  2. A trio is ONE character, so it casts ONE spell at a time. Throughput is set by the
     single best AE it has access to -- cast time + recast -- not by summing its casters.
  3. Cast+recast cycle, not damage per mana, decides throughput. Supernova is 854 damage
     but an 18.3s cycle; Lightning Blast is 477 on a 7.6s cycle and twice as mana-efficient.

Survivability does NOT require tanking. Four viable modes, each with its own gate.
"""
import itertools, model4 as M

from ae_spells import AE_SPELLS   # every AE >=60 damage at level <=50, per class

# PASSIVE mana income (mana/s) -- runs while you cast, costs no cast time.
#   NEC Lich +20/tick, 6s tick, permanent            = 3.33
#   BRD Chorus of Clarity +7/tick, free, group-wide  = 1.17
#   ENC clarity line                                 = 2.00
#   WIZ Harvest +251 on a 600s RECAST                = 0.42   (was 4.0 -- a 10x error)
PASSIVE = {'NEC':3.33,'BRD':1.17,'ENC':2.00,'WIZ':0.42}
BASE_REGEN = 3.0
# ACTIVE mana conversion: costs CAST TIME, so it competes with your AE for the same seconds.
#   SHM McMerin's Feast: 1.25s cast + 1.5s recast, 0 mana, +36 mana, -67 HP at 50
#   -> 13.1 mana/s IF you spend every second on it. A healer partner covers the HP.
ACTIVE = {'SHM':(36.0, 2.75)}
MANA_UNITS  = {'WIZ':100,'MAG':100,'NEC':100,'CLR':100,'DRU':100,'SHM':100,'ENC':100,
               'PAL':45,'SHD':45,'BST':45,'RNG':40,'BRD':40,'WAR':0,'MNK':0,'ROG':0,'BER':0}
MANA_PER_UNIT = 60.0
DS_PER_ATTACKER = 17.5

TANKS = {'WAR','PAL','SHD'}
# Speed at 50, from spells.json. Bard's Selo's is only +15% in Legends -- Song of Travel
# (+65%) is level 51 and out of reach, so Bard is NOT the swarm-kite engine here.
SPEED = {'DRU':75,'SHM':75,'RNG':52,'BST':30,'MAG':20,'BRD':15}
ROOT   = {'ENC','NEC','WIZ','DRU','SHM','CLR','PAL'}
AE_MEZ = {'ENC'}

def survivability(T):
    """Which AOE mode is available, and what it is worth."""
    modes=[]
    if T & TANKS:            modes.append(('tank', 3))
    if max([SPEED.get(c,0) for c in T] or [0]) >= 50: modes.append(('kite', 3))
    if T & AE_MEZ:           modes.append(('ae-mez', 2))
    if T & ROOT:             modes.append(('root-park', 1))
    if max([SPEED.get(c,0) for c in T] or [0]) >= 15: modes.append(('snare-kite', 1))
    return modes

_MEL={}
def _melee(key):
    if key not in _MEL:
        st = M.evaluate(key,'avg',front=True,charm=False,rates='max')
        _MEL[key]=(st['wtot']+st['lane_total'])/M.STANCE_DMG*0.95 + st['procbuff']
    return _MEL[key]

def cycle_avg(dmg, mana, cycle, pool, passive, active):
    """Steady-state AE output when mana conversion competes with casting for the same time.

    f = fraction of time casting AE, (1-f) converting HP to mana.
      spend  = f * mana/cycle
      income = passive + (1-f) * active_rate
    Solve f, then damage/mob/s = f * dmg/cycle. Falls back to the pool-burn model when
    the trio has no active converter.
    """
    if active > 0:
        f = (passive + active) / (mana/cycle + active)
        f = min(1.0, f)
        return f*dmg/cycle, f
    drain = mana/cycle
    if drain <= passive: return dmg/cycle, 1.0
    burst = pool/(drain-passive); med = pool/passive
    casts = burst/cycle + passive*med/mana
    return casts*dmg/(burst+med), burst/(burst+med)

def aoe(trio, n=24, npull=None):
    T=set(trio)
    modes=survivability(T)
    if not modes: return None                       # nothing keeps you alive in a big pull
    mode,quality = max(modes, key=lambda m:m[1])
    pool    = sum(sorted(MANA_UNITS[c] for c in T)[-2:]) * MANA_PER_UNIT
    passive = BASE_REGEN + sum(PASSIVE.get(c,0) for c in T)
    active  = max([ACTIVE[c][0]/ACTIVE[c][1] for c in T if c in ACTIVE] or [0.0])
    income  = passive + active
    # A player casts the best spell they can SUSTAIN, not the highest nominal throughput.
    # Optimise over every AE the trio can reach.
    opts=[o for c in T for o in AE_SPELLS.get(c,[])]
    if not opts: return None
    scored=[(cycle_avg(o[0],o[1],o[2],pool,passive,active), o) for o in opts]
    (ae_per_mob, duty), (dmg,mana,cycle,kind,nm) = max(scored, key=lambda x: x[0][0])
    n = npull[mode] if npull else n
    ae = ae_per_mob*n
    ds = DS_PER_ATTACKER*n if mode=='tank' else 0.0  # you only get a shield if they hit you
    # You cannot swing while casting, and an AOE farm is continuous casting. Credit melee
    # only for the fraction of the cycle spent medding, and only if you are tanking.
    melee = _melee(tuple(sorted(T)))*(1-duty) if mode=='tank' else 0.0
    return dict(trio=tuple(sorted(T)), dps=ae+ds+melee, ae=ae, ds=ds, melee=melee,
                spell=nm, kind=kind, mode=mode, pool=pool, income=income, duty=duty,
                perm=ae_per_mob)

if __name__=='__main__':
    import sys
    N=int(sys.argv[1]) if len(sys.argv)>1 else 24
    rows=[r for r in (aoe(t,N) for t in itertools.combinations(M.CLASSES,3)) if r]
    rows.sort(key=lambda r:-r['dps'])
    print(f"AOE FARMING — pull of {N}, no target cap, one cast at a time")
    print(f"{'#':>3} {'trio':<16}{'DPS':>7}{'AE':>7}{'shield':>7}{'melee':>7}  {'mode':<11}{'duty':>6}{'mana/s':>7}{'pool':>7}  AE spell")
    for i,r in enumerate(rows[:12],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16}{r['dps']:>7.0f}{r['ae']:>7.0f}{r['ds']:>7.0f}{r['melee']:>7.0f}  "
              f"{r['mode']:<11}{r['duty']*100:>5.0f}%{r['income']:>7.1f}{r['pool']:>7.0f}  {r['kind']} {r['spell']}")
    print()
    for t in (('BRD','DRU','WIZ'),('SHD','DRU','BRD'),('ENC','MAG','WIZ'),('DRU','SHM','WIZ'),('BRD','DRU','SHM')):
        r=aoe(tuple(sorted(t)),N)
        rank=[('+'.join(x['trio'])) for x in rows].index('+'.join(sorted(t)))+1
        print(f"   {'+'.join(sorted(t)):<14} {r['dps']:>6.0f} DPS  rank {rank:>3}/{len(rows)}  "
              f"mode={r['mode']:<10} duty {r['duty']*100:>3.0f}%  {r['spell']}")
