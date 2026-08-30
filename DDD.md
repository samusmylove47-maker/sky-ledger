# DENON'S DESPERATE DIRGE — the mechanics, verified

**Established:** 29 August 2026
**Prompted by:** the player's screenshot of DDD at rank 0 vs rank X, and the instruction to
research this properly rather than trust eqlwiki prose.

Sourcing follows `SOURCING.md`: eqlwiki **structured fields** are tier 2, eqlwiki **prose**
is tier 5. The findings below come from the spell data's own `effects` and `description`
fields and from measured logs — not from any guide page.

---

## 1. The error that mattered most: I was reading the wrong field

I previously wrote *"no AE spell in the game states a target cap, so damage scales linearly
with the pull, unbounded."* **That is false.** Target caps are published in the
**`description`** field, and my spell database carries no description field at all — so my
scan of `effects` found nothing and I drew exactly the wrong conclusion.

Re-fetched from the wiki pages, **10 of 34 AE spells at level ≤ 50 state a cap**:

| Cap | Spells |
|---|---|
| **4** | Lightning Blast · Column of Lightning · Gravity Flux · Lightning Strike · Pillar of Fire · Avalanche · Pogonip |
| **8** | **Denon's Desperate Dirge** |
| 25 | Earthquake (246 dmg) · Tremor (122 dmg) |
| unstated | Frost Storm · Supernova · Upheaval · the Rain/Storm family · Word Divine |

**`Lightning Blast` — the spell my entire previous AOE top-12 was built on — is capped at 4
targets *and* is OUTDOORS ONLY.** Its own description says so: *"2.04 damage per mana on a
single target, 8.15 damage per mana on a full quad. Outdoors only."* That ranking is void.

**DDD's 8-target cap is the highest of any AE in the game that does real damage.** The only
larger caps belong to Earthquake and Tremor, at 246 and 122 damage.

---

## 2. Rank scaling — measured from the player's screenshot, not back-solved

| | DDD 0 | DDD X | |
|---|---|---|---|
| Damage | 315 | **504** | **×1.60** |
| Resist Check | 0 | **−150** | a landing-rate gain, not a damage gain |
| Mana Cost | 800 | **640** | **×0.80** |

**Damage per mana improves ×2.00**, but the damage itself only ×1.60 — half of the gain is
the mana cut. The earlier handoff *back-solved* mote rank 10 as ×2.0 damage to close a 2.3×
residual against a guide's measured 3,000. With the real ×1.60 the accounting is:

```
504 × 1.60 (Singing Mastery 3) × ~~2.00~~ 1.68 (Amplification, MEASURED) × 1.30 = 1,761
```

> ### MEASURED 29 August 2026 — the Amplification toggle test, and it moves two things
>
> `corpus/amp/eqlog_Shara_rivervale_20260829.txt`, parsed by `amp.py`. The player's own
> design: sing `Denon's Desperate Dirge IX` with Amplification out of the spell bar,
> memorise it, sing again, on the same mob type. State tracked line by line.
>
> | | rock golem | elemental visier |
> |---|---|---|
> | Amplification **off** | **1583** (n=1) | 1415 (n=1) |
> | Amplification **on** | **2659** (n=6, identical every time) | unusable — see below |
>
> **Amplification is ×1.6797, or +1076 flat.** ~~×2.00~~ **struck.** ×2.00 would have
> predicted 3,166 where 2,659 was measured — 1.19× too high.
>
> **Multiplicative or additive cannot be separated from one mob type, and I will not
> pick.** The second pair would separate them and is unusable: the visier's amped line is
> flagged `(Critical)` *and* is a killing blow. Recorded anyway because it is suggestive —
> additive predicts 1415 + 1076 = **2491** and the log reads **2491**, where multiplicative
> predicts 2377. **One truncated line is not evidence.** Two clean non-kill hits on a
> second mob type settle it.
>
> **The chain now misses by more, not less, and that is the useful part.** With ×2.00 the
> build above gave 2,097 against a measured 2,659 — **−21%**. Correcting Amplification down
> to the measured 1.68 gives 1,761 — **−34%**. *Correcting one term made the total worse*,
> which means a different term carries the error. This file already names two untested
> candidates, Jam Fest 3 (+5 casting levels) and Improved Familiar (+9). **Neither is
> measured and I am not closing this by fitting to it.**
>
> **Four things fell out of the same 400 lines, free:**
>
> 1. **`"Your voice booms."` is Amplification's own pulse**, on the same 6-second tick as
>    every other song, and it correlates perfectly with the memorised state across 20
>    firings. **That is how to read this state out of any log** — no boom, no Amplification.
> 2. **Killing blows truncate to remaining hit points.** Six hits land on a kill and *every
>    one* is below the deterministic value for its mob and state: 2491, 2659, 2659, 1147,
>    1851, 1831 where the true value is 2659. **Any histogram of song damage that keeps
>    killing blows carries phantom low values**, and this repo's earlier weapon-endpoint
>    identifications should be re-checked for the same contamination.
> 3. **The crit multiplier is ×3.00 and the true damage is not an integer.** 7978 against a
>    2659 non-crit is 3.0004 — but 3 × 2659 = 7977. A pre-floor value of **2659.33** floors
>    to 2659 and triples to exactly 7978. The client floors the display and crits the
>    unfloored number.
> 4. **DDD damage is deterministic per target, and target-dependent.** Six identical 2659s,
>    no variance at all — so it is not a roll. But the visier took 1415 unamped where the
>    golem took 1583, a 12% difference. Resist, level or type; **not identified**.

~~against the guide's 3,000 — a 1.43× residual, down from 2.3×, and with no back-solved
constant. Jam Fest 3 (+5 casting levels) and Improved Familiar (+9) plausibly cover it.~~
**Struck: measurement replaced the guide as the anchor, and the residual grew.**

The **−150 resist check** is a large and entirely unmodelled gain: DDD checks Magic resist,
and at max rank it lands against targets that would otherwise resist it.

---

## 3. Why Improved Damage focus does nothing, and what does — the mechanism

The player said improved-damage focus does not affect DDD but "mana of preservation" does.
Both halves are confirmed, and the reason is in the `Limit` clauses:

```
Improved Damage I / II / III        (and every Gallenite's variant)
    Increase Spell Damage by 1% to 20%
    Limit Target: Exclude Caster AE
    Limit Target: Exclude Caster PB
    Limit Target: Exclude Target AE      <-- DDD is Targeted AE.  EXCLUDED.
```

**Every spell-damage focus in the game excludes all three AE target types.** So no
spell-damage focus can touch DDD — *or any other AE*. That is a level playing field, not a
DDD penalty.

The mana and haste focuses carry **no target-type limit**, only a level cap, and DDD is
level 43:

| Focus | Effect | Level cap | Applies to DDD? |
|---|---|---|---|
| **Jolum's Superior Abatement** | **−15% spell mana cost**, Limit Type: Detrimental | 65 | **yes** |
| Jolum's Abatement / Major | −15% mana | 50 / 60 | yes |
| **Mana Preservation II** | **−10% spell mana cost** | 44 | **yes** — just fits |
| Mana Preservation I | −10% mana | 20 | no |
| **Naki's Superior Pernicity** | **+15% spell haste** | 51 | **yes** — 3.00 s cast → 2.55 s |

So the achievable floor is **640 × 0.85 = 544 mana** on a **2.55-second** cast.

---

## 4. Does DDD crit? Yes — on measured evidence

DDD is `Magic DD`, Targeted AE. The corpus contains a direct analogue: **`Frost Storm`, also
a Targeted-AE direct-damage spell, crits at 13.2% with a multiplier of ×3.03.**

Measured across the corpus, spells fall into two clean classes:

| crits | Lifetap Strike ×3.065 · Puma Maw ×3.006 · Frost Storm ×3.031 · Vampiric Embrace ×3.034 · Dismiss Undead · Condemnation |
|---|---|
| **never crits** | Smiting Strike **0/727** · Earthquake 0/39 · Reaving Strike 0/35 · Scream of Death 0/29 · Chaos Flux 0/24 |

The non-critting group is procs, melee riders and **PB AE**; the critting group includes
**Targeted AE**. DDD is on the critting side.

**The ×3.00 constant itself is evidence that `Destructive Fury` applies to spell damage:** a
base crit of ×2.0 plus Destructive Fury 3's +100% *of the bonus* gives exactly
`1 + 2×1.0 = 3.00`, which is what eight independent spells measure.

### The crit AAs, corrected

The player's recollection had two of these swapped. From the AA catalogue, verbatim:

| AA | Effect | Who |
|---|---|---|
| **Fury of Magic** 4 | **+2/4/7/10% crit chance**, direct damage spells | Archetype — **any trio** |
| **Destructive Fury** 3 | **+30/60/100% crit damage**, direct damage spells | Archetype — **any trio** |
| **Unbound Destruction** 3 | **+2/4/6% crit chance** | **Wizard**, free |
| **Unbound Nature** 3 | **+2/3/4% crit chance** (text says "a spell", broader) | **Druid**, free |
| Improved Familiar | +3% crit damage, **+9 casting levels**, +25 resists, +6 mana regen | Wizard, 6 pts |

- The **6%** is **Wizard's**, not Druid's. Druid's is **4%**.
- There is **no Wizard +30% crit-damage AA.** Crit damage comes from `Destructive Fury`
  (+100%), which is Archetype and available to every trio.
- **Critical Affliction / Destructive Cascade / Unbound Affliction / Unbound Cascade are
  DoT-only** and do nothing for DDD, which is instant.

Maximum crit chance on DDD = **10% (Fury of Magic) + 6% (WIZ) + 4% (DRU) = 20%**, if they
stack. At ×3.00 that is a mean multiplier of **×1.40**.

---

## 5. The other two class contributions the player named — both confirmed

**Shaman `Cannibalization` (AA, 5 points, level 40, requires Mental Clarity 3):**
> *"consumes 1924 health to restore 1066 mana"* — 3-minute refresh.

The player said "1000 mana for 2000 health instantly." Confirmed, near-exact. On top of the
castable `Cannibalize` line (0 mana, 1.25 s cast + 1.5 s recast, −50 HP → +28 mana at 50)
and `McMerin's Feast` (−67 HP → +36 mana).

**Necromancer `Lich`:** +20 mana per tick, permanent, costs HP — 3.33 mana/s passive, the
best uninterrupted mana income in the game.

---

## 6. What this makes DDD

At max rank with the stack that provably applies:

| | conservative (Amplification at the wiki's 10%) | reported (Amplification ×2.0 + Empowering) |
|---|---|---|
| non-crit per target | 887 | 2,097 |
| mean per target (20% crit ×3.00) | 1,242 | 2,935 |
| per cast, 8 targets | **9,935** | **23,482** |
| mana | 544 | 544 |
| **damage per mana** | **18.3** | **43.2** |
| cast | 2.55 s, **zero recast** | 2.55 s, **zero recast** |

**The zero recast is the structural advantage I kept missing.** Frost Storm is a 17-second
cycle; Supernova 18.3; Upheaval 29. **DDD has `recast_time = 0.00`** — it chains as fast as
you can cast it, six times over in the time Frost Storm fires once, limited only by mana.
That, the 8-target cap, and two multiplier systems no other class has are why the player's
claim holds.

### What is still open

| | |
|---|---|
| **Amplification: ×1.10 or ×2.00** | The wiki description says 10%, its effect slot says 0.7%, players report 100%. This is a **2.4× swing** on DDD. **Test: cast DDD with Amplification up, then down.** |
| Whether crit AAs stack across classes | 10% vs 20% crit is a 1.13× swing |
| Whether the "unstated cap" spells are truly uncapped | decides whether Frost Storm competes at 30+ mobs |
| The guide's 1.43× residual | Jam Fest and casting levels, unquantified |

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*


---

## OPEN — Denon's Desperate Dirge deals one of TWO values to the same mob type

**Found 30 Aug 2026 while checking Session D's killing-blow detector against this
corpus.** `bard.py`, Shara, rank IX, non-crit, killing blows excluded.

**Fourteen of twenty target-name groups are bimodal, and the pair is almost always
2659 / 3177.** `a spiroc vanquisher` 2659×21 and 3177×21; `a watchful guard`
2659×26 / 3177×16; `a crystaline cloud`, `a gust of wind`, `The Spiroc Lord`,
seven more spiroc types, and `heart harpie` all the same pair. `a rock golem`
carries 1583 / 2659 instead, and `Protector of Sky` 2161 / 3177.

**3177 / 2659 = 1.1948.** Not a clean +20% (that would give 3190).

**It is a state that toggles, not a per-hit roll.** Sorting the 455 hits at those
two values by time gives **22 alternating runs, the longest 70 hits**: 43, 24, 70,
10, 56, 8, 32, 10, 26, 42, 4, 56, 24, 9… A random per-cast effect cannot produce
runs of seventy.

**Not explained by:** mob level or zone — both values land on the same named mob
types. Not rank — the log sings `Denon's Desperate Dirge IX` throughout. Not
Amplification — it was up for the whole measured stretch.

**Candidates, unseparated:** a long-uptime buff lapsing and being recast; a song
entering and leaving the twist rotation; an exaltation click state (`Djarn's
Amethyst Ring (Exaltation) shimmers briefly` precedes every cast).

**The test is one screenshot of the buff bar during a 3177 run and one during a
2659 run.** Until then this is recorded and not guessed at — and note that it
makes every single-value DDD figure in this file a figure for *one of two states*,
including the 2,659 the Amplification measurement rests on.