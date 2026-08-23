#!/usr/bin/env python3
"""EQ Legends trio damage model — see BUILDS.md.

Ranks all 560 class trios by sustained damage. Weapon data is pulled from the
EQL50ups catalogue (the dataset behind eqlsource's 50 Upgrades planner).

    python3 model.py                 # baseline
    PET=44.5 python3 model.py        # pet at the measured all-fights floor
    K=0.10  python3 model.py         # ATK coefficient at the classic-folklore value
"""
import os, urllib.request
BASE = "https://samusmylove47-maker.github.io/EQL50ups/data/items/"
for _slot in ("PRIMARY", "SECONDARY"):
    _f = f"sh-{_slot}.json"
    if not os.path.exists(_f):
        urllib.request.urlretrieve(BASE + _slot + ".json", _f)

import json, itertools
CLASSES=['WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST','CLR','DRU','SHM','ENC','MAG','NEC','WIZ']
L=50; R=0.55
import os
K=float(os.environ.get('K','0.025'))   # %DPS per 100 ATK (dev-refused)
PETV=float(os.environ.get('PET','85'))                      # level, mean weapon roll
DEF={'WAR','PAL','SHD'}; STRK={'BER','MNK','ROG','WAR'}; BSK={'BER'}
EVA={'BRD','MNK','RNG','BST','ROG'}; CHAN={'CLR','DRU','SHM','ENC','MAG','NEC','WIZ'}
CHARM={'ENC'}; SUMMON={'MAG','NEC','BST','SHD'}
HEAL={'CLR','DRU','SHM','PAL','RNG','BST'}
pri=json.load(open('sh-PRIMARY.json')); pri=pri['items'] if isinstance(pri,dict) else pri
sec=json.load(open('sh-SECONDARY.json')); sec=sec['items'] if isinstance(sec,dict) else sec
def elig(it,cls):
    cl=it.get('cl') or []
    if 'ALL' in cl: return True
    if any(c.startswith('ALL_EXCEPT') for c in cl):
        ex=[c for c in cl if not c.startswith('ALL_EXCEPT')]
        return not (set(cls)&set(ex))
    return bool(set(cl)&set(cls))
def bonus(dmg,dly,hand):        # eqlwiki Game_Mechanics, client-validated 2/2
    return hand*max(L,dmg)*(min(dly,50)/40.0)*(L/100.0)
def hitvals(dmg,dly,hand,crit):
    b=bonus(dmg,dly,hand)
    normal=R*dmg+b
    cr=(max(R*dmg,dmg)+5)*1.7+b
    return (1-crit)*normal+crit*cr
def weapons(cls):
    twos,ones=[],[]
    for i in pri:
        w=i.get('wp')
        if not w or not elig(i,cls): continue
        d,dl,sk=w['dmg']*2,w['dly'],str(w.get('skill',''))
        (twos if sk.startswith('2H') else ones).append((d,dl,i['n'],'SECONDARY' in (i.get('sl') or [])))
    offs=[]
    for i in sec:
        w=i.get('wp')
        if not w or not elig(i,cls): continue
        if 'SECONDARY' not in (i.get('sl') or []): continue
        offs.append((w['dmg']*2,w['dly'],i['n']))
    return twos,ones,offs
def build(cls):
    cls=set(cls)
    has=lambda s: bool(cls&s)
    crit=0.05+(0.06 if 'BER' in cls else 0.0)
    M=1.8 if cls&{'BER','WAR'} else 1.6
    hasteM=1.85 if 'MNK' in cls else 1.75
    dw=0.832 if 'MNK' in cls else (0.693 if cls&{'WAR','RNG','ROG','BER','BRD','BST','SHD','PAL'} else 0.0)
    delta=0.85 if cls&{'CLR','DRU','SHM'} else 1.0
    twos,ones,offs=weapons(cls)
    best2=max(twos,key=lambda t:(2*t[0]+bonus(t[0],t[1],1.1))/t[1]) if twos else None
    best1=max(ones,key=lambda t:(2*t[0]+bonus(t[0],t[1],0.8))/t[1]) if ones else None
    besto=max(offs,key=lambda t:t[0]/t[1]) if offs else None
    def rate(dly,mult): return 10.0/max(1,int(dly/mult))
    opts=[]
    if best2:
        d,dl,n,_=best2; h=hitvals(d,dl,1.1,crit)
        opts.append(('2H '+n, rate(dl,hasteM)*M*h, rate(dl,hasteM*2)*M*h if 'BER' in cls else None))
    if best1 and besto and dw>0:
        d,dl,n,_=best1; h=hitvals(d,dl,0.8,crit)
        od,odl,on=besto; oh=hitvals(od,odl,0.0,crit)
        mainr=rate(dl,hasteM); offr=rate(odl,hasteM)*dw
        base=mainr*M*h+offr*oh
        bsk=(rate(dl,hasteM*2)*M*h+rate(odl,hasteM*2)*dw*oh) if 'BER' in cls else None
        opts.append((f'DW {n} / {on}', base, bsk))
    if not opts: return None
    lab,base,bskrate=max(opts,key=lambda o:o[1])
    # damage stance: Berserker (2x speed, already in bskrate) else Offensive (2x dmg)
    if 'BER' in cls and bskrate: stance_dps=bskrate*0.8394*delta; sname='Berserker'
    else: stance_dps=base*2*0.8394*delta; sname='Offensive'
    bal=base*0.7387*delta
    pet=PETV if has(CHARM) else (15.6 if has(SUMMON) else 0.0)
    fren_bal=25.0 if 'BER' in cls else 0.0
    fren_st=62.5 if 'BER' in cls else 0.0
    procs=9.5 if has({'SHD','NEC'}) else 0.0
    rng = (1.0191*(1+1.04*K)) if 'RNG' in cls else 1.0     # strikethrough + 104 ATK x k
    bal*=rng; stance_dps*=rng
    starved=bal+pet+fren_bal+procs
    free=stance_dps+pet+fren_st+procs
    mit=('Defensive' if has(DEF) else ('Channeler' if has(CHAN) else ('Evasive' if has(EVA) else 'NONE')))
    return dict(trio='+'.join(sorted(cls)),weapon=lab,stance=sname,starved=starved,free=free,
                sustained=0.65*starved+0.35*free, pet=pet, mit=mit, heal=bool(cls&HEAL),
                aggro=('AE' if 'WAR' in cls else ('single' if has(DEF) else 'weak')))
rows=[r for r in (build(c) for c in itertools.combinations(CLASSES,3)) if r]
def show(title,key,n=14,filt=None):
    print('\n'+title)
    print(f"  {'trio':<16}{'sust':>7}{'starv':>7}{'free':>7}  {'mit':<10}{'agg':<7}{'stance':<10}weapon")
    sel=[r for r in rows if (filt(r) if filt else True)]
    for r in sorted(sel,key=lambda x:-x[key])[:n]:
        print(f"  {r['trio']:<16}{r['sustained']:7.1f}{r['starved']:7.1f}{r['free']:7.1f}  {r['mit']:<10}{r['aggro']:<7}{r['stance']:<10}{r['weapon'][:34]}")
show('TOP BY SUSTAINED DAMAGE (0.65 starved + 0.35 free)','sustained')
show('TOP BY BURST (endurance-free)','free')
show('TOP THAT CAN ALSO TANK (has Defensive or Channeler) AND SELF-HEAL','sustained',12,
     lambda r: r['mit'] in ('Defensive','Channeler') and r['heal'])
for t in (('RNG','CLR','ENC'),('SHD','RNG','BER'),('PAL','ENC','MNK'),('RNG','CLR','WAR'),('WAR','RNG','BER')):
    r=build(t); print(f"\n{r['trio']:<16} sust {r['sustained']:6.1f} | starved {r['starved']:6.1f} | free {r['free']:6.1f} | {r['mit']:<10} | {r['weapon'][:40]}")
