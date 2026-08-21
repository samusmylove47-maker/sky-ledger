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

**The deciding variable is not the class. It is where you stand.**

| You are… | Better third slot | Confidence |
|---|---|---|
| In the mob's **front arc** — you tank, or the mob faces you | **RANGER** | Wins under *every* parameter combination at G ≈ 30% |
| **Behind** the mob — someone else holds aggro | **MONK** | Wins across essentially its whole range at G ≈ 10% |
| Mid-range group content (G ≈ 15–25%) | **Cannot be called** | Bands overlap; see §4 |

Where **G** = the target's *active-defense* avoidance (dodge + block + parry + riposte).

Because Paladin + Enchanter is fundamentally a **front-line chassis** — plate, Defensive
and Mage Hunter stances, taunt, heals, mez — the archetypal build for this trio stands in
the front arc. **On that reading, Ranger is the better third slot.** If you are instead the
back-line damage slot in a group with a real tank, take Monk.

Anyone telling you this is a blowout either way is using one of three refuted things: the
backwards "Striker = 5× weapon skills" figure, the additive reading of strikethrough, or a
made-up value for the ATK coefficient.

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

### 1.2 Strikethrough is worth ~6.6%, not 30%

Three separate deductions apply to the headline number:

1. **It is 30% only at level 50.** Ranks gate at **levels 12 / 30 / 50** → 10% / 20% / 30%.
2. **It is multiplicative, not additive.** It recovers 30% of *already-avoided* swings:
   gain = `0.3·G/(1−G)`. It is not +30 percentage points onto your hit chance.
3. **Scope:** it touches only the four active-defense gates. It does **not** touch the
   miss/AC roll. So G is active-defense avoidance *alone*, smaller than any "total
   avoidance" figure.

| G | strikethrough gain |
|---|---|
| 10% | +3.33% |
| 15% | +5.29% |
| 18% | +6.59% |
| 25% | +10.00% |
| 30% | +12.86% |

And if you fight from **behind**, riposte never fires and probably parry doesn't either —
G collapses and this ability collapses with it. That is why position decides the question.

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

It is the largest single term in the comparison — *if the cap-raise works*. Nobody has ever
observed it in a stat window. See §6.

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

These are the reasons the middle of the range cannot be called. None is a rounding error.

- **k (%DPS per +100 ATK)** — dev-refused outright. Not invented here; parameterised instead.
- **G for any Legends target** — dodge/parry/block/riposte rates are published **nowhere**.
  eqlsource, the most rigorous source for this game, carries no such measurement.
- **Whether Unbound Alacrity's cap-raise functions** — never observed in a stat window. It
  is the largest single term in the comparison and it rests on one patch-note sentence.
- **The haste cap's numeric value** — the "75%" figure sits on a page that is a near-verbatim
  fork of a Project 1999 classic guide, carrying level-60 parse tables and Kunark drops.
  *(Resolved:* haste is percentage-denominated and multiple sources combine **additively** —
  proven by a dev worked example where 41% + 34% reaches the cap at 75.)*
- **The Striker partition** — which abilities count as "weapon skill". Listed as an open
  question by the site that mines the client files.
- **Dual Wield 252 vs 210** — calibrated by a single parse at skill 252 and extrapolated
  linearly down to 210. The weakest link in Monk's case.
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
