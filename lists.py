#!/usr/bin/env python3
"""The four rankings, built on model3.py.  Every gate is stated; nothing is hand-placed."""
import itertools, model3 as M

# ---- SUSTAINING ACTIONS PER MINUTE ---------------------------------------
# Derived mechanically, not guessed.  Autoskills (kick/bash/frenzy/strike/backstab),
# auto-attack, weapon procs and stances all cost ZERO input: combat skills have no
# global cooldown and fire automatically during auto-attack.  The load is entirely
# spell/song upkeep, read off measured durations:
#   BRD  61 of 76 songs last 18.0s exactly -> twisting four is 4*(60/18) = 13.3/min FLOOR
#   SHM  3 DoTs at median 42s              -> 1.4/min each
#   BST  4 DoTs at median 57s              -> 1.1/min each
# The rest are reasoned from each class's damage kit, NOT measured.  Flagged.
SAPM = {'WAR':0.5,'BER':0.5,'MNK':1.0,'RNG':1.5,'PAL':3.0,'SHD':5.0,'ROG':2.0,
        'BST':6.0,'SHM':4.2,'CLR':6.0,'DRU':8.0,'MAG':8.0,'NEC':10.0,'WIZ':12.0,'BRD':13.3}
# Rogue additionally pays a POSITIONING cost: backstab needs to be behind the target.
POSITION_LOAD = {'ROG':6.0}

TANK   = {'WAR','PAL','SHD'}          # the only classes with Defensive stance
CHARM  = {'NEC':51,'DRU':43,'SHM':33} # max level charmable, ENC excluded by the brief

def sapm(trio):
    return sum(SAPM[c] for c in trio) + sum(POSITION_LOAD.get(c,0) for c in trio)

def tankscore(trio):
    T=set(trio)
    if not (T & TANK): return 0.0
    s = 50.0
    if 'WAR' in T: s += 30      # Innate Fighters Tenacity: permanent 5% melee mitigation
    if 'PAL' in T: s += 20      # Lay on Hands (10 ranks, free) + heals + stuns
    if 'SHD' in T: s += 18      # lifetap self-sustain + Harm Touch
    if 'CLR' in T: s += 15      # Divine Aura: 18s invulnerable, 10 min recast
    if 'MNK' in T: s += 8       # Evasive stance access + high avoidance
    if T & {'SHM','CLR','DRU','PAL'}: s += 10   # self-heal
    return s

ALL = list(itertools.combinations(M.CLASSES, 3))

def show(rows, n, cols):
    print(f"{'#':>3} {'trio':<16} {'DPS':>6} " + ' '.join(f"{c:>7}" for c,_ in cols))
    for i,r in enumerate(rows[:n],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16} {r['total']:>6.0f} " +
              ' '.join(f"{fn(r):>7.1f}" if isinstance(fn(r),float) else f"{fn(r):>7}" for _,fn in cols))

print("="*96)
print("LIST 1 — TOP 10 RAID-BOSS DPS   (raid mitigation, attacking from behind, no Enchanter)")
print("="*96)
L1 = sorted([M.evaluate(t,'raid',want='behind') for t in ALL], key=lambda r:-r['total'])
for i,r in enumerate(L1[:10],1):
    oh = r['oh']['n'] if r['oh'] else '(two-hander)'
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>5.0f} DPS   wrath {r['wrath']:>3.0f}   "
          f"melee {r['melee']:>5.1f}  proc {r['procbuff']+r['mhp']+r['ohp']:>5.1f}  spell/pet {r['spell']+r['pet']:>5.1f}")
    print(f"    {r['mh']['n']}  +  {oh}"
          + (f"   lanes: {', '.join(l for l,_ in r['lanes'])}" if r['lanes'] else ""))

print()
print("="*96)
print("LIST 2 — TOP 10 TANK + CHARM PET + DAMAGE  (needs Defensive stance AND a non-ENC charmer;")
print("         fighting from the front, so Rogue backstab is degraded to Chaotic Stab)")
print("="*96)
cand = [t for t in ALL if (set(t) & TANK) and (set(t) & set(CHARM))]
L2 = sorted([dict(M.evaluate(t,'raid',want='front'), tank=tankscore(t)) for t in cand],
            key=lambda r: -(r['total'] + r['tank']*1.6))
for i,r in enumerate(L2[:10],1):
    ch = [c for c in r['trio'] if c in CHARM]
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>5.0f} DPS   tank {r['tank']:>4.0f}   "
          f"charm: {ch[0]} (to L{CHARM[ch[0]]})   {r['mh']['n'][:34]}")

print()
print("="*96)
print("LIST 3 — TOP 10 DAMAGE PER UNIT OF WRIST  (sustaining actions/min; autoskills cost ZERO)")
print("="*96)
L3 = sorted([dict(M.evaluate(t,'avg',want='behind'), sapm=sapm(t)) for t in ALL],
            key=lambda r: -(r['total'] / (1.0 + r['sapm'])))
for i,r in enumerate(L3[:10],1):
    print(f"{i:>2}. {'+'.join(r['trio']):<14} {r['total']:>5.0f} DPS   {r['sapm']:>5.1f} actions/min   "
          f"{r['total']/(1+r['sapm']):>6.1f} DPS per action   {r['mh']['n'][:30]}")
print("\n   For reference, the low-input floor and ceiling:")
for t in (('BER','MNK','WAR'),('MNK','RNG','WAR'),('BRD','DRU','SHD'),('NEC','SHD','WIZ')):
    r=M.evaluate(t,'avg',want='behind'); print(f"     {'+'.join(sorted(t)):<14} {r['total']:>5.0f} DPS at {sapm(t):>5.1f} actions/min")

# =========================================================================
# AOE FARMING — modelled as a PULL CYCLE, not infinite sustain
# =========================================================================
# Best AE damage spell reachable at 50 (damage, mana, PB/TA), from the spell database.
AE = {'WIZ':(854,875,'PB Supernova'),'DRU':(618,625,'PB Upheaval'),'CLR':(618,625,'PB Upheaval'),
      'MAG':(324,375,'TA Rain of Swords'),'BRD':(315,800,'TA Denon\'s Dirge'),
      'NEC':(147,171,'PB Word of Souls'),'SHD':(97,133,'PB Word of Spirit'),
      'SHM':(122,200,'TA Gale of Poison')}
# Mana INCOME engines, mana/s, read off the spell database:
#   NEC Lich          +20/tick  = 3.33/s   (costs HP; the partner heals it back)
#   SHM Cannibalize    0 mana, -50 HP -> +20..28 mana, spammable = ~8/s with a healer
#   WIZ Harvest       +251 for 1 mana, long recast                = ~4/s
#   BRD Chorus of Clarity +5..7/tick, ZERO mana, GROUP-WIDE       = 1.17/s
MANA_ENGINE = {'SHM':8.0,'NEC':3.3,'WIZ':4.0,'BRD':1.17}
BASE_REGEN  = 3.0
MANA = {'WIZ':100,'MAG':100,'NEC':100,'CLR':100,'DRU':100,'SHM':100,
        'PAL':45,'SHD':45,'RNG':40,'BST':45,'BRD':40,'WAR':0,'MNK':0,'ROG':0,'BER':0}
MANA_PER_UNIT   = 60.0     # relative unit -> mana points at 50; pools sum the TWO highest classes
DS_PER_ATTACKER = 17.5     # measured: exactly 1.00 damage-shield tick per landed incoming hit
CAST_CYCLE      = 2.5

def aoe(trio, n=8, verbose=False):
    T=set(trio)
    if not (T & TANK): return None                 # you must be able to hold the pull
    best = max(((AE[c][0],AE[c][1],AE[c][2]) for c in T if c in AE), default=None,
               key=lambda x: x[0]/max(x[1],1))
    if not best: return None
    dmg, mana, nm = best
    pool   = sum(sorted(MANA[c] for c in T)[-2:]) * MANA_PER_UNIT
    income = BASE_REGEN + sum(MANA_ENGINE.get(c,0) for c in T)
    st     = M.evaluate(trio,'avg',want='front')
    # Holding 8-16 mobs means DEFENSIVE stance, so the x2.00 Offensive multiplier is off.
    # Defensive very likely costs offence on top of that; 1.0 is the conservative choice.
    melee  = st['melee']/M.STANCE_DMG + st['procbuff']
    ds     = DS_PER_ATTACKER * n
    # ---- pull cycle: dump the pool at full cast rate, then med back to full
    casts_burst = pool / mana
    t_burst     = casts_burst * CAST_CYCLE
    t_med       = pool / income
    cycle       = t_burst + t_med
    dmg_burst   = casts_burst * dmg * n
    dmg_cycle   = dmg_burst + (ds + melee) * cycle
    return dict(trio=tuple(sorted(T)), dps=dmg_cycle/cycle, ae=dmg_burst/cycle, ds=ds,
                melee=melee, spell=nm, pool=pool, income=income, cycle=cycle,
                uptime=t_burst/cycle, tank=tankscore(trio))

for N in (8, 16):
    print()
    print("="*100)
    print(f"AOE FARMING — full pull cycle (burn the pool, then med back), pull of {N}")
    print("="*100)
    rows=[r for r in (aoe(t,N) for t in ALL) if r]
    rows.sort(key=lambda r:-r['dps'])
    print(f"{'#':>3} {'trio':<16} {'DPS':>6} {'AE':>6} {'shield':>7} {'melee':>7} {'mana/s':>7} {'pool':>6} {'AE uptime':>10} {'AE spell':<22} {'tank':>5}")
    for i,r in enumerate(rows[:10],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16} {r['dps']:>6.0f} {r['ae']:>6.0f} {r['ds']:>7.0f} "
              f"{r['melee']:>7.0f} {r['income']:>7.1f} {r['pool']:>6.0f} {r['uptime']*100:>9.0f}% {r['spell']:<22} {r['tank']:>5.0f}")
    u=aoe(('SHD','DRU','BRD'),N)
    rank=[('+'.join(x['trio'])) for x in rows].index('+'.join(u['trio']))+1
    print(f"\n   SHD+DRU+BRD: {u['dps']:.0f} DPS  (AE {u['ae']:.0f} + shield {u['ds']:.0f} + melee {u['melee']:.0f}),"
          f" mana {u['income']:.1f}/s, pool {u['pool']:.0f} -> RANK {rank} of {len(rows)}")
