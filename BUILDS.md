# EQ LEGENDS — WHAT THE TOP BUILDS ACTUALLY ARE

**Established:** 23 August 2026
**Method:** 44 research agents across five rounds, plus a damage model run over all
**560** class trios. Every numeric claim graded and adversarially re-derived.
Tiers: **TM** measured parse > **T1** dev > **T2** structured wiki > **T3** named guide >
**T4** aggregator > **T5** inherited classic prose.

Companion to `MONK-VS-RANGER.md`, which answers the narrower Paladin+Enchanter question.
Same standard as `CLIENT-TRUTH.md`: *a number without its source is a number that can lie.*
The model is committed as `model.py` — every row below re-runs with one command.

---

## 0. The finding

**Berserker + Enchanter is the dominant core in the game, and almost nobody is playing it.**

Every one of the top eleven trios by sustained damage contains both. The third slot is
nearly free — it buys mitigation, aggro or healing, and costs only 0–10% damage.

| # | Trio | Sustained | Starved | Burst | Mitigation | Aggro | Note |
|---|---|---|---|---|---|---|---|
| 1 | **BER+ENC+SHD** | **216.2** | 176.2 | 290.5 | Defensive | single | the optimum |
| 1= | BER+ENC+NEC | 216.2 | 176.2 | 290.5 | Channeler | weak | ties, but no plate |
| 3 | BER+ENC+RNG | 210.5 | 169.3 | 287.1 | Channeler | weak | wins if ATK coeff is high |
| 4 | BER+ENC+MNK | 208.0 | 168.7 | 281.0 | Channeler | weak | haste cap 185 |
| 5 | **BER+ENC+WAR** | 206.7 | 166.7 | 281.0 | Defensive | **AE** | the only real multi-mob tank |
| 5= | BER+ENC+PAL | 206.7 | 166.7 | 281.0 | Defensive | single | + Mage Hunter, + heals |
| 12 | **BER+CLR+ENC** | 194.2 | 158.2 | 261.0 | Channeler | weak | charm + best 2H + real healing |
| — | ENC+RNG+SHD | 159.1 | 139.2 | 196.0 | Defensive | single | *no Berserker* |
| — | *ENC+MNK+PAL* | *147.1* | *127.9* | *182.6* | Defensive | single | *the current character* |
| — | *BER+RNG+SHD* | *150.6* | *109.4* | *227.2* | Defensive | single | *the proposed trio* |
| — | *CLR+ENC+RNG* | *138.0* | *121.7* | *168.4* | Channeler | weak | *the Cleric concept* |
| — | CLR+RNG+WAR | 59.6 | 41.3 | 93.8 | Defensive | AE | survivability, not damage |

**The single highest-value change available: swap the Ranger for an Enchanter.**

```
BER+RNG+SHD  150.6   ->   BER+ENC+SHD  216.2      +44%
```

Trade +104 ATK and strikethrough — worth about **+4.5%** of own melee — for a charm pet
worth **85 DPS that costs zero endurance**. Two separate instincts, both right, that belong
in the *same* build.

Optimum vs the three builds under consideration: **+44%** over SHD+RNG+BER, **+47%** over
PAL+ENC+MNK, **+57%** over RNG+CLR+ENC.

---

## 1. Why Berserker + Enchanter

They win for unrelated reasons, which is why the pair compounds.

### Berserker brings three things nobody else has

**The only cap-breaking stance.** Verbatim:

> "While this stance is active, **attack speed and combat skill recharge rate is doubled**
> and your chance to hit and **combat skill damage is increased by 25%**. Every point of
> damage dealt consumes **half** that amount in endurance… You also take **8.3% of outgoing
> damage to yourself**." <span>T2</span>

Haste otherwise caps at **175** (Monk 185). Berserker doubles *through* the cap — the only
route to 350 effective attack speed in the game.

**Against Offensive specifically, the 2× cancels** — Offensive gets its 2× from damage per
swing, Berserker from swing rate. The real edge is elsewhere:

| channel | Berserker | Offensive | edge |
|---|---|---|---|
| auto-attack | 2× speed | 2× damage/swing | **equal** |
| combat skills | 1.25× dmg × 2 uses = 2.5× | 2× | **1.25×** |
| weapon procs | 2× swings = **2× procs** | 1× procs | **2×** |

Blended: **+7% to +20%** if Offensive also buffs combat skills, **+14% to +59%** if
"melee damage" means auto-attack only. Unresolved, and it is the largest open question on
the Berserker side.

**The best two-handed weapon**, and **Frenzy** (real, trainable — 209 skill-ups in the log
corpus; 216 hits / 190 misses, mean 60.8, max 637), which doubles in frequency under the
stance. Plus **Unbound Fury**, +6% crit, autogranted.

### Enchanter brings a second body that costs nothing

Measured over 133 committed EverQuest Legends client-log fixtures — 88,701 timestamped
lines, 24,264 damage events: <span>**TM**</span>

| | value | n |
|---|---|---|
| charmed pet ÷ owner damage | **0.774×** (range 0.40–1.89) | 475 vs 733 hits, 887s |
| per swing: charmed / owner / summoned | **87.0 / 75.4 / 26.2** | 587 / 11,800 / 417 |
| charmed pet, best sustained | **112.6 DPS** | 14,864 dmg / 132s |
| same target vs a named boss | **4.05× owner** | 6,453/66 vs 1,594/37 on Grandmaster R\`tal |
| summoned pet ÷ owner | **0.167×** | 495 hits, 1,035s |
| **charm ÷ summon** | **4.65×** | — |

**Charmed pets hit harder per swing than a level-50 player** (87.0 vs 75.4) and only trail
on total because they swing 0.69× as often.

The decisive property is not the size — it is that **pet damage is not billed to endurance.**
Every point of a Berserker's or a knight's output draws on a bar that only Force of Nature
refills, at 3.17/sec. The pet draws on nothing. In a fight measured in minutes, that is the
whole ballgame: it is why Build A wins the *starved* column even where it loses the *burst*
column.

---

## 2. The damage model

`DPS = swing_rate × multi_attack × mean_hit × land_rate × cast_duty`

**Mean hit** uses the client-validated damage-bonus formula — **not** damage/delay ratio:

```
Damage Bonus = HandMod × max(Level, WeaponDamage) × (min(Delay,50)/40) × (Level/100)
               HandMod = 1.1 two-handed, 0.8 one-handed.  MAIN HAND ONLY.
```

Validated 2-for-2 against live client captures: Earthshaker (2H, 70 delay) predicts **50**,
client shows 50; Whitened Treant Fists (1H, 28 delay) predicts **13**, client shows 13.
<span>**TM**</span>

**Ratio is the wrong metric and it misled this analysis for two rounds.** The bonus scales
with *delay* and *weapon damage*, both of which ratio divides away:

| weapon @+10 | ratio | mean hit | note |
|---|---|---|---|
| Cudgel of the Fool (BER) 90/52 | 1.731 | **123.69** | delay 52 — 2 past the cap, near-optimal |
| Baton of the Sky (CLR) 66/40 | 1.650 | **76.82** | +50 AC, +150 mana |

The Cudgel is **1.53× the Baton per hit** — not the 1.049× ratio implies. Because
`min(Delay,50)` caps the bonus, **delay beyond 50 is pure waste**: Earthshaker at 70 delay
has the highest raw damage of any reachable 2H and one of the worst scores.

**Swing rate** `= 10 / floor(delay / haste_multiplier)` — delay in tenths of a second.
Cudgel at the 175 cap = 0.345/s; under Berserker (350) = **0.714/s**.

**Parameters, stated once.** R = 0.55 mean weapon roll · land 0.8394 damage stance /
0.7387 Balanced · multi-attack 1.8 with BER or WAR, else 1.6 · cast duty 0.85 with a healer
class, else 1.00 · crit 5% base, +6% with Berserker's Unbound Fury · charm pet 85 DPS ·
summoned pet 15.6 DPS · Ranger +1.91% strikethrough and +104 ATK × k, k = 2.5%/100 ATK.

**Sustained** = 0.65 × starved + 0.35 × burst, reflecting that endurance binds in long fights.

---

## 3. Sensitivity — does the ranking survive?

**Yes.** BER+ENC tops every run; only the third slot reshuffles.

| pet value | #1 | #2 | #3 |
|---|---|---|---|
| 44.5 (measured all-fights floor) | BER+ENC+SHD 175.7 | BER+ENC+NEC 175.7 | BER+ENC+RNG 170.0 |
| **85 (baseline)** | **BER+ENC+SHD 216.2** | BER+ENC+NEC 216.2 | BER+ENC+RNG 210.5 |
| 112.6 (best measured sustained) | BER+ENC+SHD 243.8 | BER+ENC+NEC 243.8 | BER+ENC+RNG 238.1 |

| ATK coefficient k | #1 |
|---|---|
| 2.5% / 100 ATK | BER+ENC+SHD 216.2 |
| 10% / 100 ATK (classic folklore) | **BER+ENC+RNG 217.2** — Ranger takes the third slot |

So *k* decides only whether the third slot is Shadow Knight or Ranger. It never dislodges
the core.

---

## 4. Choosing the third slot

The damage spread across viable third slots is under 5%. Pick on what the number cannot show.

| Third | Damage | What it uniquely adds |
|---|---|---|
| **SHD** | 216.2 | Defensive stance · plate · lifetap sustain · procs · best shield in game (Obtenebrate, 35 AC) |
| **WAR** | 206.7 | **The only AE aggro in the game** — Heroic Leap, Area Taunt, Cleave |
| **PAL** | 206.7 | Defensive **and** Mage Hunter · heals · Unbound Life |
| **CLR** | 194.2 | Best healing kit · Channeler · the Baton (if you want AC on the weapon) |
| **RNG** | 210.5 | +104 ATK · strikethrough · **Force of Nature**, the only endurance regen |
| **MNK** | 208.0 | Haste cap 185 · Striker · Feign Death |

**If you tank, take Warrior.** Across the entire AA tree there are exactly **two**
multi-target hate tools and both are Warrior-only:

> **Heroic Leap** | 1 rank | **0 AA cost** | *"attracting the attention of up to 8 opponents
> within a 40 foot radius… increasing their hatred for you by 1250 points."* Refresh 30s.
> **Requires Level 12.** <span>T2</span>

10,000 hate per 30 seconds across 8 mobs, free, from level 12. Without it your only AE
anything is Rampage on a **10-minute** cooldown. **One AE swing per 10 minutes is not a tank.**

And the aggro hole is worse than it looks for caster-ish trios: Ranger's only hate spell
(**Jolt**) is a *dump*, Cleric's (**Atone**) *wipes* the hate list, and the Enchanter's aggro
AA is a third dump. **Damage shields generate zero aggro.** Whether healing generates threat
in Legends is **unverified** — eqlwiki's Aggro, Hate_Management and Tanking pages are empty.

---

## 5. Mitigation — and a correction

Cleric and Enchanter both grant **Channeler**: *−40% to all incoming damage.* An earlier
version of this analysis claimed a non-knight trio had "no mitigation stance." That was wrong.

| fight | Defensive `0.5+0.3m` | Channeler `0.60` | winner |
|---|---|---|---|
| pure melee | **2.00× eHP** | 1.67× | Defensive +20% |
| ⅓ magic | 1.67× | 1.67× | tie |
| pure magic | 1.25× | **1.67×** | Channeler +33% |

**The entire cost of having no knight is ≤20% effective HP, melee-only.** Crossover at
m = 1/3 magic damage.

**Evasive is refuted as a posture.** *"95% chance to evade all incoming attacks. Every point
of damage evaded consumes 2 endurance."* Its cost scales with the damage that *would have*
landed, so it worsens exactly as the fight gets harder:

| stance | endurance per point neutralized |
|---|---|
| Channeler | 0.5 end + 0.5 mana |
| Defensive | 1.0 |
| **Evasive** | **2.1** |

9.5× Channeler's rate. It is an 8–15 second panic button, not a stance.

---

## 6. Stance economics

Verbatim costs, normalized. Base damage rate D:

| stance | dmg rate | endurance/sec | gain per endurance |
|---|---|---|---|
| Balanced | 1.0 | **0** | free — *and doubles endurance regen* |
| Offensive | 2.0 | 1.0 | 1.000 |
| **Berserker** | 2.0 | 1.0 | **1.000** + 2× skill recharge + 25% skill dmg |
| Striker | 3.0 | 3.0 | **0.667** |

**Striker is the worst damage stance in the game** and Berserker strictly dominates it.
Offensive charges only *bonus* damage; Striker charges **all** damage — hence half the
efficiency. Corroborated behaviourally in the log corpus: **berserker 128 uses, striker 8.**

A Striker opener is a **net loss**: worth at most +0.83% of a 180s fight even if endurance
were free, and endurance spent there is endurance not spent in Offensive, which converts
1.5× better.

---

## 7. Risk the damage number does not show

**Charm break, measured:** 33 events. **21% turned on the owner within 30 seconds** — worst
case **2,821 damage across 24 hits**. 64% were re-charmed inside 30s. That is the variance
you buy with the pet, and it lands hardest on a build with no Defensive stance.

**Berserker self-damage:** 8.3% of outgoing damage reflected onto you. Fine with a healer,
dangerous solo.

**Charm may be barred where it matters most.** Named-mob stat blocks carry flags including
`Uncharmable` and `Unmezzable`. Prevalence across the full named roster is **not established
here** — it is the largest single unknown in the charm case, and it would not change trash
or leveling performance at all.

---

## 8. Known gaps

Struck-through entries were closed by later evidence.

- **k, %DPS per +100 ATK** — dev-refused: *"We aren't going to spoil the exact formula."*
  Parameterised, never invented. Decides only SHD vs RNG in slot three.
- **Whether Offensive's +100% buffs combat skills** — decides whether Berserker's edge over
  Offensive is +7% or +59%.
- **Base endurance regen and per-class pool sizes** — unpublished. Bounds the *magnitude* of
  the starved-vs-burst split, not its direction. No uptime percentage is quoted here because
  any such figure would be fabricated.
- **`Uncharmable` prevalence on named and raid mobs** — see §7.
- **Monk kick-line damage** — withheld as balance-sensitive.
- ~~**G, target avoidance**~~ — **CLOSED.** Measured **5.98%** across 22,604 swings
  (dodge 2.74 · parry 2.33 · block 0.92 · riposte 0.00). Miss is a separate 36.25% bucket
  strikethrough never touches. Slow does **not** shrink G (7.95% vs 6.88%, n.s.).
- ~~**Haste cap value**~~ — **CLOSED.** 175, Monk 185, sources combine additively.
- ~~**Whether the Monk cap-raise works**~~ — **CLOSED.** Confirmed in play.
- ~~**Whether charmed pets can be geared**~~ — **CLOSED.** Since 7 Jul 2026 charmed pets
  equip from the pet inventory; items are removed when charm breaks.

**Rejected as evidence:** the Master Yael D0–D4 sweep. Same boss, same group, tier the only
variable — but re-measurement does not reproduce (**D1 −12%, D2 −9%, D4 +64%**) at n=1 per
tier. Not used.

**What the model does not price:** aggro, survivability, charm-break variance, group
desirability, or gear contention. It is a damage model. §4 and §7 exist because the damage
number alone would mislead.

---

## 9. Recommendations

**Maximum damage, and you have a healer:** `BER + ENC + SHD` — 216.2. Charm pet, best 2H,
Defensive stance, plate, lifetaps.

**Maximum damage that can hold multiple mobs:** `BER + ENC + WAR` — 206.7, and the **only**
build in the game with AE aggro. Costs 4% damage. If you tank, this is the pick.

**Self-sufficient, no healer:** `BER + CLR + ENC` — 194.2 with the best healing kit in the
game. Costs 10% damage for near-total independence.

**If the ATK coefficient turns out to be high:** `BER + ENC + RNG` — 210.5, and the only one
that refills its own endurance bar.

**Currently played, `PAL+ENC+MNK` at 147.1**, is a sound build and its utility case is real —
the damage gap to the optimum is 47%, but roughly two-thirds of that is the Cudgel and the
Berserker stance, not the Enchanter, which it already has.

---

*Reproduce: `python3 model.py`. Fan analysis. Not affiliated with Daybreak Game Company,
Game Jawn or Darkpaw Studios.*
