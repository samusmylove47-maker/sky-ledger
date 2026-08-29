I have everything computed. Writing the design.

---

# TRIO DAMAGE MODEL — design spec

**Working title for the page:** *What a Swing Is Worth* · `/tools/swing-value.html`
**Engine:** `engine/trio-damage.js`, pure, no DOM, no fetch, importable by the 50 Upgrades bundle.
**Written for:** an engineer who has not been in this session. Every number below was computed by running the code in this spec, not transcribed. Working files: `/tmp/claude-0/-home-user-sky-ledger/caaa72f1-a659-51f4-8828-08bfb34cde0c/scratchpad/tdm/{chain,lanes,model,run1,run2,run3,run4}.mjs`.

---

## 00 · The one design decision, and the measurement that forces it

**The tool prints deltas and refuses to print a DPS number.** Not as modesty — because we ran the test.

I computed the same main-hand lane eight ways, varying the three choices this project has not settled: crit applied once or twice, `E[rx]` flat or Wrath-scaled, HandMod 0.69 or 0.8 (`run3.mjs`).

| quantity | spread across the eight forms |
|---|---|
| **the level** (Thelvorn +10 lane DPS) | **134.0 → 153.7, a 14.7% spread** |
| the 2H-vs-1H **delta** | −20.7% → −22.8%, **2.1 points** |
| the damage-bonus **delta** | +31.8% vs +31.8% under crit×1 and crit×2 — **exactly identical**; only `E[rx]` moves it, by 1.8 points |

The crit form cancels out of a ratio to the last decimal. Swing rate, haste, stance and multi-attack cancel too, because they multiply both sides. What survives in a delta is only what differs between the two loadouts. So a delta is a far better-founded object than a level, and it is what a gear planner actually needs.

The level is also not merely uncertain, it is **known to be wrong in a known direction**. `HANDOFF.md` §1: the model's *floor* — worst of 560 trios, raid mitigation — sits at **1.51× the measured median per character**, and **162 of 213 logged raid fights fall below it**. Turning off the two largest assumptions together (Offensive stance and on-cooldown ability rates) still leaves **2.61×**. Every number this chain has produced was a ceiling printed as an estimate.

> **The rule the tool enforces in code:** `scoreLoadout()` never returns a bare number. It returns a band, a lane decomposition, a list of refusals, and the seven-field derived-claim envelope. `deltaFor()` is the only function whose output is intended for a headline.

---

## 01 · Inputs

Three groups. Everything else is derived.

```ts
interface Context {
  classes: [ClassCode] | [ClassCode, ClassCode] | [ClassCode, ClassCode, ClassCode];
  levels:  Record<ClassCode, number>;      // reuse ht(item, ctx).best from the planner
  race?:   RaceCode;                        // carried for item legality only; no damage term
  str?:    number;                          // omit → STR_MOD fallback, and a refusal is raised
  stance:  StanceId;                        // default 'offensive' if any martial class
  mode:    'avg' | 'raid';                  // target mitigation
  laneRates: 'med' | 'max';                 // corpus median, or every ability on cooldown
  front:   boolean;                         // you are tanking → Rogue backstab degrades
  hastePct?: number;                        // omit → HASTE_CAP + 10 if MNK
}

interface WeaponInput {                     // exactly the planner's Gt(item, tier).weapon
  name: string; dmg: number;                // tier-upgraded, from jt(wp.dmg, tier)
  delay: number; skill: string;
  slots: string[];                          // item.sl — needed for the offhand legality refusal
  procName?: string;
}

interface Loadout { primary?: WeaponInput; secondary?: WeaponInput; range?: WeaponInput; }
```

**Inputs deliberately not taken.** AC, HP, mana, saves, weight, resists. None enters the damage chain and taking them would imply they do. Worn ATK is not taken either: **0 of 2,263 catalogued items carry an `ATTACK` stat** (verified across all 19 shards this session), and the 2 wiki items that do are era-gated out of Legends, so the field is structurally zero and the tool says so rather than offering an input box that can only ever read 0.

---

## 02 · The chain

```
Wrath        = Offense + ((2·STR) − 150)/3 + WornATK + SpellATK + (RNG ? 104 : 0)
U            = 2·DMG + 1                                        base-roll maximum
B            = floor(HandMod · max(Level, DMG) · (min(Delay,50)/40) · (Level/100))
               HandMod 0.8 (1H) / 1.1 (2H)      MAIN HAND ONLY, measured 0 off-hand

E[rx](W,Mt)  = 0.967 · (1 + elast(Mt) · (W − 365))              calibrated, not generative
critBase     = (1−0.1272) + 0.1272·1.70 = 1.08904
critRatio    = trio's own crit factor ÷ critBase                 1.000 baseline, 1.039 BER, 1.060 WAR

E[hit|land]  = critRatio · (critBase · U · E[rx] · Mt + 1.1) + B
swings/s     = (1 + haste/100) / (Delay/10) · chain · stanceRate
laneDPS      = swings/s · P(land) · E[hit|land] · stanceDmg
```

Three details an implementer will get wrong if they are not called out.

**Crit is applied once.** `1.08904` *is* the crit factor — `(1−0.1272) + 0.1272×1.70`. It is already inside the closed form in `DAMAGE-CHAIN.md` §2, and the trailing `+1.1` is the `+5` crit floor term folded in (`1.7 × 5 × 0.1272 = 1.081`). `model4.py`'s `lane_dps()` then multiplies the whole thing by `(1-cr)+cr*cm` a second time:

```python
hit = 1.089*U*e_rx(wrath,mode)*MITF[mode] + B + 1.1
hit *= (1-cr)+cr*cm          # ← 1.08904 again for any trio without BER or WAR
```

Whether that is a bug or an absorbed calibration **depends on how `E_RX_BASE = 0.967` was fitted, and the repo does not record it.** `DAMAGE-CHAIN.md` §11 calls it "back-solved from an identified main hand"; §8 says of the same character "nothing here is fitted to its damage." Those cannot both hold. Against the one pinned lane the double form lands at **+1.6%** and the single form at **−5.0%** — evidence, but confounded, because I also moved HandMod 0.69→0.8 in the same step. So: **ship the single-crit form with `critRatio`, exactly as `model4.py` already does correctly for its ability lanes via `critadj`, and treat `E_RX_BASE` and the crit form as one entangled pair that must be refitted together.** Record it as OPEN. It costs the tool nothing, because it cancels out of every delta.

**Crit does not touch the bonus.** `B` is added after the crit, per `DAMAGE-CHAIN.md` §2 (`FinalDamage = DamageDone + B`). `model4.py` crits it. On Thelvorn +10 that is 11.2 damage crit-multiplied that should not be.

**Stance multiplies last, and it scales `B`.** Confirmed by the parity test: non-crit damage is even **100.00%** of the time under Offensive (760/760 once killing blows are excluded) against ~55% in every other stance, and endpoints double exactly on the same weapon in the same file (86→172, 89→178, 184→368).

**Procs are per minute.** They do not enter `laneDPS` and they do not scale with swing rate. Exposure test ΔlogLik **+8.19**; correlation of PPM with swing rate **−0.03**. Haste and multi-attack buy zero extra procs, and any implementer who multiplies a proc by a swing count has reintroduced the single most common error in this field.

---

## 03 · Constants, every one with its tier

`M` measured · `T1–T5` the site's ladder · **`D` derived** (an envelope, not a tier — a derived number has no source, it has a derivation) · **`OPEN`** (the tool refuses or bands).

### Swing outcome
| constant | value | tier | evidence |
|---|---|---|---|
| `P_LAND` | 0.5765 | **M** | n=21,122 and n=23,013 swing attempts |
| `ACC_OFFENSIVE` | ×1.081 | **M** | band 1.00–1.21; bash lane floored at exactly 1 damage |
| `G_AVOID` | 6.17–6.29% | **M** | dodge 2.67 / parry 2.31 / block 0.98 / **riposte 0.00** |
| `STRIKETHROUGH` | +30%, RNG | T2 | acts only on the avoidance bucket, never the miss roll → ~+2.4% total DPS |

### The roll
| constant | value | tier | evidence |
|---|---|---|---|
| `U = 2·DMG + 1` | — | **M** | two weapons identified from their own histograms: Thelvorn +8 DMG 36 → 84.2 predicted vs 86 measured; Whitened Treant Fists +4 DMG 19 → 39.0 vs 40. The rival `2(2·DMG+1)` is off by +83%/+95% |
| `E_RX_BASE` | 0.967 at Wrath 365 | **D** | back-solved from one identified main hand. **Fit path not recorded — entangled with the crit form. OPEN.** |
| `MITF.raid` | 0.73 | **OPEN** | seven properly-paired boss fights span 0.41–2.01, median 0.91. Cannot resolve a 0.73. Recorded as *untestable by this instrument*, which is not the same as *survived a test* |
| `maxExtraChance` | 0.49 | **OPEN** | ±10% on `E[rx]` |
| eqlwiki's published weighted-d20 | — | **REFUTED** | simulated twice at 400k draws: U-shaped, P(1) 16–37%, P(10) 1.3–2.5%, P(20) 26–59%, against measured 2.16 / 23.08 / 5.99. Its mean is right and its shape is wrong. **Do not code it.** |

### Crit
| `CRIT_RATE` 0.1272 · `CRIT_MULT` 1.70 on the rolled part only | **M** | five weapons |
| `BER_CRIT_ADD` +0.06 · `WAR_CRIT_DMG` +0.30 | T2 | enter as `critRatio` 1.0386 / 1.0596, never as absolutes |
| spell and proc crit **×3.00** at 12.2% | **M** | ten independent spells, exact to 3 s.f. (517/172, 729/243, 432/144, 126/42, 2246/741). The constant is itself evidence Destructive Fury 3 applies to spells: ×2.0 base +100% of the bonus = exactly 3.00 |
| — but **not universal** | **M** | Earthquake 0/39, Smiting Strike 0/658, Scream 0/29 never crit |

### Damage bonus — **corrected this session**
| `HAND_MOD` | **0.8 (1H) / 1.1 (2H)** | **T5 formula + T2 corroboration + M window** | eqlwiki `Game Mechanics` § *Working Legends Damage Bonus Formula*, added 2026-08-11, twelve days before our first `HandMod` commit. Verified live: Skycleaver 2H 30/35 → **24**, printed 24. Efreeti Standard 1H 3/10 → **5**, printed 5. Earthshaker +10 2H 74/70 → **50**, client window 50. Whitened Treant Fists 1H 14/28 → 14 at L50 and **13 at L49**, printed 13 — the batch spans two levels, which eqlwiki's own L49 observations independently corroborate. |

**`HandMod 0.69` is wrong and must not be carried forward.** It fails 0 of 13 T2 statblock rows, every miss in the same direction. `SOURCING.md` §3 grades it *M / clean*; `DAMAGE-CHAIN.md` lines 55 and 376 carry it. The two client windows it rests on (`Garduk`, `Arydryidriyorn`) **have no parse anywhere in the repository or the corpus** — a tier-M grade on a constant whose reading is not in the repo does not meet our own standard, and that is the deeper fault. `DAMAGE-CHAIN.md` line 376 also says Efreeti Standard is "the only 1H `Dmg Bon` line on a wiki statblock"; there are thirteen, in the same scrape the line cites. Fix on our side before anything ships.

### Rates
| `MH_CHAIN` 1.520, CI **[1.465, 1.569]** | **M** | DA 56%, TA 14.2% conditional |
| `OH_CHAIN` 1.4911 — **the offhand never triples** | **M** | P(≥3) 0.0017 vs 0.0406 main, a 24× gap |
| `DW_SUCCESS` 0.88 | **M** | separable because haste is identical in both hands |
| `HASTE_CAP` **75, band [75, 85]** | **OPEN** | eqlwiki's Legends-authored caps table (T5, but its 51–60 row cannot be a P99 import) and eqltools (T3, "about 75% at 50") **agree**. Monk `Unbound Alacrity` +3/6/10% is T2 and "3/6/10% of 75" vs "75+10 points" differ by 2.5. **Our own 1.900 measurement does not settle this and must not be quoted as if it did** — it sits above the 1.75 ceiling both sources give, the file contains no player haste buff or stance line, and 1.900 is also precisely our measured berserker-stance rate multiplier. It may be measuring stance. |

### Stances — all eight, measured off a bash lane that floors at exactly 1 damage
| stance | dmg | acc | rate | tier |
|---|---|---|---|---|
| **offensive** | **×2.00** | ×1.081 | ×1.00 | **M** |
| balanced | ×1.00 | ×1.00 | ×1.00 | **M** |
| defensive | ×1.00 | ×0.95 | ×1.00 | **M** |
| **berserker** | ×1.00 | ×1.01 | **×1.90** | **M** |
| evasive | ×1.00 | ×1.00 | ×1.00 | **M** (incoming hit rate ×0.08) |
| mage hunter | ×1.00 | ×0.97 | ×1.00 | **M** |
| ranged | ×1.00 | ×1.081 | ×1.00 | **M** (grants DA/TA to the bow, no damage multiplier) |
| **striker** | **`null`** | ×1.00 | ×1.00 | **OPEN — the tool refuses** |

Offensive does **not** touch procs or spells (Puma Maw 172 → 172). Berserker never clearly beats Offensive: ×1.90 rate against ×2.00 × ×1.081 = ×2.16, but the intervals overlap.

### Wrath
| `OFFENSE` caps at 50: WAR 210 · MNK 230 · ROG 210 · RNG 210 · BER 210 · PAL/SHD/BRD/BST/SHM/CLR/DRU 200 · ENC/MAG/NEC/WIZ 140 | **M-validated** | eqlbase, 21/21 against skill plateaus visible in the logs. eqlwiki's class-page skill tables measured **35% accurate (130/373 cells) and were rejected** |
| `SPELL_ATK` 61 | T2 | |
| `RNG_ATK` +104 | T2 | Hunter Attack Power, 26 ranks × 4, cost 0 AA, level 8 — worth **+11 to +13% of total DPS typically, +19% on a raid boss** |
| `WORN_ATK` **0** | **M** | 0 of 2,263 catalogued items; 2 of 11,534 wiki items and both era-gated |
| `STR_MOD` 120 | **OPEN** | assumes STR caps at 255; a client panel in this project reads **INT 295**. `EQUIPMENT-TRUTH.md` §1 says a 255 cap would pin the modifier and make STR gear worth nothing; the planner assumes 510; eqlwiki adds `if STR < 75: modifier = 0`, a clause our chain omits. **Decides whether STR converts to damage at all.** |

### Ability lanes — measured, and individually the worst part of the model
| lane | pre-stance mean | rate med / max | owners |
|---|---|---|---|
| kick | 58.50 | .32 / .54 | BST MNK RNG WAR |
| bash | 71.15 | .33 / .54 | PAL SHD WAR |
| strike | 35.05 | .27 / .50 | MNK |
| **smite** | 31.30 **+417 flat rider** | .17 / .31 | PAL — the rider fires 658/658 landed smites, is **not** stance-doubled and **never** crits |
| frenzy | 57.21 | .47 / .72 | BER — **2.918 attempts per activation**, P(3) > P(2); one hit per activation understates Berserker by roughly half |
| backstab | 178.69 | .29 / .47 | ROG — ×0.20 from the front |

**Against the one fully-pinned character these lanes miss by −41.2% (strike), −19.2% (bash), −10.4% (smite), +8.7% (kick) while the total lands at +0.1%.** That is cancellation, not agreement, and any trio that shifts the lane mix loses the cancellation and keeps the errors. The UI must therefore show lanes separately and label the ability half with its own error band — see §05.

### Procs and non-melee
| proc lanes: **1 two-handed · 2 dual-wielding · +1 Ranger bow · 0 from armour** | **M + D** | mechanistic: an Exaltation carries its **source item's** slot restriction onto the host, and 382/385 catalogued combat effects sit on PRIMARY/SECONDARY/RANGE. Re-verified on the shipped catalogue this session: **91 items carry a proc effect and 91 of 91 are weapon-slot-only, 0 on armour.** Control test: a spell-damage line falls within 1 s of an ordinary swing 20.9% of the time and within 1 s of an `(Exaltation)` message **16.9% — below chance**; Golden Efreeti Boots 0 of 25 |
| `WEAPON_PROC_PPM` 2.4, band 2.1–2.7 | **M** | |
| damage shield 17.5 DPS/attacker | **M** | exactly 1.00 tick per landed **incoming** hit; does not stack, does not scale with gear, **zero unless you are tanking** |
| charm pet 66.8 DPS; summoned 17.5–31 | **M** | |
| **the player tanks, not the pet** | **M** | bosses aimed 1,318 melee attempts at the player and 59 at anything else (4.3%); on Nagafen 186:1 |
| Spirit of the Puma | **M** | 154 damage at 400% rate mod ≈ 8 procs/min ≈ **25 DPS self, 127 group-wide across five melee**. "Huge" is a group statement, not a per-character one |

---

## 04 · Refusals — how the tool declines to answer

A refusal is a first-class return value, not an exception and not a zero. Each carries `{ code, why, settle }` — *what would settle it* is mandatory, matching the site's own idiom.

| code | fires when | what the tool shows |
|---|---|---|
| `STANCE_UNMODELLED` | stance is `striker` | The lane panel greys out and reads: *"Striker is not a flat multiplier and its own crit test refutes one. **Settle:** one bash lane floored at 1 damage, in Striker, for 200 swings."* No number is produced — not even a guess bracketed by balanced and offensive. |
| `TWO_HANDER_BLOCKS_OFFHAND` | `primary.skill` starts `2H` and a secondary is set | Off-hand lane scores 0, with the standing named: *classic-inherited and unmeasured on Legends.* eqlwiki `Game Mechanics` § Dual Wield compares the better dual arrangement against the two-hander, which presumes the rule but does not measure it. **None of the four inventory exports in this corpus shows a two-handed primary at all.** Ships as a dismissible banner, not a hard block. |
| `OFFHAND_NOT_LEGAL` | `secondary.slots` lacks `SECONDARY` | 219 of 431 melee weapons have no SECONDARY; 214 are `sl: ["PRIMARY"]` exactly. Aldryn and Thelvorn — the two best 1H weapons, both PAL, both 20/26 — are **both** PRIMARY-only and cannot be paired. This one already cost this project a published ranking. |
| `NO_DUAL_WIELD` | no class in the trio has Dual Wield | eqlbase per-class table (BRD BST MNK RNG ROG WAR). Prefer eqlbase over eqlwiki class pages, which measured 35% accurate on skill caps. |
| `STR_UNKNOWN` | `context.str` omitted, or STR > 255 | The STR term is shown as a **range spanning both readings** (cap active → contributes 0 further; cap absent → contributes 2/3 per point), because the project's own files contradict each other. Never a point value. |
| `MITIGATION_UNTESTABLE` | `mode === 'raid'` | The whole raid column carries a band, not a value: seven paired fights span 0.41–2.01. |
| `LANE_MIX_UNVALIDATED` | any ability lane is present | Named in the results panel, not hidden in a footnote: *"ability lanes miss by −41% to +9% individually against the one character we can check; only their sum has ever landed."* |
| `PROC_SOCKET_DEAD` | a proc Exaltation is socketed into a non-weapon position | *"No donor in the catalogue can legally fill a proc socket on a non-weapon position — 91 of 91 proc donors are weapon-slot-only, and an Exaltation carries its source item's slot restriction onto the host."* Shown **at the socket**, not after the pick. |
| `NO_ABSOLUTE_DPS` | any caller requests a level rather than a delta | Returns the band plus the residual line. There is no code path that emits a single DPS scalar. |

**Two things the tool refuses on principle, not on missing data.**

*It will not print archery.* The corpus holds **nine archery lines, all low-level**. Ranger has `Weapon Mastery of the Scout` (+100% base archery damage) and `Innate Called Shot`, and neither has ever been measured here. Absence of evidence is evidence of absence only where the corpus could have contained the thing — and at level 50 it could have, and did not.

*It will not rank trios.* That is `BUILD-LISTS.md`'s job and that file carries its own ceiling notice. A page that ranks 560 trios by a number whose floor sits 1.51× above measured play is the exact object `HANDOFF.md` §5 was written to prevent.

---

## 05 · Uncertainty — what the tool shows instead of false precision

**Three display forms, chosen by what the quantity is.**

1. **A delta gets a point and a narrow spread.** `±1.15 points`, derived not guessed: the only surviving disagreement in a same-character ratio is `E[rx]`'s Wrath elasticity, measured two ways in this session as a **2.3-point spread** on a damage-bonus delta (+31.8% flat vs +30.0% Wrath-scaled). The crit form contributes **exactly zero**.

2. **A level gets a band and the word *ceiling*.** Band width comes from `MH_CHAIN`'s own CI [1.465, 1.569] = ±3.4%, widened by `HASTE_CAP`'s [75,85] where haste is unpinned. Beside every level, unconditionally:

   > *162 of 213 logged raid fights fall below this model's own floor. Read this as a ceiling.*

3. **An open constant gets both readings, side by side, never an average.** STR, Striker, `MITF.raid`, the `E[rx]`/crit pair. Averaging two live hypotheses manufactures a number neither source supports.

**And one number the tool must carry everywhere it prints a rate: the denominator.** Wall-clock, engaged, best-60s and best-30s DPS differ by up to **1.75× on the same fight**. Re-run over the corpus this session: median best-60s/engaged **1.23**, best-30s **1.47**, best-10s **2.06**, n=29. jos437-finishing-blow alone reads 265 wall-clock / 483 engaged / 581 best-60s / 678 best-30s. **Four shipped Legends meters divide by four different things** — `eql-meter` `fight/mod.rs:347` per-fight elapsed; `EQBuddy` `SessionStats.cs:1692` combat-time only; `everquest-companion` `DpsCard.tsx:85` renders both; `eql-log-reader` `README.md:57` fight-average vs rolling windows. Comparing a model number against a quoted parse without converting is a 25–46% error and it is invisible. **Everything this engine produces is engaged DPS, stamped on every output object as `denominator: 'engaged'`.** One caveat to carry with the ratios: they are measured per log file, not per fight, and a fight shorter than the window is excluded rather than reported.

---

## 06 · The UI

One page, four regions, no modals. Site voice: numbered sections, tier chips, "what would settle it" on every open row.

**Region 1 — The character strip.** Trio picker (reuses the planner's existing three-class control and `ht()` level rule), stance selector, mitigation toggle `avg | raid`, ability-rate toggle `median | on cooldown`, a `front` checkbox. Every control that widens uncertainty is visibly a *setting*, and the setting string is stamped into the output — `HANDOFF.md` §5 item 4: *a derived number without its settings is not reproducible even by its author.*

**Region 2 — The lane table.** One row per lane: name, swing rate, `E[hit|land]`, DPS, and a source chip. Weapon lanes and ability lanes are **visually separated by a rule**, with the ability block headed *"individually unvalidated"* and the weapon block headed *"predicts both swing rates to under 3% on the one character we can check."* That separation is the honest shape of what we know, and burying it would repeat exactly the fault `HANDOFF.md` §1b reports against this project.

**Region 3 — The delta strip.** The headline. `Thelvorn +10 → Earthshaker +10: −22.8% (−21.7 to −23.9)`, with a per-lane waterfall underneath showing which lanes moved and which did not. Ability lanes appear as *unchanged* bars, which is itself informative — a weapon swap moves two of six lanes.

**Region 4 — The envelope, expanded by default.** Not a footer. The seven `HANDOFF.md` §5 fields rendered as a table: model file and commit, every input with its own tier, the assumptions that are not inputs, `kind: ceiling | delta`, the settings, the residual **component-wise**, where it stops, and what would falsify it. A collapsed envelope is a hidden ceiling.

**Nothing is stored, no account, state travels in the URL** — matching 50 Upgrades exactly.

---

## 07 · Plugging into 50 Upgrades

The seam already proposed in `HANDOFF.md` §6 and it runs one way: **the planner owns *which item*, the model owns *what a swing is worth*.**

### The one function the planner calls

```js
import { deltaFor } from './engine/trio-damage.js';
```

The planner already computes everything the model needs, in `Kt()` at bundle line 10984:

```js
e.weapon && (r === `PRIMARY` ? t.weapons.primary = e.weapon
                             : r === `SECONDARY` && (t.weapons.secondary = e.weapon))
```

and `Gt()` (line 10935) already yields `{ name, damage, delay, ratio, skill, bonus }` — `damage` already tier-upgraded through `jt()`. So the adapter is four lines:

```js
const asWeapon = (w, item) => w && ({
  name: w.name, dmg: w.damage, delay: w.delay, skill: w.skill,
  slots: item.sl, procName: item.fx?.find(f => f.k === 'proc')?.n
});
```

**Where the delta belongs.** `Wn(state, position, ctx)` at line 11748 already builds the baseline totals from the rest of the set with this position emptied and class-blocked items dropped. That is exactly the "before" side of a delta, already computed, already cached by `Xn()`'s key. So a candidate's DPS delta is:

```js
deltaFor(
  { primary: asWeapon(baseline.weapons.primary), secondary: asWeapon(baseline.weapons.secondary) },
  { primary: asWeapon(candidateTotals.weapons.primary), secondary: asWeapon(candidateTotals.weapons.secondary) },
  ctx
).pct
```

It runs only for `position === 'PRIMARY' || 'SECONDARY'` — the same guard `fn()` already uses via `weaponCounts` — so Any Slot needs no change, and the planner's existing copy *"Any Slot takes any wearable item — a worn position, not a hand, so weapon damage scores nothing here"* stays true.

### Three things not to do

**Do not put the damage bonus in `wp.bonus`.** That key is taken: `Ce()` at line 9977 does `let s = L(n?.bonus ?? t.AC_BONUS); s && (a.bonus = s)` — `wp.bonus` is a shield's AC bonus. Use `wp.db`. No shipped row populates either today, which is precisely why it is easy to walk into.

**Do not fold the bonus into `RATIO`.** Tested: because the bonus is additive and barely moves with delay, adding it to `dmg/delay` promotes Rusty Two Handed Hammer 124 places and Abandoned Orc Shovel 133. Ratio stops being even a rough DPS proxy the moment a delay-independent term is inside it.

**Do not let the delta become a ranking key by default.** Ranked by ratio and by modelled main-hand DPS, the planner's 425 PRIMARY-capable melee weapons agree **9 of 10 in the top ten and 23 of 25 in the top twenty-five**. The ordering is not broken. What ratio cannot do is tell a reader *how much* a swap is worth, or that a two-hander and a one-hander at the same ratio are not the same weapon — and that is what a delta adds.

### The EP weight proposal, derived

If a weight is wanted, here it is with its derivation rather than as a taste. Reference point stated because a marginal is meaningless without one: **PAL/MNK/ENC, 40/26 one-hander main hand at +10, level 50, Offensive, haste 85, Wrath 411, average mitigation** (`run4.mjs`).

| key | marginal DPS per unit | normalised so `RATIO = 40` | shipped `melee-dps` |
|---|---|---|---|
| RATIO | 78.42 | **40.00** | 40 |
| DMG | 3.016 | **1.54** | unweighted |
| **DMG_BONUS** | 1.348 | **0.69** | absent |
| STR | 0.104 | **0.05** | 1 |
| HASTE | 0.763 | **0.39** | 2 |
| RATIO, off-hand | 68.68 | **34.5** | same as main |

A point of damage bonus is worth **1/2.24** of a point of DMG on the same weapon, because the roll contributes ~2.1×DMG to an average hit while the bonus contributes 1×B. *(Correction to an earlier pass that proposed `DMG_BONUS 19`: that figure appears to have kept a delay factor. The internally consistent weight against `RATIO 40` is 0.69.)*

**Ship `DMG_BONUS` as a new weightable key beside RATIO and DMG, at weight 0 in all five default profiles**, scored only when `weaponCounts` is true. That gives a reader who knows what they are doing a lever and costs a reader who does not exactly nothing.

**Ship the derived weights as a *second* preset — "Melee DPS, measured" — not as a replacement.** Two of the five numbers above are not scale-free and saying so is the point: worn haste is max-not-sum (`Kt()`: `o > t.haste && (t.haste = o)`), so a haste weight depends entirely on what the character already wears — Cloak of Flames at 36 is worth a great deal to a character with none and exactly zero to one wearing Renard's Belt of Quickness at 41. And **STR's marginal is contested inside this project's own files** and I would mark it *untested* rather than ship 0.05.

---

## 08 · The core scoring function

Real JavaScript, run and tested. Full files at `/tmp/claude-0/-home-user-sky-ledger/caaa72f1-a659-51f4-8828-08bfb34cde0c/scratchpad/tdm/`.

```js
// engine/trio-damage.js
// Every constant carries a tier. `D` = derived (an envelope, not a tier).
// `OPEN` = the tool refuses or bands rather than choosing.

export const SKILL = {
  TWO_HAND: new Set(['2H Slashing', '2H Blunt', '2H Piercing']),
  ONE_HAND: new Set(['1H Slashing', '1H Blunt', '1H Piercing', 'Piercing', 'Hand to Hand'])
};
export const DUAL_WIELD    = new Set(['BRD','BST','MNK','RNG','ROG','WAR']);   // eqlbase, T4
export const DOUBLE_ATTACK = new Set(['BER','MNK','PAL','RNG','ROG','SHD','WAR']);
export const MARTIAL       = new Set(['WAR','PAL','SHD','RNG','MNK','ROG','BER','BRD','BST']);

export const K = {
  P_LAND:        { v: 0.5765, tier: 'M', n: 21122 },
  ACC_OFFENSIVE: { v: 1.081,  tier: 'M', band: [1.00, 1.21] },
  G_AVOID:       { v: 0.0617, tier: 'M', band: [0.0617, 0.0629] },
  STRIKETHROUGH: { v: 0.30,   tier: 'T2' },

  CRIT_RATE:     { v: 0.1272, tier: 'M' },
  CRIT_MULT:     { v: 1.70,   tier: 'M', note: 'rolled part only' },
  CRIT_FLOOR:    { v: 1.1,    tier: 'D',  note: '1.7 * 5 * 0.1272' },
  BER_CRIT_ADD:  { v: 0.06,   tier: 'T2' },
  WAR_CRIT_DMG:  { v: 0.30,   tier: 'T2' },

  // eqlwiki `Game Mechanics` § Working Legends Damage Bonus Formula (T5 prose,
  // added 2026-08-11), corroborated 19/19 against Itempage `Dmg Bon:` statsBlocks
  // (T2) and one client window (M). NOT 0.69 — see the design note.
  HAND_MOD:      { oneHand: 0.8, twoHand: 1.1, tier: 'T5+T2+M' },

  E_RX_BASE:     { v: 0.967, tier: 'D', unsettled: 'FIT_PATH_UNRECORDED' },
  WRATH_BASE:    { v: 365,   tier: 'D' },
  ELAST:         { avg: 0.141 / 104.0, raid: 0.257 / 139.0, tier: 'D' },
  MITF:          { avg: 1.00, raid: 0.73, tier: 'OPEN' },

  MH_CHAIN:      { v: 1.520,  tier: 'M', ci: [1.465, 1.569] },
  OH_CHAIN:      { v: 1.4911, tier: 'M' },
  DW_SUCCESS:    { v: 0.88,   tier: 'M' },
  HASTE_CAP:     { v: 75,     tier: 'OPEN', band: [75, 85] },

  OFFENSE: { WAR:210, MNK:230, ROG:210, RNG:210, BER:210,
             PAL:200, SHD:200, BRD:200, BST:200, SHM:200, CLR:200, DRU:200,
             ENC:140, MAG:140, NEC:140, WIZ:140 },                 // eqlbase, 21/21
  STR_MOD:   { v: 120, tier: 'OPEN' },
  SPELL_ATK: { v: 61,  tier: 'T2' },
  RNG_ATK:   { v: 104, tier: 'T2' },
  WORN_ATK:  { v: 0,   tier: 'M', note: '0 of 2,263 catalogued items carry ATTACK' },

  STANCE: {
    offensive:  { dmg: 2.00, acc: 1.081, rate: 1.00, tier: 'M' },
    balanced:   { dmg: 1.00, acc: 1.00,  rate: 1.00, tier: 'M' },
    defensive:  { dmg: 1.00, acc: 0.95,  rate: 1.00, tier: 'M' },
    berserker:  { dmg: 1.00, acc: 1.01,  rate: 1.90, tier: 'M' },
    evasive:    { dmg: 1.00, acc: 1.00,  rate: 1.00, tier: 'M' },
    magehunter: { dmg: 1.00, acc: 0.97,  rate: 1.00, tier: 'M' },
    ranged:     { dmg: 1.00, acc: 1.081, rate: 1.00, tier: 'M' },
    striker:    { dmg: null, acc: 1.00,  rate: 1.00, tier: 'OPEN' }   // null => refusal
  }
};

export const ABILITY = {
  kick:     { owners:['BST','MNK','RNG','WAR'], mean:58.50,  rate:{med:0.32,max:0.54} },
  bash:     { owners:['PAL','SHD','WAR'],       mean:71.15,  rate:{med:0.33,max:0.54} },
  strike:   { owners:['MNK'],                   mean:35.05,  rate:{med:0.27,max:0.50} },
  smite:    { owners:['PAL'],                   mean:31.30,  rate:{med:0.17,max:0.31}, rider:417 },
  frenzy:   { owners:['BER'],                   mean:57.21,  rate:{med:0.47,max:0.72} },
  backstab: { owners:['ROG'],                   mean:178.69, rate:{med:0.29,max:0.47}, frontPenalty:0.20 }
};

const RESIDUAL = {                       // HANDOFF.md §1 — printed with every level
  fights: 213, belowFloor: 162, floorOverMeasuredMedian: 1.51, ceilingExceeded: 0,
  jos437: { onCooldown: +0.236, medianRates: +0.001, worstLaneAtMedianRates: -0.412 }
};

// --- primitives ------------------------------------------------------------

export const rollMax = dmg => 2 * dmg + 1;                             // U, tier M

/**
 * Main-hand damage bonus. Returns null for a non-melee skill; the caller must
 * pass 0 for an off-hand (measured 0, tier M) rather than calling with the
 * off-hand weapon, so that "no bonus" and "not a melee weapon" stay distinct.
 */
export function damageBonus(skill, dmg, delay, level) {
  if (!SKILL.TWO_HAND.has(skill) && !SKILL.ONE_HAND.has(skill)) return null;
  const hand = SKILL.TWO_HAND.has(skill) ? K.HAND_MOD.twoHand : K.HAND_MOD.oneHand;
  return Math.floor(hand * Math.max(level, dmg) * (Math.min(delay, 50) / 40) * (level / 100));
}

export function wrath({ classes, str, spellAtk = K.SPELL_ATK.v, wornAtk = 0 }) {
  const off     = Math.max(...classes.map(c => K.OFFENSE[c] ?? 0));
  const strTerm = str == null ? K.STR_MOD.v : ((2 * str) - 150) / 3;
  const rngAtk  = classes.includes('RNG') ? K.RNG_ATK.v : 0;
  return off + strTerm + spellAtk + wornAtk + rngAtk;
}

export const eRx = (w, mode = 'avg') =>
  K.E_RX_BASE.v * (1 + K.ELAST[mode] * (w - K.WRATH_BASE.v));

/**
 * Crit as a RATIO against the calibration baseline.
 *
 * `base` (1.08904) is already inside the calibrated closed form, because
 * E_RX_BASE was fitted through it. Only a trio's DEPARTURE from baseline —
 * Berserker crit rate, Warrior crit damage — may be multiplied in.
 * model4.py's lane_dps() multiplies the ABSOLUTE factor on top of the
 * calibrated form and so carries the baseline crit twice; its ability lanes
 * already do this correctly via `critadj`. Whether that is a bug or an
 * absorbed calibration turns on how E_RX_BASE was fitted, which the repo does
 * not record. It cancels exactly out of every delta.
 */
export function critFactor(classes) {
  const rate = K.CRIT_RATE.v + (classes.includes('BER') ? K.BER_CRIT_ADD.v : 0);
  const mult = K.CRIT_MULT.v * (classes.includes('WAR') ? 1 + K.WAR_CRIT_DMG.v : 1);
  const base = (1 - K.CRIT_RATE.v) + K.CRIT_RATE.v * K.CRIT_MULT.v;      // 1.08904
  const abs  = (1 - rate) + rate * mult;
  return { absolute: abs, base, ratio: abs / base };
}

export const swingRate = (delay, hastePct) => (1 + hastePct / 100) / (delay / 10);

/**
 * One weapon lane.
 *   E[hit|land] = critRatio * (critBase * U * E[rx] * Mt + CRIT_FLOOR) + B
 * B is added AFTER the crit (crit acts on the rolled part only) and the stance
 * multiplier is applied LAST, to the whole thing including B.
 */
export function weaponLane(o) {
  const { dmg, delay, skill, level, mainHand, classes, stance, hastePct, mode, w } = o;
  const st = K.STANCE[stance];
  const chain = mainHand
    ? (classes.some(c => DOUBLE_ATTACK.has(c)) ? K.MH_CHAIN.v : 1)
    : (classes.some(c => DOUBLE_ATTACK.has(c)) ? K.OH_CHAIN.v * K.DW_SUCCESS.v : K.DW_SUCCESS.v);

  const rate  = swingRate(delay, hastePct) * chain * st.rate;
  const strk  = classes.includes('RNG') ? K.STRIKETHROUGH.v * K.G_AVOID.v : 0;
  const pLand = Math.min(1, K.P_LAND.v * st.acc) + strk;

  const cf     = critFactor(classes);
  const rolled = cf.base * rollMax(dmg) * eRx(w, mode) * K.MITF[mode] + K.CRIT_FLOOR.v;
  const B      = mainHand ? (damageBonus(skill, dmg, delay, level) ?? 0) : 0;
  const hit    = cf.ratio * rolled + B;

  return { dps: rate * pLand * hit * st.dmg, rate, pLand, hit, B, U: rollMax(dmg) };
}

// --- the core scoring function --------------------------------------------

/**
 * scoreLoadout — never returns a bare number.
 * Returns { lanes, band, procLanes, refusals, envelope }.
 */
export function scoreLoadout(loadout, ctx) {
  const cls      = ctx.classes;
  const level    = Math.max(...cls.map(c => ctx.levels?.[c] ?? 50));
  const stance   = ctx.stance ?? 'offensive';
  const mode     = ctx.mode ?? 'avg';
  const rates    = ctx.laneRates ?? 'med';
  const refusals = [];

  if (K.STANCE[stance].dmg === null)
    refusals.push({ code: 'STANCE_UNMODELLED', stance,
      why: 'Striker is not a flat multiplier and its own crit test refutes one.',
      settle: 'One bash lane floored at 1 damage, in Striker, for 200 swings.' });

  if (ctx.str == null)
    refusals.push({ code: 'STR_UNKNOWN',
      why: 'Whether STR converts to Wrath at all is contested inside this project\'s own files: '
         + 'a 255 cap would pin the modifier, a client panel reads INT 295, and eqlwiki adds '
         + 'a `STR < 75 => 0` clause this chain omits.',
      settle: 'One client Statistics panel at two known STR values.' });

  if (mode === 'raid')
    refusals.push({ code: 'MITIGATION_UNTESTABLE',
      why: 'Seven properly-paired boss fights span 0.41 to 2.01, median 0.91. They cannot resolve a 0.73.',
      settle: 'raidstats.py to record our own max non-crit hit per fight; U = 2*DMG+1 then backs out gear.' });

  const w     = wrath({ classes: cls, str: ctx.str });
  const haste = ctx.hastePct ?? (K.HASTE_CAP.v + (cls.includes('MNK') ? 10 : 0));
  const lanes = [];
  const twoHanded = loadout.primary && SKILL.TWO_HAND.has(loadout.primary.skill);

  if (loadout.primary) {
    const p = loadout.primary;
    lanes.push({ id: 'primary', label: p.name, weapon: true,
      ...weaponLane({ ...p, level, mainHand: true, classes: cls, stance, hastePct: haste, mode, w }) });
  }

  if (loadout.secondary) {
    const s = loadout.secondary;
    if (twoHanded) {
      refusals.push({ code: 'TWO_HANDER_BLOCKS_OFFHAND', item: s.name,
        why: 'A two-handed primary occupies both hands.',
        standing: 'Classic-inherited and unmeasured on Legends. No inventory export in this '
                + 'corpus shows a two-handed primary, so the corpus could not have settled it.',
        settle: 'One client paperdoll with a two-hander equipped.' });
    } else if (!s.slots?.includes('SECONDARY')) {
      refusals.push({ code: 'OFFHAND_NOT_LEGAL', item: s.name,
        why: '219 of 431 melee weapons list no SECONDARY; 214 are ["PRIMARY"] exactly.' });
    } else if (!cls.some(c => DUAL_WIELD.has(c))) {
      refusals.push({ code: 'NO_DUAL_WIELD',
        why: 'No class in this trio has Dual Wield.', src: 'eqlbase.com/skills/dual_wield' });
    } else {
      lanes.push({ id: 'secondary', label: s.name, weapon: true,
        ...weaponLane({ ...s, level, mainHand: false, classes: cls, stance, hastePct: haste, mode, w }) });
    }
  }

  // Ability lanes. Individually unvalidated — see LANE_MIX_UNVALIDATED.
  const st    = K.STANCE[stance];
  const scale = (eRx(w, mode) * K.MITF[mode]) / (K.E_RX_BASE.v * K.MITF.avg);
  const pLand = Math.min(1, K.P_LAND.v * st.acc);
  const cf    = critFactor(cls);
  for (const [id, a] of Object.entries(ABILITY)) {
    if (!a.owners.some(c => cls.includes(c))) continue;
    const r = a.rate[rates];
    let dps = r * pLand * a.mean * scale * (st.dmg ?? 1) * cf.ratio;
    if (a.rider) dps += r * pLand * a.rider;          // flat, not stance-doubled, never crits
    if (id === 'backstab' && ctx.front) dps *= a.frontPenalty;
    lanes.push({ id, label: id, dps, ability: true, rate: r });
  }
  if (lanes.some(l => l.ability))
    refusals.push({ code: 'LANE_MIX_UNVALIDATED',
      why: 'Against the one fully-pinned character these lanes miss by -41% to +9% individually '
         + 'while their total lands at +0.1%. That is cancellation, not agreement.' });

  // Procs are PER MINUTE. Haste and multi-attack buy none. Armour sockets fire zero lanes.
  const procLanes = (twoHanded ? 1 : (loadout.secondary && !twoHanded ? 2 : 1))
                  + (loadout.range && cls.includes('RNG') ? 1 : 0);

  const total   = lanes.reduce((s, l) => s + l.dps, 0);
  const spread  = (K.MH_CHAIN.ci[1] - K.MH_CHAIN.ci[0]) / K.MH_CHAIN.v;   // 0.0684
  const band    = { low: total * (1 - spread / 2), mid: total, high: total * (1 + spread / 2) };

  return {
    lanes, band, procLanes, wrath: w, haste, level, stance, rates,
    denominator: 'engaged',
    envelope: {
      model:   { file: 'engine/trio-damage.js', chain: 'DAMAGE-CHAIN.md', commit: BUILD_SHA },
      inputs:  [['P(land)','M'], ['U = 2*DMG+1','M'], ['crit 1.70 @ 12.72%','M'],
                ['multi-attack 1.520','M'], ['stance x2.00','M'],
                ['damage bonus 0.8/1.1','T5 formula + T2 x19 + M window'],
                ['Offense caps','M-validated, eqlbase 21/21'],
                ['E[rx] 0.967','D — fit path unrecorded'],
                ['MITF raid 0.73','OPEN — untestable by this instrument'],
                ['ability lane means','M, +/-41% per lane on the one pinned character']],
      assumptions: ['weapons as given, not best-in-slot', `stance ${stance} held permanently`,
                    `ability rates = ${rates}`, 'one target', ctx.front ? 'tanking' : 'not tanking',
                    'no movement, no deaths', 'no partner buffs unless listed'],
      kind:     'ceiling',
      settings: { stance, mode, rates, haste, level, denominator: 'engaged' },
      residual: RESIDUAL,
      stops:    ['level 50', 'one target', 'no movement', 'no deaths', 'engaged denominator'],
      falsifies:['any logged fight whose per-character DPS exceeds the printed ceiling',
                 'any set of fights with gear recorded whose median lands within 20% of the floor'],
      refusals
    }
  };
}

/**
 * deltaFor — the only output intended for a headline.
 *
 * A ratio on the same character cancels swing rate, haste, stance, multi-attack
 * and (exactly) the crit form. Verified: the damage-bonus delta is +31.8% under
 * both the single- and double-crit forms, while the LEVEL moves 14.7% across the
 * same eight variants. The surviving disagreement is E[rx]'s Wrath elasticity,
 * measured two ways here as a 2.3-point spread — hence DELTA_SPREAD.
 */
const DELTA_SPREAD = 2.3;

export function deltaFor(before, after, ctx) {
  const a = scoreLoadout(before, ctx), b = scoreLoadout(after, ctx);
  const byLane = {};
  for (const l of a.lanes) byLane[l.id] = { before: l.dps, after: 0, label: l.label };
  for (const l of b.lanes) (byLane[l.id] ??= { before: 0, after: 0, label: l.label }).after = l.dps;

  const pct = 100 * (b.band.mid / a.band.mid - 1);
  return {
    pct: { low: pct - DELTA_SPREAD / 2, mid: pct, high: pct + DELTA_SPREAD / 2 },
    byLane,
    refusals: [...a.envelope.refusals, ...b.envelope.refusals],
    envelope: { ...b.envelope, kind: 'delta',
      note: 'A delta cancels the global scale. The level does not, and the level is a ceiling.' }
  };
}
```

### Test output, run

```
PAL/MNK/ENC, Thelvorn +10 (40/26) + Wu's Fist +10 (32/22), offensive, median rates
   Thelvorn, Blade of Light +10   141.2
   Wu's Fist of Mastery +10       101.5
   kick 24.8 · bash 31.1 · strike 12.5 · smite 51.2
   TOTAL band 350 / 362 / 375        measured on jos437: 381.0   (-5.0%)
   procLanes 2 · wrath 411 · refusals: STR_UNKNOWN, LANE_MIX_UNVALIDATED

swap the main hand to Earthshaker +10 (74/70, 2H)
   -36.9%   primary 141.2 -> 109.1 · secondary 101.5 -> 0 · abilities unchanged
   refusals: TWO_HANDER_BLOCKS_OFFHAND
```

Damage-bonus validation, run against the printed `Dmg Bon` fields: Skycleaver 2H 30/35 → **24** (printed 24) · Efreeti Standard 1H 3/10 → **5** (printed 5) · Earthshaker +10 2H 74/70 → **50** (client window 50) · Whitened Treant Fists 1H 14/28 → **13 at level 49** (printed 13), 14 at level 50 — which is how the thirteen 1H rows resolve, and eqlwiki's own level-49 observations independently include two of them.

---

## 09 · What it will not tell you — the site-voice section

- **It will not tell you your DPS.** It computes a ceiling. 162 of 213 logged raid fights fall below this model's own floor, and every number it has ever produced was a ceiling printed as an estimate.
- **It will not compare against your meter.** Four shipped Legends meters divide by four different things and the difference reaches 1.75× on one fight. Everything here is engaged DPS and says so on every output.
- **It will not price Striker stance, archery, or a two-hander against a pair.** Striker is not a flat multiplier; archery has nine low-level lines in the whole corpus; and no character in this corpus has ever equipped a two-hander.
- **It will not tell you what Strength is worth.** Whether it converts to damage at all is contested inside this project's own files.
- **Its weapon half and its ability half are not equally good.** Both swing rates predict from constants alone to under 3% on the one character where gear, level and stance are all pinned. The ability lanes miss by −41% to +9% individually and have only ever agreed in total.
- **It will not rank trios.** Order is more trustworthy than value, and even the order is built on best-in-slot assumptions that belong to one player.

---

## 10 · Corrections to us that this design bakes in

Send these with the contribution rather than letting the site inherit them.

1. **`HandMod` 1H is 0.8, not 0.69.** Published on eqlwiki twelve days before our first commit carrying it. Fails 0 of 13 T2 rows. Fix `DAMAGE-CHAIN.md` line 55 and line 376, `SOURCING.md` §3 (regrade from *M / clean* to *T5 formula + T2 corroboration*), and `model4.py`'s `bonus()` call. Strike "the only 1H `Dmg Bon` line on a wiki statblock" — there are thirteen. Either publish the `Garduk`/`Arydryidriyorn` readings or drop the tier-M claim on them.
2. **The crit factor is applied twice in `model4.py`'s weapon lanes** and once, correctly, in its ability lanes. Resolve it together with `E_RX_BASE`, and record the fit path this time.
3. **`model4.py` line 67, `up10()`, applies the +1/tier floor to weapon damage.** The planner's `jt()` does not, and eqlwiki's `Item Upgrade System` carves weapon damage out into its own percentage rule. Ours turns Efreeti Standard (3 dmg / 10 delay) into a 13-damage off-hand at +10 and forced the empirical `OH_RATE_CAP = 1.42` at line 33 to stop the optimiser choosing it — whose comment names Efreeti Standard by name. **If `jt` is right, that cap was patching our own upgrade rule.** One client window of any sub-10-damage weapon at any tier ≥ 1 settles it.
4. **`EQUIPMENT-TRUTH.md` presents the 10%/tier rule without exception.** Haste and the regen family take a flat +1 per tier: the planner's own Cloak of Flames capture reads 36 → 43 at +7, where the scaled rule gives 61.
5. **Our haste measurement of 1.900 must not be quoted as settling anything.** It is unattributed, sits above the 1.75 ceiling both independent sources give, comes from a file with no player haste buff or stance line, and coincides exactly with our measured berserker-stance rate multiplier. `SOURCING.md` §2 also describes eqlwiki's Haste Guide as carrying "the exact classic percentage-divides-delay formula the scanner flags"; that does not survive reading the page, which states *"Haste is measured in Rate of Attack Increase, NOT Delay Decrease"* and carries a Legends-authored caps table with a 51–60 row that no P99 import could have.
6. **Tremor's target cap is 24, not 25** — its description field reads "as many as 24 others nearby." Earthquake is the one that reads 25. Fix `DDD.md` §1.
7. **"232 of 444 melee weapons are PRIMARY-only" does not reproduce.** Against the shipped catalogue: **431 melee weapons, 219 without SECONDARY, 214 with `sl` exactly `["PRIMARY"]`.** The Aldryn/Thelvorn conclusion is unaffected — both are `sl:["PRIMARY"]`, `cl:["PAL"]`, 20/26 — but the count should be re-derived before anyone prints it.