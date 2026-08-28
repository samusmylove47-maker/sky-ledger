# THE DAMAGE CHAIN, REBUILT FROM MEASUREMENT

**Established:** 28 August 2026
**Method:** two independent parses of the committed Legends log corpus (20,268 and
21,122 self-swings), plus a third reconstruction from eqlwiki's published mechanics —
then all three checked against each other. Where they disagreed, the logs won.

This replaces the damage model in `model.py` and `model2c.py`, both of which are
**structurally wrong** and produce numbers 4–8x too low. It exists because the player
reported real in-game DPS of 600+ / 900–1000 / 1200+ against a model that topped out
at 166.5.

Same standard as `CLIENT-TRUTH.md`: *a number without its source is a number that can
lie.*

---

## 1. Ground truth first — what real characters actually do

Before any formula. These are measured from committed client logs of a real level-50
character (`Primitive`, PAL/MNK/ENC, mid-tier gear, **not** best-in-slot), counting only
that character's own damage.

| Fight | Sustained | Best window |
|---|---|---|
| `jos437-finishing-blow` | **426.5 DPS** over 466 s | **502 DPS** |
| `w70-dracoliche` | 325.9 over 177 s | — |
| `p4-pet-buff` | 310.8 over 355 s | — |
| `e2e-timeline` | 274.4 over 130 s | — |
| typical band | 130–330 | — |

An independent pass over the same corpus, segmenting on 6-second gaps, put the same top
fight at **483 DPS engaged / 582 over the best 60 s / 678 over the best 30 s**.

**The player's reported figures are corroborated, not merely asserted.** A mid-tier
character in a public log corpus already sustains 426. 600+ for an above-average build
and 900–1000 min/maxed sit exactly where the corpus points.

**`model2c.py`'s 166.5 was wrong by 2.6x against data already in the repository.** That
should have been caught here, not by the player noticing in-game.

---

## 2. The roll — measured, not derived

Per landed swing:

```
FinalDamage = W x (D20 / 10) + B
```

- **`W`** — the weapon's *effective damage unit*. Not the item's DMG stat; `W` already
  absorbs level and skill scaling.
- **`D20`** — an integer 1..20, distributed as below.
- **`B`** — the main-hand damage bonus. Added **after** the roll, un-mitigated,
  un-critted, **main hand only**. Confirmed: offhand and skill lanes measure `B = 0`.

### The D20 distribution (n = 3,609 clean landed non-crit hits, 25 groups)

| D20 | P | | D20 | P |
|---|---|---|---|---|
| 1 | 2.16% | | 11–19 | ~2–3% each |
| 2–9 | ~5–7% each | | **20** | **5.99%** ← atom, damage = `2W + B` |
| **10** | **23.08%** ← atom, damage = `W + B` | | | |

`E[D20] = 9.332`. Near-uniform over 1–9, a hard spike at 10, a thin shelf over 11–19, a
second spike at 20. **Not uniform, and not U-shaped.**

### Closed form

```
E[damage | landed, non-crit] = 0.9332 W + B
E[damage | landed, crit]     = 1.5864 W + B          (crit = 1.70x on the rolled part only)
E[damage | landed]           = 1.0176 W + B          (12.93% crit rate)
E[damage per swing ATTEMPT]  = 0.5919 W + 0.5817 B   (58.17% land rate)
```

### Recovering `W` and `B` from any log

Because both atoms are **target-independent**, they read straight off a histogram:

```
MAX = observed maximum non-crit hit
mid = modal value below 0.85 x MAX          (the D20 = 10 atom)
W = MAX - mid            B = 2 x mid - MAX
```

Gate: `mid/MAX` must fall in 0.44–0.56 (observed median **0.490**, exactly the 1/2 the
structure demands). This was cross-checked by hand on three fixtures and agrees:
`w44` slash MAX 155 → W 75, B 5; `w44` pierce MAX 64 → W 34, B −4 (offhand, no bonus);
`jos437` slash MAX 384 → W 196.

Recovered `W` is a stable weapon constant — **75 for slash across six independent
fixtures, 34 for pierce across five.**

### The quantisation is directly visible

Monk special lanes against Lord Nagafen resolve to an exact lattice
`{floor(D x k/10), k = 1..20}` with `D = 20`: observed damages are literally
2, 4, 6, … 40. **93.3% of `claw` and 90.9% of `strike` values land exactly on it.**
The "twenty damage intervals" are in the log, not an inference.

---

## 3. eqlwiki's published roll algorithm is refuted by the data

The wiki gives an offense-vs-mitigation mechanism:

```
x = U(0,1) x (Wrath + 5)          y = U(0,1) x M
A = (x + y + 10) / 2              R = (x - y) + A/2
D20 = clamp(floor(R x 20 / A), 0, 19) + 1
```

Which reduces to `floor(10 + 20(x-y)/A)`.

**Simulated independently, twice, at 400,000 draws each — it produces a U-shaped
distribution piled at both ends:**

| | P(D20=1) | P(D20=10) | P(D20=20) |
|---|---|---|---|
| Wiki algorithm (Wrath 372, M 450) | **37.1%** | **2.2%** | **26.2%** |
| Wiki algorithm (six settings, second run) | 16–31% | 1.3–2.5% | 31–59% |
| **Measured in real logs** | **2.16%** | **23.08%** | **5.99%** |

L1 distance 1.13–1.39 out of a possible 2. **This is not a near miss; it is the
opposite shape.** The wiki labels it the "inherited model" and its own text says the
`Wrath < 115` / `maxExtra` branch "remain[s] unverified on EverQuest Legends
specifically."

**Do not code the wiki algorithm.** Its *mean* happens to land near the measured mean
(9.21 vs 9.332 at Wrath 372), which is why an analysis that only checks means will pass
it. Its shape is wrong, and any sensitivity derived from it — including the ATK
sensitivity in §4 — inherits that error.

---

## 4. What +104 ATK is actually worth

The Ranger's `Hunter's Attack Power` is **26 ranks x 4 = +104 attack power, cost 0 AA,
level 8.** Confirmed verbatim from the AA catalogue.

`model2c.py` priced it at **+2.6%**. Two better estimates:

**(a) From the wiki mechanism: +26–30%.** Monte-Carlo over the full chain. I
reimplemented this from scratch and reproduced the agent's table to three decimals
(Wrath 150 → 0.478, 400 → 1.314, 800 → 2.112 — all matching). **But this rests on the
algorithm §3 just refuted, so it is an upper bound, not an answer.**

**(b) From measured target mitigation: +10–24%.** With the character and weapon fixed,
`E[D20]` measured across twelve targets spans **6.51** (Lord Nagafen) to **11.84**
(`Magi P'tasa`) — a **1.82x** total spread. If the mechanism depends on `Wrath / M`,
sensitivity to Wrath equals sensitivity to `1/M`, so +104 ATK (Wrath 372 → 476, +28%)
buys:

| assumed AC spread across those targets | gain on the variable melee term | on total DPS |
|---|---|---|
| 2x | +23.7% | +14.9% |
| 3x | +14.4% | +9.0% |
| 4x | +11.2% | +7.0% |
| 6x | +8.6% | +5.4% |

A rat-to-Nagafen range is very unlikely to be under 2x or over 6x.

> **Verdict: +104 ATK is worth +10% to +24% on the variable melee term, and +6% to
> +15% on total DPS. Central estimate ~+10% total.** That is **4x** what the old model
> said, not the 10–14x the wiki mechanism implies. Both the direction and the
> "Ranger is the best third slot" conclusion survive; the magnitude does not.

**ATK is convex where level-50 characters sit**, and worth *more* against
high-mitigation targets — which is where min/maxers measure their DPS. That is
consistent with eqlwiki's own Ranger page: Ranger "shines brightest when fighting mobs
with high mitigation."

### The scarcity argument is stronger than the coefficient

- **0 of 2,263 catalogued items carry an ATTACK stat.**
- The best attack-power *spell* in the entire 2,006-spell database is
  `Spirit of Bih'Li` (Shaman 36): **+15 Attack.** Nothing else comes close; every other
  "Attack" spell is Attack *Speed*.
- The Beastlord's `Frenzy of Spirit` gives +250 — for 48 s on a 12-minute recast,
  i.e. **6.7% uptime = +17 effective.**
- The Ranger's AA gives **+104, permanently, for free.**

**Ranger is the only meaningful source of attack power in the game.** That structural
fact justifies the community's preference regardless of whether the coefficient is 10%
or 30%.

---

## 5. Strikethrough, measured

`Unbounded Strikethrough` — Ranger, 3 ranks, **cost 0**, +10/20/30% at levels 12/30/50.

Across **21,122 of the player's own swing attempts** in 138 logs:

| Outcome | n | share |
|---|---|---|
| land | 12,060 | 57.10% |
| miss | 7,761 | 36.74% |
| dodge | 565 | 2.67% |
| parry | 488 | 2.31% |
| block | 208 | 0.98% |
| **riposte** | **0** | **0.00%** |
| absorb | 40 | 0.19% |

Active-defence avoidance **G = 5.97%**. Strikethrough acts only on that bucket, never on
the 36.74% miss roll.

```
30% strikethrough  ->  +3.14% landed swings  ->  ~+2% total DPS
```

**This is a small effect and always was.** It is not why Ranger is stacked; ATK is.

---

## 6. Where the missing 4–8x actually went

All four factors measured, none fitted to the target:

| Factor | Old model | Measured | Ratio |
|---|---|---|---|
| **The roll** | `0.45 x DMG + B` | `0.9332 x W + B`, plus 12.93% crits at 1.70x | **x2.26** |
| **Lane count** | ~2 lanes | **5–7 co-firing lanes, 3.15–5.78 swings/s** | **x1.75** |
| **Procs** | flat 9.5 DPS | **37.3% of a 426-DPS total = 159 DPS** | **x1.30** |
| **ATK / Wrath** | +2.6% | +10–24% on melee | x1.09 |
| | | | **x5.60** |

`166.5 x 5.60 = 933 DPS` — inside the reported 900–1000 min/maxed band, and above the
426 measured for a mid-tier character. **The decomposition closes.**

**The largest error was not the Ranger.** It was the roll (x2.26) and the number of
simultaneous attack lanes (x1.75). ATK is the *smallest* of the four corrections. The
player's diagnosis — "some part of the damage formula is missing" — was right; the
specific attribution to Ranger's ATK was only a fifth of it.

### The proc stack was the single most under-modelled channel

Four distinct **Exaltation** procs firing in one 466-second window:

```
Your Serpentine Bracer (Exaltation) feels alive with power.      x96
Your Mane Attraction (Exaltation) flickers with a pale light.    x69
Your Djarn's Amethyst Ring (Exaltation) shimmers briefly.        x60
Your Idol of the Underking (Exaltation) feels alive with power.  x21
```

**246 procs in 466 s, and they stack.** With five Exaltation sub-slots on the primary
and five on the secondary (`EQUIPMENT-TRUTH.md` §3), a flat 9.5 DPS for "all procs" was
never going to be close.

---

## 7. The Shaman, and why *this* player probably does not need one

`Spirit of the Puma` — **Shaman 50**, Proc Buff, 212 mana, 60 s duration, 1.5 s recast,
target **Group Member or Self**: *"Add Melee Proc: Puma Maw with 400% Rate Mod."*
`Puma Maw` is `Decrease Hit Points by 154`, prismatic.

Measured in the logs:

| | value | source |
|---|---|---|
| proc rate | **~9–10.5% of all swings** | 164 procs vs 1,749 swings, two fights |
| damage, base | 154 | spell data + a groupmate's procs |
| damage, this player | **172** | every one of 46 procs, exactly — spell-damage focus |
| **crit multiplier** | **exactly 3.00x** (517 / 172) | two spells, two logs, no variance |
| contribution | **46.5 DPS = 14.3% of total** in the dracoliche fight | |

For comparison, the Beastlord's whole `Spirit of ...` line is **150%** rate mod for
62–102 damage. Puma is 2.67x the rate mod and 1.5x the damage — but 60 seconds instead
of 44 minutes.

> **The decision-relevant part.** Puma targets a **group member**, lasts 60 s, and
> recasts in 1.5 s. A dedicated support partner can hold it on you indefinitely for
> 3.5 mana/s. The community stacks Shaman *in the DPS trio* because most players have
> no such partner. **This player does.** Spending a class slot on Shaman to
> self-provide a buff the partner can already cast is the one clear waste the corrected
> chain identifies.

---

## 8. Corrected constants

| Quantity | Old | Corrected | Evidence |
|---|---|---|---|
| Per-swing damage | `0.45 x DMG + B` | `0.9332 x W + B` | 3,609 clean hits |
| Melee crit multiplier | 1.664x | **1.70x on the rolled part only** | five weapons, crit maxima 1.694–1.727 |
| Melee crit rate | 13.2% | **12.93%**, uniform across every lane | 20,268 swings |
| **Spell/proc crit multiplier** | *(absent)* | **3.00x** | Puma Maw 517/172, Condemnation 729/243 |
| Land rate | 0.62 / 0.56 | **0.5817** | 20,268 swings |
| Avoidance G | 5.98% | **5.97%** | 21,122 swings, independent parse |
| Wrath skill term | weapon skill | **Offense** | Statistics page disambiguates |
| Offense caps | — | WAR/MNK/ROG/**RNG 252** · PAL/SHD 225 · BRD 215 · SHM/CLR/DRU 200 · casters 140 | Skill_Offense |
| Swing lanes | ~2 | **5–7 co-firing, 3.15–5.78 swings/s** | lane-level parse |
| Proc DPS | 9.5 flat | **~159 (37.3% of total)** | 246 Exaltation procs / 466 s |
| ATK cap | assumed | **none** ("Max (cap): None") | Statistics page |

### Damage tags that are *not* part of the normal roll

`(Riposte)` 411 · `(Strikethrough)` 23 · `(Flurry)` 19 · `(Rampage)` 6 are **extra
swings** — pool them with normals. `(Slay Undead)` 88 and `(Finishing Blow)` 51 are
separate multiplicative lanes and will contaminate a roll fit if included:

```
You slash a dar ghoul knight for 1047 points of damage. (Slay Undead)
```

off a weapon whose normal maximum was 99. Paladin's `Slay Undead` is
2.25/2.35/2.4% for 445/850/1250% damage — an expected **+30% against undead**, which is
most of Fear, Hate and Guk. It is content-dependent and belongs in its own term.

---

## 9. Does the corrected chain explain the community's Ranger preference?

The test set for this rebuild, stated before it ran. Answered plainly:

**Partly — and less than the framing implied.**

- ATK moves from +2.6% to **+6–15% of total DPS**. Real, and the largest single
  third-slot gain measured. But it is **4x** the old value, not 14x.
- Strikethrough is **~+2% of total DPS**, measured over 21,122 swings. It is not the
  reason and never was.
- Ranger shares the top Offense cap (252) with WAR, MNK and ROG, so that is not a
  differentiator against those three.
- **The scarcity argument is the strong one.** No item carries ATK, the best spell in
  the game gives +15, and Ranger gives +104 free and permanent. There is no substitute
  at any price. That alone explains a universal pick.

**What is still unmeasured, and could be the real reason:** archery. Ranger has
`Weapon Mastery of the Scout` (**+100% base damage on archery**, 18 AA) and
`Innate Called Shot` (**free double bow shot on stationary targets**). The corpus
contains **9 archery lines, all low-level.** The chain cannot price this channel, and
it is the obvious candidate for the remaining gap between "+10% total DPS" and "every
elite build takes it."

**So: the rebuild confirms Ranger as the best third slot for a martial trio, but it
does not, on measured evidence, reproduce a preference as lopsided as the community's.
The unmeasured archery channel is the leading explanation, and saying otherwise would
be fitting the story to the conclusion.**

---

## 10. What is still open

- **Archery.** The largest unpriced channel, and the one that decides the Ranger
  question. 9 lines in the corpus; needs a real Ranger log.
- **The true D20 generator.** The empirical table is solid; the *mechanism* producing it
  is not known, and the published one is refuted. Without it, ATK sensitivity is a
  bracket (§4b), not a number.
- **`W` from item stats.** `W` is measurable per weapon from a log, but the map from a
  catalogue `DMG` value to `W` is unknown. `W = 2 x DMG + 1` fits `W = 75` (DMG 37) and
  fails every even `W` (34, 42, 80, 90, 112, 118, 154, 176, 180, 196).
- **Exaltation proc rates and damage per source.** Known to stack and to be ~37% of
  total; not decomposed per sub-slot.
- **STR cap.** eqlwiki says 255; a client panel reads INT 295. See
  `EQUIPMENT-TRUTH.md` §1.
- **Whether worn haste stacks across positions**, which decides what the two ANY slots
  are worth.

---

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
