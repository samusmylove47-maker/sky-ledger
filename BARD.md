# What a Bard actually does — measured over one full day

**Source:** `corpus/amp/eqlog_Shara_rivervale_20260829_full.txt`, 181,345 lines,
13.5 MB, 29 August 2026, Plane of Sky. **Reproduce with `python3 bard.py`.**
Every figure below is read out of the log at run time.

**The character:** Shara, a Bard trio the owner describes as *"completely focused
on being a supporter and healer"* — spell-crit and Bard AAs bought, **not
itemised, exalted or geared for damage.** Avenrae, the owner's damage-built
character, is in the same log singing the same song four ranks lower.

---

## 1. The headline

**Shara is the single largest source of damage in the log**, above a pet that
swings 10,360 times.

| actor | total damage | spell | melee | hits |
|---|---|---|---|---|
| **Shara** (support Bard) | **2,393,541** | 2,388,509 | 5,032 | 996 |
| Heart harpie (charmed pet) | 2,382,447 | 0 | 2,382,447 | 10,360 |
| Avenrae (damage build) | 1,214,399 | 928,953 | 285,446 | 4,548 |

**99.7% of Shara's damage is one song.** Denon's Desperate Dirge accounts for
2,384,545 of 2,393,541. Melee is **0.2%**.

> **That is the answer to "even without itemising for damage".** Her output is
> not coming from items. It is a song, scaled by rank and AA, and weapon gear is
> irrelevant to it. A support build tops this log *because there is nothing for a
> damage build to add.*

## 2. DPS

Engagements are runs of damage with no gap over 15 s; only those lasting 20 s or
more are counted. Killing blows are included here (they are real damage dealt)
and excluded from every per-hit figure (they truncate — see `amp.py`).

| | Shara | Avenrae | ratio |
|---|---|---|---|
| engagements ≥ 20 s | 25 | 47 | |
| engaged seconds | 861 | 3,353 | |
| **aggregate DPS over engaged time** | **1,372.9** | **321.8** | **4.27×** |
| median engagement DPS | 1,163.7 | 202.0 | 5.76× |
| best engagement | 8,944.7 over 26 s | 3,755.3 over 27 s | 2.38× |

**Peak windows for Shara, in the conventions a meter reports:**

| window | damage | DPS |
|---|---|---|
| best 10 s | 146,562 | **14,656** |
| best 30 s | 232,562 | **7,752** |
| best 60 s | 236,410 | 3,940 |

The achieved DDD cadence is a **median 3 s** between landings (n=207 gaps under
30 s) — mana, movement and resists included.

## 3. Three mechanics this log settles

**Crit is exactly ×3.000, on two characters independently.** Shara: median crit
7,978 against median non-crit 2,659 = **3.000** (n=44). Avenrae: 5,990 against
1,996 = **3.001** (n=21). Crit rate **7.0%** and **7.7%**.

**15.2% of DDD casts are resisted** — 150 resists against 836 landings. A damage
total never shows this, and no model of mine carried it.

**A single cast lands TWICE on the same target.** Checked on uniquely-named
bosses, where there is only ever one of them: **84 of 103** landings on a
surviving target are two hits in the same second with identical values —
`Keeper of Souls [3177, 3177]`, `Bazzt Zzzt [2002, 2002]`. So **damage to one
target per cast is ~5,318, not 2,659.**

**What causes the second hit is NOT established, and I will not guess.**
Amplification was up for every boss landing in this log, so there is no off-state
to compare and that table is not a test. The one candidate testable here — the
target dying to the first hit — explains part of it and not most: single-hit rate
is 35.7% when the target died (n=14) against 18.4% when it survived (n=103).
Nineteen single hits on surviving targets remain unexplained.

## 4. What this does to my own model — two corrections and one thing that holds

- **`DDD_REPORTED = 3000` holds.** Measured median non-crit at rank IX is
  **2,659**, within 13% of the figure `aoe.py` carries from a guide.
- **The per-cast damage in my model is HALF what it should be**, if the double
  hit is general. Not applied yet: it is 84-of-103 on bosses and its cause is
  unidentified, and a 2× that turns out to be Amplification-gated would be
  wrong everywhere Amplification is down.
- **`DDD_CAP = 8` is neither confirmed nor refuted.** Max landings in one second
  is 10, but landings are not targets — 10 is consistent with 5 targets × 2 hits.
  Max *distinct target names* in one landing is 5, and generic names collapse
  ("a rock golem" ×3 reads as one), so that is a floor. **The test is one cast
  into a pull of 12+ distinctly-named mobs, counting names.**
- **Rank is worth less than I assumed.** Rank IX median 2,659 against rank V
  1,996 = **×1.332 over four ranks**, ~×1.074 per rank if uniform. Different
  characters, AAs and focus items, so this **bounds** the rank step rather than
  isolating it.

## 5. The verdict on "Bard is THE AoE class"

**Confirmed on this evidence, and the data says something stronger and more
specific than the claim.**

The finding is not *"Bard out-damages other classes"*. Both characters in this
log run DDD, and the one running it at a higher rank, on a support build with no
damage gear, produces **4.27× the damage per engaged second** of the one built
for damage. DDD is 99.7% of the winner's output and 55.4% of the loser's.

> **So it is not "build around the Bard". It is: DDD is the damage, and a
> character's output is very close to how much DDD it is running.** Avenrae's
> melee, Smiting Strike and Puma Maw together — the entire damage build — come
> to 542,000 against Shara's 2,384,545 from the song alone.

**Three limits, stated because they matter:**

1. **There is no counterfactual here.** Both characters run DDD, so this log
   cannot say what a Bard-less trio would do in the same content. It measures the
   song's dominance, not the alternative's weakness.
2. **One player-pair, one zone, one day.** Plane of Sky, level 50. It is a large
   sample of casts and a sample of one group.
3. **The claim it supports is about AE, and every figure here is AE.** Nothing in
   this log speaks to single-target raid damage, where a cast that lands twice on
   one boss is a different and much narrower advantage.
