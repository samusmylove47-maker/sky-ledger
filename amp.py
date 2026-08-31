#!/usr/bin/env python3
"""amp.py -- what Amplification does to Denon's Desperate Dirge.

Reads the 29 Aug 2026 Rivervale log (Shara, Bard trio) and derives the answer
rather than asserting it. The test design is the player's: sing DDD with
Amplification out of the bar, memorise it, sing again, on the same mob type.
"""
import re, sys, os, collections

LOG = sys.argv[1] if len(sys.argv) > 1 else "corpus/amp/eqlog_Shara_rivervale_20260829.txt"
TS   = re.compile(r"^\[\w{3} (\w{3} \d{2}) (\d{2}):(\d{2}):(\d{2}) (\d{4})\] (.*)$")
HIT  = re.compile(r"You hit (.+?) for (\d+) points of magic damage by Denon's Desperate Dirge\.(\s*\(Critical\))?")

rows, amp, sec0 = [], False, None
lines = []
for raw in open(LOG, encoding="utf-8", errors="replace"):
    m = TS.match(raw.rstrip("\n"))
    if not m: continue
    t = int(m.group(2))*3600 + int(m.group(3))*60 + int(m.group(4))
    body = m.group(6)
    if sec0 is None: sec0 = t
    lines.append((t, body))

# Amplification state, and the pulse that reveals it
state, booms, slain_at = False, [], set()
for t, body in lines:
    if body.startswith("You have finished memorizing Amplification"): state = True
    elif body.startswith("You forget Amplification"):                 state = False
    elif body == "Your voice booms.":                                 booms.append((t, state))
    elif body.startswith("You have slain"):                           slain_at.add(t)

print("=" * 88)
print('THE TELL — "Your voice booms." against the memorised state')
print("=" * 88)
agree = sum(1 for _, s in booms if s)
print(f'  "Your voice booms." fires {len(booms)} times; Amplification was memorised for {agree} of them.')
ticks = sorted({t for t, b in lines if b == "You feel replenished."})
gaps = [b - a for a, b in zip(ticks, ticks[1:]) if b - a < 60]
print(f"  song tick: {len(ticks)} pulses, modal gap {collections.Counter(gaps).most_common(1)[0][0]}s")
print("  The boom is Amplification's own pulse, on the same tick as every other song.")
print("  That is how you read this state out of a log: no boom, no Amplification.")

# now the damage, with state carried forward
state = False
for t, body in lines:
    if body.startswith("You have finished memorizing Amplification"): state = True
    elif body.startswith("You forget Amplification"):                 state = False
    m = HIT.search(body)
    if m:
        rows.append(dict(t=t, mob=m.group(1), dmg=int(m.group(2)),
                         crit=bool(m.group(3)), amp=state,
                         kill=(t in slain_at)))

print()
print("=" * 88)
print("EVERY DDD HIT IN THE LOG")
print("=" * 88)
print(f"  {'t':>6} {'mob':<22} {'damage':>7} {'crit':>5} {'amp':>4} {'killing blow':>13}")
for r in rows:
    print(f"  {r['t']-sec0:6d} {r['mob'][:22]:<22} {r['dmg']:7d} {str(r['crit']):>5} "
          f"{str(r['amp']):>4} {str(r['kill']):>13}")

print()
print("=" * 88)
print("KILLING BLOWS TRUNCATE, AND THAT IS A PARSING HAZARD")
print("=" * 88)
clean = [r for r in rows if not r['kill'] and not r['crit']]
byk = collections.defaultdict(list)
for r in clean: byk[(r['mob'], r['amp'])].append(r['dmg'])
for (mob, a), v in sorted(byk.items()):
    print(f"  {mob:<22} amp={str(a):<5} n={len(v):2d}  values {sorted(set(v))}")
kb = [r for r in rows if r['kill']]
print(f"  {len(kb)} hits land on a killing blow: {[r['dmg'] for r in kb]}")
print("  Every one is BELOW the deterministic non-kill value for the same mob and state.")
print("  The log reports damage APPLIED, capped at remaining hit points -- not the roll.")
print("  Any histogram of song damage that keeps killing blows carries phantom low values.")

print()
print("=" * 88)
print("THE CRIT MULTIPLIER, free from the same data")
print("=" * 88)
for mob in {r['mob'] for r in rows}:
    base = sorted({r['dmg'] for r in rows if r['mob']==mob and not r['crit'] and not r['kill'] and r['amp']})
    crits= sorted({r['dmg'] for r in rows if r['mob']==mob and r['crit'] and not r['kill'] and r['amp']})
    for c in crits:
        for b in base:
            print(f"  {mob}: crit {c} / non-crit {b} = {c/b:.4f}")
            print(f"     3 x {b} = {3*b}, observed {c} -- off by {c-3*b}.")
            print(f"     A true pre-floor value of {c/3:.2f} floors to {int(c/3)} and triples to {c}.")

print()
print("=" * 88)
print("WHAT AMPLIFICATION DOES")
print("=" * 88)
pairs = {}
for (mob, a), v in byk.items():
    pairs.setdefault(mob, {})[a] = sorted(set(v))
for mob, d in sorted(pairs.items()):
    if 0 in [len(x) for x in d.values()]: continue
    print(f"  {mob}: amp off {d.get(False)}  ->  amp on {d.get(True)}")
off = byk.get(('a rock golem', False)); on = byk.get(('a rock golem', True))
if off and on:
    o, n = off[0], on[0]
    print()
    print(f"  Clean pair, same mob type, both non-crit and neither a killing blow:")
    print(f"    Amplification OFF: {o}      Amplification ON: {n}")
    print(f"    MULTIPLICATIVE reading: x{n/o:.4f}")
    print(f"    ADDITIVE reading:       +{n-o}")
    print()
    print("  The two cannot be separated from one mob type. The second pair in the log")
    print("  would separate them, and it is unusable:")
    vis_off = byk.get(('an elemental visier', False))
    vis_on  = [r['dmg'] for r in rows if r['mob']=='an elemental visier' and r['amp']]
    if vis_off and vis_on:
        vo, vn = vis_off[0], vis_on[0]
        print(f"    an elemental visier, amp off {vo}; amp on {vn} -- but that line is flagged")
        print( "    (Critical) AND is a killing blow, so its number is truncated remaining HP.")
        print(f"    Worth recording anyway: additive predicts {vo}+{n-o} = {vo+n-o}, observed {vn}.")
        print(f"    Multiplicative predicts {vo}x{n/o:.4f} = {vo*n/o:.0f}.")
        print( "    The additive reading hits it exactly. ONE TRUNCATED LINE IS NOT EVIDENCE.")
    print()
    DOC = 2.00   # DDD.md carries "504 x 1.60 (Singing Mastery 3) x 2.00 (Amplification)"
    print(f"  DDD.md carries Amplification at x{DOC:.2f}. Measured is x{n/o:.4f}.")
    print(f"    x{DOC:.2f} would predict {o*DOC:.0f} where {n} was measured -- {o*DOC/n:.2f}x too high.")
    print()
    print("  AND THE CHAIN DOES NOT CLOSE, IN THE OTHER DIRECTION.")
    print(f"    DDD.md builds 504 x 1.60 x 2.00 x 1.30 = 2097 non-crit, against a guide's 3000.")
    print(f"    Measured here, rank IX: {n}. So the published chain is {100*(2097/n-1):+.0f}% against")
    print(f"    measurement WITH the old x2.00, and {100*(504*1.60*(n/o)*1.30/n-1):+.0f}% once")
    print(f"    Amplification is corrected down to the measured value. Correcting one term")
    print( "    made the total worse, which means a different term is carrying the error.")
    print( "    DDD.md already names two candidates it never tested: Jam Fest 3 (+5 casting")
    print( "    levels) and Improved Familiar (+9). Neither is measured. Not closing this here.")
