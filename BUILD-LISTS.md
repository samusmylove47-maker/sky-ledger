# FOUR RANKINGS, ON THE MEASURED CHAIN

**Established:** 29 August 2026 · **Model:** `model4.py` · **Rankings:** `lists2.py`
**Chain:** `DAMAGE-CHAIN.md` · **Itemisation:** `EQUIPMENT-TRUTH.md`
**Built from:** 24 research agents over 138 committed Legends client logs, each dossier
followed by an independent from-scratch refutation, plus direct measurement here.

Supersedes the 28 August version of this file entirely. Nine bugs in the previous model
were material; the largest changed every number by 28%.

**Constraint:** Enchanter excluded from **List 1** only. List 2 is explicitly about a charm
pet, so ENC competes there and wins a slot.

---

## 0. Does the model describe a real character?

Before any ranking. `jos437-finishing-blow.log` is a level-50 PAL/MNK/ENC with both weapons
identified from their damage endpoints. Nothing below was fitted to it.

```
model4.py, PAL+MNK+ENC, average mitigation, median ability rates
   melee output   381   ·   measured   381.0
   swing rates    slash 1.082/s vs 1.111 measured · punch 1.103/s vs 1.132 measured
   total          444   ·   measured   426.5      (+4.0%)
```

**Both hands predict from constants alone to within 3%.**

### The three player-reported anchors

| | sustained engaged | ×1.46 → peak | reported |
|---|---|---|---|
| above-average martial, no ENC | 425 | **621** | 600+ |
| min/maxed, abilities on cooldown | 648 | **946** | 900–1000 |
| BIS, open constants at the favourable end | 848 | **1238** | 1200+ |

The anchors independently demand ×1.411 / ×1.466 / ×1.416 — a **3.9% spread** — against a
measured **best-30s/engaged of 1.462**. A shipped Legends parser in the corpus offers a
`Rolling 30s` readout; **a player quoting the highest number on that display is quoting
best-30s.** See `DAMAGE-CHAIN.md` §8.

---

## 1. The five structural facts that sort all 560 trios

**1. Offensive Stance is ×2.00 damage, and only the nine martial classes have it.**
Measured off a bash lane that floors at exactly 1 damage: it reads **1** under
balanced/defensive/mage-hunter/berserker/evasive, **2** under offensive. Non-crit damage is
100.00% even under Offensive (760/760 once killing blows are excluded). It does **not**
touch procs or spells.

**2. The haste cap is 75% — 85% with a Monk.** Not the 175 the previous model carried. Worn
haste does not stack; only the highest item counts. Every trio reaches the cap with a
support partner, so **haste sets the level but does not differentiate builds.**

**3. Weapon access is single-class locked, and slot legality binds.**

| Weapon | +10 | Class | Slot |
|---|---|---|---|
| `Cudgel of the Fool` | 90/52 | BER | 2H |
| `Khyldorn the Blood Drinker` | 72/43 | SHD | 2H |
| **`Aldryn` / `Thelvorn`** | **40/26** | **PAL** | **PRIMARY only** |
| **`Wu's Fist of Mastery`** | **32/22** | **MNK** | either hand |
| `Windstriker` | 90/60 | RNG | bow |

**Aldryn and Thelvorn cannot be paired.** Both are PRIMARY-only, and they are mutually
exclusive besides. **A weapon can only go in the offhand if its slot list contains
SECONDARY** — 232 of 444 melee weapons are PRIMARY-only. The legal offhands worth carrying
are `Wu's Fist of Mastery` 32/22 (MNK), `Arydryidriyorn` 24/21 (RNG) and `Dagas` 22/21 (WAR).
The best pair in the game is `Aldryn` main + `Wu's Fist` off, which **requires PAL + MNK**,
and **dual-wield still beats every two-hander**. Legends is Classic-era only: loading all 223 in-era
weapons the catalogue is missing changes the top trio by **+0.0 DPS**.

**4. Paladin has a damage lane nothing else has.** `Smiting Strike` carries a **flat +417
rider on 658 of 658 landed smites** — not a proc, never crits, not stance-doubled. Worth
**~80 DPS to every Paladin trio**, and the previous model had no smite lane at all.

**5. Attack power still has exactly one source.** 2 of 11,534 items carry ATK and both are
era-gated behind unshipped expansions. Ranger's `Hunter's Attack Power` is **+104, free,
permanent** — and now provably has no substitute *until Kunark ships*.

---

## LIST 1 — TOP 10 RAID-BOSS DPS

Raid mitigation · attacking from behind (full Backstab) · nothing charmable on a single
boss · abilities on cooldown · **Enchanter excluded**.

| # | Trio | sustained | peak (×1.46) | Weapons |
|---|---|---|---|---|
| **1** | **PAL+RNG+ROG** | **522** | **762** | Aldryn 40/26 + Arydryidriyorn |
| 2 | NEC+PAL+RNG | 505 | 737 | Aldryn + Arydryidriyorn |
| 3 | PAL+RNG+WIZ | 494 | 721 | Aldryn + Arydryidriyorn |
| 4 | MNK+PAL+ROG | 491 | 717 | **Aldryn + Wu's Fist** |
| 5 | MNK+PAL+RNG | 488 | 712 | **Aldryn + Wu's Fist** |
| 6 | BER+PAL+RNG | 486 | 710 | Aldryn + Arydryidriyorn |
| 7 | MNK+NEC+PAL | 486 | 709 | Aldryn + Wu's Fist |
| 8 | NEC+PAL+ROG | 481 | 702 | Aldryn + Fanged Skull Stiletto |
| 9 | PAL+RNG+SHM | 478 | 698 | Aldryn + Arydryidriyorn |
| 10 | MNK+PAL+WIZ | 475 | 694 | Aldryn + Wu's Fist |

**`PAL+RNG+ROG` is #1, and it is the one build that is robust to every open question below.**
It stacks the three highest-value classes in the game: Paladin's blades *and* smite rider,
Ranger's +104 ATK, Rogue's Backstab (178.7 mean, the highest per-hit lane measured).

> **Sensitivity, stated because it is decisive.** Paladin appears in **10 of 10** — but that
> rests entirely on the `+417` smite rider, measured in **one file, one character**. Set it
> to zero and Paladin falls to **2 of 10** while Ranger rises to **9 of 10**:
>
> | | PAL in top 10 | RNG in top 10 | #1 |
> |---|---|---|---|
> | rider = 417 (measured) | **10/10** | 6/10 | PAL+RNG+ROG |
> | rider = 0 (conservative) | 2/10 | **9/10** | NEC+RNG+ROG |
>
> **`PAL+RNG+ROG` is #1 or #3 either way.** Everything else in the list moves.
> The five-minute test: cast Smite twenty times and see whether every landed one carries a
> flat ~417 on top.

> **The offhand is now capped at the measured maximum of 1.42 attempts/s.** Uncapped, the
> model picked `Efreeti Standard` (3 damage / 10 delay) and swung it at 2.30/s — 62% beyond
> anything ever observed. Capping it costs the top build 13 DPS and makes the model choose
> exactly the offhands a player would name: **Arydryidriyorn, Wu's Fist of Mastery**. The
> top three are unchanged either way.

### Ranger: the safest pick, not the single best

Over all 120 class pairs, asking "what is the best third class?":

| | wins the slot | mean trio DPS | **median regret when it is not optimal** |
|---|---|---|---|
| PAL | 53% | 410.9 | 0.0 |
| **RNG** | 42% | **415.7 — highest** | **3.0** |
| ROG | 0% | 411.1 | 22.3 |
| MNK | 0% | 405.2 | 25.9 |

**Ranger has the highest mean marginal value of any of the sixteen classes and a median
regret of 3 DPS.** That is exactly the signature of a universally-stacked class: highest
expected value, near-zero cost when it is wrong, rarely the single peak. It is a
*safest-pick* result — which is how communities actually behave.

### Archery: a Ranger should melee

Under the corrected chain the bow lane is **370–454 DPS against 506–564 meleeing — 0.72 to
0.90×.** Ranged stance carries no damage multiplier; its real effect (per a Legends patch
note) is granting double and triple attack to the bow, which only brings archery up to the
baseline melee already has. **The bow's proc socket is real but small: the best pure-RANGE
Exaltation is `Lightning Strike` 184 → 9.2 DPS**, about 1.5% of the build.

> **But it flips on one sentence.** If bows use the melee base law `U = 2·DMG+1` rather than
> `bow+arrow`, archery rises ×1.58 and **breaks even**. The only source is a page tagged
> `{{Classic Era}}` whose own damage section reads *"Needs Confirmed/Updated for EQ
> Legends"*. **Test: shoot 200 arrows at one target and read the maximum — `bow+arrow`
> predicts ~228, the melee law ~362.**

---

## LIST 2 — TOP 10 TANK + CHARM PET + DAMAGE

Gates: **Defensive stance** (WAR/PAL/SHD — the only three that have it) **and** a charm
class. Fighting from the front, so Backstab degrades to `Chaotic Stab`. **Enchanter
included.**

| Class | Charms to | Against |
|---|---|---|
| **ENC** | 51 | **any** |
| **BRD** | 51 | **any** — but on an 18-second song |
| NEC | 51 | undead only |
| DRU | 49 | animals only |
| SHM | 33 | animals only |

| # | Trio | sustained | peak | tank | charm |
|---|---|---|---|---|---|
| **1** | **NEC+PAL+RNG** | **562** | **821** | 80 | NEC → 51, undead |
| 2 | MNK+NEC+PAL | 530 | 774 | 88 | NEC → 51, undead |
| 3 | BRD+PAL+RNG | 507 | 740 | 80 | **BRD → 51, any** |
| 4 | **ENC+PAL+RNG** | 507 | 740 | 80 | **ENC → 51, any** |
| 5 | **NEC+PAL+WAR** | 504 | 737 | **110** | NEC → 51, undead |
| 6 | PAL+RNG+SHM | 491 | 717 | 80 | SHM → 33, animal |
| 7 | BST+NEC+PAL | 485 | 708 | 80 | NEC → 51, undead |
| 8 | NEC+PAL+ROG | 475 | 694 | 80 | NEC → 51, undead |
| 9 | BRD+MNK+PAL | 475 | 693 | 88 | BRD → 51, any |
| 10 | ENC+MNK+PAL | 475 | 693 | 88 | ENC → 51, any |

**NEC+PAL+RNG is the damage answer; NEC+PAL+WAR is the durable one** (tank 110 — Warrior's
free permanent 5% melee mitigation plus Lay on Hands). **ENC and BRD tie at #3–4 and are the
only charmers that work on any target** — take one of those if your content is not undead.

Two facts that change how this build actually plays:

- **A charm pet is worth ~67 DPS sustained, and ~9× a summoned pet.** Measured
  coefficient-free: pet damage falling inside the owner's own engaged segments.
- **You tank, not the pet.** Across every named and raid boss in the corpus, bosses aimed
  **1,318 melee attempts at the player and 59 at anything else** — 4.3%. On the Nagafen kill
  it was **186 to 1**. The pet is a damage source, not an off-tank, and any plan that has it
  holding the boss is wrong.

---

## LIST 3 — TOP 10 DAMAGE PER UNIT OF WRIST

**Combat skills have no global cooldown and fire automatically during auto-attack.** Kick,
Bash, Slam, Frenzy, Strike, Backstab and Smite all cost **zero input**, as do auto-attack,
weapon procs and stances. The entire wrist load is spell and song upkeep.

Derived from measured durations: **61 of 76 Bard songs last exactly 18.0 s**, so twisting
four is **13.3 recasts per minute, forever** — Bard is the worst class in the game for this
by a factor of about twenty-five. Shaman's three DoTs at 42 s median → 4.2/min.

| # | Trio | DPS | actions/min | DPS per action |
|---|---|---|---|---|
| **1** | **BER+MNK+WAR** | 499 | **2.0** | **166.5** |
| 2 | BER+RNG+WAR | 502 | 2.5 | 143.5 |
| 3 | MNK+RNG+WAR | 495 | 3.0 | 123.6 |
| 4 | BER+MNK+RNG | 490 | 3.0 | 122.5 |
| 5 | BER+PAL+WAR | 552 | 4.0 | 110.4 |
| 6 | **BER+MNK+PAL** | **574** | 4.5 | 104.4 |
| 7 | **BER+PAL+RNG** | **602** | 5.0 | 100.4 |
| 8 | MNK+PAL+WAR | 526 | 4.5 | 95.6 |
| 9 | PAL+RNG+WAR | 548 | 5.0 | 91.3 |
| 10 | MNK+PAL+RNG | 584 | 5.5 | 89.9 |

**`BER+MNK+WAR` is the rest-your-hands build**: three classes with no damage spells at all,
so all 499 DPS comes from auto-attack and autoskills. Five lanes, every stance in the game,
Triple Attack, Berserker's free +6% crit rate, Warrior's free +30% crit damage, Monk's +10%
haste-cap break. Set a stance and hold auto-attack.

**If you will accept five actions a minute, `BER+PAL+RNG` at 602 DPS is 21% more damage** —
the extra input is Paladin's heals and stuns, and the Smite lane fires on its own.

For contrast: `PAL+RNG+ROG` — the List 1 winner — costs **12.5 actions/min**, because
Backstab requires standing behind the target continuously. `BRD+DRU+SHD` is 330 DPS at
**26.3**.

---

## THE AOE FARMING TRIO — rebuilt, because my first answer was wrong

> **The previous version of this section gated on having a tank class.** That excluded every
> kiting and caster trio — i.e. the entire real AOE meta — and it is why none of the builds
> the player named appeared. Three things were wrong with it, and fixing them changed the
> answer completely.

### What was wrong, and what the corpus says

**1. AOE does not require tanking.** There are four survival modes, and only one of them
involves holding aggro. Sustained movement speed at level 50, from the spell database:

| | speed | duration |
|---|---|---|
| DRU / SHM `Scale of Wolf` | **+57%** | 45 min |
| SHM `Spirit of Bih'Li` | +55% | 36 min |
| DRU / RNG `Greater Wolf Form` | +52% | permanent |
| **BRD `Selo's Accelerando`** | **+15%** | 3 ticks |

**Bard is not the swarm-kite engine in Legends** — `Selo's Song of Travel` (+65%) is level 51
and out of reach at cap. **Druid, Shaman and Ranger carry the kiting speed.**

**2. AE spells have no target cap.** Not one of the 42 AE spells at level ≤50 states a
numeric limit, so damage scales linearly with the pull, unbounded. **Pull size is the
dominant term**, which is exactly why a kiter beats a tank: the crossover is only **~1.5×**
the tank's pull, and kiting routinely gathers 3–5×.

**3. Rain and storm spells land in waves — a 3× undercount.** Measured directly:

```
[13:46:05] You begin casting Frost Storm VII.
[13:46:06] You hit a revultant rat for 741 points of cold damage by Frost Storm.
[13:46:09] You hit a revultant rat for 741 points of cold damage by Frost Storm.
[13:46:12] You hit a revultant rat for 741 points of cold damage by Frost Storm.
[13:46:22] You begin casting Frost Storm VII.        <- next cast
```

**Three waves, three seconds apart, from one cast** — and at 13:47:16 three waves land in the
same second on *three different targets*, so each wave hits everything in the area. Median 7
hits per cast over 24 casts.

### That makes Wizard the AOE engine outright

| spell | total damage/cast | mana | cycle | dmg/s/mob | **dmg/mana** |
|---|---|---|---|---|---|
| **WIZ `Frost Storm` ×3** | **1,536** | 271 | 17 s | **90.4** | **5.67** |
| WIZ `Lava Storm` ×3 | 1,203 | 234 | 17 s | 70.8 | 5.14 |
| DRU `Lightning Blast` | 477 | 234 | 7.6 s | 62.8 | 2.04 |
| MAG `Rain of Swords` ×3 | 972 | 375 | 19.5 s | 49.8 | 2.59 |
| WIZ `Supernova` | 854 | 875 | 18.3 s | 46.7 | 0.98 |
| **BRD `Denon's Desperate Dirge`** | 315 | **800** | 3 s | 105.0 | **0.39** |

**Frost Storm is best on both axes at once.** And Bard's AE, the one spell with higher
nominal throughput, is the least mana-efficient in the game by a factor of fourteen — while
**87 of 91 Bard songs cost zero mana**, its actual free AE songs do **0.3–0.7 DPS per mob**.
Bard is an enabler in an AOE trio, not a damage source.

### The fourth correction: mana conversion competes with casting

Shaman's `McMerin's Feast` is 1.25 s cast + 1.5 s recast for +36 mana — **13.1 mana/s if you
spend every second on it.** But those are seconds you are not casting AE. Modelled as a
steady state (fraction of time casting vs converting) rather than as free income. Wizard's
`Harvest` turns out to be **+251 mana on a 600-second recast = 0.42 mana/s**, not the 4.0 I
had — a tenfold error.

### Top 3

| # | Trio | DPS at a pull of 30 | Why |
|---|---|---|---|
| **1** | **NEC+SHM+WIZ** | **1,852** | Wizard is the engine. **Shaman does two jobs in one slot** — `Cannibalize` for mana *and* `Spirit of Bih'Li` +55% for the kite — and Necromancer's `Lich` adds 3.3 mana/s passively. Casting 68% of the time, the highest duty cycle in the game. |
| **2** | **DRU+NEC+WIZ** | **1,810** | Same engine, Druid supplying `Scale of Wolf` +57% and a second AE line for when Frost Storm is down. Lower mana income (6.8/s) but the best mobility. |
| **3** | **BRD+SHM+WIZ** | **1,651** | **Your first pick, one slot changed.** Bard for gathering — snare −30%, AE aggro, a free group mana song — with Shaman replacing Druid because it covers mana *and* speed at once. |

### Where your three picks land

| your pick | DPS | rank | mode | the gap |
|---|---|---|---|---|
| **BRD+DRU+WIZ** | **1,336** | **18 / 525** | kite | 28% off the top. DRU and BRD both spend their slot on mobility; neither generates real mana, so it casts only 29% of the time against 68% for the leader. |
| **ENC+MAG+WIZ** | **1,020** | **38 / 525** | AE-mez | Three casters, but MAG and ENC bring weaker AE than the Wizard already has, and AE damage breaks mez — so the lockdown does not combine with the damage. |
| **SHD+DRU+BRD** | 458 | 196 / 525 | tank | No Wizard, so no storm waves; the best AE it can reach is Lightning Blast at a 14% duty cycle. |

**You were right that my list was wrong** — the tank gate excluded the whole real meta — and
right that Wizard-and-caster trios belong at the top. Where the model still disagrees is
narrower than it looks: it wants the non-Wizard slots spent on **mana**, not mobility, and
Shaman is the one class that supplies both.

> **The assumption doing the work is pull size by mode** — tank 10, kite 30, AE-mez 20. I
> cannot measure it; the corpus has no swarm-kiting log. If a Bard's snare and AE aggro
> genuinely gather more than a Druid's speed alone, `BRD+SHM+WIZ` moves up and your
> `BRD+DRU+WIZ` moves with it. **The test: pull until it breaks, with and without the Bard.**

---

## What would change these answers, ranked

| # | Open question | What it moves | Cheapest test |
|---|---|---|---|
| **1** | **Is the `+417` Smiting Strike rider real and general?** Measured 658/658 but in one file, one character. | **Decides List 1 outright.** PAL goes 10/10 → 2/10, RNG 6/10 → 9/10. | Smite twenty times; check every landed one carries a flat ~417. |
| **2** | **Archery base-damage law:** `bow+arrow` or `2·DMG+1`? Only source is `{{Classic Era}}`-tagged and self-flagged unconfirmed. | Decides whether a Ranger melees or shoots. ×1.58 on the bow lane. | **200 arrows at one target, read the maximum.** ~228 vs ~362. |
| **3** | **Which window is your meter reporting?** Four shipped Legends meters, four different denominators. | ×2.0 across the readings. Under a fight-average reading the residual reopens. | **One sentence: which meter, and was it the Rolling-30s field or the average?** |
| **4** | **Does the 255 STR cap bind?** T2 says yes but cites Project 1999. Your own client panel reads **INT 295**. | ×1.04 to ×1.25 on everything. | Read STR on the panel, have your partner cast Strength, read it again. |
| **5** | **Striker stance's real law.** T2 says 3×/5×; its own crit test refutes a flat multiplier. | ±20% on BER/MNK/ROG/WAR ability-heavy trios. | Kick a mob 20× under Balanced, 20× under Striker. Compare maxima. |
| **6** | **Weapon upgrade scalar: +10%/tier or +5%?** A T2 page says weapons get 5% where every other stat gets 10%. | **×0.87 on the whole model.** | **One tooltip screenshot of any weapon above +2.** |
| **7** | Endurance pool and regen at 50 — completely unpublished, zero endurance lines in 141 logs. | Decides whether 900–1200 is sustainable or a burn. | Read End/End Regen on the panel; time the drain on a dummy. |
| **8** | Whether a Bard genuinely holds a bigger pull. | The AOE top 3, decisively. | Pull until it breaks, with and without. |

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
