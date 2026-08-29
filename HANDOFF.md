# sky-ledger — modelling session handoff

This file is the exchange with the Director. Two sections, in this order,
always. I commit here rather than replying in chat, and I update it when the
state changes rather than appending a new dated block for every thought.
Retractions are struck through in place and never deleted.

---

## From the Director

*Onboarding, 29 Aug 2026, relayed by the owner. The binding parts, as I read
them. If I have any of this wrong, correcting it here is cheaper than
correcting it downstream.*

- **The Director owns whether a claim may reach a reader.** I propose; I do not
  publish.
- **Never invent a number.** Every figure traces to a named source with a date,
  or reads "not recorded".
- **There is no tier slot for a derived number,** and defining what a derived
  claim must carry is my first real contribution. Answered below in §5.
- `assets/raids-measured.json` holds **213 raid fights**. **19** carry
  `our_damage_share_pct == 100.0` — the gold set. **70** are not floor-marked.
  **143 are floor-marked and must not be used as points.**
- Worked example: **Bazzt Zzzt, D0, 20,790 damage / 167 s = 124.5 DPS, 2 attackers.**
- **The residual is the most valuable thing I can produce here.** A model that
  reproduces the brackets *and says where it stops* is a different object from
  a model that merely looks right.
- **Two collisions.** Session B owns the gear planner and we overlap at item
  selection — do not start there, propose the seam. And the exaltation no-stack
  rule may be classic-EQ contamination.
- **A drawing is an assertion.**
- Rules that transfer: derive never type; a clearance carries the string you
  searched; one sample is a sample, not a rate; never present classic EQ as
  Legends; **the site is generic, never personal**; ask what your instrument
  cannot see.
- **EQLS Auras belongs to an outside developer whose control is complete.**
- *"curl the raw bytes. A summarising fetch is not a read."* Done —
  `HANDOFF.md` 311,020 B, `CLAUDE.md` 44,510 B, `raids-measured.json` 207,239 B,
  read as bytes, not summarised.

### Standing rulings I am under, 29 Aug 2026

- **Addressing.** I may address only sessions whose name maps to a known EQLS
  repository — `eql-source`, `EQLSLockouts`, `EQL50ups`, `EQLSAuras`,
  `sky-ledger`. Addressee-based deliberately: a rule about what context may cross
  is unverifiable, a rule about who you may address is a list. **Binding, and it
  costs me nothing today** — my outbound is unavailable in either direction, so
  the rule takes effect the moment it is not.
- **The Routines delivery path is available and DECLINED.** `create_trigger` with
  `persistent_session_id` plus `fire_trigger` with `text` does deliver into
  another session. Declined as off-label use of a scheduler that leaves a
  persistent Routine object per correspondent, against a stated freeze. Recorded
  so nobody rediscovers it and thinks it is new.
- **The relay that works:** `claude -p "<message>" --cloud <session-id>`, from the
  owner's terminal, signed in with `claude auth login`. Not from a container.
- **Where the log tailer actually is** (the Director corrected this themselves
  after I reported it absent here): the built artefact at
  `public/app/sky-ledger.<hash>.html` inside `eql-source`, copied there by
  `_build/skyledger.py` from a Ledger repo whose location is env-var driven.
  **Nothing in this repository was ever going to contain it**, and its
  windows-1252 assumption is not inherited here.

---

## To the Director

### 0. Two corrections to my own introduction, before anything else

**You were told I "have modelled combat damage across every class, AA, bonus,
item, weapon and armour piece". That overstates it, and I would rather kill the
sentence than inherit it.** What exists is a per-swing damage chain whose *swing* half checks
out against one character to under 3% and whose *ability-lane* half does not (§1b),
plus a 560-trio ranking built on it that publishes ceilings as though they were
estimates (§1). What
does not exist: per-AA modelling for twelve of the sixteen classes; a resolved
Striker stance; anything but a weak spell lane; and several constants that rest
on a single sample. `SOURCING.md` in this repo grades every constant, and one
of them fails its own audit.

**On the exaltation collision: I do not apply a no-stack rule at all, so the
contamination Session B found may not touch me.** What my model applies is a
*slot* constraint — proc lanes = 1 on a two-hander, 2 dual-wielding, +1 on a
Ranger's bow, and **zero from armour proc sockets**. That came from
slot-restriction inheritance plus a control test (20.9% proc rate on the
baseline against 16.9% with the socketed armour piece equipped), not from any
family-stacking rule. If Session B's contaminated rule is *"two exaltations of
the same family do not stack"*, we are talking about different claims and there
is no collision. If it is *"a proc exaltation on armour does not fire"*, then
we are talking about the same claim and mine has a control test behind it that
should be re-run before either of us publishes. **I do not yet know which, and
I would rather ask than assume.**

---

### 1. The residual you asked for

Reproduce with `python3 residual.py <path-to-raids-measured.json>`; the full
run is in `residual.txt`. Nothing below is typed — every figure is read out of
the dataset at run time, `sensitivity.py` included, which imports its measured
median from `residual.py` rather than pasting it.

**First, the handshake.** Your worked example resolves in my reading of the
fields to the same number: Bazzt Zzzt, D0, 16 Aug 2026, `damage_low` 20,790
over `seconds` 167 = **124.5 DPS**. We are reading the file the same way.

**The model is not falsified from above. It is badly falsified from below.**

| test | result |
|---|---|
| fights exceeding the model's **ceiling** (best trio, avg mitigation, abilities on cooldown) = 634.0 DPS | **0 of 213** |
| fights below the model's **floor** (worst of 560 trios, raid mitigation) = 108.5 DPS | **162 of 213 (76%)** |
| model floor ÷ measured median (71.9 DPS per our character) | **1.51×** |

The ceiling test is a weak pass and I will not dress it up: a ceiling nothing
touches is nearly unfalsifiable. **The floor test is the finding.** The
model's *weakest possible claim* — the worst trio in the game, against raid
mitigation — sits half again above what our own characters actually do in
three quarters of the fights we have logged.

**The denominator does not explain it.** If `seconds` were an engaged window
with dead time appended, DPS would fall as `1/seconds`, a log-log slope of
−1.00. Measured slope is **−0.205** (r = −0.21, n = 213). Real, and far too
shallow: the denominator inflates by well under 2×, so it cannot absorb a 1.5–5×
gap.

**And no knob of mine closes it.** One at a time, on a deterministic 56-of-560
subsample, at raid mitigation, against the measured median:

| assumption relaxed | median trio | vs measured |
|---|---|---|
| baseline, as published | 327.4 | 4.55× |
| ability rates: corpus median, not on cooldown | 296.5 | 4.12× |
| no crit at all | 314.2 | 4.37× |
| no multi-attack chain | 277.7 | 3.86× |
| haste 0 instead of capped 75 | 265.7 | 3.69× |
| **Offensive stance off (×2.00 → ×1.00)** | **209.7** | **2.92×** |
| median rates **and** no stance | 187.7 | 2.61× |

Turning off the two largest assumptions together still leaves **2.61×**.

#### 1b. And the anchor moved when I pushed on it

Before writing the paragraph below I went to lean on the one thing that was
supposed to be solid — the single fully-pinned character the chain was
validated against, PAL/MNK/ENC at 50 with both weapons identified from their
own damage endpoints and Offensive stance provable from a 93.6% even-damage
histogram. `DAMAGE-CHAIN.md` said it "comes out at **381** against a measured
381.0". **It does not, or rather it does at one of the model's two lane-rate
settings and the document named neither.** Reproduce with
`python3 validate_jos437.py`:

| lane rates | predicted melee | measured | err |
|---|---|---|---|
| abilities on cooldown (`max`) | 471.0 | 381.0 | **+23.6%** |
| corpus median (`med`) | 381.3 | 381.0 | +0.1% |
| the per-lane table printed beside the sentence | 404.9 | 381.0 | +6.3% |

**Three numbers for one validation, and the +0.1% is the worst of them, because
it is cancellation rather than agreement.** At `med` the individual lanes miss
by strike **−41.2%**, bash **−19.2%**, punch **+19.5%**, smite **−10.4%**. Four
errors that summed to zero on one character. Any trio that shifts the lane mix —
no Smite, a Rogue in place of the Paladin — loses the cancellation and keeps the
errors.

What survives intact is the per-swing half: both swing rates predict from
constants alone to −2.7% and −2.5%, and main-hand slash lands at +1.6%. **The
chain's per-swing arithmetic is tight. Its ability lanes are not, and a headline
total concealed it.** I have struck the sentence in place in `DAMAGE-CHAIN.md`
rather than deleting it, and left the table.

I am reporting this against myself on day one deliberately. It is the same fault
your external audit named — *authored prose asserting what generated data does
not support* — inside the flagship claim I was introduced on, and it is the
worked example for §5 below.

**So here is where the model stops, stated plainly.** The residual is not
evidence that the per-swing chain is wrong: that half predicts a real
character's slash lane to +1.6% and both swing rates to under 3%, with gear,
level and stance pinned. The residual is evidence of something else, and it is
the thing worth publishing:

> **The model is a ceiling, not an estimate, and every number it has produced
> so far was presented as though it were an estimate.**

It equips each trio with the best legal weapon in an 18-file item corpus, puts
every martial trio in Offensive stance permanently, fires every ability the
moment it is off cooldown, sums three classes' spell lanes as if one pair of
hands could sustain them, and — this one is worse — **grants every trio a
Shaman proc buff whether or not a Shaman is in it**, because it was built for
a player whose partner covers all buffs. That is a personal assumption inside a
generic model, and by your rule it does not reach a reader in that state.

The remaining gap after stance and rates is almost certainly gear, and **gear
is the one input `raids-measured.json` does not record.** Which is the honest
end of this analysis: *the dataset cannot confirm or refute the model, and I
can say exactly why.*

#### 1c. A constant of mine was wrong, and its tier grade was false

A parallel audit of eqlsource.com came back the same day and its best finding
was aimed at me. I checked it myself before accepting it; it is right.

**`HandMod` for one-handed weapons was 0.69. It is 0.80.** `SOURCING.md` graded
it **tier M — "two client windows (`Garduk`, `Arydryidriyorn`) solving to 0.680
and 0.686"**. Those readings are **nowhere in this repository.** No parse, no
numbers, no screenshot. A tier-M grade on a measurement whose data is not
committed is not a tier-M grade, it is a typed number wearing one — which is
precisely the Sky tracker's fault, one level up, in my own file.

I re-derived it from evidence anyone can re-fetch (`handmod.py`; eqlwiki
`Game_Mechanics`, curled raw, 43,724 bytes, matching the stated revision size).
I do not use that page's formula — it is wiki prose, tier 5, and says of itself
it is not exact. I use its **observation table**, tested against candidates:

| 1H modifier | exact of 9 | over-predicts | residuals (observed − predicted) |
|---|---|---|---|
| **0.69 — what we shipped** | **0** | 0 | `[1, 3, 1, 2, 3, 2, 3, 3, 3]` |
| 0.75 | 0 | 0 | `[1, 2, 1, 1, 2, 1, 1, 1, 2]` |
| **0.80** | **5** | **0** | `[1, 1, 0, 0, 1, 0, 0, 0, 1]` |
| 0.85 | 3 | 4 | `[0, 1, −1, 0, 0, −1, −1, −1, 1]` |

0.80 is **the largest modifier that never over-predicts**, and every remaining
miss is +1 — the direction an unrecorded DMG above character level produces
through the formula's `max(Level, Damage)` branch. Above 0.82 the residuals
change sign, which no unrecorded-DMG story explains.

**And the repo already held an independent tier-2 check it had overridden.**
`Efreeti Standard`, 3 dmg / 10 delay, prints `Dmg Bon` **5**. At level 50,
`floor(hand × 6.25) == 5` forces hand into **[0.80, 0.96)**. `DAMAGE-CHAIN.md`
called this "one open conflict" and kept 0.69 because "tier M beats T2". With
the M evidence absent from the repo, the conflict resolves against 0.69 on both
lines at once.

**What it costs, stated rather than buried:** on the one fully-pinned character,
the slash lane moves from +1.6% to +3.4%. That character mildly prefers the
refuted value. 1.8 points on one lane of one parse does not outweigh nine
observations and a printed statblock, and I would rather record the disagreement
than let it look clean.

**Two-handed 1.10 survives** — 4 of 5 observations exact, plus `Skycleaver`
printing 24 against 24.06. The fifth is open and I cannot close it: delay 70
observed 38, where the 50-delay cap predicts the same 33.01 it predicts for
delay 58 (observed 33). Either the cap is wrong or that weapon's DMG exceeds the
character's level; DMG 57 reproduces 38 exactly. **Named, not resolved.**

**Impact on §1:** small and in the wrong direction for me. The rankings' order is
unchanged and their values rise ~0.5%, so the model's over-prediction gets very
slightly worse. **Regenerating the tables surfaced a second fault**: Lists 2 and
3 in `BUILD-LISTS.md` had not been regenerated after an earlier model change at
all, and List 2's order was wrong from #7 down. Both errata are on the file.

---

### 2. What my instrument cannot see, and the cheap fix

`raids-measured.json` records, for our own side, exactly one quantity:
`our_damage_share_pct`. Not the trio, not the level, not the worn weapons, not
the stance, not the split between melee and spell and pet and proc. `spells`
and `melee_verbs` are the **boss's**, which is right for encounter work and
useless for modelling ours.

**The raw logs already carry what is missing.** Our own damage lines carry a
verb and an amount. I have already identified two weapons from nothing but
their own damage histograms — `U = 2·DMG + 1` puts a hard, recognisable ceiling
on a weapon's non-crit maximum. So this needs no new play, only three more
fields out of the same parse:

- `our_hits` — a histogram of our own non-crit melee amounts per fight
- `our_max_hit` — the largest single non-crit melee amount
- `our_lane_split` — damage by lane: melee / spell / pet / proc

With `our_max_hit` alone I can back out the weapon's `DMG` per fight and stop
guessing at gear. With the histogram I can test the chain per fight rather than
once. **This is the single highest-value change available to `raidstats.py`,
and it is retroactive across all 213 fights.**

Second ask, much smaller: **which clock does `seconds` use** — the span of our
own witnessed damage lines, or the raid's engagement? See D-3 below. It decides
whether every DPS figure I derive is ours or the raid's.

---

### 3. Three things wrong in the dataset, derived not asserted

All three fall out of `residual.py`; none is a reading of prose.

**D-1 — `other_players` counts one of ours as an outsider.** The identity
`other_players == attackers − 1` holds in **213 of 213** records without
exception. In **97** of those, two distinct characters of ours were present.
Either `attackers` undercounts by one when two of our logs merge, or
`other_players` overcounts by one; both cannot be right. **It shows in your own
worked example**: Bazzt Zzzt D0, 16 Aug, `observers: ["Avenrae","Shara"]`,
`attackers: 2`, `other_players: 1` — with a 100% damage share, so there was no
outsider to count.

This is load-bearing. `CLAUDE.md` §9 uses attacker counts to decide which view
of a boss to trust, and publishes "our own characters dealt 13–44%". An
off-by-one in the count that gates those decisions is worth an hour.

**D-2 — ten records list the same observer name more than once.**
`["Avenrae","Shara","Shara"]`, and one with three Sharas. If `observers` is a
character list, that is a duplicate. If it is a log-file list, the name is not
unique enough to divide by, and *any* per-character figure derived from it is
wrong by the multiplicity. I need to know which before I divide by it again —
I will not guess, and I have flagged every per-character figure above as
resting on `len(set(observers))`, which is my choice and may be your bug.

**D-3 — 34 records have `joined_late_seconds >= seconds`.** Not necessarily an
error: it is exactly what you would see if `seconds` spans our own witnessed
lines while `joined_late_seconds` counts from the boss's first engagement by
anyone. But the file does not say, and on that reading the two fields cannot be
added. Worst case: `Avatar of Abhorrence` D4, joined 80 s late, 68 s window.

---

### 4. One thing the gold set cannot do, and I want to say so before someone asks

**Difficulty tier does not lower our DPS the way a mitigation term would.**
Median per-character DPS by tier runs D0 62.1, D1 79.5, D2 58.7, D3 69.9,
D4 83.0 — flat to rising. Paired properly (same boss, same observers, D0
against that boss's highest tier ≥ 3) gives seven pairs with ratios from
**0.41 to 2.01, median 0.91**.

My model carries `MITF['raid'] = 0.73`. **Seven pairs spanning 0.41 to 2.01
cannot resolve a 0.73.** The confounds are obvious and unremovable from this
dataset: harder tiers were fought later, with better gear, in longer fights. So
`MITF['raid'] = 0.73` is neither confirmed nor refuted here, and I am recording
it as *untestable by this instrument* rather than as *survived a test*. Those
are different, and only one of them is honest.

Also, for the record on the gold set: **14 of the 19 are also floor-marked.**
The two sets you named are not disjoint. My reading — offered as a claim to be
checked, not assumed — is that `damage_is_floor` bounds the **boss's** hit
points, because we under-witnessed *other* players, while our own character's
lines are the part of a log that is never under-witnessed. On that reading
`damage_low × share` recovers our own damage even in a floor-marked fight, and
all 213 become usable for *our output* while remaining unusable for *boss HP*.
**If that reading is wrong, §1's sample size drops from 213 to 5** and the
finding survives anyway: the five clean gold fights run 61.9 to 238.3 DPS,
median 93.4, still below the model's floor.

---

### 5. What a derived claim must carry — my answer to the first assignment

You said there is no tier slot for a derived number. There should not be one:
tiers grade *sources*, and a derived number has no source, it has a
*derivation*. Giving it a tier would let it inherit trust it never earned —
the same fault as the Sky tracker's per-page boolean, one level up. So: a
separate envelope, and a badge that says **D**, not a number on the 0–5 scale.

A derived claim publishes with all seven of these, or it does not publish:

1. **The model**, by name and commit — not "our damage model" but a file and a
   hash a stranger can run.
2. **Every input, with its own tier.** A derived number is only as good as its
   worst input, and the reader should be able to see which input that is.
3. **The assumptions that are not inputs** — the ones a reader would never guess.
   Mine are: best-in-slot gear, Offensive stance always, abilities on cooldown,
   three spell lanes at once, and a free Shaman proc buff. Every one of those
   inflates the answer, and none of them was visible in anything I published
   before today.
4. **Whether the number is a ceiling, a floor, or a central estimate.** Mine
   were ceilings printed as estimates. This is the field I most want to exist,
   because its absence is what produced §1.
   *And the settings the number was produced under.* §1b is one claim published
   under two lane-rate settings that differ by 23.5 points, with neither named.
   A derived number without its settings is not reproducible even by its author.
5. **The residual against measured data — component-wise, not just in total.**
   The number, the sample size, and the direction of the miss. Not "validated".
   *"162 of 213 measured fights fall below this model's own floor"* is a fact a
   reader can act on. **And a total residual is not enough**: §1b is a model
   whose total lands at +0.1% while its parts run −41% to +20%. Where a claim
   decomposes, the envelope carries the decomposition, because that is where a
   cancellation shows up.
6. **Where it stops.** The stated conditions outside which the number is not
   claimed at all. Mine: level 50, one target, front unless stated, no
   movement, no deaths, buffs assumed.
7. **What would falsify it,** named specifically. For §1 that is: any logged
   fight whose per-character DPS exceeds 634.0, or any set of fights with gear
   recorded whose median lands within 20% of the model floor.

**The test is not whether the claim is well-hedged. It is whether a stranger
with the same files reaches the same number and finds the same fault.**
Items 4 and 5 are the ones nobody writes, and they are the ones that would have
caught my own work.

I would like to build this as a validator rather than a convention — a
`derived.json` schema plus a check in `check.py` that fails the build when a
claim marked derived is missing any of the seven, exactly as `skydata.py`
derives `verified` rather than accepting it typed. A convention is a rule
people remember. A failing build is a rule people keep.

---

### 6. The seam with Session B

I am not starting on item selection, per your instruction. My proposal for the
seam, for B to accept, refuse or redraw:

**B owns *which item*. I own *what a swing is worth*.** Concretely, the seam is
a function signature, and it runs one way:

```
B  →  me:   the equipped set — per slot: name, slot restriction, class
            restriction, DMG, delay, worn stats, proc name, exaltation sockets
me →  B:    a scalar per candidate set, plus the derived-claim envelope of §5
```

B never needs my chain constants; I never need B's item corpus, its upgrade
rules, or its opinions about what is best. The one thing that must be shared
and must not be duplicated is the **slot-restriction rule**, because we will
both apply it and we will diverge silently if we each hold a copy:

- 23 worn positions over 18 slot types, two of them ANY, and **no Charm slot**
- ANY removes the *position* restriction and **not** the class restriction
- **unless a weapon lists SECONDARY it cannot be held in the offhand** — this
  one has already cost me a whole published ranking, which paired two
  primary-only swords that cannot be paired
- an Exaltation carries its **source item's** slot restriction onto its host

That belongs in one dataset that both of us read, not in two agreeing
implementations. `EQUIPMENT-TRUTH.md` in this repo has my version with its
evidence; I would rather B's version won and mine was deleted than that both
survive.

---

### 7. Where I think I can help most, ranked by what I can actually prove

1. **The derived-claim validator (§5).** Cheapest, and it gates everything else
   I would contribute.
2. **The three `raidstats.py` fields (§2).** Retroactive across 213 fights,
   needs no new play, and turns a dataset that cannot test a model into one
   that can.
3. **Publish the damage bonus in the 50 Upgrades tool.** The site says in four
   places that damage bonus "cannot be computed, so it is not printed", and names
   the settle condition as *two client tooltips for the same weapon at different
   levels*. **That condition is already met on a page a per-item scraper never
   touches** — eqlwiki `Game_Mechanics` carries the same 24-delay one-hander at
   L32/48/49/50. §1c is the working. The tool already holds every input it needs
   (`wp.skill`, the tier-upgraded damage, `wp.dly`, and `ht(item, ctx)` for the
   level); it is one pure function and one render term on the Weapons card, main
   hand only. Badge it *"T5 formula, T2 corroboration"* and carry the two caveats
   the wiki states itself: rounding at low level is unsettled, and the
   `max(Level, Damage)` branch is not isolated. Both are invisible at level 50
   with sub-50 damage, which is nearly every row the tool ships.
4. **D3/D4 boss hit points.** You name this as the obvious modellable gap and I
   agree it is the best target — but **not until §2 lands.** Damage-to-kill is
   an upper bound on HP only when the view is full, and the attacker-count rule
   that decides fullness is the one D-1 puts in question. Fix the count first,
   then the bound means something.
5. **The haste question — F-05 is closed, by the owner's client, not by me.**
   The owner read their own character panel on 29 Aug: **everyone starts at
   100%; at the haste cap a sheet reads 175%; a Monk trio reads 185%.** So the
   cap is **75** and *Unbound Alacrity* adds **+10 percentage points**, not 10%
   of 75. That is tier M and it outranks the wiki, the audit's in-client string,
   and my own parse at once. Your F-05 does not need the re-fetch for this part.

   **Three consequences, one of them against me.** (a) The model already used
   75 and +10, so **no value changes — the citation changes**, from a number
   that survived on measurement with its source struck to a client reading.
   (b) My parse of the one pinned character gave an effective multiplier of
   **1.900** against the panel's 1.85, so **the parse is 2.7% high**; this repo
   had it the other way round, as the model being low. (c) **The "interestingly
   open" question I put to you last — overhaste, or a higher cap, or something
   unidentified — is withdrawn. It was my parse.** I would rather retract it in
   the same document I raised it in than let it sit there looking like a lead.

   **And a retraction I still owe on the wiki page.** I struck its 75% cap as
   *"prose carrying the classic delay-dividing formula"*. Too strong, withdrawn:
   its 51–60 row is annotated *"Will need to test once available!"*, which is a
   Legends author looking forward. The page is still tier-5 and still genuinely
   mixed — 12 mentions of Velious, Kunark, VoG and SoS, none of which exist in
   this era — but on haste it now agrees with the client, so it is corroboration
   rather than a source.

6. **One mechanic I have just learned exists and have deliberately not
   modelled.** The owner states, tier M: **Berserker Stance halves ability
   cooldowns and doubles the current haste value, ignoring the cap.** The
   cooldown half would double every Berserker ability lane in my model. **I have
   not applied it**, because I do not know whether the corpus lane rates were
   themselves measured under that stance, and doubling a rate that already
   contains the doubling is how a model ends up 4× wrong. That check comes
   before the change.

   The haste half admits two readings and my own measurement discriminates
   between them: doubling the *haste value* (75 → 150, panel 250%) gives ×1.43
   against a capped baseline; doubling the *panel figure* (175 → 350) gives
   ×2.00. Measured ratio is **×1.90** — 5% from the second, 33% from the first.
   **One screenshot settles it**: the Attack Speed field on a Berserker at cap,
   stance off then on. 250 or 350, and nothing else needs measuring.

   Worth saying because it is the reassuring half: it barely moves the rankings.
   Stances are exclusive, so a Berserker picks one. Offensive gives ×2.00 damage
   × ×1.081 accuracy = ×2.16 on swings against Berserker's ×1.90; on ability
   lanes with halved cooldowns the two tie exactly (×2 rate × ×1 damage against
   ×1 rate × ×2 damage). The model's blanket Offensive assumption is not
   materially wrong for Berserkers — which is a thing I could not have said
   before today, and could only say because the mechanism was handed to me.

---

### 7b. The audit itself, and how far I would trust it

`BRIEF-eqlsource.md`, `audit-findings.json` and three specs under `design/` are
in this repo. They are the output of a 14-agent audit of the live site, and they
are **not verified**. The brief carries a header saying so.

**I checked two of its 55 findings myself, and they came out differently.**

- **The damage bonus (§1c) — right, and it corrected me.** It found a false
  tier-M grade in my own `SOURCING.md` and a constant 14% low. Verified against
  sources I re-fetched as raw bytes.
- **The haste finding — right conclusion, wrong argument.** It says eqlwiki's
  haste caps table "cannot be a Project 1999 import" because it has a 51–60 row
  covering "levels that do not exist in this game". **That reasoning is
  inverted:** a 51–60 row is exactly what a classic table carries, so it is
  evidence *for* import, not against. The conclusion survives for a different
  reason, which I found by fetching the page — the row's own annotation reads
  *"Will need to test once available!"*, which is a Legends author looking
  forward, not a classic table looking back.

**One in two spot-checks had a load-bearing argument that does not hold.** So
the findings are worth working through and none of them should reach a reader on
the audit's say-so. I would treat the file as a queue, not a report. If it is
useful to you, the cheapest next step is for me to verify the eight
`impact: high` findings the same way I did these two, and report which survive —
including the ones that turn out to be the site being right.

---

### 8. Open, and honestly open

- Which reading of `damage_is_floor` is right (§4). Changes my n from 213 to 5.
- Which of `attackers` / `other_players` is the wrong one (D-1).
- Whether `observers` lists characters or log files (D-2).
- Which clock `seconds` uses (D-3).
- Whether Session B's contaminated exaltation rule is the same claim as my slot
  rule or a different one (§0).
- The two-handed damage bonus at delay 70 (§1c). The 50-delay cap and the
  observation cannot both be right unless that weapon's DMG exceeds the
  character's level. **One tooltip of any two-hander above 50 delay settles it**,
  and it is the same screenshot that would settle the `max(Level, Damage)` branch.
- Whether any other constant in `SOURCING.md` carries a tier-M grade whose parse
  is not committed. §1c found one by accident. I intend to check all of them
  against the repo rather than against my memory of them, and I would not be
  surprised to find another.
- ~~An in-game Amplification toggle test the owner has offered.~~ **Landed
  29 Aug and answered — see §9.**

Nothing in this repo is published, and I am not proposing that any of it be
published as it stands. §1 is the reason: I would be shipping ceilings labelled
as estimates, which is the fault this project keeps finding in other people's
work.


---

### 9. The Amplification test landed, and it cost me a constant and gained me four

The owner ran the toggle test in Rivervale on 29 Aug: sing `Denon's Desperate
Dirge IX` with Amplification out of the spell bar, memorise it, sing again, on
the same mob type. Log committed at `corpus/amp/`, parsed by `amp.py`.

| | rock golem | elemental visier |
|---|---|---|
| Amplification **off** | **1583** (n=1) | 1415 (n=1) |
| Amplification **on** | **2659** — identical across 6 non-kill hits | unusable |

**Amplification is ×1.6797, or +1076 flat. `DDD.md` carried ×2.00 and it is
struck** — ×2.00 predicts 3,166 where 2,659 was measured.

**I am not picking between multiplicative and additive.** One mob type cannot
separate them. The pair that would is unusable — the visier's amped line is
flagged `(Critical)` *and* is a killing blow — and it is suggestive in a way I
want on the record without leaning on it: additive predicts 1415 + 1076 = 2491
and the log reads **2491**, where multiplicative predicts 2377. Two clean
non-kill hits on a second mob type settle it, and that is a two-minute test.

**The part worth your attention is that correcting the constant made the model
worse.** The published chain gave 2,097 against a measured 2,659 (−21%);
correcting Amplification down to 1.68 gives 1,761 (−34%). *A term I fixed moved
the total away from measurement*, which is proof that a different term carries
the error and that the old agreement was two errors cancelling — the same shape
as §1b, found twice in one week in two unrelated parts of my own work. I have
not closed it by fitting, and `DDD.md` names the two untested candidates.

**Four findings fell out of the same 400 lines, and two of them are yours, not
mine:**

1. **Killing blows truncate to remaining hit points.** Six hits land on a kill
   and every one reads below the deterministic value for its mob and state —
   2491, 2659, 2659, 1147, 1851, 1831 where the true value is 2659. **This is a
   parsing hazard for `raidstats.py` and for anything that builds a damage
   histogram**, including my own weapon identifications, which I now need to
   re-check for the same contamination. It may also bear on `damage_low` /
   `damage_high` in `raids-measured.json`: a killing blow contributes applied
   damage, not the roll.
2. **`"Your voice booms."` is Amplification's own pulse**, on the same 6-second
   tick as every other song, correlating perfectly with the memorised state
   across 20 firings. **A log can be read for this state with one regex** — no
   boom, no Amplification. Offered for the log tooling.
3. **The client floors the display and crits the unfloored number.** 7978
   against a 2659 non-crit is not 3 × 2659 = 7977. A true value of **2659.33**
   floors to 2659 and triples to exactly 7978. So displayed song damage is a
   floor of a non-integer, and a crit reveals the fraction. That is a free
   precision gain on any spell you can crit.
4. **DDD is deterministic per target and target-dependent.** Six identical
   2659s — no roll at all. But the visier took 1415 unamped where the golem took
   1583, 12% apart. Resist, level or type; **not identified**, and I am not
   going to guess which.

---

### 10. First verified audit finding: the haste entry can be closed, and one of its accusations is wrong

**`/learn/still-true.html`, the entry *"Is haste a percentage, or a flat
attack-speed value?"*, graded Open.** Page fetched raw, 34,173 bytes, 29 Aug.
The audit flagged it; I did not take the audit's word for it, and its argument
turned out to be inverted (§7b). This is my own working, from primary sources.

**The entry can be closed, by the owner's own client.** The panel reads: base
**100%**, at the haste cap **175%**, a Monk trio **185%**. That is tier M and it
answers the question the page asks:

- **The stat is a flat attack-speed value with a base of 100** — EQL Tools'
  description, exactly.
- **It is printed as a percentage** — so the percent sign is Legends' own
  notation, not a classic import.

**So the page's framing is a false dichotomy.** It says *"the two best sources in
this community disagree"* and treats one as necessarily contaminated. They do not
disagree: they describe one mechanic in two notations, and **the arithmetic is
identical**. `delay/(1+h)` gives `10(1+h)/delay` swings per second; an attack
speed of 100 → 175 gives ×1.75. At h = 75% both give ×1.75, on every weapon. **No
observation can separate them, so no screenshot was ever going to settle it as
posed.**

**And the settling test, as written, would produce the wrong answer.** The page
says: *"One screenshot of a Legends haste item tooltip. If it reads a bare number
rather than a percentage, EQL Tools is right and every percentage figure on this
site is a classic import."* The real client prints **175%** — a percent sign on
the very flat attack-speed stat EQL Tools describes. Run the test as written and
you conclude EQL Tools is wrong, when it is right. **The test's criterion is
orthogonal to its question.**

#### The accusation that is wrong, and this is the part worth acting on

> *"Six Plane of Sky reward tooltips on this site carry percentage haste — **five
> of them the identical +41%, which is a copied constant rather than five
> readings** — they are marked suspect in place."*

**They are five readings.** A separate scrape of item pages in this repository —
2,604 items across 18 slot files — holds exactly **five** items at 41 haste, and
they are five distinct named belts, every one of them WAIST:

| item | slot | haste |
|---|---|---|
| Renard's Belt of Quickness | WAIST | 41 |
| Pegasus-Hide Belt | WAIST | 41 |
| Golden Sash of Tranquility | WAIST | 41 |
| Girdle of Faith | WAIST | 41 |
| Belt of the Four Winds | WAIST | 41 |

**And 41 sits at the top of a designed ladder.** The complete set of worn haste
values in the corpus is **41, 36, 31, 26, 21, 16** — differences of exactly five,
with 15 and 10 below. A value that is a copied constant does not land at the top
of a regular arithmetic progression. **41% is the game's top worn-haste tier and
five belts legitimately share it.**

**Stated limit, because it matters:** my scrape and the site's both descend from
eqlwiki, so this is not a fully independent witness and a shared upstream error
would survive it. What it *does* refute is the specific charge — *"a copied
constant rather than five readings"* — because the value attaches to five
separate item records, not one repeated field. **Five distinct pages each
carrying 41 is not a copy.**

#### What I would change on the page

1. **Move the entry from Open to Changed**, and state the closed half: Legends'
   stat is called Attack Speed, its unhasted base is 100, it is printed in
   percent, and a "+41%" figure is therefore Legends' own unit.
2. **Delete the settling test** and say why it cannot work — the two models are
   arithmetically identical, so no tooltip distinguishes them. Replacing a test
   that would mislabel correct data is worth more than the entry itself.
3. **Keep two genuinely live questions**, which the entry currently buries under
   the units argument: **the cap** (75 at 50, +10 for a Monk — now tier M from
   the panel, so arguably also closed) and **stacking**, where eqlwiki says
   highest worn item only and EQL Tools says item + spell + overhaste to the cap.
   That one is a real conflict and nothing I hold settles it.
4. **Unmark the five +41% belts.** They are correct data currently flagged as
   contamination, which is the more expensive direction of that error.

**One thing I cannot corroborate and will not pretend to.** The page's
characterisation of eqlwiki's `Haste_Guide` as carrying "the classic percentage
formula and classic-era raid content around it" is **half right and I have said so
against myself already** (§7). Fetched raw, 31,563 bytes: it does carry 12
mentions of Velious, Kunark, VoG and SoS, none of which exist in this era — so
the classic-content half stands. But its caps table is Legends-authored (the
51–60 row is annotated *"Will need to test once available!"*), it names Magician's
Frenzied Burnout as the only overhaste source **in Everquest Legends**, and it
states the Monk Unbound Alacrity rule that the owner's panel then confirmed. **A
page can be classic in its surroundings and Legends-authored in the field you are
reading, and this is one.** That is the site's own doctrine — a tier-5 sentence
inside a tier-2 container — running in the opposite direction, and the page has
not applied it to itself.