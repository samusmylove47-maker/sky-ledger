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

## 5. RE-ATTRIBUTED — and the verdict moves against what I first said

**The owner supplied two facts the log cannot infer, and both change the answer.**
`Heart harpie` is Avenrae's **charm pet** and the primary output of the PAL/ENC/BRD
build under test — corroborated in the log by `heart harpie has been charmed` ×47.
`Puma Maw` is a proc from a **Shaman buff cast by Shara's trio**, so by this
project's standing rule that classes are not credited for buffs, it belongs to
neither build's kit. `attribute.py` reruns everything on that basis.

| build | kit only |
|---|---|
| **Avenrae PAL/ENC/BRD** — own lines 1,125,536 + charm pet on enemies 2,381,463 | **3,506,999** |
| **Shara SHM/BRD/CLR** — own lines | **2,392,636** |
| buff-granted (Puma Maw), credited to neither | 187,369 |
| pet damage that landed on *us* across charm breaks, excluded | 17,615 |

**Avenrae's build out-totals Shara's by 1.47×.** My earlier headline — that the
support Bard was the largest source of damage in the log — **was an artefact of
reading the log's actor names instead of the builds.** Withdrawn.

### What survives, and it is the more interesting result

| | Shara | Avenrae (incl. pet) |
|---|---|---|
| engagements ≥ 20 s | 25 | 44 |
| ~~engaged seconds~~ | *withheld — see below* | *withheld* |
| **aggregate DPS** | **1,372.9** | **774.4** |
| median engagement DPS | 1,163.7 | 794.4 |
| best engagement | 8,944.7 over 26 s | 2,416.9 over 110 s |

**Shara wins the rate by 1.77×. Avenrae wins the total by 1.47×, by being engaged
five times as long.** That is not a tie dressed up — it is a structural difference
and it is the finding:

> **DDD is mana-limited burst. The charm pet is a rate.** The song produces more
> damage per second of combat and can only be run for a fraction of the time; the
> pet produces less per second and never stops. **One build was engaged several
> times longer than the other, and that is why it wins on total while losing on
> rate.**
>
> **The per-character engaged seconds are withheld, and the ratio between them is
> too.** Ruled by the Director 30 Aug 2026: *"Never publish a comparison of
> engaged time between characters."* Two named characters compared on how hard
> they played is a privacy problem as well as a voice one, and this file published
> exactly that until it was struck. **The finding survives whole in the form that
> matters** — engaged time dominates, and a tool built on this must be willing to
> tell a reader their problem is not their gear. The figures remain in the parse
> for modelling; they do not appear in anything a person reads.

### The charm pet, and a constant of mine that is an order of magnitude wrong

10,281 hits, 2,381,463 damage, 3,237 s engaged: **729.8 DPS aggregate, 763.6
median engagement, best 1,004.7.**

**`model4.py` carries `CHARM_PET = 66.8`. Measured here it is 10.9× that.** That
constant was established from a much lower-geared window and I propagated it into
every ranking that scores a charmer. **List 2 — tank + charm pet + damage — is
built on a pet worth a tenth of the real one and cannot stand.** Not silently
patched: 66.8 was measured too, and I want to know which conditions separate them
before I move it. The 47 charm events and the 17,615 damage taken across breaks
are the cost side that no single number captures.

## 6. The verdict on "Bard is THE AoE class"

**Half confirmed, and the half that fails is the half I got wrong first time.**

**Confirmed:** DDD is the highest-rate damage in this log by a wide margin, and it
is nearly rate-independent of gear. Shara's 1,372.9 DPS comes 99.6% from a song,
0.2% from melee, on a build with no damage itemisation at all. Nothing else here
approaches its per-second output, and its best 30 s window is 7,752 DPS.

**Not confirmed:** *"everything else needs to be built to fit around it."* The
build that produced the most damage in this log is PAL/ENC/BRD, and the largest
single component of it is **the charm pet, not the song** — 2,381,463 against
672,456 from its own DDD. A build that fits around DDD and drops the pet would
have lost this day badly.

**What the data actually supports** is narrower and more useful than either
version: **DDD is the best burst and AE lane in the game, the charm pet is the
best sustained lane, and the winning build ran both.** The Bard slot earns its
place in nearly every trio — my own ranking already put it in all eleven of the
top AOE trios — but it earns it as one of two engines, not as the thing the
others orbit.

**Three limits, unchanged:** there is no Bard-less counterfactual in this log;
it is one player-pair, one zone, one day; and every figure is AE, so nothing here
speaks to single-target raid damage.