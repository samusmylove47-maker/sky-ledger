# THE DAMAGE CHAIN, REBUILT FROM MEASUREMENT

**Established:** 28 August 2026 · **Revised the same day after adversarial review**
**Method:** nine research agents over the committed Legends log corpus, plus independent
re-derivation here. Four parses of ~100,000 log lines and 20,000–23,000 self-swings.
Where a wiki formula and a histogram disagreed, the histogram won — twice, including
against a model published in the first draft of this file.

This replaces `model.py` and `model2c.py`, both **structurally wrong** and 4–8x too low.
Same standard as `CLIENT-TRUTH.md`: *a number without its source is a number that can lie.*

> **Revision notice.** The first version of this document, committed at `a8b4f8e`, gave
> the roll as a 20-step lattice `W x (D20/10) + B` with a measured `EmpiricalD20()`
> table. **That model is refuted and §2 below replaces it.** A lattice admits at most 20
> distinct damage values per weapon; one file shows **82 distinct values covering every
> integer 2→99** on a single verb against a single target. The refutation was verified
> here before being accepted. The mistake is left described rather than deleted because
> the *reason* it survived the first pass is instructive: the mean and the mid/max ratio
> both fit, and only the support ruled it out.

---

## 1. Ground truth first — what real characters actually do

Measured from committed client logs of a real level-50 character (`Primitive`,
PAL/MNK/ENC, mid-tier gear, **not** best-in-slot), counting only that character's own
damage.

| Fight | Sustained | Best window |
|---|---|---|
| `jos437-finishing-blow` | **426.5 DPS** over 466 s | **502 DPS** |
| `w70-dracoliche` | 325.9 over 177 s | — |
| `p4-pet-buff` | 310.8 over 355 s | — |
| typical band | 130–330 | — |

An independent pass segmenting on 6-second gaps put the same top fight at **483 DPS
engaged / 582 over the best 60 s / 678 over the best 30 s**.

**The player's reported figures are corroborated, not merely asserted.** And
`model2c.py`'s 166.5 was refutable without leaving the repository — that should have
been caught here, not in-game.

> **Convention warning.** Wall-clock, engaged and peak-60s DPS differ by up to **1.75x**
> on the same fight. The anchors and the model must use the same one or the comparison
> is meaningless. Everything below is **engaged** DPS.

---

## 2. The per-swing chain

```
Wrath  = Offense + ((2 x STR) - 150)/3 + WornATK + SpellATK
U      = 2 x DMG + 1                                   base-roll maximum
B      = HandMod x max(Level, DMG) x (min(Delay,50)/40) x (Level/100)
         HandMod = 0.69 (1H) | 1.10 (2H)               MAIN HAND ONLY, else 0

r  ~  continuous on (0,1]     offense-vs-mitigation roll,  E[r] = 0.721 measured
x  =  1                                              with probability 1 - 0.49
   =  min(2.25, 1 + max(10, (Wrath-80)/2) x U(0,1))   with probability 0.49

DamageDone  = U x r x x
if crit (p = 0.1272):   DamageDone = 1.7 x (max(DamageDone, DMG) + 5)
FinalDamage = DamageDone + B
if Offensive Stance:    FinalDamage = 2.00 x FinalDamage
```

Closed form:

```
E[hit | landed] = 1.089 x U x E[rx](Wrath, Mt) + B + 1.1
Lane DPS        = swing_rate x P(land) x E[hit | landed] x StanceMult
```

### `U = 2 x DMG + 1` — confirmed, by identifying the actual weapons

The map from a catalogue `DMG` stat to in-game damage was twice declared unclosable. It
was closed by a merge line naming the weapon, dated to the same day as the fight logs:

```
[Wed Aug 05 20:27:07 2026] You have successfully merged two items together
                           to create a new item: Thelvorn, Blade of Light +8
```

and the committed inventory dump supplying the offhand. Two identified weapons against
two real histograms:

| lane | weapon | DMG | predicted max | **measured** | err |
|---|---|---|---|---|---|
| main slash | `Thelvorn, Blade of Light +8` | 36 | 84.2 | **86** | −2.1% |
| offhand claw | `Whitened Treant Fists +4` | 19 | 39.0 | **40** | −2.5% |

The rival reading `U = 2(2 x DMG + 1)` predicts 157.2 and 78.0 — **off by +83% and
+95%, refuted.** This was the one place a coefficient could have been fitted to the
600/900/1200 anchors, and measurement decided it **against** them.

The same two lanes give `maxExtra = 2.230` and `2.282` independently — so **2.25, not
the wiki's 2.10.**

---

## 3. Offensive Stance is x2.00, and it is the single largest term

Not in `model2c.py` at all. Confirmed here by an independent parity test:

| stance | hits | **% even damage** | land rate |
|---|---|---|---|
| **offensive** | 1,069 | **98.8%** | **56.9%** |
| defensive | 856 | 57.4% | 46.3% |
| berserker | 783 | 56.8% | 44.0% |
| balanced | 470 | 55.1% | 44.9% |
| striker | 103 | 54.4% | 57.5% |

**Damage under Offensive is even 98.8% of the time and ~55% otherwise.** That is the
signature of a x2 applied last, and nothing else produces it. Two further confirmations:
endpoints double exactly on the same weapon in the same file (`86 → 172`, `90 → 180`,
`89 → 178`, `184 → 368`), and land rate rises with it.

```
Offensive melee multiplier = 2.00 damage x 1.084 accuracy = x2.167
```

---

## 4. eqlwiki's published roll algorithm is refuted

```
x = U(0,1) x (Wrath + 5)     y = U(0,1) x M
A = (x + y + 10) / 2         R = (x - y) + A/2
D20 = clamp(floor(R x 20 / A), 0, 19) + 1
```

Simulated independently, twice, at 400,000 draws:

| | P(D20=1) | P(D20=10) | P(D20=20) |
|---|---|---|---|
| Wiki algorithm (Wrath 372, M 450) | **37.1%** | **2.2%** | **26.2%** |
| Wiki algorithm, six settings, second run | 16–31% | 1.3–2.5% | 31–59% |
| **Measured** | **2.16%** | **23.08%** | **5.99%** |

A U-shape where the data is centrally massed. L1 distance 1.13–1.39 out of 2. Its *mean*
lands near the measured mean, which is why a means-only check passes it. **Do not code
it.** `tools/wrath.py` reproduces this in one command.

Its structure is still used for `E[rx]` as a *calibrated* function — fitted to the
measured `k_nc = 0.976` on lanes where `B ≈ 0` — not as a generative model.

---

## 5. What +104 ATK is actually worth

`Hunter's Attack Power`: **26 ranks x 4 = +104 attack power, cost 0 AA, level 8.**
Full Ranger self-buff package = **+139** (Wrath 372 → 511).

| Case | Gain on the variable melee term |
|---|---|
| +104 alone, average targets | **+14.1%** |
| +139 package, average targets | +17.1% |
| +139 package, **raid boss** (Mt ≈ 320, matches measured Nagafen) | **+25.7%** |
| +139 package, hardest measured target | +32 to +41% |
| after dilution by the un-multiplied damage bonus | ~+15% on the melee lane |
| **on total DPS** | **+11 to +13% typical, +19% on a raid boss** |

`model2c.py` said **+2.6%**. So: **4–5x higher, and worth most exactly where min/maxers
measure their DPS.** ATK is convex in the level-50 band and has no cap
(Statistics page: *"Max (cap): None"*).

### The scarcity argument is stronger than the coefficient

- **0 of 909 catalogued weapons — and 0 of 2,263 items — carry an ATTACK stat.**
- The best attack-power **spell** in the entire 2,006-spell database is
  `Spirit of Bih'Li` (Shaman 36): **+15 Attack.** Every other "Attack" spell is Attack
  *Speed*.
- Beastlord's `Frenzy of Spirit` gives +250 — for 48 s on a 12-minute recast, i.e.
  **6.7% uptime = +17 effective.**
- Ranger's AA gives **+104, permanently, passively, for zero AA points.**

**Ranger is the only meaningful source of attack power in the game, at any price.**

---

## 6. Strikethrough, measured

`Unbounded Strikethrough` — Ranger, 3 ranks, **cost 0**, +10/20/30% at levels 12/30/50.
Across **21,122 of the player's own swing attempts** in 138 logs:

| Outcome | share |
|---|---|
| land | 57.10% |
| miss | 36.74% |
| dodge / parry / block | 2.67 / 2.31 / 0.98% |
| **riposte** | **0.00%** |

Active-defence avoidance **G = 5.97%** (an independent parse got 6.17–6.29%).
Strikethrough acts only on that bucket, never on the miss roll.

```
30% strikethrough  ->  +3.14% landed swings  ->  ~+2.4% total DPS
```

**Small, and it never was the reason for Ranger.**

---

## 7. Procs are per-minute, not per-swing

Settled by an exposure test: **ΔlogLik = +8.19** favouring active-time over swing-count;
cross-file CV 0.324 (PPM) vs 0.396 (per-swing); correlation of PPM with swing rate
**≈ −0.03**.

> **Consequence: haste and multi-attack buy zero extra procs.** Any model that scales
> procs with swing rate — including one of this workflow's own dossiers — is wrong.

**Spell and proc criticals are exactly 3.00x**, across ten independent spells:

| spell | normal | crit | ratio |
|---|---|---|---|
| Condemnation of Nife | 243 | 729 | **3.000** |
| Dismiss Undead | 144 | 432 | **3.000** |
| Lifebite | 42 | 126 | **3.000** |
| Puma Maw | 172 | 517 | 3.006 |
| Frost Storm | 741 | 2246 | 3.031 |

### The Exaltation proc stack

Four distinct Exaltation procs firing in one 466-second window, and **they stack**:

```
Your Serpentine Bracer (Exaltation) feels alive with power.      x96
Your Mane Attraction (Exaltation) flickers with a pale light.    x69
Your Djarn's Amethyst Ring (Exaltation) shimmers briefly.        x60
Your Idol of the Underking (Exaltation) feels alive with power.  x21
```

246 procs in 466 s. Procs run **9–55% of total damage** across the corpus (`jos438` =
55%). `model2c.py` carried a flat 9.5 DPS for all procs.

---

## 8. The anchor test — the residual dissolves, but not where §8 first said

> **This section was wrong twice and is now right for a checkable reason.** The first
> version said the chain was 1.25x short. The second said the shortfall was a unit error and
> applied a x1.22 best-60s conversion. **Both halves of that second answer were off, in
> opposite directions, and they cancelled.** The model was ~1.22x too *fast* (haste cap 175
> where it is 75), and the conversion is ~1.20x *larger* (best-30s, not best-60s). Two
> offsetting errors gave the right answer for the wrong reasons.

### Validation first — does the chain describe a real character?

`jos437-finishing-blow.log`, PAL/MNK/ENC at 50, both weapons identified from their damage
endpoints, provably in Offensive stance (93.6% even damage), 395 s engaged. **Nothing here
is fitted to its damage.**

| lane | predicted DPS | measured DPS | err |
|---|---|---|---|
| slash `Thelvorn +10` 40/26 | 152.3 | 148.7 | +2.4% |
| punch `Wu's Fist +10` 32/22 | 101.6 | 92.5 | +9.9% |
| bash | 36.7 | 38.5 | −4.8% |
| kick | 22.5 | 22.8 | −1.4% |
| smite (with the +417 rider) | 58.9 | 57.2 | **+1.0%** |
| strike | 32.9 | 21.3 | +54% ← the one bad lane |
| **total melee** | **404.9** | **381.0** | **+6.3%** |

~~Re-run from the repo's own `model4.py`, that character's melee comes out at **381 against a
measured 381.0**.~~ **Struck 29 Aug 2026. That sentence was typed beside a generated table and
did not survive being re-run.** The claim is true only at one of the model's two lane-rate
settings, the document named neither, and the table immediately above it says +6.3% — three
different numbers for one validation. Reproduce with `python3 validate_jos437.py`:

| lane rates | predicted melee | measured | err |
|---|---|---|---|
| `rates='max'` — abilities on cooldown | **471.0** | 381.0 | **+23.6%** |
| `rates='med'` — corpus median | **381.3** | 381.0 | **+0.1%** |
| the hand-built per-lane table above | 404.9 | 381.0 | +6.3% |

**And the +0.1% is worse than it looks, because it is cancellation, not agreement.** At
`med` the lanes miss individually by strike **−41.2%**, bash **−19.2%**, smite **−10.4%**,
kick **+8.7%**. A total that lands on the nose while its parts are 40% out is not a
validated model; it is four errors that happened to sum to zero on one character. **Any
build that shifts the lane mix — a trio without Smite, a Rogue instead of a Paladin —
loses the cancellation and keeps the errors.**

What genuinely holds up, and is not affected by any of the above, is the swing rate: both
predict from constants alone to within 3% (slash 1.082 vs 1.111 measured; punch 1.103 vs
1.132). **The chain's per-swing half is tight. Its ability-lane half is not, and the
headline number concealed that.**

### The haste correction — the single largest change in this revision

`HASTE_CAP = 175` was unsourced. Three independent lines kill it:

| | |
|---|---|
| ~~T2~~ **T5, struck** | eqlwiki `Haste_Guide` says 75% for levels 31–50 — but it is a **prose guide page carrying the classic delay-dividing formula**, which `eqlsource.com/learn/contamination.html` names as the one mechanic *known* to have changed. **Do not cite it.** See `SOURCING.md` §2. |
| **175 is unbuildable** | best worn haste in 2,604 items is 41%; best partner-castable at L≤50 is +60% (ENC 47); Monk Alacrity +10. Ceiling **111%**. |
| **direct measurement — the only citation that survives** | the identified `Thelvorn` at delay 26 swings **1.111 att/s** over 395 s. Against an unhasted `(10/26) × 1.520 = 0.585`, the **effective attack-speed multiplier is 1.900** — an attack-speed stat of 190 where the client panel reads 100 unhasted. `model3.py`'s 175 predicted 1.788 att/s, **61% too fast**; the value now in use is 2.7% low. |

### The three anchors

| | sustained engaged | ×1.46 → peak | reported | factor the anchor demands |
|---|---|---|---|---|
| **(a)** above-average martial, no ENC, median ability rates | **425** | 621 | 600+ | **×1.411** |
| **(b)** min/maxed, +10 BIS, full partner package, abilities on cooldown | **648** | 946 | 900–1000 | **×1.466** |
| **(c)** BIS, every open constant at the favourable end of its band | **848** | 1238 | 1200+ | **×1.416** |

The three anchors independently demand **×1.411 / ×1.466 / ×1.416 — a spread of 3.9%** —
against an independently measured **best-30s / engaged = 1.462**.

Three things make this a result rather than a lucky fit:

1. **The uniformity is the evidence.** A unit error is multiplicative and moves all three
   together. Under the *old* model the three anchors demanded ×0.98 / ×1.28 / ×1.30 — a
   **32% spread**, which is a *shape* error and cannot be a units artefact. Fixing the
   physics collapsed the spread to 3.9%; only then does a single conversion apply cleanly.
2. **The mechanism is sourced.** `eql-log-reader` — a shipped Legends parser sitting in this
   corpus — offers **`Rolling 10s` / `Rolling 30s`** readouts, documented as *"what's hitting
   right now — better reflects bursts."* A player quoting the highest number on a Rolling-30s
   display **is quoting best-30s.**
3. **Every correction moved the model AWAY from the anchors.** Haste 175→75 costs −22%; the
   missing `P(land)` on ability lanes −7%; multi-attack 1.589→1.520 −1.3%; the offhand slot
   fix −36 DPS. The only additions are the smite lane (+80, from a 658/658 adjacency count)
   and `SPELL_ATK` 15→61 (a wiki spell page). A fitter does not report a chain of changes
   that all cost ceiling and *then* close the gap with a factor measured beforehand.

> **What would falsify it:** the player saying that number was a fight average rather than a
> rolling peak. Under a fight-average reading the residual reopens to ~×1.6.
> **The check is one sentence: which meter, and was it the Rolling-30s field or the average?**

## 9. Does the corrected chain explain the community stacking Ranger?

The test set for this rebuild, stated before it ran. **Partly — and plainly, not fully.**

**What it does explain:**
- **Scarcity.** No item carries ATK, the best spell gives +15, Ranger gives +104 free.
  No substitute exists at any price. That alone justifies a universal pick.
- **It is worth most where min/maxers measure** — +19% of total DPS on a raid boss.
- Strikethrough and the RNG-locked `Conflagration` proc ride the same slot for free.

**What it does not explain:** +11–13% typical total DPS is real but not overwhelming, and
on measured evidence **a Rogue's Backstab lane is worth ~+150 DPS (+25%) in the same
slot — more than the Ranger.** `BER / ROG / SHM` out-damages `BER / RNG / SHM` on
sustained single-target numbers.

**The unpriced remainder is archery.** Ranger has `Weapon Mastery of the Scout`
(**+100% base archery damage**, 18 AA) and `Innate Called Shot` (**free double bow shot
on stationary targets**). The corpus holds **nine archery lines, all low-level.**

> Either archery is the missing piece, or the community's preference is driven by the
> raid-boss case plus scarcity rather than raw sustained DPS. **No coefficient was
> manufactured to make Ranger win.**

---

## 10. The Shaman — and why *this* player does not need one

`Spirit of the Puma` — Shaman 50, 212 mana, `Add Melee Proc: Puma Maw with 400% Rate
Mod`; `Puma Maw` = 154 hit points, prismatic.

| | value |
|---|---|
| proc rate | **8.0 ppm** (400% mod x ~2 ppm base) — *not* per-swing |
| damage, base / with focus | 154 / **172** |
| crit | **3.00x** at ~11.6% |
| **DPS, self** | **~25** |
| observed in one fight | 46.5 DPS (12.2 procs/min — above the modelled rate) |
| **DPS, group-wide** | **~127** from one cast across five melee |

**"Huge" is a group statement, not a per-character one.** And Shaman is not an ATK
class: its only ATK buff is +15, its `Harnessing of Spirit` gives +67 STR = +44.7 Wrath,
worth nothing once STR is capped. `Avatar` (+100 ATK) is **Shaman 60 — unreachable at
cap 50.**

> **The decision.** Puma targets a **group member** on a 1.5 s recast for ~3.5 mana/s.
> A dedicated support partner holds it on you indefinitely. The community puts Shaman in
> the DPS trio because most players have no such partner. **This player does.** Spending
> a class slot to self-provide a buff already covered is the clearest waste the corrected
> chain identifies.

---

## 11. Corrected constants — the full table

Everything a build model needs. `[REV]` = a reviewer's number adopted over the researcher's.

### Wrath and the roll

| Quantity | Value | Source |
|---|---|---|
| `Wrath` | `Offense + ((2·STR)−150)/3 + WornATK + SpellATK` | T2 |
| **Offense cap at 50** | **WAR 210 · MNK 230 · ROG 210 · RNG 210 · BER 210 · PAL/SHD/BRD/BST/SHM/CLR/DRU 200 · ENC/MAG/NEC/WIZ 140** | T2 ×2, 15/15 agree; validated 21/21 against skill plateaus in the logs |
| `STR_MOD` | 120 (STR capped at 255) | **ASSUMED — see §12 item 2** |
| **`SPELL_ATK`** | **61** (was 15) | `Share Form of the Great Wolf` DRU 45 = **+51 ATK**, + `Spiritual Brawn` +10 |
| `WORN_ATK` | **0** | 2 of 11,534 items carry ATK and both are era-gated; all 12 worn ATK effects are Kunark/Velious |
| `U` | `2·DMG + 1` | TM, two identified weapons |
| `B` | `HandMod · max(50,DMG) · (min(dly,50)/40) · 0.5`, **main hand only** | 0.69 (1H) / 1.10 (2H). **2H confirmed** by a client `Dmg Bon` line: `Skycleaver` prints 24, formula gives 24.06 (+0.3%). **1H rests on two client windows** (`Garduk`, `Arydryidriyorn`) solving to 0.680 and 0.686 — tier M. **One open conflict:** the only 1H `Dmg Bon` line on a wiki statblock, `Efreeti Standard`, prints 5 against a predicted 4.31 (−13.7%) and wants 0.75–0.80. Tier M beats T2 so 0.69 stands, but a 3-damage/10-delay weapon is exactly the row a classic import carries through unchanged. **One more client 1H screenshot settles it.** |
| `E_rx` base | **0.967 at Wrath 365** | TM, back-solved from an identified main hand |
| Order of operations | **stance multiplies BEFORE the crit, and scales `B` too** | non-crit damage is 100.00% even under Offensive (760/760 once killing blows are removed); crit damage only 42.2% |

### Stances — all eight, measured

The instrument was an accident of gear: a **bash lane floored at exactly 1 damage** turns
every stance into a direct multiplier readout.

| stance | damage | accuracy | swing/recharge | who |
|---|---|---|---|---|
| **offensive** | **×2.00** | ×1.081 *(band 1.00–1.21)* | ×1.00 | the 9 martial classes |
| balanced | ×1.00 | ×1.00 | ×1.00 | 9 martial |
| defensive | ×1.00 | **×0.95** | ×1.00 | WAR PAL SHD · incoming dmg/hit ×0.47 |
| **berserker** | **×1.00** | ×1.01 | **×1.90** | BER only |
| evasive | ×1.00 | ×1.00 | ×1.00 | BRD BST MNK RNG ROG · incoming **hit rate ×0.08** |
| **striker** | **not a flat multiplier** | ×1.00 | ×1.00 | BER MNK ROG WAR — **see §12 item 4** |
| ranged | ×1.00 | ×1.081 | ×1.00 | grants DA/TA to the bow; **no damage multiplier** |
| mage hunter | ×1.00 | ×0.97 | ×1.00 | BER PAL SHD |

**Offensive does not touch procs or spells** (Puma Maw 172→172). **Berserker never clearly
beats Offensive**: ×1.90 rate against ×2.00 damage × ×1.081 accuracy = ×2.16, but the
intervals overlap and two open unknowns push toward Berserker.

### Rates

| Quantity | Value | Note |
|---|---|---|
| **`HASTE_CAP`** | **75** (**85** with a Monk's `Unbound Alacrity`) | **was 175 — worth ×1.28.** Worn haste does **not** stack; only the highest item counts |
| `MH_CHAIN` | **1.520** `[REV]` | DA 56%, TA 14% conditional. CI [1.465, 1.569]; between-session sd 0.11 |
| `OH_CHAIN` | **1.4911** `[REV]` | **the offhand never triples** — P(≥3) 0.0017 vs 0.0406 main, a 24× gap |
| `DW_SUCCESS` | **0.88** | newly separable, because haste must be identical in both hands |
| Skill gates | Dual Wield BRD BST MNK RNG ROG WAR · Double Attack BER MNK PAL RNG ROG SHD WAR · **Triple Attack BER MNK RNG WAR + ROG** | Rogue was missing |
| Flurry / Rampage / riposte | +0.21% / 0 sustained / ~2% | all rounding errors |

### Lanes

| Quantity | Value |
|---|---|
| pre-stance lane means | kick **58.50** · bash **71.15** · strike **35.05** · smite **31.30** · frenzy 57.21 · backstab 178.69 |
| lane rates (median / on cooldown) | kick .32/.54 · bash .33/.54 · strike .27/.50 · smite .17/.31 · frenzy .47/.72 · backstab .29/.47 |
| **`SMITE_RIDER`** | **+417 flat**, not stance-doubled, **never crits**, fires 658/658 landed smites | 
| lane ownership | kick BST MNK RNG WAR · bash PAL SHD WAR · strike MNK · frenzy BER · backstab ROG · **smite PAL** |
| **Slam** | **remove — it is a racial (Barbarian/Ogre/Troll), not a class skill** |
| Frenzy | **2.918 attempts per activation**, P(3) > P(2) — a distinct multi-hit ability |

> **`SMITE_RIDER` is free money the old model missed entirely: ~80 DPS on every Paladin
> trio**, which is most of why Paladin now appears in nine of the top ten.

### Procs and non-melee

| Quantity | Value |
|---|---|
| **proc lanes** | **1 two-handed · 2 dual-wielding · +1 on a Ranger's bow.** Mechanistic, not just testimony: an Exaltation carries its **source item's slot restriction** onto the host, and 382/385 combat effects live on PRIMARY/SECONDARY/RANGE items — a proc in a bracer makes the bracer weapon-slot-only |
| sub-slot ladder | Slot1/2 Ornamentation (+0) · **Slot7 Focus (+1)** · Slot8 Click (+2) · Slot9 Worn (+3) · **Slot10 Proc (+4)** — 66/66 dump rows |
| `WEAPON_PROC_PPM` | **2.4** `[REV]` (band 2.1–2.7). The researcher's 4.02 counted AE hit lines as separate proc events |
| proc crit | 3.00× at 12.2% — **but not universal**: Earthquake 0/39, Smiting Strike 0/658, Scream 0/29 never crit |
| **spell rank** | **×1.00** `[REV]` — `Spirit of the Puma V` delivers Puma Maw at exactly its rank-I book value (n=93). The "ranks multiply 3–4×" claim is dead |
| **charm pet** | **66.8 DPS** `[REV]` (coefficient-free: pet damage inside the owner's engaged segments) |
| **charm caps** | ENC 51 *any* · **BRD 51 *any*, on an 18 s song** · NEC 51 *undead* · **DRU 49** *animal* · SHM 33 *animal* |
| **the player tanks, not the pet** | bosses aimed **1,318 melee attempts at the player and 59 at anything else** (4.3%); on Nagafen 186:1 |
| summoned pets | MAG 35 · BST 30 · ENC 31 · NEC 22 · SHD 9 — a charm pet is ~9× a summoned one |
| damage shield | 17.5 DPS per attacker, ~0.13 mana/s, **0 unless you are tanking** |

### Items

| | |
|---|---|
| upgrade | `v + max(tier, floor(v·0.1·tier))`; DMG doubles at +10, **delay never changes**. *A T2 page says weapons get +5%/tier — the tier-change ceiling test favours 10%. See §12 item 6.* |
| **slot legality** | main hand needs `PRIMARY` in `sl`; offhand needs `SECONDARY`. **232 of 444 melee weapons are PRIMARY-only** |
| **Aldryn and Thelvorn cannot be paired** | both are PRIMARY-only. The old #1 build was illegal |
| best pair in the game | **`Aldryn`/`Thelvorn` 40/26 main + `Wu's Fist of Mastery` 32/22 off — needs PAL + MNK.** Dual-wield beats every two-hander |
| not in EQL | `Rheumguls`, `Wu's Tranquil Fist`, `Beckon` are eqlwiki `{{Delete}}` |
| era | **Classic only.** One Kunark zone string in 138 logs, dated nine days pre-launch. Loading all 223 catalogue-missing in-era weapons changes the top trio by **+0.0 DPS** |

### Bugs this revision fixed in `model3.py`, in order of damage

`HASTE_CAP = 175` (×1.28) · ability lanes missing `P(land)` (×0.93) · **no smite lane at
all** (−80 DPS per Paladin trio) · `CLASSES` missing `ENC` (**105 of 560 trios never
evaluated, including the ground-truth character**) · offhand accepted PRIMARY-only weapons ·
`ONEH` missing `'Piercing'` (92 weapons) · `ALL_EXCEPT` inverted (80 weapons) · `{{Delete}}`
items still ranked · `spells.json` path unresolvable, so **every weapon proc silently
scored 0**.

---

## 11b. Four measurements that came back small, recorded so nobody re-runs them

- **Riposte is ~2% of damage and does not favour tanks.** It fires 730 times in the corpus
  against Flurry's 35, which looked significant. As a share of total damage it is **1.9%
  while tanking (n=5) and 2.2% while not (n=7)** — no meaningful difference, because a
  character taking hits is also missing swings of their own. Not worth modelling.

- **Pet DPS is not measurable at level 50 from this corpus.** Only three named allies attack
  the same targets as the logging character, two are group members rather than pets, and the
  one clear pet log runs at 8–12 DPS owner damage — a low-level fight. The project's earlier
  *"charm pets measure 0.774x owner damage"* should be treated as **unverified**, not as a
  measurement.

- **Berserker Stance has no damage multiplier.** Compared within the same file and verb so
  the weapon is held fixed, its max-endpoint ratio against Balanced is **1.000**, where
  Offensive is exactly **2.000** by the same method. Berserker is a pure speed and
  skill-recharge stance, and since stances are exclusive its 2x speed does **not** stack with
  Offensive's 2x damage — they are alternatives. *(n=2 file-verb pairs; small.)*

- **Berserker's Frenzy is a burst lane, not an ordinary autoskill.** Attempts sharing one
  timestamp average **2.89 for frenzy** against 1.48–1.71 for every other verb, with a max of
  seven. Modelling Frenzy as one hit per activation understates Berserker by roughly half.

---

## 12. What is still open, ranked by how much it moves the answer

| Unknown | Swing |
|---|---|
| **Do armour Proc Exaltation sockets fire on melee swings?** | **+100 to +260 DPS.** Closes the residual alone. A 60-second in-game test. |
| **Multi-attack (DA/TA) law** | ±1.5–2x on every weapon lane. The last constant still sourced from classic EQ, and the corpus measures 1.5–2x *above* it. |
| **Archery** | Decides the Ranger question. 9 lines in the corpus. |
| `maxExtraChance` (0.49 assumed) | ±10% on `E[rx]`. Atom mass hints it is higher. |
| Target mitigation `Mt` | ±25% on mean damage; **±2x on the Ranger's value** (+11% trash → +41% hardest). |
| Whether Striker/Berserker beat Offensive for skill-heavy builds | ±20% on autoskill-heavy trios. |
| Endurance sustain | Offensive charges 1:1 on bonus damage. 600+ may be a 30–120 s burn, not a 5-minute average. |
| Kunark/Velious weapons quarantined from the Sky-era catalogue | up to +40% if real BIS exceeds DMG 40 (1H). |
| STR cap (255 per wiki; a client panel reads INT 295) | decides whether STR gear converts to Wrath at all. |

---

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
