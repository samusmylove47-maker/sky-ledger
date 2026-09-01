#!/usr/bin/env python3
"""m4 — model3.py rebuilt with reviewer-corrected constants. Every knob is a module global
so the sensitivity sweep can move exactly one thing at a time."""
import json, os, itertools, re, math

# DERIVED FROM __file__, NOT HARD-CODED. Until 1 Sep 2026 this read
# REPO="/home/user/sky-ledger", and the consequence was measured rather than reasoned:
# a fresh clone with ZERO shard files of its own imported this module successfully and
# loaded 515 weapons and 1,973 spells -- ALL OF THEM FROM /home/user/sky-ledger.
#
# So every weapon and spell figure this model publishes came from one machine's
# absolute path regardless of where the code was running. On a machine without that
# path it fails; on a machine WITH a stale copy there it silently reads a different
# tree, which is worse.
#
# AND IT MADE A GREEN GATE MEANINGLESS. fetch_shards.py fetches the three shards INTO
# THE CLONE and verifies them against their pins -- and this module then read a
# different copy. A gate that verifies bytes the consumer does not use. That is the
# sharpest form of the fault this repository has spent a week finding in other
# people's instruments, and it was here, green, the whole time.
#
# verify_upgrade.py:20 has always used the derived form. TWO FILES, ONE REPOSITORY,
# TWO CONVENTIONS FOR THE SAME CONSTANT -- and the hard-coded one is the one every
# published weapon figure went through. check_paths.py now fails on the typed form.
REPO = os.path.dirname(os.path.abspath(__file__))
CLASSES=['WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST','CLR','DRU','SHM','MAG','NEC','WIZ','ENC']
MARTIAL={'WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST'}
L=50

# ---- Wrath ---------------------------------------------------------------
OFFENSE={'WAR':210,'MNK':230,'ROG':210,'RNG':210,'BER':210,
         'PAL':200,'SHD':200,'BRD':200,'BST':200,
         'SHM':200,'CLR':200,'DRU':200,'ENC':140,'MAG':140,'NEC':140,'WIZ':140}
STR_MOD=120.0; SPELL_ATK=61.0; RNG_ATK=104.0
ELAST={'avg':0.141/104.0,'raid':0.257/139.0}
WRATH_BASE=365.0; E_RX_BASE=0.967
MITF={'avg':1.00,'raid':0.73}
def e_rx(w,mode): return E_RX_BASE*(1.0+ELAST[mode]*(w-WRATH_BASE))

# ---- swing outcome -------------------------------------------------------
P_LAND_BAL=0.5765; ACC_OFF=1.081
G_AVOID=0.0617; STRIKETHROUGH=0.30
BER_CRIT_RATE=0.06; WAR_CRIT_DMG=0.30
STANCE_DMG=2.00; CRIT_RATE=0.1272; CRIT_MULT=1.70

# ---- multi-attack --------------------------------------------------------
MH_CHAIN=1.520; OH_CHAIN=1.4911; DW_SUCCESS=0.88
# Measured ceiling on offhand attempts/s across 138 logs.
# THIS COMMENT USED TO SAY the cap was needed "without it the model picks Efreeti
# Standard (3 dmg / 10 delay)". That was true, and the reason was our own bug: up10()
# turned Efreeti Standard's base 3 into 13 rather than 6. With the floor removed the
# cap is INERT -- verify_upgrade.py section 5 runs the rankings with it and without it
# and gets identical DPS, identical offhand and an identical top 12. It is retained as
# a physical constraint on attempt rate, not as a patch. If it ever starts binding
# again, that is a signal about the catalogue, not a thing to re-tune.
OH_RATE_CAP=1.42

# ---- haste ---------------------------------------------------------------
# TIER M, 29 Aug 2026 -- the player's own character panel: everyone starts at 100%,
# a sheet at the haste cap reads 175%, a Monk trio reads 185%. So the cap is 75 and
# the Monk Unbound Alacrity adjustment is +10 percentage points, not 10% of 75.
# These were the values already in use; what changed is that they now have a source.
# The 395s jos437 parse gives 1.900 against the panel's 1.85 -- the PARSE is 2.7%
# high, not the model 2.7% low, which is how DAMAGE-CHAIN.md had it until today.
HASTE_CAP=75.0; MNK_ALACRITY_ADD=10.0
# NOT MODELLED: Berserker Stance halves ability cooldowns and doubles the current
# haste value ignoring the cap (player, tier M). The cooldown half would double every
# BER ability lane; it is left out because the corpus lane rates may already have been
# measured under that stance, and doubling a rate that contains the doubling is a 4x
# error. See DAMAGE-CHAIN.md "Berserker Stance" for the two haste readings and the
# one screenshot that settles them.

DUAL_WIELD={'BRD','BST','MNK','RNG','ROG','WAR'}
DOUBLE_ATTACK={'BER','MNK','PAL','RNG','ROG','SHD','WAR'}
TRIPLE_ATTACK={'BER','MNK','RNG','WAR','ROG'}

# ---- ability lanes -------------------------------------------------------
LANE_OWNER={'kick':{'BST','MNK','RNG','WAR'},'bash':{'PAL','SHD','WAR'},'strike':{'MNK'},
            'frenzy':{'BER'},'backstab':{'ROG'},'smite':{'PAL'}}
# PRE-stance lane means. kick/bash/strike/smite are TM: jos437 level-50 Offensive / 2.00
# (the only file where character, level, gear and stance are all pinned). frenzy/backstab
# have no level-50 sample -> established pooled value, which is a LOWER-geared window.
LANE_MEAN={'kick':58.50,'bash':71.15,'strike':35.05,'frenzy':57.21,'backstab':178.69,'smite':31.30}
LANE_RATE_MAX={'kick':0.54,'bash':0.54,'strike':0.50,'frenzy':0.72,'backstab':0.47,'smite':0.31}
LANE_RATE_MED={'kick':0.32,'bash':0.33,'strike':0.27,'frenzy':0.47,'backstab':0.29,'smite':0.17}
LANE_RATE=dict(LANE_RATE_MED)   # baseline = corpus MEDIAN; _MAX is the ceiling case
SMITE_RIDER=417.0          # flat, NOT stance-doubled, never crits

# ---- procs ---------------------------------------------------------------
PROC_PPM=2.4; PROC_CRIT_MULT=3.00; PROC_CRIT_RATE=0.122
PROC_BUFF={'SHM':(154.0,8.0),'BST':(102.0,3.0),'RNG':(35.0,2.0),'SHD':(80.0,2.0),'PAL':(60.0,2.0)}
SPELL_FOCUS=172.0/154.0
def proc_dps(dmg,ppm): return ppm/60.0*dmg*SPELL_FOCUS*(1+PROC_CRIT_RATE*(PROC_CRIT_MULT-1))
def weap_proc_dps(dmg,hand=1.0): return PROC_PPM*hand/60.0*dmg*(1+PROC_CRIT_RATE*(PROC_CRIT_MULT-1))

SPELL_LANE={'WIZ':167.6*0.40,'NEC':55.6,'SHM':51.2,'RNG':24.0,'SHD':24.7,
            'CLR':7.2,'DRU':6.9,'PAL':2.8,'MAG':0.0,'BST':0.0,'BRD':0.0,'ENC':0.0}
PET_LANE={'MAG':35.0,'BST':30.0,'NEC':22.3,'ENC':31.0,'SHD':8.6}
CHARM_PET=66.8; CHARMERS={'ENC','NEC','BRD'}

# ---- items ---------------------------------------------------------------
# Item upgrade to +10.  PERCENTAGE ONLY -- no +1/tier floor.  See verify_upgrade.py.
# The floor was in this line until 31 Aug 2026 as max(10, ...), and it was never
# measured: across the ten client captures this project and Session B hold between
# them, ZERO sit below base damage 10, which is the only region where the floor term
# is reachable.  EQUIPMENT-TRUTH.md section 2 graded the floor tier M off a tooltip
# whose five rows all tie -- a positive-control failure, not a confirmation.
# Dropping it is the conservative branch (the floor overstated 265 of 429 catalogue
# weapons, up to 5.50x on Truwian Baton) and it makes this file agree with Session B's
# upgrade.ts, so one item no longer gets two values across the seam.
# STILL UNMEASURED IN BOTH DIRECTIONS.  One client window of any sub-10-damage weapon
# at any tier >= 1 settles it; until then this is a choice, not a finding.
def up10(v,N=10): return v+(v*N)//10
ONEH={'1H Blunt','1H Slashing','1H Piercing','Piercing','Hand to Hand'}
TWOH={'2H Blunt','2H Slashing','2H Piercing'}
DELETED={'Rheumguls',"Wu's Tranquil Fist",'Beckon'}     # eqlwiki {{Delete}}: not in EQL
WEAP={}
for f in ('sh-PRIMARY.json','sh-SECONDARY.json','sh-RANGE.json'):
    for it in json.load(open(os.path.join(REPO,f)))['items']:
        if it.get('wp'): WEAP.setdefault(it['n'],it)
WEAP=list(WEAP.values())
SPELLS={s['name']:s for s in json.load(open(os.path.join(REPO,'spells.json')))['spells']}
def proc_damage(nm):
    s=SPELLS.get(re.sub(r'<[^>]+>','',nm or ''))
    if not s: return 0
    t=0
    for e in (s.get('effects') or []):
        m=re.search(r'(?:Decrease|decrease)\s+(?:Current\s+)?(?:Hit ?[Pp]oints|Hitpoints|HP)(?: when cast)? by (\d+)',e)
        if m: t=max(t,int(m.group(1)))
    return t
CONDITIONAL=('Dismiss Undead','Dismiss Summoned','Banish Undead','Banish Summoned')
def legal_w(w,T):
    cl=w['cl']
    if not cl: return True
    if cl[0]=='ALL_EXCEPT': return bool(set(T)-set(cl[1:]))
    if 'ALL' in cl: return True
    return bool(set(cl)&set(T))
def weapon_rows():
    out=[]
    for it in WEAP:
        if it['n'] in DELETED: continue
        w=it['wp']; d,dl,sk=w.get('dmg'),w.get('dly'),w.get('skill')
        if not d or not dl or sk=='Archery': continue
        kind='2H' if sk in TWOH else ('1H' if sk in ONEH else None)
        if not kind: continue
        pr=[e['n'] for e in (it.get('fx') or []) if e.get('k')=='proc']
        pd=max([proc_damage(p) for p in pr] or [0])
        cond=any(any(c in p for c in CONDITIONAL) for p in pr)
        sl=it.get('sl') or []
        out.append(dict(n=it['n'],kind=kind,dmg=up10(d),dly=dl,cl=it.get('cl') or [],
                        proc=pd,cond=cond,sl=sl))
    return out
WROWS=weapon_rows()
# Main-hand damage bonus. HAND_1H was 0.69 until 29 Aug 2026 and that was wrong:
# 0.69 reproduces 0 of the 9 one-handed observations on eqlwiki `Game_Mechanics`
# (rev 2026-08-11, re-fetched 43,724 B on 29 Aug), missing every one LOW by 1 to 3.
# 0.80 reproduces 5 of 9 exactly and is the LARGEST modifier that never over-predicts;
# every remaining miss is +1, the direction unrecorded DMG-above-level produces through
# the max(L,dmg) branch. Independently, `Efreeti Standard` 3/10 prints Dmg Bon 5, and
# floor(hand * 6.25) == 5 forces hand into [0.80, 0.96). See handmod.py.
HAND_1H=0.80; HAND_2H=1.10
def bonus(dmg,dly,hand): return hand*max(L,dmg)*(min(dly,50)/40.0)*(L/100.0)

def lane_dps(U,B,rate,wrath,mode,sm,pland,cr,cm,st):
    hit=1.089*U*e_rx(wrath,mode)*MITF[mode]+B+1.1
    hit*=(1-cr)+cr*cm
    return rate*(pland+st*G_AVOID)*hit*sm

def evaluate(trio,mode='raid',front=False,charm=True,rates='max'):
    """front=True  -> you are tanking, so Rogue backstab degrades to Chaotic Stab.
       charm=False -> nothing charmable in the fight (a single raid boss).
       rates       -> 'max' abilities on cooldown (min/maxed) | 'med' corpus median."""
    global LANE_RATE
    LANE_RATE = dict(LANE_RATE_MAX if rates=='max' else LANE_RATE_MED)
    T=set(trio)
    off=max(OFFENSE[c] for c in T)
    wrath=off+STR_MOD+SPELL_ATK+(RNG_ATK if 'RNG' in T else 0)
    martial=bool(T&MARTIAL)
    sm=STANCE_DMG if martial else 1.0
    pland=P_LAND_BAL*(ACC_OFF if martial else 1.0)
    haste=HASTE_CAP+(MNK_ALACRITY_ADD if 'MNK' in T else 0.0)
    hm=1+haste/100.0
    mhc=MH_CHAIN if (T&DOUBLE_ATTACK) else 1.0
    ohc=OH_CHAIN*DW_SUCCESS if (T&DOUBLE_ATTACK) else DW_SUCCESS
    dw=bool(T&DUAL_WIELD)
    cr=CRIT_RATE+(BER_CRIT_RATE if 'BER' in T else 0.0)
    cm=CRIT_MULT*(1+WAR_CRIT_DMG if 'WAR' in T else 1.0)
    st=STRIKETHROUGH if 'RNG' in T else 0.0
    best=None
    for mh in WROWS:
        if not legal_w(mh,T) or 'PRIMARY' not in mh['sl']: continue
        U=2*mh['dmg']+1
        B=bonus(mh['dmg'],mh['dly'],HAND_2H if mh['kind']=='2H' else HAND_1H)
        rate=hm/(mh['dly']/10.0)*mhc
        d=lane_dps(U,B,rate,wrath,mode,sm,pland,cr,cm,st)
        pm=weap_proc_dps(mh['proc'],1.0) if (mh['proc'] and not mh['cond']) else 0.0
        oh_d,oh_pm,oh=0.0,0.0,None
        if mh['kind']=='1H' and dw:
            for o in WROWS:
                if o['kind']!='1H' or not legal_w(o,T) or o['n']==mh['n']: continue
                if 'SECONDARY' not in o['sl']: continue
                Uo=2*o['dmg']+1
                ro=min(hm/(o['dly']/10.0)*ohc, OH_RATE_CAP)
                dd=lane_dps(Uo,0.0,ro,wrath,mode,sm,pland,cr,cm,st)
                pp=weap_proc_dps(o['proc'],0.5) if (o['proc'] and not o['cond']) else 0.0
                if dd+pp>oh_d+oh_pm: oh_d,oh_pm,oh=dd,pp,o
        tot=d+pm+oh_d+oh_pm
        if best is None or tot>best['wtot']:
            best=dict(mh=mh,oh=oh,mhd=d,mhp=pm,ohd=oh_d,ohp=oh_pm,wtot=tot)
    lanes=[];lane_total=0.0
    scale=(e_rx(wrath,mode)*MITF[mode]/(E_RX_BASE*MITF['avg']))
    critadj=((1-cr)+cr*cm)/((1-CRIT_RATE)+CRIT_RATE*CRIT_MULT)
    for ln,owners in LANE_OWNER.items():
        if not (T&owners): continue
        v=LANE_RATE[ln]*pland*LANE_MEAN[ln]*scale*sm*critadj
        if ln=='smite': v+=LANE_RATE[ln]*pland*SMITE_RIDER
        if ln=='backstab' and front: v*=0.20     # Chaotic Stab: minimal damage from the front
        lanes.append((ln,v)); lane_total+=v
    pb=max([proc_dps(d_,p_) for c,(d_,p_) in PROC_BUFF.items() if c in T]+[proc_dps(*PROC_BUFF['SHM'])])
    spell=sum(SPELL_LANE.get(c,0.0) for c in T)
    pet=max([PET_LANE.get(c,0.0) for c in T] or [0.0])
    charmdps=CHARM_PET if (charm and (T&CHARMERS)) else 0.0
    pet=max(pet,charmdps)
    total=best['wtot']+lane_total+pb+spell+pet
    return dict(trio=tuple(sorted(T)),total=total,wrath=wrath,haste=haste,lanes=lanes,
                lane_total=lane_total,procbuff=pb,spell=spell,pet=pet,charmdps=charmdps,
                melee=best['wtot']+lane_total,**best)

def run(mode='raid',n=12,**kw):
    res=[evaluate(t,mode,**kw) for t in itertools.combinations(CLASSES,3)]
    res.sort(key=lambda r:-r['total']); return res

if __name__=='__main__':
    import sys
    mode=sys.argv[1] if len(sys.argv)>1 else 'raid'
    res=run(mode)
    print(f"{'#':>3} {'trio':<16}{'DPS':>7}{'wrath':>6}{'ht':>5}  {'main':<28}{'offhand':<24}{'weap':>6}{'abil':>6}{'proc':>6}{'sp/pet':>7}")
    for i,r in enumerate(res[:12],1):
        print(f"{i:>3} {'+'.join(r['trio']):<16}{r['total']:>7.0f}{r['wrath']:>6.0f}{r['haste']:>5.0f}  "
              f"{r['mh']['n'][:28]:<28}{(r['oh']['n'][:24] if r['oh'] else '-'):<24}"
              f"{r['wtot']:>6.0f}{r['lane_total']:>6.0f}{r['procbuff']:>6.0f}{r['spell']+r['pet']:>7.0f}")
