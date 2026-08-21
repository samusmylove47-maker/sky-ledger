# PALADIN + ENCHANTER + (MONK | RANGER)

**Established:** 21 August 2026
**Method:** 29 research agents across two rounds, every numeric claim graded and
adversarially re-derived. Sources tiered by the eqlsource.com scheme: **TM** measured
parse > **T1** dev > **T2** structured wiki > **T3** named guide > **T4** aggregator >
**T5** inherited classic prose.

This file follows `CLIENT-TRUTH.md`'s standard: *a number without its source is a number
that can lie.* Every figure below names its source. Every gap says so out loud.

---

## 0. The verdict

### If you are TANKING — front arc, multiple enemies, fights lasting minutes

**RANGER**, unless you dual-wield.

| Your weapon setup | Monk's priced edge | Ranger needs, from ATK alone | Winner |
|---|---|---|---|
| **Shield + 1H, or 2H** (Dual Wield contributes 0) | +4.86% | c > 2.56% per 100 ATK | **RANGER** |
| **Dual-wielding** | +9.86% + unpriced kicks | c > 6.91% per 100 ATK | **MONK** |

Monk's second-largest term, Dual Wield 252 vs 210, is worth **exactly zero** unless the
character actually holds two weapons — and a multi-mob front tank normally holds a shield
(AC, block) or a two-hander. That, plus **Force of Nature**, is why the tanking case goes
to the Ranger.

The margin is small: low single digits on own melee, and own melee is only **~31%** of this
character's output once the Enchanter's charm pet (~2x a player) is in the denominator. This
is a tiebreaker-grade decision, not a build-defining one.

### The general case, by position

| You are… | Better third slot |
|---|---|
| Front arc, tanking, long fights | **RANGER** (endurance + ATK; see above) |
| Behind the mob, someone else tanks, dual-wielding | **MONK** |

**Correction to an earlier version of this document.** It asserted that front-arc tanking
put the character at G ~ 30%, where Ranger won "under every combination." That rested on an
*assumed* G. G has since been **measured at 5.98%** (§4.1). The Ranger verdict survives for
the tanking case, but on entirely different grounds — endurance and ATK, not strikethrough.

---

## 1. The asker's premises, judged

| Premise | Verdict |
|---|---|
| Ranger gets **+104 ATK** from AA | **TRUE.** 26 ranks × +4, **0 cost**, from level 8 |
| **ATK is the hardest stat to gain** | **TRUE, and stronger than stated** — see §1.1 |
| "Most classes get 25–40 ATK per class self-buff" | **FALSE.** 10 of 16 classes have **no** ATK self-buff at all |
| Strikethrough "ignores 30% of certain defensive layers" | **Directionally right, worth far less than 30%** — see §1.2 |
| Monk has Mend, FD, high skill caps | **Mixed; mostly dominated on *this* chassis** — see §5 |

### 1.1 ATK really is unbuyable — measured, not asserted

Counted directly over the full level-50 catalogue (the `EQL50ups` dataset behind
eqlsource's 50 Upgrades planner):

```
items in catalogue      3,663
carrying stat values    1,713
carrying AC             1,413
carrying STR              386
carrying ATTACK             0
```

The absence is **real, not a coverage hole**. The planner's own schema declares ATTACK as a
first-class stat key — `{key:'ATTACK',label:'Attack',group:'Combat'}` — and accumulates an
`attack` total per set. The corpus is *capable* of containing the thing, so its silence
means something. (That is `CLIENT-TRUTH.md` §3.4's lesson applied in the one direction where
it licenses a conclusion rather than forbidding one.)

Add: **Paladin receives 0 ATK from AAs and 0 ATK from spells** (machine-grepped: zero hits
for "Increase ATK by" on the whole Paladin page). Monk gets none either. So +104 is the
largest direct ATK source available to this character, and gear cannot dilute it.

**But scarcity is not value.** +104 ATK is worth `104k`, where *k* = %DPS per 100 ATK, and
*k* is **refused by the developers**: *"We aren't going to spoil the exact formula."*
"Hardest to gain" and "most worth having" are different claims. Only the first is established.

### 1.2 Strikethrough is worth ~1.9%, not 30%

Three separate deductions apply to the headline number:

1. **It is 30% only at level 50.** Ranks gate at **levels 12 / 30 / 50** → 10% / 20% / 30%.
2. **It is multiplicative, not additive.** It recovers 30% of *already-avoided* swings:
   gain = `0.3·G/(1−G)`. It is not +30 percentage points onto your hit chance.
3. **Scope:** it touches only the four active-defense gates. It does **not** touch the
   miss/AC roll. So G is active-defense avoidance *alone*, smaller than any "total
   avoidance" figure.

| G | strikethrough gain |
|---|---|
| **5.98% — MEASURED (§4.1)** | **+1.91%** |
| 10% | +3.33% |
| 18% | +6.59% |
| 30% | +12.86% |

G is no longer a free parameter: it has been **measured at 5.98%** across 22,604 parsed
swings (§4.1), so the real value of this ability is **+1.91% of own melee** — under +1% once
the charm pet is in the denominator. Fighting from behind would shrink it further, but even
front-arc, where all four gates are live, it is small. Riposte was measured at **0.00%**
outside Enrage.

---

## 2. The two abilities that actually decide it

### Monk — Unbound Alacrity  ·  **T1 PRIMARY, verified firsthand**

> "Added the Unbound Alacrity AA, a new autogranted class AA for Monk. Gives a passive
> **3/6/10% increase in your current and maximum haste value**."
> — everquestlegends.com, official patch notes, 28 July 2026

3 ranks, cost 0, levels 12/30/50. A full-catalogue grep for `haste|attack speed|alacrit`
across all 16 class boards returns **exactly two hits**: this, and a Magician pet ability.
**Paladin has no haste. Enchanter has no haste on its AA board. Ranger has none at any
layer.** This term is not duplicated anywhere on the chassis and Ranger has no answer to it.

**The cap-raise works — confirmed in play.** Maximum haste is **175** (+75%); a Monk raises
it to **185** (+85%). That is a **185/175 = +5.71%** swing-rate gain, and both builds have
enough haste sources to pin their respective caps (96 points available against a 75 cap, 106
against 85), so the gain is exactly +5.71% and not the larger clipped-regime figure. Applied
to the auto-attack share of melee (~85%), it is **+4.86% of own melee** — the largest single
*priced* term on either side.

### Ranger — Unbounded Strikethrough  ·  **T1 wording, mirrors only**

> "This passive ability increases the chance you will strike through your opponent's active
> defenses, such as dodge, block, parry, and riposte, by **10/20/30%**.
> Requirements: Level 12/30/50." — eqlwiki Ranger page; 3 ranks, **0 cost**

Original dev note dated 2026-06-16. **The official original is no longer reachable** — the
everquestlegends.com archive serves full text from 7 July 2026 onward and pre-launch beta
notes now redirect to the homepage. It survives via two mirrors. This is a genuine
absence-of-corpus, not evidence the note is wrong.

### Ranger — Hunter's Attack Power  ·  **26 ranks, settled**

> "This passive ability increases your attack power by 4 points per rank.
> Requirements: level 8." — eqlwiki; **26 ranks, 0 cost**

The "**7 ranks**" scare is dead, and it is refuted *by the site that produced the 7*:
eqltools explains it as a level-gated client read — the in-game AA window only shows ranks
the reading character can reach; **13 of 135 abilities came back short, Ranger's worst at 7
against 26**. eqltools publishes 26. Triple-sourced.

*Caveat that survives:* the **×4 per rank** is effectively single-sourced to one client
description string. eqprogression independently confirms 26 / free but publishes no
per-rank value. Call it "+104 with the multiplier single-sourced," not a quoted total.

---

## 3. Striker Stance — real, Monk-unique, and **not scoreable**

This is the ability a whole line of community argument rests on. It survives as fact and
collapses as an argument.

**What holds.** It exists — observed **35×** in a full-log sweep of a real 1.15–2.05M-line
EQL log (TM). Monk uniquely grants it on this chassis: Striker is BER/MNK/ROG/WAR only;
Paladin, Ranger and Enchanter do not grant it. Verified across three sites with independent
lineages.

**What collapses.** Four blows:

1. **The multiplier in circulation is backwards.** Shipped text: weapon-skill abilities
   **3×**, NON-weapon-skill abilities **5×**. The popular "5× on skill attacks" phrasing
   dropped the word "non-".
2. **The competing stance is on the chassis anyway.** Paladin grants **Offensive**:
   *"Outgoing melee damage is increased by 100% and your chance to hit is increased by 25%."*
   Both stances give the identical +25% hit, so that term cancels. Striker's marginal value
   is Striker-vs-Offensive, not Striker-vs-nothing.
3. **On a plain reading it does not touch auto-attack at all.** The shipped text says
   "abilities" on *both* sides of the split; Offensive says "melee damage." eqltools —
   which mines the client install files — lists *"which abilities count as 'weapon skill'
   for Striker's 3×/5× split"* verbatim as an **open question**.
4. **It is exactly twice as endurance-expensive per point of damage**, and this argument
   needs no unpublished coefficient:

   | stance | output | endurance cost | damage per endurance |
   |---|---|---|---|
   | Offensive | 2D | **D** (bonus only) | **2.00** |
   | Striker, weapon-skill | 3D | **3D** (all damage) | 1.00 |
   | Striker, non-weapon-skill | 5D | **5D** (all damage) | 1.00 |

   Verbatim: Striker charges *"every point of damage dealt"*; Offensive charges *"every
   point of **bonus** damage dealt."* The Strategy-skill reduction applies to both, so the
   **ratio is stance-independent** and survives the unpublished savings curve.

Striker is a **burst** tool, not a sustain tool. The measured log agrees behaviourally:
striker 35 uses against offensive 176 and defensive 210. A maintained guide with in-game
access says outright that *"offensive stance (or berserker stance) is probably better in
most cases."*

**Ruling: option value, nothing more. Not scored. Any verdict resting on it is void.**

> **It is also structurally unmeasurable.** The same parser project states that 17 of 18
> stances and invocations are `not-observable`: *"Striker multiplies weapon-skill damage and
> prints nothing."* The log does not attribute damage to stance. A "just parse it" experiment
> cannot settle this.

---

## 4. The recomputation

**DPS ∝ S × (1 − G) × h × D.** Only three terms differ; Paladin, Enchanter, gear and
Offensive stance are common and cancel.

```
Ranger edge = (1 + 0.3·G/(1−G)) × (1 + 1.04k)
Monk   edge = DualWield(1.06–1.08) × Alacrity(1.000 | 1.034–1.057)
            = 1.060 … 1.142
```

**Crossover in G**, at k = 2.5%/100 ATK:

| Monk swing edge | crossover G |
|---|---|
| 1.060 — Alacrity fails, DW low | 9.9% |
| 1.080 — Alacrity fails, DW high | 14.9% |
| 1.096 | 18.5% |
| **1.119 — central** | **23.2%** |
| 1.142 — Alacrity high, DW high | 27.4% |

**The crossover sits anywhere in G ≈ 10%–27%** — a range spanning essentially the entire
plausible domain of the variable. That is the cleanest statement of why the middle cannot
be called.

**But the edges are robust:**

| G | Ranger | Monk | Result |
|---|---|---|---|
| **10%** (behind the target) | +6.02% | +6.0% … +14.2% | **MONK** across essentially its whole range |
| 18% (typical group, front arc) | +9.36% | +6.0% … +14.2% | straddles — no call |
| **30%** (front arc, high avoidance) | +15.79% | +6.0% … +14.2% | **RANGER** under every combination |

**The cast-gate discount.** On a Paladin/Enchanter chassis you do not swing during a cast
bar, so every melee delta is multiplied by the melee duty cycle δ. **δ multiplies both
sides** — it does not move the crossover, it only shrinks the stakes. At δ ≈ 0.5 a 2.5pp
melee difference is a 1.25pp character difference. Whatever the answer is, it is small.

---

## 4.1 G is no longer unknown — it is measured

Prior rounds could not find a single published dodge/parry/block/riposte rate. They exist —
not in a wiki, but inside the log fixtures that Legends log-parser projects commit to
GitHub. Parsed across **22,604 resolved player swings** against 50+ distinct NPCs
(Lord Nagafen, Master Yael, Avatar of Abhorrence, Lord of Ire, Grandmaster R`tal, King
Tranix):

| gate | rate |
|---|---|
| dodge | 2.74% |
| parry | 2.33% |
| block | 0.92% |
| riposte | **0.00%** |
| **G — front-arc active defense** | **5.98%** |

Miss is a **separate** 36.25% bucket that strikethrough never touches.

Verbatim from the fixtures: `1105 Lord Nagafen, but miss!` / `94 ... blocks!` /
`48 ... parries!` / `22 ... dodges!` — 94+48+22 = 164 = 5.10% of n=3,218. Per-target spread:
Yael 3.97% (n=881) · Nagafen 5.10% (n=3,218) · dar ghoul knight 6.47% (n=1,807) ·
Avatar of Abhorrence 8.92% (n=695) · Lord of Ire 11.09% (n=613). <span>**TM**</span>

**Consequences.** Strikethrough at rank 3 is worth `0.3 x 0.0598/(1-0.0598)` = **+1.91%** of
own melee — not the +12.9% an assumed G of 30% implied, and well under +1% of
character-plus-pet output. Two further measured results: **slow does NOT shrink G** (7.95%
slowed vs 6.88% unslowed, z=1.53, not significant — EQL slow is a flat attack-speed change
while the gates are skill-driven), and **NPCs do not multiclass** (every catalogued named-mob
stat block carries exactly one class), which kills an inference chain an earlier round used
to argue endgame G was high.

**The one place G reaches 1.0:** Enrage — 31 of 34 catalogued named mobs carry it, 100%
frontal riposte at ~10% HP. Standard practice is to stop attacking through it.

---

## 4.2 Endurance is the binding constraint, and only one slot can raise it

This is what actually decides the tanking case.

Offensive Stance charges **1 endurance per point of bonus damage**, so its drain scales 1:1
with your own damage. The Paladin's Defensive stance drains the *same pool*, charging 1
endurance per point of damage prevented — so tanking and damaging compete for one resource.
Offensive therefore behaves as a **battery, not a multiplier**.

**Only the Ranger can refill it.** <span>**T1**</span>

> "The Ranger spell Force of Nature is now a permanent self-only buff. Force of Nature's hit
> Point regeneration has been increased, and it has been given Endurance regeneration as
> well, at the same scaling as Chloroplast."
> — official patch notes, 23 June 2026

Force of Nature: **+6/tick base, max +19/tick** (a tick is 6s), permanent, self-only, free
after one cast. Paladin, Enchanter **and** Monk have **zero** endurance restoration between
them — all four class spell lists and AA lists were checked. The only other endurance-regen
AA is Circular Breathing, an Archetype AA open to every class, so it cancels.

**Magnitude is unknown; sign is certain.** Base endurance regen and per-class pool sizes are
unpublished, and the Strategy savings curve is listed as an open question by the site that
mines the client files. Any specific "Offensive uptime %" figure is therefore fabricated and
is not stated here. What *is* established: endurance is finite, contested by two stances,
scales with your own damage, and **exactly one of the two candidate slots adds to it.**

**Two hypotheses tested and killed.** Monk's Strategy cap is 250 — identical to Ranger's, and
Paladin's is *also* 250, so with best-of-three caps the third slot cannot move endurance
efficiency at all. And the Striker opener is a **net damage loss**: Offensive converts
endurance to damage 1.5x better, so endurance burned in Striker is endurance not spent in
Offensive. Drop it regardless of which class you pick.

---

## 4.3 Two Monk channels that do not exist

- **Return Kick — does not exist in EverQuest Legends.** Three sources enumerate the Monk AA
  list as exactly five entries: Dragon Force, Improved Mend, Purify Body, Rapid Feign,
  Unbound Alacrity. The single site carrying Return Kick self-labels it `ref` =
  *"seeded from the classic EQ AA framework as a reference backbone."* A plain web search
  returns an AI-generated summary asserting it is a Legends Monk AA; the underlying links are
  Allakhazam (classic) and that `ref` row. **The search layer manufactures the claim.**
- **Double Riposte** is an Archetype AA available to all classes, and riposte caps are equal
  across Paladin, Monk and Ranger. Cancels.

Ranger's complete AA list, for symmetry: Hunter's Attack Power, Innate Called Shot,
Unbounded Strikethrough, Weapon Mastery of the Scout.

**Damage shield very nearly cancels.** The Enchanter — in *both* builds — supplies Feedback
(DS 11, slot 1). Ranger's Shield of Brambles is DS 12 in the same slot: a marginal **+1** per
landed incoming swing. Not a tiebreaker.

---

## 5. Chassis fit — what each slot actually adds

**Stances.** Monk's set is a strict **superset** of Ranger's:

```
PAL = {Balanced, Defensive, Mage Hunter, Offensive}      ENC = {Channeler}
RNG = {Balanced, Evasive, Offensive, Ranged}             → adds Evasive, Ranged
MNK = {Balanced, Evasive, Offensive, Ranged, Striker}    → adds Evasive, Ranged, Striker
```

**Invocations.** Ranger's five (Divine, Inversion, Over Channel, Recovery, Spellblade) are
**byte-identical to Paladin's five** — the Ranger slot adds **zero** invocations. Monk adds
Unyielding.

**Itemization — a wash.** Measured over the same 3,663-item catalogue: best-AC-per-slot
totals are PAL 287 · PAL+MNK 292 · PAL+RNG 289, out of ~290. Adding Monk is worth **+5 AC**,
adding Ranger **+2 AC**, both confined to one wrist/back slot. Equipable counts:
PAL+MNK 2,599 items / **320 weapons**; PAL+RNG 2,553 / **350 weapons**.

**Monk's classic package, audited on this chassis:**

- **Mend — refuted as commonly stated.** "25% of health / 6-minute timer" is classic
  contamination on a Legends wrapper (the source page carries a first-person classic
  anecdote) and is contradicted by a T1 note that Legends *shortened* the cooldown. Legends
  values are unpublished. It duplicates a Paladin heal line — but does so **without mana**,
  a genuine if unquantifiable point on a mana-strained chassis.
- **Feign Death — holds.** Monk's one genuinely non-redundant contribution. Roughly 50–70%
  covered by Enchanter mez/lull/memory-blur (an estimate, not a source).
- **Skill caps — mostly dominated.** Defense 225 is beaten by Paladin's **230**. Monk has
  **no Parry** — the trio runs 180 where Ranger raises it to **205**. Riposte ties Paladin's.
  Hand-to-Hand 270 is dead weight on a plate chassis holding weapons. The worn-weight AC
  bonus is **voided by the plate the Paladin slot exists to unlock**.
- **What survives, real and narrow:** Dual Wield **252 vs 210** (the single biggest melee
  skill term), Dodge 250, and Block 205 — knights do not block, so Block is genuinely
  additive at ~+1.2pp avoidance.

---

## 6. Known gaps — the honest ledger

Struck-through entries were closed by later evidence. The rest still stand.

- **k (%DPS per +100 ATK)** — dev-refused outright. Not invented here; parameterised instead.
- ~~**G for any Legends target**~~ — **CLOSED.** Measured at **5.98%** across 22,604 parsed
  swings in committed log fixtures (§4.1).
- ~~**Whether Unbound Alacrity's cap-raise functions**~~ — **CLOSED.** Confirmed in play:
  max haste 175, Monk 185.
- ~~**The haste cap's numeric value**~~ — **CLOSED.** 175 (+75%), Monk 185 (+85%). Sources
  combine **additively**, per a dev worked example where 41% + 34% reaches the cap.
- **Base endurance regeneration and per-class endurance pool size** — unpublished, and the
  Strategy savings curve is an open question on the site that mines the client files. This
  bounds the *magnitude* of Force of Nature's advantage, not its sign (§4.2). Any specific
  "Offensive uptime %" figure would be fabricated, so none is stated.
- **Monk kick-line damage** (Flying Kick, Round Kick, Eagle Strike, Tiger Claw) — withheld as
  balance-sensitive. Only "Flying Kick damage starts at 50" is published, with no scaling
  formula. **The largest unpriced quantity remaining, and it is on the Monk side.**
- **The Striker partition** — which abilities count as "weapon skill". Listed as an open
  question by the site that mines the client files.
- **Dual Wield 252 vs 210** — calibrated by a single parse at skill 252 and extrapolated
  linearly down to 210. The weakest link in Monk's case — and worth **exactly zero** if the
  character carries a shield or a two-hander.
- **Whether strikethrough applies to archery** — unpublished, and it matters, because
  Ranger's other free AAs push toward a bow build.
- **eqlsource excludes AA data by policy** (*"AA planning… belong to other tools"*), so no
  AA claim in this document reaches T2 on the game's most disciplined source.

### Rejected as evidence

The **Master Yael D0–D4** measurements — same boss, same group, tier as the only variable,
which looked like a clean instrument for pricing ATK against scaling AC. Re-measurement does
not reproduce: **D1 −12%, D2 −9%, D4 +64%**, at n=1 per tier. *"Damage to kill is what a
fight cost, not a constant."* Not used.

---

## 7. The one test that would settle it

**Read your stat window's Haste *cap* row at level 50.** Compare a level-50 Monk against a
level-50 non-Monk. If the cap reads ~10 points higher on the Monk, Unbound Alacrity is real,
Monk's largest term is real, and Monk takes the endgame-group case outright. If it does not,
Ranger-by-a-nose stands.

It takes five seconds and needs no parser. It is worth more than every wiki page cited here.

*(The previously obvious experiment — parse Striker vs Offensive — is refuted: Striker
prints nothing per hit.)*

---

## 8. One branch never priced

Ranger opens a **ranged** build: Ranged stance, Innate Called Shot free, Weapon Mastery of
the Scout at 30/60/100% archery base damage. Whether strikethrough applies to archery is
**unpublished**, and Legends archery damage is likewise unpublished. Note the measured log
recorded `ranged` stance used **once**.

**If you intend to play at range, this comparison does not apply to you and Ranger's real
case is unevaluated.** If you intend to play in melee, it applies, and §0 is the answer.

---

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
