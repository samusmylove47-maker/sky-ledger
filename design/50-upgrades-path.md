# THE 50 UPGRADES UPGRADE PATH
## A change plan for `eqlsource.com/EQL50ups`, in priority order

**Written for:** an engineer with the planner source in front of them and no context from the session that produced this.
**Scope:** additions only. Nothing here proposes a rewrite, a new framework, a DPS screen, or a change to the sourcing standard. Every change is designed to survive that standard rather than route around it.

---

## 0. Ground rules, and how to read this document

### 0.1 Tier labels
Every number below carries the tier the site's own `/sources.html` hierarchy assigns it:

| Tag | Meaning |
|---|---|
| **M** | measured — read off a live client window, or parsed from a client combat log |
| **T1** | patch notes |
| **T2** | structured wiki data — a named field on a named page (an `{{Itempage}}` `statsBlock`, a spell table row) |
| **T3** | named community guide |
| **T4** | aggregator |
| **T5** | wiki prose, including prose that happens to live inside a machine-shaped template parameter |
| **derived** | computed by this project from other numbers. Never a tier on its own; it inherits the worst tier of its inputs and must be badged. |

The rule that matters most for this work: **a structured field is a container, not a provenance.** Cite the field, never the site.

### 0.2 Verification base
Everything below was checked against the shipped artefacts, not against a description of them:

- `assets/index-CZSHStxu.js` — 503,385 bytes, `md5 f5bbbc334d2bc21e603c466f3ef5e2d8`.
- A beautified copy of that file, 23,899 lines. **All line numbers in this document refer to that beautification.** Identifiers (`Kt`, `Gt`, `Wn`, `jt`, …) are minifier output and *will not match your source tree.* Each one is quoted with enough of its body to find by content. Search for the code fragment, not the name.
- `data/meta.json` — `v: 1`, `builtAt: 2026-08-26T18:00:13.371Z`.
- `data/contamination.json`.
- All 19 shards under `data/items/` — 4,004 rows, 3,663 unique names. Every published count in `meta.json.counts` reproduces exactly (3,663 / 2,263 slotted / 1,713 statted / 538 with effects / 299 with an id / tier-M 5, tier-2 2,045, tier-5 126, unattributed 1,487).

Catalogue facts re-derived today, used throughout (all **T2**, a census of the shipped shards):

```
560   rows carry wp
431   melee weapons        (wp.skill in the seven melee labels)
123   two-handers          (2H Slashing | 2H Blunt | 2H Piercing)
425   PRIMARY-capable melee
  0   of the 123 two-handers list SECONDARY in sl
219   of 431 melee lack SECONDARY;  214 have sl exactly ["PRIMARY"]
265   of 431 melee have base dmg < 10   (61.5%)
  0   of 3,663 rows populate wp.bonus
  0   of 3,663 rows carry an ATTACK stat
146   rows carry a k:"proc" effect; 55 of those carry no slot at all;
      of the 91 that carry a slot, 91 are PRIMARY/SECONDARY/RANGE and 0 are armour
 38   wp rows carry no skill — all AMMO arrows, and none carries a delay
526   PRIMARY rows, of which 101 carry no wp at all (held items, instruments)
383   SECONDARY rows, of which 171 carry no wp at all (shields)
```

### 0.3 Three rules the changes must not break

1. **Sourced and derived never share typography.** The planner's whole argument is that "scraped" and "computed" are different kinds of thing. Every derived figure introduced below carries a badge at the point of use, exactly like the existing `Tier 5 · wiki stats, era unplaced` chip.
2. **Absent is not zero.** Where a value cannot be computed, print `—` and say why. Do not print `0`.
3. **Where two sources disagree, print the disagreement.** Two changes below (P1's rounding caveat, P5's upgrade-curve divergence) exist only to say "this is unsettled" in public. That is the site's own convention and it is cheaper than being wrong.

---

# P1 — Damage bonus (flagship)

**Why first:** the planner names this gap in its own copy, in four places, and the gap is closable today with a T2 harvest plus a published formula. It is the only change here that adds a number the tool does not currently have.

### 1.0 What the site says now

`/tools/50-upgrades.html` §03, "What it will not tell you":
> "Damage bonus is absent. A client window shows one, no source carries it per item, and it appears to be derived from level and weapon type rather than stored on the item."

Bundle line 16082, Contamination callout, figure `0`, label `damage bonuses printed`:
> "The live client shows a Dmg Bon line and no source in this project carries it per item, so this planner prints nothing there. A dry streak is a ceiling, not a zero, and an absent figure is shown as absent rather than reconstructed from a classic formula."

`data/meta.json` → `dataReliability.dmgBonus.note`:
> "The client shows a Dmg Bon line (13 on Whitened Treant Fists, 50 on Earthshaker). No source carries it per item; jmoyers has it on 1 item only. It is probably derived from character level and weapon type. `wp.bonus` is emitted only where a source actually printed it."

`data/contamination.json` → signature `dmg-bonus`, `settle`:
> "Two client tooltips for the same weapon at different character levels would show whether it is stored or derived. Until then it cannot be computed, so it is not printed."

**Three of those four sentences are now false, and the fourth's settle condition has been met by someone else.** The site's read of the *shape* — derived from level and weapon type, not stored on the item — was right, and is now confirmed.

### 1.1 The evidence, by tier

**T5 — the formula.** eqlwiki `Game Mechanics`, section "Main Hand Damage Bonus on EverQuest Legends" → "Working Legends Damage Bonus Formula", added 2026-08-11 by user Maergoth (revision size 41269→43724). Verbatim:

```
Damage Bonus Raw = Hand Modifier × max(Character Level, Weapon Damage)
                   × (min(Weapon Delay, 50) / 40) × (Character Level / 100)
Hand Modifier: One-Handed 0.8 · Two-Handed 1.1
```

This is wiki prose, so it is **T5 by the site's own rule**, and it says of itself: "It should not yet be described as the exact server formula." The same section publishes 14 rows it labels "Confirmed Legends Observations … directly observed in-game", including the exact test `contamination.json`'s settle line asks for — *one* 24-delay one-hander at four character levels: L32→5, L48→12, L49→12, L50→13. One weapon, four levels. That answers stored-vs-derived on its own.

It earns belief only because two independent bodies of evidence reproduce it.

**T2 — 19 eqlwiki `{{Itempage}}` statsBlocks carry a literal `Dmg Bon:` line.** 18 of the 19 are already rows in the shipped catalogue (Skycleaver is the exception). I evaluated the published formula against all 18, with `floor()`, using the catalogue's own `dmg`/`dly`/`skill`:

| item | skill | dmg | dly | printed | B(L50) | B(L49) |
|---|---|---|---|---|---|---|
| Efreeti Standard | 1H Blunt | 3 | 10 | 5 | **5** | 4 |
| Bixie Sword Blade | 1H Slashing | 2 | 16 | 7 | 8 | **7** |
| Djinni Stave | 1H Blunt | 5 | 19 | 9 | **9** | **9** |
| Sphinx Claw | 1H Slashing | 12 | 20 | 10 | **10** | 9 |
| Windhowl | Hand to Hand | 12 | 22 | 10 | 11 | **10** |
| Spirit Render | Hand to Hand | 10 | 23 | 11 | **11** | **11** |
| Efreeti War Club | 1H Blunt | 11 | 26 | 12 | 13 | **12** |
| Efreeti Long Sword | 1H Slashing | 11 | 28 | 13 | 14 | **13** |
| Whitened Treant Fists | 1H Blunt | 14 | 28 | 13 | 14 | **13** |
| Efreeti Mace | 1H Blunt | 10 | 30 | 15 | **15** | 14 |
| Spiroc Battle Staff | 1H Blunt | 8 | 30 | 15 | **15** | 14 |
| Spiroc Wingblade | 1H Slashing | 15 | 38 | 18 | 19 | **18** |
| Blade of Abrogation | 1H Slashing | 20 | 39 | 19 | **19** | 18 |
| Efreeti War Axe | 2H Slashing | 12 | 28 | 19 | **19** | 18 |
| Efreeti War Staff | 2H Blunt | 10 | 30 | 20 | **20** | 19 |
| Efreeti War Maul | 2H Blunt | 15 | 35 | 24 | **24** | 23 |
| Efreeti Wind Staff | 2H Blunt | 12 | 36 | 24 | **24** | 23 |
| Efreeti Zweihander | 2H Slashing | 24 | 45 | 30 | **30** | 29 |

**18 of 18 fit, at level 49 or level 50.** All six two-handers fit at 50. Of the twelve one-handers, six fit at 50, four fit at 49, two fit at both. The level split is not a free parameter: eqlwiki's own independently-published level-49 observations include 1H delay 22→10 and delay 23→11, which are two of these rows unchanged.

Solving for the feasible modifier band under truncation:
- Six 2H rows at L50 force the two-handed modifier into **[1.0971, 1.1022)** — a 0.5%-wide band containing 1.10.
- The seven L50-consistent 1H rows force the one-handed modifier into **[0.8000, 0.8205)**. Note the lower endpoint: **0.8 is the smallest value that fits.** Anything below it fails, which is why a lower constant looks plausible on any single row and fails on all of them.

**M — the site's own client window.** `it-PRIMARY.json` → Earthshaker → `sdc`: *"observed in a live client window at +10 — Base Dmg 74, Delay 70, Ratio 1.057, Strength 16, Stamina 16, SV Void 10."* `1.10 × max(50, 74) × (50/40) × 0.50 = 50.875 → 50`, and `meta.json` records the client showing 50. This is the row that proves the formula takes **tier-upgraded** damage, not base damage: at +0 Earthshaker's damage is 37 and `max(50,37)=50` gives 34; only the upgraded 74 gives 50.

### 1.2 What the site currently believes about `jmoyers` is a refresh gap, not a parser bug

`meta.json.provenance.repos[0]` pins `jmoyers/everquest-companion` at `sha d25455e`, `src/main/data/items.json`, role *"enrichment: iconId, typed effects, statsBlock, broad name coverage"*. At that pinned commit, 3 items carry `Dmg Bon` inside `statsBlock`. At that repository's head (`fd5e5bb`, 2026-08-27 — one day after this build), 20 do. Every one of the wiki lines was added by a single editor between 2026-08-18 and 2026-08-23, in one Plane of Sky pass.

So: at the moment the sources were captured, the sentence was arguably true. It is not true now. Note also that jmoyers' *structured* `stats` array carries no damage-bonus key on any of its 11,534 items — the figure lives only inside the raw `statsBlock` string, which is precisely the field `meta.json` says is ingested from that repo.

### 1.3 The change

#### 1.3a Pipeline — harvest the 18 (T2, no derivation at all)

Refresh the `jmoyers` pin (or re-scrape eqlwiki directly), and in the statsBlock parser that already extracts DMG and Atk Delay, add:

```js
const m = /Dmg\s*Bon(?:us)?:\s*(\d+)/i.exec(statsBlock)
if (m) wp.db = Number(m[1])          // T2, harvested
```

**Do not put it in `wp.bonus`.** That key is taken. Bundle line 9979, inside the weapon-record builder (`function Ce(e, t)`):

```js
let s = L(n?.bonus ?? t.AC_BONUS);
s && (a.bonus = s)
```

`wp.bonus` is a **shield's AC bonus**. It happens to be unpopulated on all 3,663 rows today, which is exactly why it is easy to walk into. Use a new key. I use `wp.db` below.

Watch one upstream hazard while you are in there: two label conventions exist. The 19 rows spelled `Dmg Bon:` are internally consistent. Rows spelled `Dmg Bonus:` are not — a Butcherblock hammer prints 113 on a 45-delay two-hander against Efreeti Zweihander's 30 at the same delay, and Cudgel of the Fool's `Dmg Bonus 40` does not reproduce under any modifier. **Harvest `Dmg Bon:` only, and treat `Dmg Bonus:` as a suspect source value** — this is the same two-authoring-conventions phenomenon the planner already documents for tradeability flags.

#### 1.3b Engine — one pure function

New module, no dependencies:

```ts
// engine/dmgBonus.ts
//
// Source: eqlwiki `Game Mechanics` § "Working Legends Damage Bonus Formula"
//   (T5 — wiki prose; the page states it "should not yet be described as the
//    exact server formula").
// Corroboration: 18 eqlwiki {{Itempage}} statsBlock `Dmg Bon:` fields (T2),
//   all 18 reproduced exactly at level 49 or 50; and one live client window
//   on Earthshaker +10 (M), which reads 50 against a predicted 50.

export const TWO_HANDED = new Set(['2H Slashing', '2H Blunt', '2H Piercing'])

// Accepts both the catalogue's current `Piercing` label and the `1H Piercing`
// label a separate correction proposes; this set must survive that rename.
export const MELEE = new Set([
  '1H Slashing', '1H Blunt', 'Piercing', '1H Piercing', 'Hand to Hand',
  '2H Slashing', '2H Blunt', '2H Piercing',
])

export function handModifier(skill?: string): 0.8 | 1.1 | null {
  if (!skill || !MELEE.has(skill)) return null
  return TWO_HANDED.has(skill) ? 1.1 : 0.8
}

/**
 * @param dmg   the TIER-UPGRADED damage — i.e. jt(wp.dmg, upgrade), not wp.dmg.
 *              Proved by the Earthshaker +10 client window (M).
 * @param delay wp.dly (never upgraded; the planner does not scale delay)
 * @param level the character level (see §1.3c)
 */
export function derivedDmgBonus(
  skill: string | undefined, dmg: number, delay: number, level: number,
): number | null {
  const hand = handModifier(skill)
  if (hand === null) return null
  if (!(dmg > 0) || !(delay > 0) || !(level > 0)) return null
  return Math.floor(hand * Math.max(level, dmg) * (Math.min(delay, 50) / 40) * (level / 100))
}
```

**Two constants that are settled, and one that is not.**

- Two-handed **1.10** — settled to within 0.5% by six printed figures plus one client window. Ship it.
- One-handed **0.80** — the published value, and the exact lower endpoint of the band the twelve one-handed rows allow. Ship it. Note for anyone who finds an older number in a neighbouring repository: a constant of 0.69 appears in this project's `DAMAGE-CHAIN.md`; it fits **0 of 12** one-handed rows, missing every one low by 1 to 3, and the two client windows it was back-solved from have no parse anywhere in that repository. It is wrong. Do not use it, and do not treat the fact that it existed as a reason to withhold the one-handed arm.
- **Rounding below level 50 — unsettled.** The wiki's own directly-observed rows at L32 and L48 on a 24-delay one-hander are off by one under truncation. Also unsettled: the `max(Character Level, Weapon Damage)` branch has never been isolated in-game. Both are invisible at level 50 with sub-50 damage, which is almost every row shipped. §1.3d says what the UI shows instead.

#### 1.3c Where the level comes from

The planner keeps a level **per class** (`ctx.levels`, normalised by `Ze()`, defaulting to `1`) because item level requirements are checked per qualifying class — the character page already says so: *"an item's level requirement is checked against the class that qualifies you for it."* The damage formula wants a **character** level, and the client's `/who` line prints one number for a trio (`[50 PAL/MNK/ENC]`).

```ts
export function characterLevel(ctx?: { classes: string[]; levels: Record<string, number> }) {
  if (!ctx?.classes.length) return null
  const lv = Math.max(...ctx.classes.map(c => ctx.levels[c] ?? 1))
  return lv > 1 ? lv : null      // 1 is the default, not a statement
}
```

Two things to state in the popover rather than hide:
- Using the max across the trio is an **assumption**, not a measurement. It matches the single level the client's `/who` line prints, and it is identical to any other reading whenever the three levels are equal, which is the normal case. The existing `st(ctx)` helper (first class's level) is the alternative and agrees in that case.
- **Level 1 is treated as "not set", not as "level 1".** `Ze()` defaults every class to 1, so the planner cannot distinguish a fresh loadout from a genuine level-1 character. At level 1 the formula returns 0 for nearly every weapon, and printing `0` would violate the site's own absent-is-not-zero rule. Print `—` and the hint *"set a level on the character page"* instead.

#### 1.3d Where it is computed, and where it renders

**Computed at the aggregator, not in the per-item scaler.** Bundle line 10935, `function Gt(e, t)`, builds the scaled view of one item at one tier. It has no level and no position, so it cannot decide this. Bundle line 10984, `function Kt(e)`, iterates equipped positions and ends each with:

```js
e.weapon && (r === `PRIMARY`
  ? t.weapons.primary = e.weapon
  : r === `SECONDARY` && (t.weapons.secondary = e.weapon))
```

Extend `Kt` with an optional context argument (default `undefined`, so every existing call site keeps its behaviour):

```js
function Kt(entries, ctx /* optional */) {
  …
  if (e.weapon) {
    if (r === `PRIMARY`) {
      t.weapons.primary = { ...e.weapon, dmgBonus: dmgBonusFor(i, e.weapon, ctx) }
    } else if (r === `SECONDARY`) {
      t.weapons.secondary = e.weapon        // main hand only — measured 0 off-hand (M)
    }
  }
}
```

where

```ts
function dmgBonusFor(item, scaledWeapon, ctx) {
  if (item.wp?.db != null) return { value: item.wp.db, standing: 'T2' }   // harvested wins
  const level = characterLevel(ctx)
  if (level === null) return { value: null, standing: 'no-level' }
  const v = derivedDmgBonus(scaledWeapon.skill, scaledWeapon.damage, scaledWeapon.delay, level)
  if (v === null) return { value: null, standing: 'not-melee' }
  return { value: v, level, standing: 'derived', approximate: level < 50 }
}
```

`scaledWeapon.damage` is already `jt(e.wp.dmg, t)` — the tier-upgraded value — which is what the Earthshaker window validates.

**Render site 1 — the Weapons card in the Stat sheet**, bundle lines ~20061–20085. Today the Primary row prints:

```
74/70   dmg/dly · ratio 1.057
```

Add a third term:

```
74/70   dmg/dly · ratio 1.057 · Dmg Bon 50
```

and, on rows where the standing is `derived`, a chip in the same family as the existing `Tier 5 · wiki stats, era unplaced` chip, reading **`Tier 5 formula · Tier 2 corroboration`**. On the 18 harvested rows the chip reads **`Tier 2 · eqlwiki statblock`**.

**Never suppress the Secondary row's absence silently.** Print one hint under the card: *"Damage bonus is main hand only. The off-hand measures zero."* (**M**, from combat-log parses in the neighbouring project.) This matters because Efreeti Standard is `sl: ["SECONDARY"]` and the wiki prints a `Dmg Bon: 5` on it — an item that can never be a main hand, carrying a figure it will never deliver.

**Render site 2 — the item dialog.** The item card is position-free, so label it explicitly: `Dmg Bon (main hand) 5`.

**Render site 3 — the swap diff.** Bundle line 11824, `function Qn(e, t, n, r = St)`, is the candidate-vs-worn comparison; four call sites, two of which know the slot. Add an options bag with defaults that preserve current behaviour:

```js
function Qn(cand, candTier, worn, wornTier, opts = {}) {
  …
  if (opts.position === 'PRIMARY' && opts.ctx) {
    // push a DMG_BONUS row computed on both sides
  }
}
```

This matters more than it sounds: on a big two-hander the bonus is **not constant across +0..+10**, because it climbs once upgraded damage passes character level. Earthshaker's bonus goes 34 → 50 across the slider with no other term moving.

**Do not add it to `zn(e, t)`** (line 11681). `zn` is the generic per-item stat list, and it feeds three things that would be corrupted by a main-hand-only, level-dependent figure: the row subtitle builder `Bn` (line 11702), the planar-set stat summation at line 17673 (which would *add up* damage bonuses across a set — nonsense), and the compare map at 11825. Compute at the render sites instead.

#### 1.3e Build-time assertion — the cheapest audit on the site

The 18 harvested rows become an anchor set. Add a build check:

```js
// pipeline/checks/dmgBonus.mjs
for (const row of catalogue.filter(r => r.wp?.db != null)) {
  const d = jt(row.wp.dmg, TIER0)
  const fits = [49, 50].some(L => derivedDmgBonus(row.wp.skill, d, row.wp.dly, L) === row.wp.db)
  assert(fits, `${row.n}: printed ${row.wp.db}, derived ${…} at L49/L50`)
}
```

Today this passes 18 of 18. It runs on every build, in public, exactly like the contamination scanner, and it turns the `dmg-bonus` signature from "nothing to mark" into a real marked/unmarked count. If a rescrape brings in a row that breaks it, you find out at build time and the row is named.

#### 1.3f Copy changes (do these in the same commit, or the tool contradicts its own sources page)

`data/meta.json` → `dataReliability.dmgBonus` — replace wholesale:

```json
{
  "confidence": "derived-with-anchors",
  "note": "eqlwiki's Game Mechanics page publishes a working Legends formula (Tier 5 prose): Hand Modifier × max(Character Level, Weapon Damage) × (min(Delay, 50) / 40) × (Level / 100), with Hand Modifier 0.8 one-handed and 1.1 two-handed. It reproduces all 18 `Dmg Bon:` figures on eqlwiki item statblocks that this catalogue also holds (Tier 2), at level 49 or 50, and it reproduces the +10 Earthshaker client window exactly (Tier M, 50 against a predicted 50). Where a source printed the figure it is shown as Tier 2; everywhere else it is derived and badged as derived. Main hand only — the off hand measures zero. Two things the wiki states about itself and this planner repeats: the rounding rule below level 50 is unsettled, and the max(Level, Damage) branch has not been isolated in game. Both are invisible at level 50 with sub-50 damage."
}
```

`data/contamination.json` → signature `dmg-bonus`:
- `classic`: correct it. The current text — *"Classic printed a Dmg Bonus line on weapons, derived from character level and weapon delay"* — merges two cases. In classic EverQuest the **one-handed** bonus was a function of level alone; delay entered only for two-handers. eqlwiki's Game Mechanics page names the old one-handed formula outright as `floor((Level - 25) / 3)`.
- `legends`: replace with the formula, the 18-of-18 anchor result, and the Earthshaker window.
- `settle`: mark settled and cite the readings.
- `findings[0]`: `"18 of 18 harvested Dmg Bon figures reproduce from the published formula. Where a source printed the figure the planner prints the source's; everywhere else it prints a derived figure, badged."`

Bundle line 16080–16082, the Contamination callout: the figure `0` and the label `damage bonuses printed` become `18` and `damage bonuses sourced, the rest derived and badged`, with body text saying which is which.

`/tools/50-upgrades.html` §03: the damage-bonus bullet moves out of "What it will not tell you" and into the page body as a derivation with its standing.

#### 1.3g A signature worth adding while you are here

`data/contamination.json`, new signature `dmg-bonus-table`, group `changed`. Two eqlwiki **class pages** carry a section headed "Primary Hand Damage Bonuses" giving a flat level-only table — *"Level 28: 1 … Level 46: 7, Level 49: 8, Level 52: 9, Level 55: 10, Level 58: 11"* — with the line "This is the same for all melee classes." It is a straight classic import: it runs to levels 52, 55 and 58, which a level-50 game cannot reach. At level 50 it yields a flat **8** for every one-hander, against observed one-handed figures of 5, 7, 9, 10, 10, 11, 12, 13, 13, 15, 15, 18, 19 (**T2**) and a client reading of 13 on Whitened Treant Fists (**M**).

It is **unevenly marked in exactly the way the scanner exists to catch**: the Monk page carries the table under a red banner reading `'''This is not yet confirmed for EverQuest Legends.'''`; the Warrior page carries the identical table bare. One marked, one unmarked, and that is the whole population. `markRule`: a class page carrying the table without the banner is an unmarked hit.

This is the first signature the page could close on the day it ships, which is worth having on a page where every other row counts hits and closes nothing.

### 1.4 Acceptance

- Earthshaker +10, level 50 → `Dmg Bon 50`, chip reads `Tier 5 formula · Tier 2 corroboration`.
- Efreeti Standard in SECONDARY → Weapons card shows no bonus on the Secondary row; item dialog shows `Dmg Bon (main hand) 5` badged `Tier 2`.
- A 40/26 one-hander at +10, level 50 → 13. At level 30 → prints a range `7–8`, not `7`.
- No level set anywhere → `—` plus the hint. Never `0`.
- An arrow (38 rows carry `wp` with no `skill` and no `dly`) → `—`, silently.
- A two-hander in an Any Slot → nothing changes; `Kt` only populates `weapons` for PRIMARY/SECONDARY, and the existing copy *"Any Slot takes any wearable item — a worn position, not a hand, so weapon damage scores nothing here"* stays true.
- Build check passes 18/18.

---

# P2 — A two-handed primary blocks the off hand

**Why second:** it is the only change here that fixes numbers the tool prints *wrong today*, and the fix is one line in one function.

### 2.0 State of play

**The slot legality underneath is already correct and should be said so, plainly.** `Pe(items)` (line 10133) indexes every item into `bySlot` keyed by its own `sl` list; `ze(state, slot)` (line 10389) serves `bySlot.get(slot)` plus literal-`ANY` items. A PRIMARY-only weapon is already unofferable in the secondary position. The shards are 100% clean on this: all 383 SECONDARY rows carry SECONDARY in `sl`, all 526 PRIMARY rows carry PRIMARY, and **0 of 123 two-handers list SECONDARY**. No illegal off-hand can be selected. Do not "fix" this; it works.

What is missing is the **interaction**. Searching the shipped bundle: `"2H "` occurs exactly once and it is demo fixture data (`wp:{dmg:37,dly:70,skill:'2H Slashing'}`); `two-hand`, `two-handed`, `twohand`, `dual`, `wield`, `off-hand` return zero; the single `OFFHAND` occurrence is a slot-name alias in the inventory parser (`OFFHAND: 'SECONDARY'`). `Kt()` sums positions one at a time with no cross-position rule. So a user can equip Earthshaker (2H Slashing) in PRIMARY and a shield in SECONDARY and the stat sheet totals both.

### 2.1 The change

There is already a precedent in the code for "positions dropped from the totals for a legality reason" — class blocking. Line 11745:

```js
function Un(e, t) {
  return t?.classes.length ? Hn(e).filter(e => Yt(e.item, t) === `blocked`) : []
}

function Wn(e, t, n) {
  let r = new Set(Un(e, n).map(e => e.position));
  return Kt(Hn(e).filter(e => e.position !== t && !r.has(e.position)))
}
```

Mirror it:

```js
// New, beside Un(). Returns position ids suppressed by the equipped primary.
function twoHandSuppressed(rows) {
  const prim = rows.find(r => r.position.id === 'PRIMARY')
  const skill = prim?.item?.wp?.skill            // note: 101 PRIMARY rows carry no wp at all
  return TWO_HANDED.has(skill) ? new Set(['SECONDARY']) : new Set()
}

function Wn(e, t, n) {
  let r = new Set(Un(e, n).map(e => e.position));
  for (const p of twoHandSuppressed(e)) r.add(p);          // <-- the one line
  return Kt(Hn(e).filter(e => e.position !== t && !r.has(e.position)))
}
```

**This one line covers three surfaces at once**, because they all route through `Wn`:
- The whole-loadout totals — line 20624, `x = useMemo(() => Wn(b, void 0, y), …)`.
- The marginal baseline with a position emptied — line 20625, `S = useMemo(() => g ? Wn(b, g, y) : x, …)`.
- The candidate-scoring baseline fed to `fn()` via `Gn(Wn(rows, position.id))` at lines 18341–18342 and 22873.

**One more call site needs its own guard: auto-fill.** The generator at line 11861 (`function* tr(...)`) builds totals with a local `c = e => Kt([...e.entries()].map(...))` and scores each position independently, so it will happily place a secondary alongside a two-handed primary. It runs two passes; after each pass, recompute the suppressed set from the current placement map and drop those positions from the candidate list and from the result:

```js
const suppressed = twoHandSuppressed(placementsAsRows(l))
o = o.filter(v => !suppressed.has(v.position.id))
```

and mention it in the run message the existing `er()` builder produces — it already reports `skipped` positions with reasons, so this fits its shape: `"Secondary not filled — the primary is two-handed."`

### 2.2 UI

Follow the existing blocked-slot precedent (line 20306), which already renders a `blocked` cell class and a tooltip of the form *"{item}: this loadout cannot equip it — … Its stats are not something the character can actually wear."*

Render the SECONDARY position greyed with:

> **Off hand — closed.** Your primary is two-handed, so nothing can go here. Classic EverQuest worked this way and no session in this project has ever put a two-hander on a character, so this is an inherited rule rather than a measured one. *(Dismiss)*

**Make it a dismissible banner, not a hard block.** Two reasons, and both belong in the design:
1. The rule is **inherited from classic EverQuest, not measured on Legends**. No log in the 138-log corpus shows a two-handed primary; both `/outputfile` dumps are the same character with a one-hander. The Legends-side support is indirect: eqlwiki's `Game Mechanics` Dual Wield section describes its own calculator comparing "the stronger arrangement … against the two-handed weapon", which presumes the exclusivity but does not state it.
2. Silently deleting a user's off-hand item is worse than telling them.

**Do not add a dual-wield class gate.** Whether Legends gates dual wield by class is genuinely unsettled — classic EQ did; Legends' three-class loadouts make it non-obvious; nothing in the corpus settles it. `eqlbase.com/skills/dual_wield` publishes a per-class table (Bard 210, Beastlord 210, Monk 252, Ranger 210, Rogue 210, Warrior 210) at **T4**, which is a candidate source if the owner ever wants it, but the geometric 2H rule is safe and the class rule is not. Ship one and not the other.

### 2.3 What this makes sayable, that the planner cannot say today

219 of 431 melee weapons (**T2**) cannot be paired at all, and the two strongest one-handers in the catalogue — **Aldryn, Blade of the Ocean** and **Thelvorn, Blade of Light**, both `sl:["PRIMARY"]`, `cl:["PAL"]`, `wp:{dmg:20,dly:26}` — are both primary-only and cannot be worn together. That is a real, checkable, useful fact about Paladin gearing that falls straight out of data the planner already holds.

---

# P3 — The proc-socket layer

**Why third:** it is small, it is the only place in the tool where a user can be led into a dead end by the UI, and it makes the exaltation tab tell the truth about what a socket can do.

### 3.0 State of play — most of this is already right

The exaltation ladder shipped in the bundle (line 12937, `var zr`) matches an independent 66-of-66 solve from four client `/outputfile` dumps (**M**) exactly:

```
ornamentation  unlockTier 0   exportSlot 2
focus          unlockTier 1   exportSlot 7
click          unlockTier 2   exportSlot 8
worn           unlockTier 3   exportSlot 9
proc           unlockTier 4   exportSlot 10
```

Donor legality is already implemented and is **stricter than most proposals for it**. `Hr(donor, host)` (line 12978) returns false unless their slot lists intersect *and* their class lists intersect; `Ur(host, legalDonors)` (line 12985) narrows the host's class and slot lists by every legal donor; the UI already prints *"Donor restrictions narrow this item out of … slot X. Your active loadout can no longer use it."* and *"N donors share no slot or class with the item holding them — the game would refuse the socket."* Donor stats are never added to the sheet: `Kt()` sums positions only.

**Do not re-implement any of that.** It is done.

### 3.1 The two gaps

**Gap 1 — a dead end the user only discovers after picking.** `Br(upgrade)` (line 12964) returns sockets by tier alone, with no reference to the host's position. So a bracer at +4 opens a **Proc** socket. But of the 91 slottable catalogue rows carrying a `k:"proc"` effect, **91 of 91 sit on PRIMARY, SECONDARY or RANGE and 0 sit on armour** (**T2**, census of all 19 shards). Combined with `Hr`'s slot-intersection requirement, that means the proc socket on a bracer **cannot be legally filled by anything in the catalogue**. The user finds out only by opening the donor list and seeing it empty, or by picking a donor and watching the host get narrowed out of its own slot.

**Gap 2 — proc lanes are not counted anywhere.** An exaltation carries its **source item's slot restriction onto the host**, and 382 of 385 catalogued combat effects sit on PRIMARY/SECONDARY/RANGE items — so a proc socketed into a bracer would make the bracer weapon-slot-only and therefore unwearable. The consequence is that a build's proc capacity is fixed by its hands: **1 lane on a two-hander, 2 dual-wielding, +1 on a Ranger bow, and zero from armour.** That is the largest structural gate on a melee build and the tool currently cannot represent it.

### 3.2 The change

**3.2a — at the socket, before the pick.** In the per-position socket builder (`function fs(e, t, n)`, line 18944, which already produces `{sockets, filled, openCount, restricted, lostClasses, lostSlots, blocksLoadout}`), add a field:

```js
const WEAPON_POSITIONS = new Set(['PRIMARY', 'SECONDARY', 'RANGE'])
…
procLaneEligible: WEAPON_POSITIONS.has(a.position.type),
```

and render, on a non-weapon host's unlocked proc socket, in place of the donor picker:

> **No donor can fill this.** Every proc effect in this catalogue — 91 of 91 — sits on a Primary, Secondary or Range item, and an exaltation carries its source item's slot restriction onto its host. Socketing one here would make this item weapon-slot-only and therefore unwearable.

That is a **T2** statement about the catalogue, and it is falsifiable the moment an armour proc appears in a rescrape — which is the right property.

**3.2b — proc lanes on the character sheet.** One line in the Stat sheet, beside the Weapons card:

```
Proc lanes   1     two-handed primary
Proc lanes   2     primary + secondary
Proc lanes   3     primary + secondary + Ranger bow
```

Computed as: `(primary ? 1 : 0) + (secondary && !twoHandedPrimary ? 1 : 0) + (rangeIsBow && ctx.classes.includes('RNG') ? 1 : 0)`.

Badge it as a **stated inference, not a measurement**, in the site's own voice, and give the reasoning in the tooltip. The honest standing: the slot-restriction-inheritance mechanism is **M** (solved from four inventory dumps, 66/66 rows); "armour proc sockets fire zero lanes" is mechanism plus a player report, corroborated only negatively — the corpus holds exactly one slot-10 exaltation (`Primary-Slot10 Thelvorn, Blade of Light (Exaltation)`), and a control test found spell-damage lines falling within 1s of an ordinary melee swing 20.9% of the time versus 16.9% within 1s of an `(Exaltation)` message, i.e. *below* chance (Golden Efreeti Boots: 0 of 25). Say that it is an inference. It reads better than a bare assertion and it is what happened.

Note this depends on P2: the proc-lane count needs to know the primary is two-handed. Ship P2 first.

---

# P4 — `DMG_BONUS` as a weightable EP key, shipped at weight 0

**Why fourth:** it gives a reader who knows what they are doing a lever, costs a reader who does not exactly nothing, and commits the planner to no DPS claim.

### 4.0 The problem, stated exactly

`fn()` (line 11134) scores weapons with two keys, at line 11184:

```js
i.weapon && (r.weaponCounts ?? !0) && (c(`RATIO`, i.weapon.ratio), c(`DMG`, i.weapon.damage))
```

`RATIO` = upgraded damage ÷ delay is the only damage term carrying a non-zero weight in any of the five shipped profiles (`hn`, line 11326: melee-dps RATIO 40, balanced RATIO 20; `DMG` is scorable but unweighted everywhere). Neither key sees the damage bonus, and the omission is not symmetric between weapon families.

In the planner's own unit, at level 50 with upgraded damage ≤ 50, the bonus adds a **delay-independent** constant to ratio: **+0.6875 for a two-hander, +0.50 for a one-hander** (it grows further once upgraded damage passes 50 — Earthshaker's is 0.727). The best two-hander in the catalogue prints ratio 1.731; the term not being printed is worth another 0.688 of it. Nine of the top ten weapons by modelled main-hand damage are two-handers, and that is exactly where the ratio column understates.

For scale, under the neighbouring project's measured chain (`E[hit|landed] = 1.089·U·E_rx + B + 1.1`, `U = 2·DMG+1`, `E_rx = 0.967`, all **M**), adding B raises expected damage per landed main-hand swing by **+31.8%** on Cudgel of the Fool +10, **+31.6%** on Earthshaker +10 and **+15.0%** on Thelvorn +10. Those are **model output, not measurement**, and nothing in this change depends on them — they are here to show the term is not a rounding error.

**The good news, and it should be said in the copy: the ordering is not broken.** Ranking all 425 PRIMARY-capable melee weapons at +10 by ratio, and again by modelled main-hand damage, they agree **8 of 10 in the top ten and 20 of 25 in the top twenty-five**. What ratio cannot do is tell a reader *how much* a swap is worth, or that a two-hander and a one-hander at the same ratio are not the same weapon.

### 4.1 The change

```js
// fn(), line 11184 — add a third weapon key
i.weapon && (r.weaponCounts ?? !0) && (
  c(`RATIO`, i.weapon.ratio),
  c(`DMG`, i.weapon.damage),
  c(`DMG_BONUS`, i.weapon.dmgBonus?.value ?? 0)
)
```

and the mirror in `mn()` (line 11194, the pre-compiled fast scorer) beside its existing `ratio` and `dmg` cases:

```js
case `dmg_bonus`: {
  const w = e.wp; if (!w) break
  const v = derivedDmgBonus(w.skill, jt(w.dmg, t), w.dly, s.level)
  v && (o += v * s.weight)
  break
}
```

Note `mn()` closes over weights and options at build time and is memoised by `Xn()` with a cache key that already includes the class levels (`r.classes.map(e => r.levels[e] ?? 0).join('.')`), so a level change correctly invalidates the cache. No cache work needed.

Gate on `weaponCounts`, which is already `n === 'PRIMARY' || n === 'SECONDARY'` at line 11789 and `position.type !== 'ANY'` at 18198/18317 — so Any Slot keeps scoring nothing and the existing copy stays true. The `weapon.dmgBonus` field is populated only on `weapons.primary` after P1, so the off-hand scores zero without a special case.

**Ship it at weight 0 in all five default profiles.** Add it to the Weights tab's key list with a one-line note. Do not change any shipped profile's behaviour in this commit.

### 4.2 If someone later wants a defensible weight

A point of damage bonus is worth roughly **1/2.1** of a point of DMG on the same weapon, because the roll contributes ~2.1×DMG to an average hit while the bonus contributes 1×B. `RATIO 40 / DMG_BONUS 19` is internally consistent. **That is a derivation and must be badged as one.** It is not a measurement and it should not be defaulted on.

### 4.3 Three things not to do

**Do not fold the bonus into `RATIO`.** I tested it. Because the bonus is additive and barely moves with delay, adding it to dmg/delay promotes **Rusty Two Handed Hammer 124 places** (rank 358 → 234), **Abandoned Orc Shovel 126 places** (369 → 243) and **Micah 140 places** (411 → 271). Ratio stops being even a rough damage proxy the moment a delay-independent term is inside it. eqlwiki's Game Mechanics page offers a "Normalized Primary Score = ((2 × Weapon Damage) + Damage Bonus) / Weapon Delay" for exactly this comparison; it is a fine thing to *show*, and a bad thing to *rank on* without saying so.

**Do not ship a DPS number.** It would be the first figure on the site that no source carries and no client window prints — a model output in the same typography as a scraped stat, on a page whose whole argument is that those are different kinds of thing. Note also that `ATTACK` is aggregated by `Kt()` (`t.attack += e.flat.ATTACK ?? 0`) and is **structurally always zero**: 0 of 3,663 catalogue rows carry an ATTACK stat, and a wider wiki census finds 2 of 11,534 items with one, both era-gated out of this game. The one stat with the largest leverage on melee damage cannot be bought at any price in this era. If a damage screen is ever wanted it belongs on its own page, with its own standing, and with a measurement-convention warning attached — wall-clock, engaged, best-60s and best-30s damage rates differ by up to 2.0× on the same log (median best-60s/engaged 1.23, best-30s/engaged 1.47, best-10s/engaged 2.06, n=29 fights, **M**), and four shipped Legends meters use four different denominators by default.

**Do not touch the cap-aware scorer.** `Wn()` builds the baseline from the rest of the set with this position emptied and class-blocked items dropped; `fn()` clips attribute gains at 510 and resist gains at 1000 against what the character already has; `dn(e, t) { let n = Math.max(t, e) - t; return { counted: n, wasted: e - n } }` scores only the excess haste over the best already worn. That is genuinely rarer than it sounds and it is the strongest thing in the engine. A worked example on the tools page — a ring that looks better in isolation and scores lower in a set already near the attribute cap — would be the best single argument for using this planner over any other.

---

# P5 — Say the weapon-damage upgrade divergence out loud

**Why fifth:** it costs one sentence, it affects 61.5% of the catalogue's weapons, and one client window settles it.

### 5.0 The divergence, read from the bundle

Two upgrade functions, ten lines apart:

```js
function At(e, t) {                       // line 10822 — every scaled stat
  …
  if (e <= 10) return e + n;              // +1 per tier floor
  let r = Ot(t);
  return e + Math.floor(e * r / 10)       // 10% of base per tier
}

function jt(e, t) {                       // line 10831 — weapon damage only
  let n = Ot(t);
  return e + Math.floor(e * n / 10)       // 10% per tier, NO floor
}
```

`At` is algebraically identical to the rule `value + max(tier, floor(value × 0.1 × tier))` at every whole tier. `jt` drops the `+1/tier` floor entirely. `Gt()` sends `wp.dmg` through `jt` and every other scaled stat through `At`.

**No capture distinguishes the two rules for weapon damage,** because both captured weapons have base damage above 10: Whitened Treant Fists 14 → 14/15/16/18 at +0..+3 under either rule; Earthshaker 37 → 74 at +10 under either.

But **265 of the 431 melee weapons in the catalogue — 61.5% — have base damage below 10** (**T2**, verified across all 19 shards), and under `jt` their damage does not move at all at +1. Under the floor rule a 9-damage weapon reaches 19 at +10 instead of 18; a 3-damage weapon reaches 13 instead of 6.

The upstream is ambiguous rather than silent, which is why this is worth saying rather than guessing. eqlwiki `Item Upgrade System`, verbatim: *"A minimum increase of +1 to a stat is guaranteed at the start of each tier"* and, in a separate bullet, *"Weapon damage is increased at +5% per Tier."* The page states the floor as a rule about *stats* and then carves weapon damage out into its own percentage — leaving exactly the question the two functions answer differently.

### 5.1 The change

**No code change.** One line in §03 "What it will not tell you":

> Below 10 base damage, a weapon's damage does not move until the percentage clears 1. Whether the +1-per-tier floor that every other stat obeys also applies to weapon damage has not been checked, and 265 of 431 melee weapons are in that band.

And one line naming the capture that settles it: **Efreeti Standard at +1 or higher** — 3 damage / 10 delay, a Plane of Sky cleric quest reward, already in the catalogue as a SECONDARY item. The shipped rule says DMG 3 at +1, +2 and +3; the floor rule says 4, 5, 6. Any sub-10-damage weapon at any tier ≥ 1 does the same job.

### 5.2 A related claim the site can already close, and does not

The +5%-per-tier bullet on eqlwiki's `Item Upgrade System` page is **refuted by the site's own capture**. Whitened Treant Fists at +0/+1/+2/+3 reads 14/15/16/18; +5%/tier predicts 14/14/15/16. The +3 reading kills it outright — even granting the page's own mid-tier accumulation rule, +5% cannot exceed a 20% cumulative bonus at tier 3, and 18 from a base of 14 requires 28.6%. `jt()` ships the winning rule; no page on the site says so, and no page mentions the conflict. EQL Tools lists the same question as open on its own upgrades page (*"the wiki says +5%, this site's tools use +10%. One weapon read at two tiers settles it"*) — so publishing the closure is a contribution outward, not a correction inward.

---

# P6 — Six small changes, none of which needs a design

Grouped because each is one line to a few lines, and each removes a statement that is currently false or a display that is currently broken.

### 6.1 `haste-stacking` — close the finding, it is already fixed
`data/contamination.json` → signature `haste-stacking`, `findings[0]` currently reads: *"Not detected in this build. Either the scorer was fixed or the scanner's pattern no longer matches; check both before believing this line."* It was fixed. `dn(e, t)` (line 11127) is called as `dn(t, r.existing?.haste ?? 0)`, with the second argument the best haste already worn elsewhere in the set (computed by `Wn()` with the candidate's own position excluded); `Kt()` takes the maximum on the totals side (`o > t.haste && (t.haste = o)`) and counts `hasteSources`. The two halves of the engine agree. Replace the ambiguous finding with a positive statement naming the function. This is currently the **only row on that page that can be closed**, and a scanner that can say "this one is fixed, here is the code" is more persuasive than one that only counts hits. (The separate `haste-pct` signature — what the number *means* — is untouched by this and stays open.)

### 6.2 The upgrade curve deserves the green light, not just the base values
`data/meta.json` → `dataReliability.stats.note` currently says *"AC/attributes/saves/dmg/delay reproduce the client exactly on every Tier 0 sample."* The five `sdc` capture records also validate the **upgrade curve**, which is far more load-bearing — a base value is applied once, the curve is applied to every one of 1,713 statted rows at eleven tiers. **22 of 22 upgraded fields reproduce exactly** across the five records:

- Bone-Clasped Girdle +4 — AC 4→8, HP 75→105, MANA 75→105, STR/STA/DEX 7→11 (6 fields)
- Bladestopper +6 — AC 25→40, HP 50→80, STA 15→24 (3)
- Cloak of Flames +7 — AC 10→17, HP 50→85, AGI 9→16, DEX 9→16, **HASTE 36→43**, SV Fire 15→25 (6)
- Earthshaker +10 — DMG 37→74, STR 6→16, STA 6→16, **SV Void → 10** (4)
- Whitened Treant Fists +1/+2/+3 — DMG 15, 16, 18 from base 14 (3)

Two rules fall out that nothing else settles. **Haste takes the flat +1/tier rule** (`Mt`), not the scaled one: 36+7=43, where the scaled rule gives 61 — an 18-point gap, so a reader recomputing by hand concludes the planner is broken. And the **+1/tier floor is confirmed where it actually binds**, on three items and seven fields: Bone-Clasped's STR/STA/DEX 7→11 at +4 (percentage gives 9), Cloak's AGI/DEX 9→16 at +7 (gives 15), Earthshaker's STR/STA 6→16 at +10 (gives 12). Split the confidence note in two — base values, and the curve — and add the +5%-vs-+10% closure from §5.2. Three sentences, and it converts a modest disclaimer into the strongest claim on the site.

### 6.3 Publish the derived Void save rule
Read out of the bundle (`Ft()`, line 10852, plus `Wt()` at 10929): at upgrade tier n > 0, an item carrying at least two distinct stats from `{STR STA INT AGI DEX CHA WIS SV_FIRE SV_COLD SV_POISON SV_MAGIC SV_DISEASE}` gains `SV Void = n`, taken as the max against any upgraded base Void. It validates **2 of 2** against client windows (Earthshaker +10 → 10; Midnight Clad Straps +6 → 6). This is a genuinely good piece of reverse-engineering that currently exists only in minified code, and it is exactly the derived-rather-than-sourced number the sources page is scrupulous about labelling everywhere else. Add a short `dataReliability.voidSave` card with the rule and the two checks — and name the untested edge in the same card: an item with fewer than two qualifying stats (an AC-and-HP-only piece) derives no Void, and no capture covers that case. Note also that base Void exists on only 2 catalogue rows (Darkspun Shroud 1, Anthemion Armbands 2), so the derived value depends solely on tier and should not be ranked on.

### 6.4 `ATTACK` — document the empty column
`meta.json.statKeys` publishes `ATTACK` and `Kt()` sums it, but no row and no page says why the column is empty. Add a `dataReliability.attack` card in the same shape as the others: confidence `structurally-absent`, note along the lines of *"0 of 3,663 rows carry an ATTACK stat and that is correct rather than missing — the stat exists in the client and on 2 of 11,534 wiki items, both era-gated out of this game, so worn ATK is a channel behind unshipped expansions."* One card, and an unexplained empty column becomes a documented fact.

### 6.5 The monk suspect rule does not reproduce its own output
`meta.json.dataReliability.weaponSkill.suspectRule` is printed on screen beside `suspectCount: 4`, so a reader can apply it by hand. Applied literally to the shipped shards it selects **5** rows, not 4 — the fourth suspect plus **Bloodclaw Mace**, whose name contains "claw" inside "Bloodclaw" and whose `cl` list names MNK explicitly. The site is right to exclude it (it is a mace with a `Blood Claw` proc, not fist gear), so this is not a wrong suspect list — it is a rule string that does not reproduce its own count. Add a word boundary: `/\b(fist|knuckle|claw|cestus|ulak|fistwrap)/i`. That reproduces the published 4 exactly. One regex, no data change, no weapon moved. *(Do not replace the name regex with a shape test on size and weight — I ran that variant and it misses Brass Knuckles, which is MEDIUM/wt 1, and picks up Efreeti Scimitar and Fool's Gold Stein.)*

### 6.6 Wiki markup is rendering literally in 48 effect names
48 `fx[].n` entries across 48 items carry unescaped wiki markup — e.g. Thelvorn ships `{"k":"proc","n":"<span class='itemeff'>Dismiss Summoned</span>","d":"Combat, Casting Time: Instant","lv":45}`. React escapes it, so **the markup shows literally on screen**: Thelvorn's paperdoll line currently reads `Effect: <span class='itemeff'>Dismiss Summoned</span>, Dismiss Summoned`. A recursive scan finds markup at `fx[].n` and nowhere else — one parser, one field. All 48 have a same-kind twin carrying the same effect name, so **nothing loses an effect if the markup rows are dropped**; but a plain dedupe on `(k, n, d, lv)` after stripping tags collapses only 43 of 48, because five twins differ in payload (Staff of Writhing's clean twin carries `Rate +75%` that the markup row lacks). So: strip tags in the pipeline's effect parser, then **merge rather than dedupe** — "prefer the entry with a populated `lv`, then the longer `d`" resolves all five without a human. Separately, 4 items list one effect name under two different `k` (click + proc); those need a human read of the source page, since click and proc are different lanes.

---

# Appendix A — Things that are already right, so nobody spends a day re-implementing them

- **Secondary-slot legality.** `Pe()` / `ze()` already serve only slot-legal candidates. Shards are 100% clean.
- **Exaltation donor legality.** `Hr()` requires slot ∩ slot and class ∩ class; `Ur()` narrows the host; the UI already warns when a donor narrows a host out of its own slot.
- **The exaltation ladder.** Matches a 66/66 independent solve.
- **Max-not-sum worn haste**, on both the totals side and the scoring side, with an honest *"Assumed, not measured"* standing.
- **Cap-aware marginal scoring** at 510 attributes / 1000 resists, against what the rest of the set already carries.
- **`weaponCounts`** correctly false for Any Slot.
- **The 23-position model** (18 slot types, EAR/WRIST/FINGERS doubled, two Any Slots, no Charm) matches the client `/outputfile` ladder exactly.
- **The weapon-skill distrust card**, which reports Monk fist-weapon suspects rather than correcting them. That is a defensible reading of the site's own standard and it should not be changed. Note only that the wiki has since been corrected to agree with the site's client window: `Whitened Treant Fists` revision 171348 (2026-08-21, user FizzleMaster, comment "Corrected flags and stats") changed `Skill: 1H Blunt` → `Skill: Hand to Hand`, the category to `Hand to Hand`, the flags to `No Trade, Placeable`, and added `Dmg Bon: 13` — closing three open items at once, all in the site's favour. Re-scrape and promote; the settle line drops from four client tooltips to three.

# Appendix B — Suggested commit order

1. **P1a** pipeline harvest + build assertion (data only, no UI change; the 18 rows land as `wp.db`).
2. **P1b** `engine/dmgBonus.ts` + `Kt` context arg + Weapons card + item dialog + swap diff + copy in `meta.json`, `contamination.json`, §03, bundle callout. *This is the flagship; ship it as one visible change.*
3. **P2** the `Wn` one-liner + auto-fill guard + the dismissible banner.
4. **P3** proc-lane count and the empty-socket notice (depends on P2).
5. **P4** `DMG_BONUS` key at weight 0.
6. **P5** the §03 sentence.
7. **P6** the six small ones, individually, in any order.

# Appendix C — A caution that belongs on the sources page, not in a commit

Five days separated this build (`2026-08-26`) from the wiki state read for this document (`2026-08-29`), and in those five days one editor rewrote roughly forty Plane of Sky item pages against a live client — changing flags, changing skills, adding damage bonuses — in the site's favour every time. **Three of the site's open questions closed themselves while nobody was looking.** Three of the changes above exist only because of that.

The lesson is not "re-scrape more often". It is that a signature should carry a **re-check date**, not only a scan date, and that a sentence in the present tense about what all sources currently say is exactly the claim a wiki edit falsifies quietly. `contamination.json`'s scoped *"no source **in this project** carries it per item"* is defensible as of its scan date and needs only a date attached; `meta.json`'s unscoped *"No source carries it per item"* is the one that is now plainly false. They are not equally wrong and they should not be fixed with the same edit.