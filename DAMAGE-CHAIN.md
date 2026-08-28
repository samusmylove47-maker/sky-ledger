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

## 8. The anchor test — with its residual stated

Best build the chain can construct: **BER / RNG / SHM**, dual-wield 40/26 + 24/21, haste
capped, Offensive Stance, Wrath 541. Swing rates are **measured corpus maxima**, not
derived.

| Anchor | Build | melee+proc | +DoT lane | Residual |
|---|---|---|---|---|
| **600+** above-average, no ENC | no Ranger/ENC, Wrath 372 | 500 | **610** | **hit** |
| **900–1000** min/maxed | BER/RNG/SHM | 609 | **743** | **−20 to −26%** |
| **1200+** BIS | + Backstab lane (ROG) | 759 | **926** | **−23%** |

**The chain reproduces the 600 anchor and lands ~1.25x short of the top two.** The old
model was 4–8x low; this is ~1.25x low, and nothing was tuned to get there.

### The one test that would close it — ANSWERED, AND THE ANSWER IS NO

**29 August 2026, from the player.** Proc Exaltations fire **only from the primary and
secondary weapon slots**, plus the ranged slot for a Ranger. Armour sockets do not proc.
So the ceiling is:

| Setup | Proc slots that actually fire |
|---|---|
| Two-hander | **1** |
| Dual wield | **2** |
| Ranger with a bow equipped | **+1** (ranged slot) |

**This kills the leading explanation for the residual.** The "armour proc sockets go from
4 lanes to 10-20, worth +100 to +260 DPS" hypothesis is dead. The gap between the chain's
610 / 743 / 926 and the observed 600 / 900-1000 / 1200+ has to come from somewhere else.

What is left, in order of remaining size:

1. **The multi-attack (DA/TA) law** — still the only constant in the chain sourced from
   classic EverQuest, and the corpus measures swing rates **1.5-2x above** what it
   predicts. This is now the largest unexplained term.
2. **Berserker Stance doubling combat-skill recharge**, which would double the autoskill
   lanes (~156 DPS on a lane-heavy build).
3. **Striker Stance** (3x weapon-skill / 5x non-weapon-skill), never measured.
4. **Burst vs sustained framing** — Offensive charges endurance 1:1 on bonus damage, so
   the top anchors may be a 30-120 s burn rather than a five-minute average.
5. Kunark/Velious weapons quarantined from the Sky-era catalogue.

> **An unresolved tension, recorded rather than smoothed over.** The corpus shows four
> distinct Exaltation proc messages in one 466-second window, and **two of them are not
> weapons**:
>
> ```
> Your Serpentine Bracer (Exaltation) feels alive with power.      x96   <- WRIST
> Your Djarn's Amethyst Ring (Exaltation) shimmers briefly.        x60   <- FINGERS
> Your Mane Attraction (Exaltation) flickers with a pale light.    x69
> Your Idol of the Underking (Exaltation) feels alive with power.  x21   <- RANGE
> ```
>
> The inventory dump confirms `Fingers-Slot7 Djarn's Amethyst Ring (Exaltation)` — a ring
> Exaltation socketed into a ring, firing 60 times in eight minutes. Either these are
> **worn/click effects rather than damage procs** (most likely), or the slot rule is
> narrower than the messages suggest. **Resolving which decides whether the 37.3% non-melee
> share of a real 426-DPS parse is reachable at all**, so it is the first thing to settle.

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

## 11. Corrected constants

| Quantity | Old | Corrected | Evidence |
|---|---|---|---|
| Base-roll max | `0.45 x DMG` | **`U = 2 x DMG + 1`** | two identified weapons, −2.1% / −2.5% |
| `maxExtra` | — | **2.25** | measured 2.230 / 2.282; wiki says 2.10 |
| **Offensive Stance** | absent | **x2.00 damage, x1.084 land** | 98.8% even damage, n=1,069 |
| Melee crit | 1.664x @ 13.2% | **`1.7 x (max(D,DMG)+5)` @ 12.72%** | 23,013 swings |
| **Spell/proc crit** | absent | **3.00x** | ten spells |
| Land rate | 0.62 / 0.56 | **0.5765** base, **0.6231** Offensive | n=23,013 / 2,258 |
| Avoidance G | 5.98% | **5.97–6.29%** | three independent parses |
| Wrath skill term | weapon skill | **Offense** | Statistics page |
| Offense caps | — | WAR/MNK/ROG/**RNG 252** · PAL/SHD 225 · BRD 215 · SHM/CLR/DRU 200 · casters 140 | Skill_Offense |
| Proc model | per-swing, 9.5 DPS flat | **per-minute; 9–55% of total damage** | ΔlogLik +8.19 |
| HandMod | 0.8 (1H) | **0.69 (1H) / 1.10 (2H)** | two client windows |
| ATK cap | assumed | **none** | Statistics page |

### Damage tags that are not part of the normal roll

`(Riposte)` 411 · `(Strikethrough)` 23 · `(Flurry)` 19 · `(Rampage)` 6 are **extra
swings** — pool with normals. `(Slay Undead)` 88 and `(Finishing Blow)` 51 are separate
multiplicative lanes and contaminate a roll fit:

```
You slash a dar ghoul knight for 1047 points of damage. (Slay Undead)
```

off a weapon whose normal maximum was 99. Paladin's `Slay Undead` is 2.25/2.35/2.4% for
445/850/1250% damage — expected **+30% against undead**, i.e. most of Fear, Hate and Guk.
Content-dependent; its own term.

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
