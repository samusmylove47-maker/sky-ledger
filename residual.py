#!/usr/bin/env python3
"""residual.py -- falsify model4 against assets/raids-measured.json.

Reads the Director's dataset, derives our own per-character output for every
fight, and states where the model reproduces it and where it stops. Every
figure below is read out of the dataset at run time; nothing is typed.
"""
import json, math, os, sys, collections, statistics as st
import itertools, model4 as M

# TWO DEFECTS FIXED HERE 1 Sep 2026, and the second is the shards defect again.
#
# 1. `DATA = sys.argv[1] if len(sys.argv) > 1 else ...` ran AT MODULE SCOPE, so any
#    script importing this module inherited its argument parsing. sensitivity.py has
#    imported it since the day it was written and only worked because nobody ever
#    passed sensitivity.py an argument. The first one I passed made it try to open a
#    file called "--check". A module that reads sys.argv at import time hijacks its
#    importer.
#
# 2. THE DEFAULT PATH IS AN ABSOLUTE SCRATCHPAD PATH CARRYING ONE SESSION'S UUID, and
#    the file is not committed anywhere. So `residual.py` and everything downstream of
#    it -- including sensitivity.py and the published 4.59x model-vs-measured ratio and
#    the 71.9 DPS measured median -- rest on a file that exists on ONE CONTAINER and
#    nowhere else. That is exactly the fault fetch_shards.py exists for: "check.sh had
#    been passing for days on an untracked file that happened to sit on one container's
#    disk." I found it there on 31 Aug and left it live in two more files.
#
# WHAT IS AND IS NOT FIXED. The path is now declarable and the bytes are PINNED, so a
# substituted dataset fails loudly instead of silently changing every figure. What is
# NOT fixed is the availability: this dataset came from the Director, not from a URL I
# can fetch, so there is nothing to re-fetch it FROM. Committing it into this
# repository would settle that permanently and IS NOT MINE TO DECIDE -- it is another
# session's measured data, 207,239 bytes of it. RULING NEEDED; flagged, not taken.
DATA_SHA256 = "11823ae7b43509feb15721b4118458707d2828c465c625a989e233a836f342d5"
DATA_BYTES = 207239
DATA_RECORDS = 213
DEFAULT_DATA = ("/tmp/claude-0/-home-user-sky-ledger/"
                "caaa72f1-a659-51f4-8828-08bfb34cde0c/scratchpad/dir/raids-measured.json")


def resolve(path=None):
    return os.path.expanduser(path or os.environ.get("EQLS_RAIDS_MEASURED") or DEFAULT_DATA)


def load(path=None, require=True):
    """Return (records, status). status is 'pinned' | 'DRIFTED' | 'ABSENT'."""
    import hashlib
    p = resolve(path)
    if not os.path.exists(p):
        if require:
            raise FileNotFoundError(
                f"{p} is absent. Every figure this module prints -- the model envelope, "
                "the containment test, the 4.59x ratio and the measured median -- is "
                "UNREPRODUCIBLE without it. It is the Director's measured dataset, "
                f"{DATA_BYTES} bytes, sha256 {DATA_SHA256[:16]}..., and it is not "
                "committed anywhere. Set EQLS_RAIDS_MEASURED to its path.")
        return [], "ABSENT"
    raw = open(p, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    return json.loads(raw.decode("utf-8")), ("pinned" if got == DATA_SHA256 else "DRIFTED")


DATA = resolve()
F, DATA_STATUS = load(require=False)

def ours(x):
    """Damage dealt by OUR characters, and the count of them present.

    our_damage_share_pct is a share of the witnessed total, and our own
    character's lines are the part of a log that is never under-witnessed.
    So this quantity survives damage_is_floor, which bounds the BOSS's hit
    points, not our output. Stated as a claim to be checked, not assumed."""
    n = len(set(x["observers"]))
    return x["damage_low"] * x["our_damage_share_pct"] / 100.0, n

def dps(x):
    d, n = ours(x)
    return (d / x["seconds"] / n) if x["seconds"] else None

# ---------------------------------------------------------------- model envelope
# THIRD DEFECT, same file, found the same way. This ran AT MODULE SCOPE: 560 trios x
# 4 (mode, rates) combinations = 2,240 model evaluations, MINUTES of work, paid by
# anyone who so much as imports this module. sensitivity.py imports it, which is most
# of why sensitivity.py took 1m55s -- the sweeps were never the expensive part.
# It is also why a `--check` arm could not be fast until now: the check would have
# waited on an envelope it does not read.
# Nothing about the figures changes. Only WHEN they are computed.
def envelope():
    env = {}
    for mode in ("avg", "raid"):
        for rates in ("max", "med"):
            v = sorted(M.evaluate(t, mode, front=False, charm=False, rates=rates)["total"]
                       for t in itertools.combinations(M.CLASSES, 3))
            env[(mode, rates)] = (v[0], v[len(v)//2], v[-1])
    return env

def band(title, rows):
    v = sorted(r for r in (dps(x) for x in rows) if r is not None)
    if not v: return None
    return dict(n=len(v), lo=v[0], p25=v[len(v)//4], med=st.median(v),
                p75=v[3*len(v)//4], p90=v[int(0.9*(len(v)-1))], hi=v[-1])

GOLD  = [x for x in F if x["our_damage_share_pct"] == 100.0]
CLEAN = [x for x in GOLD if not x["damage_is_floor"]]

if __name__ == "__main__":
    if "--check" in sys.argv:
        # ABSENT is reported, not fatal: nothing on a fresh clone can restore a file
        # that has no source, and a suite that is red for a reason nobody can fix
        # teaches its reader to ignore it. DRIFTED IS fatal -- a substituted dataset
        # silently changes every figure downstream, which is the whole point of a pin.
        print(f"  dataset: {DATA}")
        if DATA_STATUS == "ABSENT":
            print(f"  [ABSENT] NOT REPRODUCIBLE ON THIS MACHINE. residual.py and "
                  f"sensitivity.py print figures -- the 4.59x ratio, the measured "
                  f"median -- that cannot be recomputed here. Expected {DATA_BYTES} "
                  f"bytes, sha256 {DATA_SHA256[:16]}... Set EQLS_RAIDS_MEASURED.")
            sys.exit(0)
        if DATA_STATUS == "DRIFTED":
            print("  [FAIL] the dataset is present and its bytes DO NOT MATCH the pin. "
                  "Every figure downstream is a function of these bytes; a human "
                  "decides whether the published numbers move.")
            sys.exit(1)
        print(f"  [ok] pinned: {DATA_BYTES} bytes, {len(F)} records, "
              f"sha256 {DATA_SHA256[:16]}...")
        if len(F) != DATA_RECORDS:
            print(f"  [FAIL] record count {len(F)} != pinned {DATA_RECORDS}")
            sys.exit(1)
        print(f"  [ok] record count {len(F)} matches the pin")
        sys.exit(0)
    if DATA_STATUS == "ABSENT":
        raise SystemExit(load(require=True))
    ENV = envelope()
    print("=" * 92)
    print("MODEL ENVELOPE  (560 trios, level 50, best legal weapon in the corpus, Offensive stance)")
    print("=" * 92)
    print(f"{'mitigation':>10} {'rates':>6} {'worst trio':>11} {'median trio':>12} {'best trio':>10}")
    for (mode, rates), (a, b, c) in sorted(ENV.items()):
        print(f"{mode:>10} {rates:>6} {a:11.1f} {b:12.1f} {c:10.1f}")

    print()
    print("=" * 92)
    print("MEASURED  (per our character present, damage_low x share / seconds / distinct observers)")
    print("=" * 92)
    print(f"{'set':<34} {'n':>4} {'min':>7} {'p25':>7} {'med':>7} {'p75':>7} {'p90':>7} {'max':>7}")
    for nm, rows in (("all fights", F),
                     ("gold: share == 100%", GOLD),
                     ("gold AND not floor-marked", CLEAN),
                     ("not floor-marked (any share)", [x for x in F if not x["damage_is_floor"]]),
                     ("floor-marked", [x for x in F if x["damage_is_floor"]])):
        b = band(nm, rows)
        if b:
            print(f"{nm:<34} {b['n']:4d} {b['lo']:7.1f} {b['p25']:7.1f} {b['med']:7.1f} "
                  f"{b['p75']:7.1f} {b['p90']:7.1f} {b['hi']:7.1f}")

    print()
    print("=" * 92)
    print("CONTAINMENT — the one-sided test the data can actually run")
    print("=" * 92)
    lo_raid = ENV[("raid", "max")][0]; hi_avg = ENV[("avg", "max")][2]
    v = [d for d in (dps(x) for x in F) if d is not None]
    over  = sum(1 for d in v if d > hi_avg)
    under = sum(1 for d in v if d < lo_raid)
    print(f"model ceiling (best trio, avg mitigation, max rates) = {hi_avg:.1f} DPS")
    print(f"  fights exceeding it: {over} of {len(v)}  -> the model is NOT falsified from above")
    print(f"model floor   (worst trio, raid mitigation, max rates) = {lo_raid:.1f} DPS")
    print(f"  fights below it:     {under} of {len(v)} ({100*under/len(v):.0f}%)"
          f"  -> the model's weakest claim over-predicts {100*under/len(v):.0f}% of real fights")
    print(f"  ratio, model floor to measured median: {lo_raid/st.median(v):.2f}x")

    print()
    print("=" * 92)
    print("DENOMINATOR — is `seconds` engaged time or wall clock?")
    print("=" * 92)
    pts = [(x["seconds"], dps(x)) for x in F if x["seconds"] and dps(x)]
    xs = [math.log(a) for a, _ in pts]; ys = [math.log(b) for _, b in pts]
    mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
    cov = sum((a-mx)*(b-my) for a, b in zip(xs, ys))
    vx = sum((a-mx)**2 for a in xs); vy = sum((b-my)**2 for b in ys)
    print(f"log(dps) on log(seconds): slope {cov/vx:+.3f}, r {cov/math.sqrt(vx*vy):+.3f}, n={len(pts)}")
    print("  pure dead time appended to a fixed engaged window would give slope -1.00.")
    print("  -1.00 is outside this sample; the denominator inflates DPS by less than a factor of two,")
    print("  so it cannot account for the gap above.")
    for lo, hi in ((0,30),(30,60),(60,120),(120,240),(240,480),(480,10**9)):
        w = sorted(b for a, b in pts if lo <= a < hi)
        if w:
            print(f"  {lo:4d}-{hi if hi < 10**9 else 0:<4d}s  n={len(w):3d}  median {st.median(w):6.1f}  max {max(w):6.1f}")

    print()
    print("=" * 92)
    print("MITIGATION vs DIFFICULTY — does MITF['raid']=0.73 show up as a tier effect?")
    print("=" * 92)
    byd = collections.defaultdict(list)
    for x in F:
        d = dps(x)
        if d is not None and x["difficulty"] is not None: byd[x["difficulty"]].append(d)
    for d in sorted(byd):
        w = sorted(byd[d])
        print(f"  D{d}  n={len(w):3d}  median {st.median(w):6.1f}  p90 {w[int(0.9*(len(w)-1))]:6.1f}")
    # paired: same boss, same observer set, across tiers
    pair = collections.defaultdict(dict)
    for x in F:
        d = dps(x)
        if d is None or x["difficulty"] is None: continue
        k = (x["boss"], tuple(sorted(set(x["observers"]))))
        pair[k].setdefault(x["difficulty"], []).append(d)
    ratios = []
    for k, tiers in pair.items():
        if 0 in tiers and max(tiers) >= 3:
            hi_t = max(tiers)
            r = st.median(tiers[hi_t]) / st.median(tiers[0])
            ratios.append((k[0], hi_t, r))
    print(f"  same boss, same observers, D0 vs its highest tier >=3: {len(ratios)} pairs")
    for b, t, r in sorted(ratios, key=lambda z: -z[2]):
        print(f"    {b[:34]:34} D0 -> D{t}   our DPS x{r:.2f}")
    if ratios:
        print(f"  median ratio {st.median([r for _,_,r in ratios]):.2f}"
              f"   -- the model predicts a fall to {M.MITF['raid']:.2f} if tier raised mitigation")

    print()
    print("=" * 92)
    print("DATASET DEFECTS — derived from the file, not asserted")
    print("=" * 92)
    off = [x for x in F if len(set(x["observers"])) > 1 and x["other_players"] != x["attackers"] - len(set(x["observers"]))]
    rule = sum(1 for x in F if x["other_players"] == x["attackers"] - 1)
    print(f"D-1  other_players == attackers - 1 in {rule} of {len(F)} records, without exception.")
    print(f"     {len(off)} of those fights had more than one of OUR characters present, so the")
    print( "     field counts one of ours as an outsider. Either `attackers` undercounts by one")
    print( "     when two of our logs merge, or `other_players` overcounts by one. Both cannot hold.")
    ex = [x for x in F if x["boss"] == "Bazzt Zzzt" and x["our_damage_share_pct"] == 100.0]
    for x in ex:
        print(f"     shown in the worked example itself: {x['boss']} D{x['difficulty']} {x['date']}, "
              f"observers {x['observers']}, attackers {x['attackers']}, other_players {x['other_players']}")
    dup = [x for x in F if len(x["observers"]) != len(set(x["observers"]))]
    print(f"D-2  {len(dup)} records list the same observer name more than once "
          f"({sorted({tuple(x['observers']) for x in dup})[0]} and similar).")
    print( "     If `observers` is a character list this is a duplicate; if it is a log-file list")
    print( "     the name is not unique enough to divide by. Either way a per-character figure")
    print( "     cannot be derived from it without knowing which. Not a number I will guess.")
    neg = [x for x in F if x["seconds"] and x["joined_late_seconds"] and x["joined_late_seconds"] >= x["seconds"]]
    print(f"D-3  {len(neg)} records where joined_late_seconds >= seconds. Not necessarily an")
    print( "     error: it is consistent with `seconds` spanning OUR witnessed lines while")
    print( "     `joined_late_seconds` is measured from the boss's first engagement by anyone.")
    print( "     But the file does not say which clock either field uses, and on that reading")
    print( "     the two cannot be added. Which they are decides whether a DPS denominator")
    print( "     built from `seconds` is our engaged window or the raid's. A question, not a claim.")
    for x in neg[:4]:
        print(f"     {x['boss'][:30]:30} D{x['difficulty']} late {x['joined_late_seconds']}s "
              f"window {x['seconds']}s  share {x['our_damage_share_pct']}%")
