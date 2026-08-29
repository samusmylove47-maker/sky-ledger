#!/usr/bin/env python3
"""The four rankings on the corrected chain (model4.py). Every gate is stated."""
import itertools, model4 as M

# ---- SUSTAINING ACTIONS PER MINUTE ---------------------------------------
# Autoskills (kick/bash/strike/frenzy/backstab/smite), auto-attack, weapon procs and
# stances all cost ZERO input: combat skills have no global cooldown and fire during
# auto-attack. The load is spell and song upkeep only.
#   BRD  61 of 76 songs last exactly 18.0s -> twisting four is 13.3/min, a hard floor
#   SHM  3 DoTs at median 42s -> 4.2/min      BST  4 DoTs at 57s -> 4.4/min
# The rest are reasoned from each class's damage kit. FLAGGED as judgement, not measured.
SAPM = {'WAR':0.5,'BER':0.5,'MNK':1.0,'RNG':1.5,'ROG':2.0,'PAL':3.0,'SHD':5.0,
        'SHM':4.2,'BST':4.4,'CLR':6.0,'DRU':8.0,'MAG':8.0,'ENC':9.0,'NEC':10.0,
        'WIZ':12.0,'BRD':13.3}
POSITION_LOAD = {'ROG':6.0}          # backstab needs you behind the target, continuously
CHARM_LOAD    = {'ENC':3.0,'NEC':3.0,'DRU':3.0,'BRD':3.3}   # re-charm on break / 18s song

TANK = {'WAR','PAL','SHD'}           # the only classes with Defensive stance
# max level charmable, and against what. BRD charms ANY target on an 18s song.
CHARM = {'ENC':(51,'any'),'BRD':(51,'any'),'NEC':(51,'undead'),
         'DRU':(49,'animal'),'SHM':(33,'animal')}

def sapm(trio, charming=False):
    s = sum(SAPM[c] for c in trio) + sum(POSITION_LOAD.get(c,0) for c in trio)
    if charming: s += max([CHARM_LOAD.get(c,0) for c in trio] or [0])
    return s

def tankscore(trio):
    T=set(trio)
    if not (T & TANK): return 0.0
    s = 50.0
    if 'WAR' in T: s += 30    # Innate Fighters Tenacity: permanent 5% melee mitigation
    if 'PAL' in T: s += 20    # Lay on Hands, 10 ranks, free
    if 'SHD' in T: s += 18    # lifetap self-sustain + Harm Touch
    if 'CLR' in T: s += 15    # Divine Aura: 18s invulnerable
    if 'MNK' in T: s += 8     # Evasive access, high avoidance
    if T & {'SHM','CLR','DRU','PAL'}: s += 10
    return s

ALL = list(itertools.combinations(M.CLASSES, 3))
K = 1.46      # measured best-30s / engaged, the conversion to a quoted peak parse

print("="*104)
print("LIST 1 — TOP 10 RAID-BOSS DPS   (raid mitigation · attacking from behind · nothing")
print("         charmable on a single boss · abilities on cooldown · ENCHANTER EXCLUDED)")
print("="*104)
c1=[t for t in ALL if 'ENC' not in t]
L1=sorted([M.evaluate(t,'raid',front=False,charm=False,rates='max') for t in c1],key=lambda r:-r['total'])
for i,r in enumerate(L1[:10],1):
    oh=r['oh']['n'] if r['oh'] else '(two-hander)'
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>4.0f} sust / {r['total']*K:>4.0f} peak  wrath {r['wrath']:>3.0f}  "
          f"weap {r['wtot']:>3.0f} abil {r['lane_total']:>3.0f} proc {r['procbuff']:>3.0f} sp/pet {r['spell']+r['pet']:>3.0f}")
    print(f"    {r['mh']['n'][:30]} {r['mh']['dmg']}/{r['mh']['dly']}  +  {oh[:26]}   lanes: {', '.join(l for l,_ in r['lanes'])}")

print()
print("="*104)
print("LIST 2 — TOP 10 TANK + CHARM PET + DAMAGE   (needs Defensive stance AND a charmer ·")
print("         ENCHANTER INCLUDED · fighting from the front so backstab degrades)")
print("="*104)
c2=[t for t in ALL if (set(t)&TANK) and (set(t)&set(CHARM))]
L2=sorted([dict(M.evaluate(t,'raid',front=True,charm=True,rates='max'),tank=tankscore(t)) for t in c2],
          key=lambda r:-r['total'])
for i,r in enumerate(L2[:10],1):
    ch=[c for c in r['trio'] if c in CHARM]
    best=max(ch,key=lambda c:CHARM[c][0])
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>4.0f} sust / {r['total']*K:>4.0f} peak  tank {r['tank']:>4.0f}  "
          f"charm {best} to L{CHARM[best][0]} ({CHARM[best][1]})   {r['mh']['n'][:24]}")

print()
print("="*104)
print("LIST 3 — TOP 10 DAMAGE PER UNIT OF WRIST   (autoskills cost ZERO input; the load is")
print("         spell and song upkeep only · average mitigation · no charm to maintain)")
print("="*104)
L3=sorted([dict(M.evaluate(t,'avg',front=False,charm=False,rates='max'),sapm=sapm(t)) for t in ALL],
          key=lambda r:-(r['total']/(1.0+r['sapm'])))
for i,r in enumerate(L3[:10],1):
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>4.0f} DPS   {r['sapm']:>5.1f} actions/min   "
          f"{r['total']/(1+r['sapm']):>6.1f} DPS/action   {r['mh']['n'][:26]}")
print("\n   Reference points:")
for t in (('BER','MNK','WAR'),('MNK','RNG','WAR'),('PAL','RNG','ROG'),('BRD','DRU','SHD'),('ENC','NEC','WIZ')):
    r=M.evaluate(tuple(sorted(t)),'avg',front=False,charm=False,rates='max')
    print(f"     {'+'.join(sorted(t)):<14} {r['total']:>4.0f} DPS at {sapm(t):>5.1f} actions/min")

# =========================================================================
# AOE FARMING — pull cycle, Defensive stance, on the corrected chain
# =========================================================================
AE = {'WIZ':(854,875,'PB Supernova'),'DRU':(618,625,'PB Upheaval'),'CLR':(618,625,'PB Upheaval'),
      'MAG':(324,375,'TA Rain of Swords'),'BRD':(315,800,'TA Denon'),'ENC':(242,337,'TA Gravity Flux'),
      'NEC':(147,171,'PB Word of Souls'),'SHD':(97,133,'PB Word of Spirit'),
      'SHM':(122,200,'TA Gale of Poison')}
# Mana income engines, mana/s, read off spells.json
MANA_ENGINE = {'SHM':8.0,'NEC':3.3,'WIZ':4.0,'ENC':2.0,'BRD':1.17}
BASE_REGEN  = 3.0
MANA = {'WIZ':100,'MAG':100,'NEC':100,'CLR':100,'DRU':100,'SHM':100,'ENC':100,
        'PAL':45,'SHD':45,'RNG':40,'BST':45,'BRD':40,'WAR':0,'MNK':0,'ROG':0,'BER':0}
MANA_PER_UNIT   = 60.0
DS_PER_ATTACKER = 17.5     # measured: exactly 1.00 damage-shield tick per landed incoming hit
CAST_CYCLE      = 2.5
DEF_ACC         = 0.95     # Defensive stance accuracy, measured

def aoe(trio, n=8):
    T=set(trio)
    if not (T & TANK): return None
    best = max(((AE[c][0],AE[c][1],AE[c][2]) for c in T if c in AE), default=None,
               key=lambda x: x[0]/max(x[1],1))
    if not best: return None
    dmg, mana, nm = best
    pool   = sum(sorted(MANA[c] for c in T)[-2:]) * MANA_PER_UNIT
    income = BASE_REGEN + sum(MANA_ENGINE.get(c,0) for c in T)
    st     = M.evaluate(trio,'avg',front=True,charm=False,rates='max')
    # Holding a pull means DEFENSIVE stance: no x2.00 damage, and 5% less accuracy.
    melee  = (st['wtot']+st['lane_total'])/M.STANCE_DMG*DEF_ACC + st['procbuff']
    ds     = DS_PER_ATTACKER * n
    casts_burst = pool/mana; t_burst = casts_burst*CAST_CYCLE; t_med = pool/income
    cycle = t_burst + t_med
    dmg_cycle = casts_burst*dmg*n + (ds+melee)*cycle
    return dict(trio=tuple(sorted(T)), dps=dmg_cycle/cycle, ae=casts_burst*dmg*n/cycle,
                ds=ds, melee=melee, spell=nm, pool=pool, income=income, tank=tankscore(trio))

for N in (8, 24):
    print()
    print("="*104)
    print(f"AOE FARMING — full pull cycle, Defensive stance, pull of {N}")
    print("="*104)
    rows=[r for r in (aoe(t,N) for t in ALL) if r]
    rows.sort(key=lambda r:-r['dps'])
    print(f"{'#':>3} {'trio':<16}{'DPS':>6}{'AE':>7}{'shield':>8}{'melee':>7}{'mana/s':>8}{'pool':>7}{'tank':>6}  AE spell")
    for i,r in enumerate(rows[:8],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16}{r['dps']:>6.0f}{r['ae']:>7.0f}{r['ds']:>8.0f}{r['melee']:>7.0f}"
              f"{r['income']:>8.1f}{r['pool']:>7.0f}{r['tank']:>6.0f}  {r['spell']}")
    u=aoe(('SHD','DRU','BRD'),N)
    rank=[('+'.join(x['trio'])) for x in rows].index('+'.join(u['trio']))+1
    print(f"\n   SHD+DRU+BRD: {u['dps']:.0f} DPS  (AE {u['ae']:.0f} + shield {u['ds']:.0f} + melee {u['melee']:.0f}),"
          f" mana {u['income']:.1f}/s -> RANK {rank} of {len(rows)}  ({u['dps']/rows[0]['dps']*100:.0f}% of leader)")
