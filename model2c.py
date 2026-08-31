#!/usr/bin/env python3
"""EQ Legends unified build model v2 — melee + archery + combat skills + pets + spells.

Scores all 560 trios on two honest columns:
  BURST     resources ignored (short fight / entering with full bars)
  SUSTAINED resource-limited long run: melee = Balanced stance (free, infinite);
            casters = mana-income limited; pets and autoskills are free in both.

An actor either MELEES or CASTS, whichever is higher (both compete for the same
action time — you do not swing while a cast bar is up). Autoskills ride along with
melee for free; pets ride along with everything for free.
"""
import os, json, itertools, urllib.request

BASE="https://samusmylove47-maker.github.io/EQL50ups/data/items/"
for s in ("PRIMARY","SECONDARY","RANGE"):
    if not os.path.exists(f"sh-{s}.json"):
        urllib.request.urlretrieve(BASE+s+".json", f"sh-{s}.json")
PRI=json.load(open('sh-PRIMARY.json')); PRI=PRI['items'] if isinstance(PRI,dict) else PRI
SEC=json.load(open('sh-SECONDARY.json')); SEC=SEC['items'] if isinstance(SEC,dict) else SEC

CLASSES=['WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST','CLR','DRU','SHM','ENC','MAG','NEC','WIZ']
MARTIAL={'WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST'}
PURE   ={'CLR','DRU','SHM','ENC','MAG','NEC','WIZ'}
INT    ={'ENC','MAG','NEC','WIZ'}                 # Arcane Mastery scaling
NONHYB ={'CLR','DRU','SHM','ENC','MAG','NEC','WIZ'}  # Empower scaling
DEF={'WAR','PAL','SHD'}; STRK={'BER','MNK','ROG','WAR'}; BSK={'BER'}
EVA={'BRD','MNK','RNG','BST','ROG'}; RANGED={'BER','MNK','RNG','ROG'}
MAGEHUNT={'PAL','SHD','BER'}
L=50
R=float(os.environ.get('R','0.45'))            # measured 0.287-0.51; 0.40 raid / 0.50 soft
LAND_OFF=float(os.environ.get('LAND_OFF','0.62'))
LAND_BAL=float(os.environ.get('LAND_BAL','0.56'))
CRITMULT=float(os.environ.get('CRITMULT','1.664'))
CRITRATE=float(os.environ.get('CRITRATE','0.132'))
PET_CHARM=float(os.environ.get('PET_CHARM','85'))   # measured 44.5 floor .. 112.6 best
PET_SUMMON=float(os.environ.get('PET_SUMMON','35')) # measured 15.6 base x haste ladder + kit
ARCH_B=os.environ.get('ARCH_B','0')=='1'            # main-hand bonus applies to bows?
FRONT_ARC=os.environ.get('FRONT','0')=='1'          # tanking => Rogue backstab degraded
LANE_DECAY=float(os.environ.get('LANE_DECAY','1.0'))# 1.0 = all lanes fire fully; <1 penalises stacking

# --- MEASURED autoskill DPS (TM, 96,450 log lines) -------------------------
# CORRECTED after adversarial review:
#   SHD Reave 40.1 -> 13.4 (Balanced; 90% of the original was a flat 306 = 3% max HP, n=1 fight)
#   PAL Smite 28.4 -> 20.3 (engaged-seconds denominator; scales with MAX MANA, unmodelled)
#   WAR 2.6 -> 9.5 (zero player self-cleaves in 89,190 lines; real lane is Kick)
#   RNG 0 -> 9.5 (has Kick at level 1)
SKILL={'ROG':41.5,'SHD':13.4,'PAL':20.3,'BER':18.9,'MNK':31.2,'WAR':9.5,'BST':13.9,'BRD':0.0,'RNG':9.5}
# --- SPELLS: burst (resources ignored) / sustained (mana-income limited) ---
SPELL_BURST={'WIZ':145.5,'MAG':116.7,'DRU':97.5,'NEC':84.7,'SHM':72.0,'CLR':70.9,'ENC':70.4,
             'SHD':92.0,'PAL':71.0,'RNG':66.0,'BST':13.0,'BRD':45.7}
SPELL_SUST ={'WIZ':21.1,'MAG':18.4,'DRU':17.8,'NEC':21.5,'SHM':12.1,'CLR':13.9,'ENC':15.3,
             'SHD':18.0,'PAL':14.0,'RNG':13.0,'BST':4.0,'BRD':45.7}  # BRD songs are endurance-free
NEC_DOT_BURST=166.7   # full 8-line stack, 41.24 mana/s — burst only

def elig(it,cls):
    cl=it.get('cl') or []
    if 'ALL' in cl: return True
    if any(c.startswith('ALL_EXCEPT') for c in cl):
        ex=[c for c in cl if not c.startswith('ALL_EXCEPT')]
        return not (set(cls)&set(ex))
    return bool(set(cl)&set(cls))
def bonus(dmg,dly,hand): return hand*max(L,dmg)*(min(dly,50)/40.0)*(L/100.0)
def hitval(dmg,dly,hand,crit):
    b=bonus(dmg,dly,hand); normal=R*dmg+b; cr=(R*dmg)*CRITMULT+b
    return (1-crit)*normal+crit*cr
def rate(dly,mult): return 10.0/max(1,int(dly/mult))

def melee(cls,crit,hasteM,M,dw):
    twos=[];ones=[];offs=[]
    for i in PRI:
        w=i.get('wp')
        if not w or not elig(i,cls): continue
        d,dl,sk=w['dmg']*2,w['dly'],str(w.get('skill',''))
        (twos if sk.startswith('2H') else ones).append((d,dl,i['n']))
    for i in SEC:
        w=i.get('wp')
        if not w or not elig(i,cls) or 'SECONDARY' not in (i.get('sl') or []): continue
        offs.append((w['dmg']*2,w['dly'],i['n']))
    best=(0,'none',0)
    if twos:
        d,dl,n=max(twos,key=lambda t:(2*t[0]+bonus(t[0],t[1],1.1))/t[1])
        h=hitval(d,dl,1.1,crit); best=max(best,(rate(dl,hasteM)*M*h,'2H '+n,dl),key=lambda x:x[0])
    if ones and offs and dw>0:
        d,dl,n=max(ones,key=lambda t:(2*t[0]+bonus(t[0],t[1],0.8))/t[1])
        od,odl,on=max(offs,key=lambda t:t[0]/t[1])
        v=rate(dl,hasteM)*M*hitval(d,dl,0.8,crit)+rate(odl,hasteM)*dw*hitval(od,odl,0.0,crit)
        best=max(best,(v,f'DW {n} / {on}',dl),key=lambda x:x[0])
    elif ones:
        d,dl,n=max(ones,key=lambda t:(2*t[0]+bonus(t[0],t[1],0.8))/t[1])
        best=max(best,(rate(dl,hasteM)*M*hitval(d,dl,0.8,crit),'1H '+n,dl),key=lambda x:x[0])
    return best

def build(trio):
    cls=set(trio); has=lambda s: bool(cls&s)
    crit=CRITRATE
    M=float(os.environ.get('M','1.44'))
    hasteM=1.85 if 'MNK' in cls else 1.75
    dw=0.832 if 'MNK' in cls else (0.693 if cls&{'WAR','RNG','ROG','BER','BRD','BST','SHD','PAL'} else 0.0)
    base,wname,_=melee(cls,crit,hasteM,M,dw)
    rngbuff=1.0191*(1+1.04*0.025) if 'RNG' in cls else 1.0
    base*=rngbuff
    # melee: Berserker (2x speed) else Offensive (2x damage); Balanced is the free floor
    if 'BER' in cls:
        m_burst=base*2*LAND_OFF; stance='Berserker'
    else:
        m_burst=base*2*LAND_OFF; stance='Offensive'
    m_free=base*LAND_BAL                                   # Balanced — free, infinite
    # archery: Ranger only, and only if it beats melee
    arch_b, arch_s = (86.6,60.1) if ARCH_B else (63.2,43.9)
    if 'RNG' in cls and arch_b>m_burst:
        m_burst, m_free, wname, stance = arch_b, arch_s, '2H Windstriker (bow)', 'Ranged'
    # autoskills ride free with melee; Berserker doubles recharge & +25% dmg = 2.5x
    # MEASURED autoskill DPS already averages over whatever stances those characters ran,
    # so NO Berserker multiplier is applied on top (that would double-count).
    # Rogue backstab degrades hard from the front arc (Chaotic Stab: "minimal backstab damage").
    lanes=[]
    for c in cls:
        v=SKILL.get(c,0.0)
        if c=='ROG' and FRONT_ARC: v*=0.35
        if v: lanes.append(v)
    lanes.sort(reverse=True)
    sk=sum(v*(LANE_DECAY**i) for i,v in enumerate(lanes))*(1+CRITRATE*(CRITMULT-1))
    # pets ride free with everything
    pet=PET_CHARM if 'ENC' in cls else (PET_SUMMON if cls&{'MAG','NEC','BST'} else (20.0 if 'SHD' in cls else 0.0))
    # spells: best in trio; Arcane Mastery scales with INT-class count
    nint=len(cls&INT); am=1.0/(1.0-min(0.20+0.10*max(0,nint-1),0.6)) if nint>=1 else 1.0
    sb=max([SPELL_BURST.get(c,0) for c in cls]+[0])*am
    ss=max([SPELL_SUST.get(c,0) for c in cls]+[0])*am
    if 'NEC' in cls: sb=max(sb, NEC_DOT_BURST*am)
    # you either melee (with autoskills) or cast — not both
    burst=max(m_burst+sk, sb)+pet
    sust =max(m_free+sk,  ss)+pet
    mode='melee' if (m_burst+sk)>=sb else 'cast'
    mit=('Defensive' if has(DEF) else ('Channeler' if has(PURE) else ('Evasive' if has(EVA) else ('Balanced' if has(MARTIAL) else 'NONE'))))
    nm=len(cls&MARTIAL)
    return dict(trio='+'.join(sorted(cls)),burst=burst,sust=sust,
                score=0.65*sust+0.35*burst, weapon=wname,stance=stance,mode=mode,
                pet=pet,skills=sk,spell_b=sb,spell_s=ss,mit=mit,martial=nm,
                aggro=('AE' if 'WAR' in cls else ('single' if has(DEF|{'RNG'}) else 'none')),
                cat=('caster' if nm==0 else ('martial' if nm==3 else 'hybrid')))
ROWS=[build(c) for c in itertools.combinations(CLASSES,3)]
if __name__=='__main__':
    def show(t,sel,n=25):
        print('\n'+t)
        print(f"  {'#':>3} {'trio':<15}{'score':>7}{'sust':>7}{'burst':>7}  {'mode':<6}{'pet':>5}{'skl':>6}  {'mit':<10}weapon")
        for i,r in enumerate(sorted(sel,key=lambda x:-x['score'])[:n],1):
            print(f"  {i:>3} {r['trio']:<15}{r['score']:7.1f}{r['sust']:7.1f}{r['burst']:7.1f}  {r['mode']:<6}{r['pet']:5.0f}{r['skills']:6.1f}  {r['mit']:<10}{r['weapon'][:30]}")
    show('TOP 25 MARTIAL / MELEE (3 martial classes)',[r for r in ROWS if r['cat']=='martial'],25)
    show('TOP 10 PURE CASTER (0 martial classes)',[r for r in ROWS if r['cat']=='caster'],10)
    show('TOP 10 HYBRID / MIXED (1-2 martial classes)',[r for r in ROWS if r['cat']=='hybrid'],10)
