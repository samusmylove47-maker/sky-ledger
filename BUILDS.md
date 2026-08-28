# EQ LEGENDS — WHAT THE EVIDENCE CAN AND CANNOT SAY ABOUT BUILDS

**Established:** 23 August 2026 · **Revised after adversarial review:** 24 August 2026
**Method:** 64 research agents across seven rounds, a damage model over all 560 trios, and a
five-front adversarial attack on that model. Tiers: **TM** measured parse > **T1** dev >
**T2** structured wiki > **T3** named guide > **T4** aggregator > **T5** classic prose.

Same standard as `CLIENT-TRUTH.md`: *a number without its source is a number that can lie.*
Models committed as `model.py` (v1) and `model2c.py` (corrected). Every claim below re-runs.

---

> ## ⚠ THE MODEL BELOW IS SUPERSEDED — DPS FIGURES ARE 4–8× TOO LOW
>
> **28 August 2026.** In-game observation supplied by the player puts real sustained
> single-target DPS at **600+** for an above-average martial character with no Enchanter,
> **900–1000** min/maxed, and **1200+** best-in-slot. `model2c.py` tops out at **166.5**.
> That is not a tuning error; it is a structural one. Three defects are identified:
>
> | # | Defect | Effect |
> |---|---|---|
> | **S1** | Final damage was computed as `R × DMG` — a *fraction* of the raw DMG stat. The wiki says base damage is `(DMG × 2 + 1)` **"before strength, skill, or level are factored in."** | Ratio **4.47× too small** |
> | **S2** | **No Wrath term at all.** ATK feeds `Wrath = WeaponSkill + ((2×STR)−150)/3 + WornATK + SpellATK`, which scales variable damage on *every swing*. The model priced the Ranger's +104 ATK at +2.6%. Under Wrath it is **+149 Wrath ≈ +37%**. | Ranger undervalued **~14×** |
> | **S3** | **Exaltations were modelled as zero.** A real inventory dump shows **five augment sub-slots on Primary and five on Secondary** — see `EQUIPMENT-TRUTH.md` §3. | Unknown, plausibly large |
>
> S2 is the one that matters for the standing dispute. The player reports that essentially
> every elite martial build now includes Ranger, and that top builds cluster on
> warrior / ranger / berserker / monk **+ Shaman for Puma procs**. The model marginalised
> Ranger. Under a Wrath-scaled chain it should not. **Whether the corrected chain actually
> reproduces that preference is the whole test of the rebuild**, and if it does not, that
> will be said plainly here.
>
> A rebuild is in progress. Until it lands, **every DPS number in this file is wrong in
> absolute terms**, and the ordinal claims are only as good as the assumption that all three
> defects bias every trio equally — which S2 explicitly does not.
>
> Two further channels were found unmodelled on 28 August and are **not** in any figure here:
> the **two ANY equipment slots** (worth ~+53 Wrath, about half a Ranger's ATK line, to every
> build) and the **Exaltation sub-slots** above. Both are documented in `EQUIPMENT-TRUTH.md`.

---

## 0. What was asked for, and what is deliverable

Four ranked lists were requested: top 25 martial, top 10 caster, top 10 hybrid, top 10 META.
After adversarial review, **only one of the four is deliverable, and not as a ranking.**

| Asked for | Status | Why |
|---|---|---|
| Top 25 martial DPS | **Delivered as an unordered TIER** | Top-8 spread is 21.5 pts against +/-25 pts per-trio uncertainty. The ordering is noise. |
| Top 10 caster DPS | **WITHDRAWN** | Every public spell-damage figure is classic-EQ formula output, and the error is *non-uniform* — so neither absolute nor ordinal claims survive. |
| Top 10 hybrid DPS | **WITHDRAWN** | The model has zero resolution in the slot the ranking is about: seven trios tie to the decimal. |
| Top 10 META | **Delivered with its headline retracted** | "Every top build contains ENC+SHD" is an artifact of an untested constant. |

This is the second scope correction in this document's history. The first withdrew a
game-wide DPS claim. Publishing caster and hybrid rankings now would have reinstated exactly
that claim under new headings.

---

## 1. The three findings that killed the caster and hybrid lists

### F1 — The caster and melee "sustained" columns were different physical quantities

Melee sustained was defined as Balanced stance: free, 100% uptime, forever. Caster sustained
came from a mana model. Back-solving the published caster numbers from their own inputs:

```
NEC  166.7 DPS / 41.24 mana/s = 4.0422 dmg/mana -> 21.5 / 4.0422 = 5.319 mana/s implied
WIZ  808 dmg / 203 mana       = 3.9803 dmg/mana -> 21.1 / 3.9803 = 5.301 mana/s implied
```

Two classes pin the same hidden constant to within **0.34%**: the caster column assumed
**5.31 mana/s**, which is 32x the documented in-combat regen (0.167) and 0.84x the
out-of-combat figure (6.333). So it silently modelled a caster spending **~84% of wall-clock
out of combat** — then compared that against a melee column defined as never stopping.
**The two halves were not comparable in either direction.**

### F2 — Spell damage data is classic-EQ output, and the error is non-uniform

eqlwiki spell pages self-label `{{Classic Era}}`; Ice Comet's 808 damage / 203 mana / 5.00s
are the classic values verbatim. Official Legends notes state the spell-upgrade tiers move
damage, mana, cast time and duration **"depending on the spell."**

That clause forecloses the usual escape. If tiers scaled damage and mana *together*,
damage-per-mana would be tier-invariant and the ordinal ranking would survive stale
absolutes. It does not. And this is not theoretical: the committed spell DB gives **Denon's
Disruptive Discord 4 damage/tick against 32 measured** — an 8x error on a named spell, with
the official change note naming that spell.

**Withdraw the caster column. Not reorder — withdraw.**

### F3 — The Shadow Knight's biggest measured lane is neither portable nor a skill

`Reave` prints two lines per activation. The verb averages 4.34 DPS; the other 36.06 comes
from `Reaving Strike` — **a flat 306 that never varies, never crits, never resists**, because
it converts a percentage of *max HP*. That is one raid-buffed tank's HP pool, not a class
value. All 62 self-reave lines sit in a single 11-minute window against one boss, in a file
the upstream repo labels a bug-report slice with **zero stance lines surviving** — so the
lane has no Balanced sample at all, and Balanced is what "sustained" means.

Corrected: **40.1 -> 13.4**. Paladin's Smite has the identical structure (its magic half
scales with max *mana*): **28.4 -> 20.3**.

---

## 2. The martial tier — unordered, and that is the finding

Corrected model (`model2c.py`), all constants re-measured. **These twelve trios are
statistically indistinguishable.** Read the membership, not the order.

| Trio | score | sust | burst | autoskills | weapon |
|---|---|---|---|---|---|
| BST+MNK+ROG | 166.5 | 155.4 | 187.2 | 94.2 | DW Wu's Fist of Mastery |
| BER+BST+ROG | 157.8 | 145.3 | 181.0 | 80.8 | 2H Cudgel of the Fool |
| **BST+RNG+ROG** | 156.2 | 149.5 | 168.8 | 70.6 | **2H Windstriker (bow)** |
| MNK+ROG+SHD | 152.5 | 140.9 | 174.1 | 93.6 | 2H Khyldorn |
| BST+PAL+ROG | 152.1 | 141.7 | 171.3 | 82.3 | 2H Truvinan |
| BER+BST+MNK | 148.1 | 135.1 | 172.2 | 69.6 | 2H Cudgel of the Fool |
| BST+ROG+SHD | 147.1 | 136.0 | 167.7 | 74.8 | 2H Khyldorn |
| **BST+MNK+RNG** | 145.0 | 138.3 | 157.6 | 59.4 | **2H Windstriker (bow)** |
| BER+MNK+ROG | 143.1 | 130.1 | 167.2 | 99.6 | 2H Cudgel of the Fool |
| BST+MNK+PAL | 142.5 | 131.7 | 162.7 | 71.1 | 2H Truvinan |
| BER+ROG+SHD | 142.2 | 129.7 | 165.5 | 80.3 | 2H Cudgel of the Fool |
| **RNG+ROG+SHD** | 140.7 | 133.9 | 153.2 | 70.0 | **2H Windstriker (bow)** |

**Spread across the top eight: 21.5 points. Per-trio uncertainty: +/-25 points.** The
ordering is noise and is printed only so the arithmetic can be checked.

**What is robust: ROGUE appears in nine of twelve.** Backstab at **41.5 DPS** is the largest
single autoskill lane in the game and it survived every attack — including the front-arc
worry, which was refuted outright (zero positioning-failure messages in the corpus, and
backstab land rate while tanking is *higher*, 0.588 vs 0.538).

**Berserker is no longer dominant.** Once land rate, crit, weapon roll and multi-attack are
corrected, the Cudgel's advantage shrinks and BER holds four of twelve slots rather than
eleven of eleven. The earlier "Berserker + Enchanter is the dominant core" finding **does
not survive correction.**

**Archery arrives.** Three of the twelve are Windstriker bow builds — a channel the earlier
model could not see at all.

---

## 3. Archery, corrected twice

Windstriker +10 = **90/60**, confirmed, RNG-only, and a category break (runner-up bow is
ratio 1.100 against its 1.500).

The first research pass claimed archery was **2x Ranger melee**. That was refuted: it fed
archery and melee onto **two different damage scales** by quoting half a sentence. The full
clause reads *"a melee weapon's base damage ... is (DMG*2+1), for archery, the base damage is
Bow DMG + Arrow DMG."* Corrected, **archery is at parity: 0.87x-1.30x of Ranger melee.**

Hard limits, each confirmed three ways: **Berserker and Monk have no Archery skill at all**
(skill table, client scrape, and zero of 72 bows listing them), and only Rangers get the 4x
AA package, so a Rogue or Warrior archer does one-quarter the base damage.

**Thrown is not a channel:** ~28 DPS best case, and Throwing Boulder is race-locked to
BAR/TRL/OGR/IKS.

---

## 4. The META list, with its headline retracted

**Retraction:** "every top-10 META build contains ENC+SHD" is an artifact. In the committed
model **SHD and NEC are perfectly interchangeable** — both are pet-flag classes with no other
differentiating term. `BER+RNG+SHD 150.6 = BER+NEC+RNG 150.6` exactly. The finding decodes to
*"contains ENC, plus a pet class that also wears plate."* It was never about Shadow Knights.

**And the ENC half rests on an untested constant.** The charm-pet value is **48% of the top
build's score**, and the sensitivity test run on it was vacuous — every build in the tested
set contained ENC, so varying the constant was common-mode. Tested properly, against non-ENC
builds:

| charm pet value | #1 overall | ENC builds in top 10 |
|---|---|---|
| 44.5 (measured all-fights floor) | MNK+NEC+ROG | **4 / 10** |
| 85 (interpolated, used above) | ENC+NEC+ROG | 10 / 10 |
| 112.6 (best measured window) | ENC+NEC+ROG | 10 / 10 |

**At the measured floor the Enchanter core collapses.** Everything resting on "the charm pet
is worth 85 DPS" rests on an interpolation, not a measurement.

**What survives for META purposes** is qualitative and well-sourced:

- **The death penalty is zero.** No corpse, no XP loss, no item loss; respawn at bind.
  Survivability is worth materially less than intuition says, and every corpse-recovery and
  rez utility is worth ~nothing outside a combat rez in a raid.
- **Travel utility is not loadout-gated.** The Rituals system lets any trio cast Gate, Bind,
  every Druid ring and every Wizard port off-loadout. **Do not credit Druid or Wizard for
  ports.** What *is* gated is small: SoW/levitate/invis/see-invis, Tracking (RNG>DRU>BRD),
  Pick Lock (ROG/BRD), Shroud of Stealth.
- **Aggro:** Heroic Leap and Area Taunt are Warrior-only AE hate (8 targets, 40ft, +1250,
  30s, 0 AA cost). Every other hate tool in the game is a *dump* except Shadow Knight's two
  Terror spells. eqlwiki's Aggro, Hate_Management, Tanking and Crowd_Control pages **all
  404** — verified, not "reportedly". Whether healing generates threat is unpublished at
  every tier.
- **Aggro is worth ~zero solo**, and for a charm-pet build high taunt is an actual *malus* —
  you want the mob on the pet.
- **Control-resist is a real axis nobody scored.** The **Unyielding** invocation grants *"25%
  resistance increase to loss of control from fear, mez, and charm"* and is **BER/MNK/ROG/WAR
  only**. It counters the mechanic the difficulty sources name as the D3-D4 killer. ENC, SHD
  and every pure caster lack it.

---

## 5. Corrected constants

| Term | Was | Corrected | Basis |
|---|---|---|---|
| Land rate, Offensive | 0.8394 | **0.62** | measured, two independent parses |
| Land rate, Balanced | 0.7387 | **0.56** | measured |
| Crit multiplier | 2.006x | **1.664x** | measured, n=386, controlled |
| Crit rate | 5% / 11% | **13.2%**, and it fires on autoskills too | measured |
| Weapon roll R | 0.55 | **0.40 raid / 0.50 soft** | measured 0.287-0.51 |
| Multi-attack M | 1.6 / 1.8 | **1.44** | DA 240/630 = 38.1% |
| SHD Reave | 40.1 | **13.4** | see F3 |
| PAL Smite | 28.4 | **20.3** | engaged-seconds denominator |
| WAR lane | 2.6 (Cleave) | **9.5** (Kick) | zero player self-cleaves in 89,190 lines |
| RNG lane | 0 | **9.5** | Ranger has Kick at level 1 |

**Autoskills survived intact and are the model's best-supported term.** Direct proof — one
character, one second:

```
You try to backstab a large spider, but miss!
You bash a large spider for 1 point of damage.
You frenzy on a large spider for 33 points of damage.
You kick a large spider for 5 points of damage.
You try to smite a large spider, but miss!
You slash a large spider for 35 points of damage. (Critical)
```

Five class lanes plus auto-attack, same second. Whole-corpus census: 49 seconds containing
five distinct combat skills, 133 with four, 311 with three. `/autoskill` toggles them
per-skill with no slot budget. **There is no global cooldown and no lane cap.**

---

## 6. Channels still unmodelled

- **Striker stance** (BER/MNK/ROG/WAR): 3x weapon-skill / 5x non-weapon-skill abilities. The
  BURST column is defined as "resources ignored", which is *exactly* Striker's regime — so
  burst is wrong for every trio and wrong **asymmetrically**, under-crediting the four
  classes that have it.
- **Spellblade** (BST/PAL/RNG/SHD): turns the first spell gem into a melee proc with no cast
  bar — a genuine exception to the model's melee-or-cast rule. Measured **17.55 DPS**, 417
  damage/proc, 352/352 exclusive attribution at 1.1M-line scale. It needs an ENC spell *and*
  a hybrid invocation, so no additive per-class model can express it.
- **Damage shields:** exactly **1.00 tick per landed incoming hit** across four fixtures
  (60/60, 58/58, 39/39, 8/8), none on a miss. ~17.5 DPS single-target, **~105 DPS against six
  attackers**, for 0.13 mana/s. They do not stack and do not scale with gear. Requires that
  *you* tank — which the pet builds avoid.
- **Multi-target generally.** The whole model is single-target.

---

## 7. The one absolute validation, and its limit

`ENC+MNK+PAL` predicted **147.1** against **151.4 measured** over 3,201 seconds — 2.8% error.
It is the strongest single result here and worth stating.

It is also **n=1 trio, one character, one corpus, and right by cancellation** — a melee lane
roughly 2x too high against roughly 2x of missing everything else. The proof: correcting the
model *moved it away* from the anchor, to 166.6 (+10.0%). **A model that is right by
cancellation cannot be perturbed.** So quote 147.1 ~ 151.4 as one validated point estimate
for that one trio, and quote **no decomposition of it**.

---

## 8. Known gaps

- **The charm-pet constant** — 48% of the top score, interpolated not measured, and decisive
  for whether Enchanter cores rank at all.
- **Spell damage, all of it** — classic-EQ formula output, non-uniformly wrong.
- **The ATK coefficient** — dev-refused: *"We aren't going to spoil the exact formula."*
- **Whether the main-hand damage bonus applies to bows** — eqlwiki's own top-priority
  unverified mechanic. Swings archery by ~19%.
- **Striker uptime** — never measured, and it decides the burst column.
- **Endurance pool sizes and base regen** — unpublished. No stance-uptime figure appears
  anywhere in this document because any such figure would be fabricated.
- **In-combat mana regen** — documented at 0.167 mana/s, but the withdrawn caster model
  implies 5.31. The discrepancy is unexplained and is why F1 is fatal rather than a
  correction.

**Rejected as evidence:** the Master Yael D0-D4 sweep (re-measurement does not reproduce:
D1 -12%, D2 -9%, D4 +64%, n=1 per tier). And the "model is 4x inflated" worry, which
dissolved: the 57.5 DPS anchor is a median-of-fights over a level-7-to-50 corpus, while the
level-50 raid aggregate in the same corpus is **213.7**.

---

*Reproduce: `python3 model2c.py`. Fan analysis. Not affiliated with Daybreak Game Company,
Game Jawn or Darkpaw Studios.*
