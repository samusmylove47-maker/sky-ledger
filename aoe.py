#!/usr/bin/env python3
"""AOE farming in EQ Legends — which trio kills the most monsters at once.

Rewritten 29 Aug. Three of my earlier framings were wrong and are recorded here so the
mistakes are not repeated:

  1. I gated on having a TANK class. That excluded every kiting and caster trio, i.e. the
     entire real meta. There are four survival modes; only one involves holding aggro.
  2. I priced Bard's passive songs from their own wiki pages, which carry the BASE value.
     Only the eqlwiki CLASS page carries level scaling, and for these three songs that is a
     7x error -- 8/tick where the real level-50 figure is 57/tick.
  3. I modelled Denon's Desperate Dirge as a sustained cast. It is a BURST: 800 mana on a
     3-second cast with no recast, capped at 8 targets. Throughput is casts-per-pull gated
     by the mana POOL, not a steady-state rate.

Run:  python3 aoe.py [pull_size]
"""
import itertools
import model4 as M
from ae_spells import AE_SPELLS

# ── BARD ────────────────────────────────────────────────────────────────────
# eqlwiki Bard class page, verbatim (the spell pages omit the scaling):
#   Chords of Dissonance        "2 (L2)  to 14 (L50) per tick"   Stringed
#   Denon's Disruptive Discord  "8 (L18) to 16 (L50) per tick"   Brass
#   Selo's Chords of Cessation "26 (L48) to 27 (L50) per tick"   Stringed
BARD_TICK = 57.0          # combined, level 50, before multipliers.  TICK = 6s
TICK      = 6.0
# Symphonic Aura (AA, verbatim): "allows one/two/three/four/five Bard songs to auto pulse.
# In order for a song to be eligible, it must have no mana cost, have no cooldown, and be a
# non-targeted area of effect song." All three PB AE songs qualify. DDD does not.
# Two DISJOINT multiplier systems, both verbatim from the AA catalogue:
INSTRUMENT_MASTERY = 1.60     # T2  "+20/40/60% ... Brass, Percussion, String and Woodwind"
SINGING_MASTERY    = 1.60     # T2  "+20/40/60% ... songs that use the Singing skill"
INSTRUMENT_EXALT   = 1.40     # REPORT ONLY -- absent from the wiki entirely
# Denon's Desperate Dirge, eqlwiki spell page verbatim: "causes between 311 and 405 damage
# to up to 8 enemies", 315 base, 800 mana, 3.00s cast, 0.00 recast, Targeted AE, Singing.
DDD_MANA, DDD_CAST, DDD_CAP = 800.0, 3.0, 8
DDD_WIKI     = 315.0 * SINGING_MASTERY * 1.10   # Amplification at the wiki description's 10%
DDD_REPORTED = 3000.0                            # T3 measured, wiki-hosted guide, rank 10

# ── MANA ────────────────────────────────────────────────────────────────────
PASSIVE = {'NEC':3.33,'BRD':1.17,'ENC':2.00,'WIZ':0.42}    # runs while you cast
ACTIVE  = {'SHM':(36.0, 2.75)}                             # costs cast time
BASE_REGEN = 3.0
MANA_UNITS = {'WIZ':100,'MAG':100,'NEC':100,'CLR':100,'DRU':100,'SHM':100,'ENC':100,
              'PAL':45,'SHD':45,'BST':45,'RNG':40,'BRD':40,'WAR':0,'MNK':0,'ROG':0,'BER':0}
MANA_PER_UNIT = 60.0

# ── SURVIVAL ────────────────────────────────────────────────────────────────
TANKS  = {'WAR','PAL','SHD'}
SPEED  = {'DRU':57,'SHM':57,'RNG':52,'BST':30,'MAG':20,'BRD':15}   # sustained, level 50
ROOT   = {'ENC','NEC','WIZ','DRU','SHM','CLR','PAL'}
AE_MEZ = {'ENC'}
DS_PER_ATTACKER = 17.5

PULL_SECONDS = 90.0        # one gather-and-detonate cycle

def modes(T):
    m=[]
    if T & TANKS: m.append(('tank',3))
    if max([SPEED.get(c,0) for c in T] or [0]) >= 50: m.append(('kite',3))
    if T & AE_MEZ: m.append(('ae-mez',2))
    if T & ROOT: m.append(('root-park',1))
    if max([SPEED.get(c,0) for c in T] or [0]) >= 15: m.append(('snare-kite',1))
    return m

_MEL={}
def _melee(key):
    if key not in _MEL:
        st=M.evaluate(key,'avg',front=True,charm=False,rates='max')
        _MEL[key]=(st['wtot']+st['lane_total'])/M.STANCE_DMG*0.95+st['procbuff']
    return _MEL[key]

def aoe(trio, n=24, npull=None, exalt=True, ddd=DDD_REPORTED):
    T=set(trio); ms=modes(T)
    if not ms: return None
    mode,_ = max(ms, key=lambda x:x[1])
    if npull: n = npull[mode]
    pool    = sum(sorted(MANA_UNITS[c] for c in T)[-2:]) * MANA_PER_UNIT
    passive = BASE_REGEN + sum(PASSIVE.get(c,0) for c in T)
    active  = max([ACTIVE[c][0]/ACTIVE[c][1] for c in T if c in ACTIVE] or [0.0])

    # --- free layer: Bard songs auto-pulsing under Symphonic Aura. No mana, no keypress,
    #     no target cap. Runs for the whole pull regardless of what you are casting.
    bard_ps = 0.0
    if 'BRD' in T:
        bard_ps = BARD_TICK*INSTRUMENT_MASTERY*(INSTRUMENT_EXALT if exalt else 1.0)/TICK*n

    # --- mana budget for the pull
    budget = pool + passive*PULL_SECONDS
    cast_left = PULL_SECONDS
    dmg_total = 0.0
    detail = {}

    # --- Denon's Desperate Dirge: the detonation. Best damage per mana in the game when it
    #     is at full targets, but capped at 8 and it must be paid for up front.
    if 'BRD' in T and ddd:
        casts = min(budget/DDD_MANA, cast_left/DDD_CAST)
        if casts >= 1:
            d = casts*ddd*min(n, DDD_CAP)
            dmg_total += d; detail['ddd']=d/PULL_SECONDS
            budget -= casts*DDD_MANA; cast_left -= casts*DDD_CAST

    # --- whatever casting time is left goes to the best conventional AE the trio can afford
    opts=[o for c in T for o in AE_SPELLS.get(c,[])]
    if opts and cast_left > 0 and budget > 0:
        best=None
        for dmg,mana,cycle,kind,nm in opts:
            casts=min(budget/mana, cast_left/cycle)
            v=casts*dmg*n
            if best is None or v>best[0]: best=(v,nm,casts)
        if best and best[0]>0:
            dmg_total += best[0]; detail['ae']=best[0]/PULL_SECONDS; detail['spell']=best[1]

    # --- Shaman can convert HP to mana, but only in seconds it is not casting. Credit it
    #     only if there is idle casting time left.
    if active and cast_left>0:
        pass   # already reflected: leftover cast time simply was not needed

    ds    = DS_PER_ATTACKER*n if mode=='tank' else 0.0
    melee = _melee(tuple(sorted(T)))*max(0.0, cast_left/PULL_SECONDS) if mode=='tank' else 0.0
    dps   = dmg_total/PULL_SECONDS + bard_ps + ds + melee
    return dict(trio=tuple(sorted(T)), dps=dps, mode=mode, n=n, bard=bard_ps, ds=ds,
                melee=melee, pool=pool, income=passive, **detail)

if __name__=='__main__':
    import sys
    NP={'tank':10,'kite':30,'ae-mez':20,'root-park':12,'snare-kite':24}
    if len(sys.argv)>1:
        k=int(sys.argv[1]); NP={m:k for m in NP}
    rows=[r for r in (aoe(t,npull=NP) for t in itertools.combinations(M.CLASSES,3)) if r]
    rows.sort(key=lambda r:-r['dps'])
    print(f"AOE FARMING — pull by mode {NP}")
    print(f"{'#':>3} {'trio':<16}{'DPS':>7}{'BRDaura':>9}{'DDD':>8}{'AE':>7}{'shield':>7}  {'mode':<10} spell")
    for i,r in enumerate(rows[:12],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16}{r['dps']:>7.0f}{r['bard']:>9.0f}"
              f"{r.get('ddd',0):>8.0f}{r.get('ae',0):>7.0f}{r['ds']:>7.0f}  {r['mode']:<10} {r.get('spell','-')}")
    print("\nThe player's picks:")
    for t in (('BRD','DRU','WIZ'),('BRD','DRU','SHD'),('ENC','MAG','WIZ')):
        k=tuple(sorted(t)); r=aoe(k,npull=NP)
        rank=[('+'.join(x['trio'])) for x in rows].index('+'.join(k))+1
        print(f"   {'+'.join(k):<14}{r['dps']:>7.0f} DPS  rank {rank:>3}/{len(rows)}   "
              f"aura {r['bard']:>5.0f}  DDD {r.get('ddd',0):>6.0f}  AE {r.get('ae',0):>5.0f}")
