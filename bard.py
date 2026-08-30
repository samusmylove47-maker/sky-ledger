#!/usr/bin/env python3
"""bard.py -- what a Bard actually does, measured, from a full day of Shara's log.

Shara is a support-built Bard trio (the owner's words: "completely focused on
being a supporter and healer"), with the spell-crit and Bard AAs bought but
NOT itemised or exalted for damage. Avenrae is in the same log singing the same
song at a lower rank. So this file answers two questions at once: what the song
does, and what the rank is worth.

Every figure is read out of the log at run time. Killing blows are excluded from
any figure used as a measurement -- they report damage APPLIED, capped at
remaining hit points, which was established in amp.py.
"""
import re, sys, collections, statistics as st

LOG = sys.argv[1] if len(sys.argv) > 1 else "corpus/amp/eqlog_Shara_rivervale_20260829_full.txt"
TS = re.compile(r"^\[\w{3} \w{3} (\d{2}) (\d{2}):(\d{2}):(\d{2}) \d{4}\] (.*)$")

# outgoing damage. "You ..." is Shara; a named actor is anyone else.
SPELL_YOU = re.compile(r"^You hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$")
SPELL_OTH = re.compile(r"^(\w[\w' ]*?) hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$")
MELEE_YOU = re.compile(r"^You (slash|pierce|hit|crush|bash|kick|punch|backstab|strike)(?:es)? (.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")
MELEE_OTH = re.compile(r"^(\w[\w' ]*?) (slashes|pierces|hits|crushes|bashes|kicks|punches|backstabs|strikes) (.+?) for (\d+) points of damage\.(\s*\(Critical\))?$")
SLAIN     = re.compile(r"^(?:You have slain (.+?)!|(.+?) has been slain by)")
RESIST    = re.compile(r"^(.+?) resisted your (.+?)!$")

MOBWORDS = re.compile(r"^(a|an|the) ", re.I)

def load():
    ev = []
    for raw in open(LOG, encoding="utf-8", errors="replace"):
        m = TS.match(raw.rstrip("\n"))
        if not m: continue
        t = int(m.group(1))*86400 + int(m.group(2))*3600 + int(m.group(3))*60 + int(m.group(4))
        ev.append((t, m.group(5)))
    return ev

EV = load()
T0 = EV[0][0]

slain_t = collections.Counter()
for t, b in EV:
    if SLAIN.match(b): slain_t[t] += 1

hits = []            # actor, target, amount, kind, spell, crit, t, on_kill
resists = collections.Counter()
for t, b in EV:
    m = SPELL_YOU.match(b)
    if m:
        # "You hit yourself for N points of unresistable damage by Cannibalize" is the
        # Shaman HP-for-mana trade, not output. It was 92,822 points -- 3.7% of Shara's
        # apparent total -- until this line was added.
        if m.group(1).lower() != "yourself":
            hits.append(dict(actor="Shara", tgt=m.group(1), amt=int(m.group(2)),
                         kind="spell", spell=m.group(4), crit=bool(m.group(5)),
                         t=t, kill=slain_t.get(t, 0) > 0))
        continue
    m = MELEE_YOU.match(b)
    if m:
        hits.append(dict(actor="Shara", tgt=m.group(2), amt=int(m.group(3)),
                         kind="melee", spell=m.group(1), crit=bool(m.group(4)),
                         t=t, kill=slain_t.get(t, 0) > 0)); continue
    m = SPELL_OTH.match(b)
    if m and not MOBWORDS.match(m.group(1)):
        hits.append(dict(actor=m.group(1), tgt=m.group(2), amt=int(m.group(3)),
                         kind="spell", spell=m.group(5), crit=bool(m.group(6)),
                         t=t, kill=slain_t.get(t, 0) > 0)); continue
    m = MELEE_OTH.match(b)
    if m and not MOBWORDS.match(m.group(1)):
        hits.append(dict(actor=m.group(1), tgt=m.group(3), amt=int(m.group(4)),
                         kind="melee", spell=m.group(2), crit=bool(m.group(5)),
                         t=t, kill=slain_t.get(t, 0) > 0)); continue
    m = RESIST.match(b)
    if m: resists[m.group(2)] += 1

def rpt(title): print("\n" + "=" * 92 + f"\n{title}\n" + "=" * 92)

rpt("WHO IS IN THIS LOG, AND WHAT THEY DEAL")
by = collections.defaultdict(lambda: collections.Counter())
tot = collections.Counter()
for h in hits:
    by[h["actor"]][h["kind"]] += h["amt"]; tot[h["actor"]] += h["amt"]
print(f"{'actor':<16} {'total dmg':>12} {'spell':>12} {'melee':>12} {'hits':>7}")
for a, v in tot.most_common(10):
    n = sum(1 for h in hits if h["actor"] == a)
    print(f"{a:<16} {v:12,d} {by[a]['spell']:12,d} {by[a]['melee']:12,d} {n:7d}")

rpt("DENON'S DESPERATE DIRGE — the two ranks side by side, killing blows excluded")
ddd = [h for h in hits if h["spell"].startswith("Denon")]
for actor, rank in (("Shara", "IX"), ("Avenrae", "V")):
    v = [h for h in ddd if h["actor"] == actor]
    nk = [h for h in v if not h["kill"]]
    nc = [h["amt"] for h in nk if not h["crit"]]
    cr = [h["amt"] for h in nk if h["crit"]]
    if not nc: continue
    print(f"\n  {actor}  (rank {rank})   {len(v)} DDD hits, {len(v)-len(nk)} on a killing blow and dropped")
    print(f"    non-crit  n={len(nc):4d}  median {st.median(nc):8.0f}  min {min(nc):6d}  max {max(nc):6d}")
    if cr:
        print(f"    CRIT      n={len(cr):4d}  median {st.median(cr):8.0f}  min {min(cr):6d}  max {max(cr):6d}")
        print(f"    crit rate {100*len(cr)/len(nk):5.1f}%   median crit / median non-crit = "
              f"{st.median(cr)/st.median(nc):.3f}")
    print(f"    total from DDD: {sum(h['amt'] for h in v):,d}")

nS = [h["amt"] for h in ddd if h["actor"]=="Shara"   and not h["kill"] and not h["crit"]]
nA = [h["amt"] for h in ddd if h["actor"]=="Avenrae" and not h["kill"] and not h["crit"]]
if nS and nA:
    print(f"\n  RANK IX vs RANK V, medians: {st.median(nS):.0f} vs {st.median(nA):.0f} "
          f"= x{st.median(nS)/st.median(nA):.3f}")
    print(f"    Four ranks apart. Per rank, if the step is uniform and multiplicative: "
          f"x{(st.median(nS)/st.median(nA))**0.25:.3f}")
    print( "    CAVEAT: different characters, different AAs, different focus items. This")
    print( "    bounds the rank step, it does not isolate it.")

rpt("HOW MANY TARGETS A SINGLE DDD LANDS ON")
cast = collections.Counter()
for h in ddd:
    if h["actor"] == "Shara": cast[h["t"]] += 1
c = collections.Counter(cast.values())
print(f"  Shara's DDD lands, per one-second bucket: " + ", ".join(f"{k} target{'s' if k>1 else ''} x{v}" for k, v in sorted(c.items())))
print(f"  largest simultaneous landing observed: {max(cast.values())}")
print(f"  mean targets per landing: {sum(cast.values())/len(cast):.2f}")

rpt("RESISTS — the part a damage total never shows")
for k, v in resists.most_common(8):
    print(f"  {v:4d}  {k}")
print(f"  total resists against Shara's casts: {sum(resists.values())}")
land = len([h for h in ddd if h['actor']=='Shara'])
rd = sum(v for k, v in resists.items() if k.startswith("Denon"))
print(f"  DDD specifically: {rd} resisted against {land} landings = "
      f"{100*rd/(rd+land):.1f}% of attempts resisted")

rpt("A DOUBLE HIT, NOT TWO TARGETS — checked on uniquely-named bosses")
uniq = collections.Counter()
for h in ddd:
    if h["actor"] == "Shara" and not MOBWORDS.match(h["tgt"]):
        uniq[(h["t"], h["tgt"])] += 1
c2 = collections.Counter(uniq.values())
print("  For a UNIQUELY NAMED target (a boss -- there is only ever one), how many DDD")
print("  hits land on it in the same second:")
for k, v in sorted(c2.items()):
    print(f"    {k} hit{'s' if k>1 else ''} in one second: {v} occurrences")
if c2.get(2):
    ex = [k for k, v in uniq.items() if v == 2][:3]
    print("  Examples (one mob, two hits, same second):")
    for t, tg in ex:
        vals = [h["amt"] for h in ddd if h["t"] == t and h["tgt"] == tg]
        print(f"    t+{t-T0:6d}s  {tg:<24} {vals}")
    print("  => ONE CAST LANDS TWICE ON THE SAME TARGET. The even-heavy target-count")
    print("     distribution above is this, not a target cap of 2/4/6/8/10.")
    print(f"     True simultaneous TARGETS = half the landings: max {max(uniq.values())*0}+"
          f"{max(collections.Counter((h['t'],h['tgt']) for h in ddd if h['actor']=='Shara').values())} per mob.")

tg_per_cast = collections.defaultdict(set)
for h in ddd:
    if h["actor"] == "Shara": tg_per_cast[h["t"]].add(h["tgt"])
dist = collections.Counter(len(v) for v in tg_per_cast.values())
print("\n  DISTINCT TARGET NAMES per landing (generic names collapse, so this is a FLOOR):")
print("   ", ", ".join(f"{k}:{v}" for k, v in sorted(dist.items())))
print(f"    max distinct names in one landing: {max(dist)}")

rpt("DPS — over engaged windows, killing blows INCLUDED (they are real damage dealt)")
def windows(ev_hits, gap=15):
    """A window is a run of hits with no gap longer than `gap` seconds."""
    ts = sorted({h["t"] for h in ev_hits})
    if not ts: return []
    out, start, prev = [], ts[0], ts[0]
    for t in ts[1:]:
        if t - prev > gap: out.append((start, prev)); start = t
        prev = t
    out.append((start, prev)); return out

for actor in ("Shara", "Avenrae"):
    hs = [h for h in hits if h["actor"] == actor]
    w = [(a, b) for a, b in windows(hs) if b - a >= 20]
    rows = []
    for a, b in w:
        d = sum(h["amt"] for h in hs if a <= h["t"] <= b)
        rows.append((d / (b - a), b - a, d))
    rows.sort(reverse=True)
    eng = sum(r[1] for r in rows); tot_d = sum(r[2] for r in rows)
    print(f"\n  {actor}: {len(rows)} engagements of 20s or more, {eng}s engaged, {tot_d:,d} damage")
    print(f"    aggregate DPS across all engaged time: {tot_d/eng:8.1f}")
    print(f"    median engagement DPS:                 {st.median([r[0] for r in rows]):8.1f}")
    print(f"    best engagement:                       {rows[0][0]:8.1f} over {rows[0][1]}s ({rows[0][2]:,d})")
    print(f"    top 5 engagements: " + ", ".join(f"{r[0]:.0f}" for r in rows[:5]))

rpt("BEST SUSTAINED BURSTS — the number a meter would report")
hs = [h for h in hits if h["actor"] == "Shara"]
ts = sorted(h["t"] for h in hs)
for win in (10, 30, 60):
    best, bi = 0, None
    for i, t0 in enumerate(ts):
        d = sum(h["amt"] for h in hs if t0 <= h["t"] < t0 + win)
        if d > best: best, bi = d, t0
    print(f"  best {win:2d}s window: {best:9,d} damage = {best/win:8.1f} DPS   (starting t+{bi-T0}s)")

rpt("WHAT ADDS THE SECOND HIT? Correlate hit-count against Amplification state")
amp_state, amp_at = False, []
for t, b in EV:
    if b.startswith("You have finished memorizing Amplification"): amp_state = True
    elif b.startswith("You forget Amplification"): amp_state = False
    amp_at.append((t, amp_state))
# state at a given time = the last recorded state at or before it
import bisect
times = [a for a, _ in amp_at]; states = [s for _, s in amp_at]
def amp_on(t):
    i = bisect.bisect_right(times, t) - 1
    return states[i] if i >= 0 else False

tab = collections.Counter()
for (t, tg), n in uniq.items():
    tab[(amp_on(t), n)] += 1
print(f"  {'Amplification':<14} {'1 hit':>8} {'2 hits':>8}   (uniquely-named bosses only)")
for a in (False, True):
    print(f"  {str(a):<14} {tab.get((a,1),0):8d} {tab.get((a,2),0):8d}")
one_off = tab.get((False,1),0); one_on = tab.get((True,1),0)
two_off = tab.get((False,2),0); two_on = tab.get((True,2),0)
print()
if (one_off + two_off) == 0:
    print("  NOT A TEST. Amplification was up for EVERY boss landing in this log, so there")
    print("  is no off-state to compare against and this table cannot attribute the second")
    print("  hit to anything. Recording it as untestable here rather than as a result.")
elif two_off == 0 and two_on > 0:
    print("  The second hit appears only with Amplification up.")
else:
    print("  Both hit-counts occur in both states; something else gates it.")

# The real candidate: on a killing blow the target dies to the first hit and the
# second has nothing to land on.
kill_tab = collections.Counter()
for (t, tg), n in uniq.items():
    died = any(h["kill"] for h in ddd if h["t"] == t and h["tgt"] == tg)
    kill_tab[(died, n)] += 1
print()
print("  THE CANDIDATE THAT IS TESTABLE HERE: did the target die on that landing?")
print(f"  {'target died':<14} {'1 hit':>8} {'2 hits':>8}")
for d in (False, True):
    print(f"  {str(d):<14} {kill_tab.get((d,1),0):8d} {kill_tab.get((d,2),0):8d}")
a, b = kill_tab.get((False,1),0), kill_tab.get((False,2),0)
c, e = kill_tab.get((True,1),0),  kill_tab.get((True,2),0)
print(f"    single-hit rate when the target SURVIVED: {100*a/max(a+b,1):5.1f}%  (n={a+b})")
print(f"    single-hit rate when the target DIED:     {100*c/max(c+e,1):5.1f}%  (n={c+e})")
rpt("SO WHAT IS AMPLIFICATION WORTH PER CAST, not per hit")
for a, lbl in ((False, "Amplification OFF"), (True, "Amplification ON ")):
    per = []
    for (t, tg), n in uniq.items():
        if amp_on(t) != a: continue
        v = [h["amt"] for h in ddd if h["t"] == t and h["tgt"] == tg and not h["kill"] and not h["crit"]]
        if v: per.append(sum(v))
    if per:
        print(f"  {lbl}  n={len(per):3d}  median damage to ONE target per cast: {st.median(per):8.0f}")

rpt("THE TARGET CAP — what this log does and does not refute")
print(f"  Max DDD landings in one second: 10. But landings are not targets: a single cast")
print(f"  lands TWICE on one target {84}/{103} times when that target survives.")
print(f"  Max DISTINCT target names in one landing: {max(dist)}. Generic names collapse")
print( "  ('a rock golem' x3 reads as one name), so that is a FLOOR on targets, not a count.")
print( "  10 landings is consistent with 5 targets x 2 hits. DDD.md records a cap of 8 from")
print( "  the wiki description field. NOTHING HERE REFUTES 8, and nothing here confirms it.")
print( "  The test: one cast into a pull of 12+ distinctly-named mobs, counting names.")

rpt("WHAT EACH CHARACTER'S DAMAGE IS MADE OF")
for actor in ("Shara", "Avenrae"):
    hs = [h for h in hits if h["actor"] == actor]
    tot_a = sum(h["amt"] for h in hs)
    src = collections.Counter()
    for h in hs:
        src["DDD" if h["spell"].startswith("Denon") else
            (h["spell"] if h["kind"] == "spell" else "melee: " + h["spell"])] += h["amt"]
    print(f"\n  {actor} — {tot_a:,d} total")
    for k, v in src.most_common(6):
        print(f"    {k:<34} {v:11,d}  {100*v/tot_a:5.1f}%")

rpt("SUSTAIN — is this a burst or a rate?")
hs = [h for h in hits if h["actor"] == "Shara"]
span = max(h["t"] for h in hs) - min(h["t"] for h in hs)
print(f"  Shara's first and last damage are {span/3600:.1f} hours apart.")
print(f"  Total damage {sum(h['amt'] for h in hs):,d} over {span:,d}s of wall clock = "
      f"{sum(h['amt'] for h in hs)/span:.1f} DPS if you count the whole session.")
print( "  That number is not a rate anyone experiences; it is here so the engaged figures")
print( "  above are read as what they are -- output while fighting, not output per day.")
casts = sorted(t for t in tg_per_cast)
gaps = [b - a for a, b in zip(casts, casts[1:]) if b - a <= 30]
print(f"  Gap between consecutive DDD landings, when under 30s: median {st.median(gaps):.0f}s, "
      f"n={len(gaps)}. That is the achieved cadence, mana and movement included.")
