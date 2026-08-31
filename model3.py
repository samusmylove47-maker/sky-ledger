#!/usr/bin/env python3
"""EQ Legends trio model v3 — built on the measured damage chain in DAMAGE-CHAIN.md.

Every constant traces to a measurement or is flagged ASSUMED. Run:  python3 model3.py
"""
import json, os, itertools, urllib.request, collections, math

BASE = "https://samusmylove47-maker.github.io/EQL50ups/data/items/"
for s in ("PRIMARY", "SECONDARY", "RANGE"):
    if not os.path.exists(f"sh-{s}.json"):
        urllib.request.urlretrieve(BASE + s + ".json", f"sh-{s}.json")

CLASSES = ['WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST','CLR','DRU','SHM','MAG','NEC','WIZ']
MARTIAL = {'WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST'}
L = 50

# ---- Wrath ---------------------------------------------------------------
# Offense cap AT LEVEL 50 (the "cap until 50" column). Warrior's is confirmed 210
# from a cached class page; 200 and 140 classes show no until-50 reduction.
# PAL/SHD/BRD until-50 values are NOT published -> ASSUMED equal to their above-50 cap.
OFFENSE = {'WAR':210,'MNK':210,'ROG':210,'RNG':210,'BER':210,      # 252 above 50 -> 210 at 50
           'PAL':225,'SHD':225,'BST':225,                          # ASSUMED (BST unpublished)
           'BRD':215,'SHM':200,'CLR':200,'DRU':200,
           'MAG':140,'NEC':140,'WIZ':140}
STR_MOD   = 120.0     # ((2*255)-150)/3, STR hard-capped at 255
SPELL_ATK = 15.0      # Spirit of Bih'Li, supplied by the support partner to everyone
RNG_ATK   = 104.0     # Hunter's Attack Power, 26 ranks x 4, cost 0

# ATK -> damage elasticity, from the measured mitigation spread (DAMAGE-CHAIN.md §5).
# +104 ATK measured at +14.1% on an average target and +25.7% (for +139) on a raid boss.
ELAST = {'avg': 0.141/104.0, 'raid': (0.257/139.0)}
WRATH_BASE = 372.0    # the corpus character's Wrath, where E_rx = 0.973 was measured
E_RX_BASE  = 0.973
MITF = {'avg': 1.00, 'raid': 0.73}      # measured MitFactor, Nagafen 0.70-0.73

def e_rx(wrath, mode):
    return E_RX_BASE * (1.0 + ELAST[mode] * (wrath - WRATH_BASE))

# ---- swing outcome (measured) -------------------------------------------
P_LAND_BAL, P_LAND_OFF = 0.5765, 0.6231
G_AVOID = 0.0617                        # active-defence avoidance, measured
STRIKETHROUGH = 0.30                    # Ranger, 3 ranks, free
# crit AAs.  Combat Fury (General, +5% rate) is available to every trio, so it is
# baseline and does not differentiate.  These two do:
BER_CRIT_RATE = 0.06                    # Unbound Fury, free
WAR_CRIT_DMG  = 0.30                    # Unbound Wrath, free: +30% melee CRIT DAMAGE
STANCE_DMG  = 2.00                      # Offensive, measured by the parity test
CRIT_RATE, CRIT_MULT = 0.1272, 1.70

# ---- skills --------------------------------------------------------------
DUAL_WIELD    = {'BRD','BST','MNK','RNG','ROG','WAR'}
DOUBLE_ATTACK = {'BER','MNK','PAL','RNG','ROG','SHD','WAR'}
TRIPLE_ATTACK = {'BER','MNK','RNG','WAR'}
OFFENSIVE     = MARTIAL                 # all nine martial classes have Offensive stance
DEFENSIVE     = {'WAR','PAL','SHD'}
STRIKER       = {'BER','MNK','ROG','WAR'}
BERSERKER_ST  = {'BER'}

# Damage-dealing autoskill lanes, by the verb the client actually logs.
# Monk's five specials collapse into 'strike' and 'kick' in every log -> two lanes, not six.
LANE_OWNER = {'kick':{'BST','MNK','RNG','WAR'}, 'bash':{'PAL','SHD','WAR'},
              'strike':{'MNK'}, 'frenzy':{'BER'}, 'backstab':{'ROG'}, 'slam':{'WAR'}}
# measured mean damage per landed hit (n=9,983, level 50) and measured fire rate /s
LANE_STAT = {'kick':(57.71,0.28),'bash':(67.71,0.36),'strike':(54.09,0.48),
             'frenzy':(57.21,0.50),'backstab':(178.69,0.30),'slam':(67.71,0.30)}

# ---- haste ---------------------------------------------------------------
HASTE_CAP = 175.0
MNK_ALACRITY = 1.10                     # Unbound Alacrity, +10% to current AND max haste

# ---- class self-proc buffs (PPM; procs do NOT scale with swing rate) -----
PROC_BUFF = {'SHM':(154.0,8.0),'BST':(102.0,3.0),'RNG':(35.0,2.0),'SHD':(80.0,2.0),'PAL':(60.0,2.0)}
PROC_CRIT_MULT, PROC_CRIT_RATE = 3.00, 0.116
SPELL_FOCUS = 172.0/154.0               # measured: this player's Puma reads 172 not 154

def proc_dps(dmg, ppm):
    return ppm/60.0 * dmg * SPELL_FOCUS * (1 + PROC_CRIT_RATE*(PROC_CRIT_MULT-1))

# ---- measured swing-rate ceilings (attempts/s, includes double/triple/flurry) ----
# Corpus maxima: slash 1.97, pierce 1.42, claw 1.03, kick .54, bash .54, strike .50,
# frenzy .72, backstab .47.  A floor on effective swing time is a real EQ mechanic and
# the model must not extrapolate past what was observed; 2.5 allows headroom for BIS
# haste above what the corpus characters carried.  ASSUMED ceiling, flagged.
RATE_CAP_MH, RATE_CAP_OH = 2.50, 1.60

# ---- sustained non-melee lanes, measured per class from the corpus ------------
# Summed DPS of every DoT/nuke uniquely attributable to that class.  Pure nukers are
# mana-limited over a long fight, so WIZ carries a sustain haircut.  WEAKEST TABLE HERE.
SPELL_LANE = {'WIZ':167.6*0.40,'NEC':55.6,'SHM':51.2,'RNG':36.3,'SHD':24.7,
              'CLR':7.2,'DRU':6.9,'PAL':2.8,'MAG':0.0,'BST':0.0,'BRD':0.0}
PET_LANE   = {'MAG':35.0,'BST':30.0,'NEC':25.0}   # summoned pets, measured band

# ---- items ---------------------------------------------------------------
# superseded rule -- see model4.py and verify_upgrade.py. The +1/tier floor this
# line used to carry is unmeasured; percentage-only is the conservative branch.
def up10(v, N=10): return v + (v*N)//10
ONEH = {'1H Blunt','1H Slashing','1H Piercing','Hand to Hand'}
TWOH = {'2H Blunt','2H Slashing','2H Piercing'}
WEAP = {}
for f in ('sh-PRIMARY.json','sh-SECONDARY.json','sh-RANGE.json'):
    for it in json.load(open(f))['items']:
        if it.get('wp'): WEAP.setdefault(it['n'], it)
WEAP = list(WEAP.values())

import re
SPELLS = None
for p in ('spells.json','corpus/everquest-companion/src/main/data/spells.json'):
    if os.path.exists(p): SPELLS = {s['name']: s for s in json.load(open(p))['spells']}; break
def proc_damage(nm):
    if not SPELLS: return 0
    s = SPELLS.get(nm)
    if not s: return 0
    t = 0
    for e in (s.get('effects') or []):
        m = re.search(r'Decrease (?:Hit ?[Pp]oints|HP)(?: when cast)? by (\d+)', e)
        if m: t += int(m.group(1))
    return t
# procs whose name says they only fire on a creature type — not general-purpose
CONDITIONAL = ('Dismiss Undead','Dismiss Summoned','Banish Undead','Banish Summoned')

def legal(it, trio):
    cl = set(it.get('cl') or [])
    if 'ALL' in cl: return True
    return bool(cl & set(trio))

def weapon_rows():
    out = []
    for it in WEAP:
        w = it['wp']; d, dl, sk = w.get('dmg'), w.get('dly'), w.get('skill')
        if not d or not dl or sk == 'Archery': continue
        kind = '2H' if sk in TWOH else ('1H' if sk in ONEH else None)
        if not kind: continue
        pr = [e['n'] for e in (it.get('fx') or []) if e.get('k') == 'proc']
        pd = max([proc_damage(p) for p in pr] or [0])
        cond = any(any(c in p for c in CONDITIONAL) for p in pr)
        out.append(dict(n=it['n'], kind=kind, dmg=up10(d), dly=dl, cl=it.get('cl') or [],
                        proc=pd, cond=cond, procname=(pr[0] if pr else '')))
    return out
WROWS = weapon_rows()

def bonus(dmg, dly, hand):
    return hand * max(L, dmg) * (min(dly,50)/40.0) * (L/100.0)

def lane_dps(U, B, rate, wrath, mode, stance_mult, pland, cr=CRIT_RATE, cm=CRIT_MULT, st=0.0):
    hit = 1.089 * U * e_rx(wrath, mode) * MITF[mode] + B + 1.1
    hit *= (1 - cr) + cr*cm
    pland = pland + st * G_AVOID          # strikethrough converts avoided swings to landed
    return rate * pland * hit * stance_mult

def evaluate(trio, mode='raid', want=None):
    T = set(trio)
    off = max(OFFENSE[c] for c in T)
    wrath = off + STR_MOD + SPELL_ATK + (RNG_ATK if 'RNG' in T else 0)
    martial = bool(T & MARTIAL)
    stance_mult = STANCE_DMG if martial else 1.0
    pland = P_LAND_OFF if martial else P_LAND_BAL
    haste = HASTE_CAP * (MNK_ALACRITY if 'MNK' in T else 1.0)
    hm = 1 + haste/100.0
    da = 0.476 if T & DOUBLE_ATTACK else 0.0
    ta = 0.238 if T & TRIPLE_ATTACK else 0.0
    chain = 1 + da + da*ta
    dw = bool(T & DUAL_WIELD)
    cr = CRIT_RATE + (BER_CRIT_RATE if 'BER' in T else 0.0)
    cm = CRIT_MULT * (1 + WAR_CRIT_DMG if 'WAR' in T else 1.0)
    st = STRIKETHROUGH if 'RNG' in T else 0.0

    best = None
    for mh in WROWS:
        if not legal_w(mh, T): continue
        U = 2*mh['dmg'] + 1
        B = bonus(mh['dmg'], mh['dly'], 1.10 if mh['kind']=='2H' else 0.69)
        rate = min(hm / (mh['dly']/10.0) * chain, RATE_CAP_MH)
        d = lane_dps(U, B, rate, wrath, mode, stance_mult, pland, cr, cm, st)
        pm = proc_dps(mh['proc'], 2.0) if (mh['proc'] and not mh['cond']) else 0.0
        oh_d, oh_pm, oh = 0.0, 0.0, None
        if mh['kind']=='1H' and dw:
            for o in WROWS:
                if o['kind']!='1H' or not legal_w(o, T) or o['n']==mh['n']: continue
                Uo = 2*o['dmg']+1
                ro = min(hm/(o['dly']/10.0) * 0.85 * (1+da), RATE_CAP_OH)
                dd = lane_dps(Uo, 0.0, ro, wrath, mode, stance_mult, pland, cr, cm, st)
                pp = proc_dps(o['proc'],1.0) if (o['proc'] and not o['cond']) else 0.0
                if dd+pp > oh_d+oh_pm: oh_d, oh_pm, oh = dd, pp, o
        tot = d + pm + oh_d + oh_pm
        if best is None or tot > best['wtot']:
            best = dict(mh=mh, oh=oh, mhd=d, mhp=pm, ohd=oh_d, ohp=oh_pm, wtot=tot)

    lanes, lane_total = [], 0.0
    for ln, owners in LANE_OWNER.items():
        if T & owners:
            mean, rate = LANE_STAT[ln]
            v = rate * mean * (e_rx(wrath,mode)*MITF[mode]/(E_RX_BASE*MITF['avg'])) * stance_mult
            v *= ((1-cr) + cr*cm) / ((1-CRIT_RATE) + CRIT_RATE*CRIT_MULT)
            if ln == 'backstab' and want == 'front':
                v *= 0.20                 # Chaotic Stab: minimal damage when not behind
            lanes.append((ln, v)); lane_total += v

    pb = max([proc_dps(d_,p_) for c,(d_,p_) in PROC_BUFF.items() if c in T] or [0.0])
    partner_puma = proc_dps(*PROC_BUFF['SHM'])   # the support partner supplies Puma regardless
    pb = max(pb, partner_puma)

    spell = sum(SPELL_LANE.get(c,0.0) for c in T)
    pet   = max([PET_LANE.get(c,0.0) for c in T] or [0.0])
    total = best['wtot'] + lane_total + pb + spell + pet
    return dict(trio=tuple(sorted(T)), total=total, wrath=wrath, off=off, **best,
                lanes=lanes, lane_total=lane_total, procbuff=pb, martial=martial,
                dw=dw, haste=haste, chain=chain, spell=spell, pet=pet,
                melee=best['wtot']+lane_total)

def legal_w(w, T):
    cl = set(w['cl'])
    return ('ALL' in cl) or bool(cl & T)

if __name__ == '__main__':
    res = [evaluate(t) for t in itertools.combinations(CLASSES, 3)]
    res.sort(key=lambda r: -r['total'])
    print(f"{'#':>3} {'trio':<16} {'DPS':>7} {'wrath':>6} {'weapon (main)':<30} {'offhand':<22} {'melee':>6} {'proc':>6} {'spell':>6}")
    for i, r in enumerate(res[:25], 1):
        print(f"{i:>3} {'+'.join(r['trio']):<16} {r['total']:>7.0f} {r['wrath']:>6.0f} "
              f"{r['mh']['n'][:30]:<30} {(r['oh']['n'][:22] if r['oh'] else '-'):<22} "
              f"{r['melee']:>6.0f} {r['procbuff']+r['mhp']+r['ohp']:>6.0f} {r['spell']+r['pet']:>6.0f}")
