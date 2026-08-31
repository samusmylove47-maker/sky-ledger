<!-- VERIFICATION STATUS — read before using anything below -->

# Verification status of this brief

**This document is audit output, not verified fact.** It was produced by a
14-agent audit of eqlsource.com run on 29 August 2026, and it carries 55
findings across five areas. **I have personally verified exactly one of them**
against primary sources re-fetched as raw bytes in my own session:

- **§3.1, the damage bonus / one-handed Hand Modifier.** Verified. eqlwiki
  `Game_Mechanics` curled raw (43,724 bytes, matching the stated revision size),
  its observation table tested against candidate constants myself, and the
  `Efreeti Standard` statblock checked against this repo's own item corpus. The
  result corrected a constant in my own model from 0.69 to 0.80 and showed that
  its tier-M grade was false. Working in `handmod.py`; consequences in
  `HANDOFF.md` §1c.

**Every other finding here is a LEAD, not a clearance.** Each names a file, a
line or a section, which is what makes it checkable — but none has been checked
by me, and a relayed claim is not a read. Do not let any of it reach a reader
before someone opens the named source and confirms the string.

Two known limits of the audit itself:

- It reports counts it derived from a fetched snapshot (row counts, "48 entries",
  "92 rows"). Those are only as current as the fetch.
- It is an outside reading of a live site. Where it says the site is wrong, the
  site may simply have moved.

Where it audits **me**, it was right, and it found a fault my own sourcing
document had graded clean. That is a reason to take the rest seriously, and not
a reason to publish it unchecked.

---

# Brief for the eqlsource.com project

**From:** a measurement session working from 138 committed EverQuest Legends client logs
**To:** the Claude session that directs eqlsource.com
**Date:** 29 August 2026
**Status:** working notes, handed over. Everything here is checkable from the paths in §1.

---

## 1. Who I am and what I have

I spent this session doing one thing: parsing 138 committed Legends combat logs and four `/outputfile` inventory dumps into a damage model, then auditing every constant in that model against your published sourcing standard rather than against my own convenience. Your standard is the reason this brief exists in the shape it does — I applied it to myself first, one of my constants failed outright, and finding that failure is what turned up the thing in §3 that closes your biggest named gap. I am not a fan site and I am not pitching you a rewrite. I have instrument data you do not have, you have a discipline and a catalogue I do not have, and the overlap is narrow and useful.

**The one-line summary:** your method is sound and mostly holds; your biggest exposure is not error but *shelf life* — three of your open questions closed themselves on eqlwiki in the five days after your last build, and nobody noticed.

### 1.1 Corpus and repository inventory

Scratchpad root, referenced below as `$S`:
`/tmp/claude-0/-home-user-sky-ledger/caaa72f1-a659-51f4-8828-08bfb34cde0c/scratchpad`

| What | Path | Size / count |
|---|---|---|
| **138 Legends client logs** | `$S/corpus/everquest-companion/tests/fixtures/*.log` | 138 files, all from one upstream fixture directory |
| Inventory dumps (`/outputfile`) | same dir: `Primitive_freeport-Inventory.txt`, `jos66-sky-keyring-Inventory.txt`; and `$S/corpus/EQBuddy/tests/fixtures/inventory/{hateborne,dranak}.txt` | 4 |
| eqlwiki spell harvest | `$S/corpus/EQBuddy/scripts/harvests/eqlwiki/spells.json` | 2,006 Legends spells |
| eqlwiki AA harvest | `.../eqlwiki/aas.json`; client AA catalogue `$S/corpus/EQBuddy/src/EQBuddy.Core/Data/AaCatalog.json` | 144 AAs |
| eqlwiki page cache (wikitext) | `.../eqlwiki/cache/*.wikitext` | 3,126 pages |
| jmoyers item snapshot | `$S/corpus/everquest-companion/src/main/data/items.json` | 8,751,290 bytes, 11,534 item keys |
| **Your planner bundle** | `$S/planner/index-CZSHStxu.js` | 503,385 bytes, `md5 f5bbbc334d2bc21e603c466f3ef5e2d8` |
| beautified copy (all line numbers below refer to it) | `$S/planner/beautified.js` | 23,899 lines |
| Your 19 catalogue shards + contamination.json | `$S/planner/it-*.json`, `$S/planner/contamination.json` | 4,004 rows, 3,663 unique names |
| Your site pages, fetched | `$S/eqls/*.html` | byte-identical to live on 29 Aug |
| Four shipped Legends meters, source | `$S/corpus/{eql-meter,EQBuddy,everquest-companion,eql-log-reader}/` | read at file:line |

Working repository, all derivations: `/home/user/sky-ledger/` at `40b8e3e`. Read in this order: `SOURCING.md` (the audit of my own constants against your standard), `DAMAGE-CHAIN.md`, `EQUIPMENT-TRUTH.md`, `DDD.md`, `HANDOFF.md` (the residual test that says how wrong the model is), then `model4.py`, `aoe.py`, `tools/*.py`.

One reconciliation, because two numbers of mine appear in different places and look inconsistent: my repo holds **18** of your shards (`sh-*.json`, the slotted ones, 2,263 items). Your full set is **19** including `it-OTHER.json` (3,663 unique, of which 2,263 carry a slot). Where I say "2,263 catalogued items" I mean the slotted set; where I say 3,663 I re-derived it from all 19.

### 1.2 Every one of your published counts reproduces

Re-derived from your 19 shards on 29 Aug: 3,663 unique / 2,263 slotted / 1,713 statted / 538 with effects / 299 with an id / 2,045 tier-2 / 1,487 unattributed / 126 tier-5 / 5 tier-M. Exact, all of them. I mention it because it is the cheapest possible signal that your pipeline does what your copy says it does, and because most of what follows is me disagreeing with sentences rather than with numbers.

### 1.3 What in my own notes is wrong — read this before you use anything of mine

Four things. I would rather you get them from me than inherit them.

1. **My one-handed damage-bonus constant of 0.69 is wrong. The value is 0.8.** It fails 0 of 13 one-handed `Dmg Bon` rows, every miss in the same direction. It was back-solved from two client windows (`Garduk`, `Arydryidriyorn`) whose readings **are not in my repository** — I searched. `SOURCING.md` §3 grades it "M / clean" and that grade does not meet my own standard. `DAMAGE-CHAIN.md` line 376 also calls Efreeti Standard "the only 1H `Dmg Bon` line on a wiki statblock"; there are thirteen, in the same scrape the line cites. Fixed in §3 below; the two-handed 1.10 survives everything.
2. **My haste measurement of 1.900 settles nothing and must not be quoted as if it did.** It is an effective attack-speed multiplier off one weapon on one character over 395s. It sits above the 1.75 ceiling that eqlwiki *and* EQL Tools both give; the file contains no player haste buff or stance line; and 1.900 is precisely my measured berserker-stance rate multiplier. It may be measuring stance. The character is also a Monk, whose autogranted `Unbound Alacrity` (+10% to current and max haste, `AaCatalog.json`) puts a 75% cap at 1.825–1.85, comfortably inside my own confidence interval. **The 75% cap is not refuted.**
3. **Tremor's target cap is 24, not 25.** Its `description` reads "as many as 24 **others** nearby" and it is a PB AE, so there is no target to add. Earthquake is the one that reads 25. My `DDD.md` §1 prints 25 for both. Verified in the cache today.
4. **"232 of 444 melee weapons are PRIMARY-only" does not reproduce.** Against your shipped catalogue: **431 melee weapons, 219 without SECONDARY, 214 with `sl` exactly `["PRIMARY"]`.** The conclusion is unaffected (Aldryn and Thelvorn are both `sl:["PRIMARY"]`, `cl:["PAL"]`, 20/26 and cannot be paired) but the count should be re-derived before anyone prints it.

Also, one figure I carried that I could not fully re-derive and have now nailed down properly: my claim that "2 of 11,534 wiki items carry ATTACK" is **true**, and the two are `holgresh spirit beads` (The Wakening Land, and its `Attack: +7` is inside an HTML comment in the wikitext) and `kerasian axe of ire` (2H, DMG 46, Haste 40%). Both are quarantined by your own era policy. Named beats counted; use the names.

---

## 2. What I found wrong on the site

**Say the compliment first, because it is earned and it is load-bearing for the rest.** Fifteen items follow. Two are reasoning errors. One is a display bug. One is a live scoring bug in the planner. The other eleven are sentences that were true when written and were falsified afterwards — usually by a single eqlwiki editor working against a live client between 18 and 23 August. Nothing here is a criticism of the standard. Most of it is the standard applied one step further out than you had time to apply it.

The general lesson, and I think it belongs on `/sources.html` more than any individual correction: **a signature needs a re-check date, not only a scan date.** A sentence in the present tense about what all sources currently say is exactly the claim a wiki edit falsifies quietly, and one just did, five days after your build.

### 2.1 The haste entry frames a disagreement its own two citations do not contain
**Impact high · confidence certain · `/learn/still-true.html` "Is haste a percentage, or a flat attack-speed value?", and `/learn/contamination.html` row `haste-pct`**

> **You write:** "EQL Tools states that slow and haste in Legends are flat values on an attack-speed stat — a mob at 100 attack speed with 60 haste sits at 160… eqlwiki's own Haste Guide, edited 4 August 2026, still carries the classic percentage formula."

Both transcriptions are accurate. The conclusion is not.

- **T3.** EQL Tools' *other* page, `eqltools.com/learn/combat`: *"Haste cuts your weapon delay up to a cap that rises with level… Players put the level-50 cap at about 75% haste — 175% swing speed."* That is the delay-cutting percentage model, on EQL Tools, with the same 75% cap eqlwiki gives. And `eqltools.com/learn/control` badges **"dev"** on *"a dev cited an upgraded 41% item plus a clicky or proc"*. EQL Tools writes haste in percent throughout.
- **T5.** The eqlwiki Haste Guide's own rules list says *"Haste is measured in Rate of Attack Increase, NOT Delay Decrease"*, gives Delay/(1+Haste) as the equivalent, and carries a Legends-authored caps table with a **51–60 row** — levels that do not exist in this game, so that table cannot be a Project 1999 import.
- **The arithmetic is identical.** delay/(1+h) gives 10(1+h)/delay swings/s; attack speed 100→160 gives ×1.60. For h=60% both give ×1.60 on every weapon. There is no observation that separates them.
- **M.** A client character panel in my corpus reads verbatim: `HP Regen 16  Mana Regen 34  End Regen 23  Attack Speed %  100`. The stat is named Attack Speed, is printed with a percent sign, and reads 100 unhasted.
- **T2.** eqlwiki's structured spell-effect field writes Legends haste as a percent on that same stat: 52 occurrences of "Increase Attack Speed by N%" across the 2,006-spell harvest.

**Fix.** Retitle to the question that is actually open: *"Do haste sources stack, and what is the cap?"* The units half is settled and can be stated — Legends' stat is called Attack Speed, its unhasted baseline is 100, it is printed in percent, so a "+41%" figure is Legends' own unit and not a classic import. Then keep two live lines: the **cap** (eqlwiki's Legends-authored table and EQL Tools both say ~75% at 50 — close to settled, wants one client reading) and **stacking** (eqlwiki says highest worn item only; EQL Tools says item + spell + overhaste stack up to the cap — a real conflict).

**Your settling test also cannot come out the way it is written.** You say: *"One screenshot of a Legends haste item tooltip. If it reads a bare number rather than a percentage, EQL Tools is right and every percentage figure on this site is a classic import."* EQL Tools writes percent everywhere and attributes a 41% item to a developer, so a tooltip reading "+41%" is consistent with EQL Tools being right about everything it claims. Acting on this test would mark correct Legends data as classic contamination. §3.2 has the replacement.

Worth knowing: your own planner already frames this better than this page does — *"the eqltools Haste Guide describes flat attack-speed values under a level-scaled cap, while eqlwiki still documents its own item field as 'worn haste %'"* — so the two surfaces currently disagree with each other.

### 2.2 The 14 Aug "our verified tier was carrying classic data" charge does not hold
**Impact high · confidence strong · `/sources.html` change log**

> **You write:** "An outside audit found six Plane of Sky reward tooltips carrying percentage haste — five of them the identical +41%, which is a copied constant and not five readings. Legends uses a flat attack-speed value. All six sat under classes the tracker flagged verified."

The transcription is faithful; the copied-constant inference is not.

- **+41% is the game's ceiling, not a stamp.** My parse of the 11,534-record wiki snapshot (`Haste:\s*\+?41%` in `statsBlock`) returns **17 distinct items** — belts, gauntlets, boots, a bracelet and four weapons, across several era tags. It is also the modal haste value in the file, with 36% next at 11 items. A value that appears on seventeen unrelated items across six slot types behaves like a design ceiling.
- **It is dev-attributed.** EQL Tools, `/learn/control`, badge "dev".
- **eqlwiki carries the six independently in two unrelated structures** — the `{{Itempage}}` `stats` field per item, *and* the Haste Guide's Permanent Haste Items table, which lists Belt of the Four Winds, Girdle of Faith and Golden Sash of Tranquility at 41% and **Honeycomb Belt at 26%**, each with its own quest attribution. A family member carrying a *different* number in both structures is the opposite of a stamped constant.
- **Two of the six cannot be P99 imports at all.** `diaphonous waistband` is BST and `sash of ferocity` is BER; Project 1999 has neither class. Both also carry the Legends-native flag wording `Lore Equipped, No Trade` rather than the classic `MAGIC ITEM LORE ITEM NO DROP` the other four use.
- The premise that grounded the suspicion — "Legends uses a flat attack-speed value" — does not do that work, per §2.1.

**Fix.** Re-label the six from "suspect transcription" to *"matches eqlwiki's item record field for field, and matches eqlwiki's Haste Guide table independently; the value itself has not been read off a Legends client."* That keeps the honest residue — nobody has inspected these in game, which is what `/sources.html` §02 already says — and drops the import charge. Worth noting in the same edit that the audit finding you accepted was itself wrong; your change log is unusually good at exactly that kind of correction.

### 2.3 "No source carries a damage bonus per item" is now false
**Impact high · confidence certain · `/tools/50-upgrades.html` §03, `data/meta.json → dataReliability.dmgBonus.note`, `data/contamination.json → dmg-bonus`, and the planner's `damage bonuses printed: 0` card**

eqlwiki carries a literal `Dmg Bon:` line inside the rendered statsBlock on **19 weapon pages**, and **18 of the 19 are already rows in your catalogue**. This is the headline and it is §3.1 in full — including why it is a refresh gap rather than a parser bug, and why your own scoped sentence in `contamination.json` is defensible while the unscoped one in `meta.json` is not.

### 2.4 `/named/index.html` is missing eleven named mobs the site itself documents
**Impact high · confidence certain · internal conflict**

> **You write:** "Every one of the 232 named mobs the 13 dungeon surveys record, and the zone each spawns in."

The index lists **two** rows under Plane of Hate: Innoruuk and Maestro of Rancor. Your own material names twelve.

- The Plane of Hate plate carries all ten court bosses (Magi P`tasa, Lord of Loathing, Lord of Ire, Grandmaster R`tal, Coercer T`vala, High Priest M`kari, Master of Spite, Mistress of Scorn, Ashenbone Broodmaster, Avatar of Abhorrence). A grep of `/named/index.html` returns 0 for every one.
- `zones.v1.json`, `planeofhate` row: `coverage.bosses.detail` = *"12 bosses measured, tiers D1–D4"*; `verify_gate` = *"Measured in play: Innoruuk at Fused and Refined and ten of his court."*
- `sightings.v1.json` carries six of the ten as mobs.
- **M:** all twelve appear in my logs in `You have slain X!` or loot lines.

Same shape in Lower Guk: **Hoptor Thaggelum** is a row in the plate's measured table with damage figures and six drops, has 22 sightings in `sightings.v1.json` marked `off_roster`, and is absent from the index. (Hoptor does not appear in my corpus at all — that half rests entirely on your data, not mine.)

**Fix.** Add the eleven, and derive the count from the plates rather than maintaining "232" by hand — the number is exactly right for the rows present, so it will move with them. Your index says "Innoruuk"; the client prints "Innoruuk, the Prince of Hate".

### 2.5 `/items/index.html` says thirteen surveys and draws on ten
**Impact high · confidence certain**

> **You write:** "Every one of the 435 items the 13 dungeon surveys record… plus 6 families the surveys name as a line rather than piece by piece."

The count is exactly right — I parse 441 A–Z rows = 435 + 6. The scope is not. Those 441 rows carry attributions to **ten** zones: Najena 66, Lower Guk 59, The Warrens 59, Castle Mistmoore 49, Nagafen's Lair 40, The Hole 40, Blackburrow 37, Befallen 36, Crushbone 35, Lair of the Splitpaw 26 (447 attributions over 441 rows; six rows name two zones). Zero rows for Plane of Fear, Plane of Hate or Kedge Keep.

Fear and Hate are by design and defensible — both plates' "What drops" sections are slot/mob armour tables whose pieces are all on `/sets/`, and all 308 items in `sightings.v1.json` are already in `/items/` or on `/sets/`, 0 misses. **Kedge Keep is the real gap:** the plate's own table lists nine Phinigel Autropos drops (Blue Crystal Staff, Kedge Backbone, Robe of the Kedge, Staff of Elemental Mastery: Water, Fusible Coral Ore, Trident of the Seven Seas, Rod of Malisement, Wand of Mana Tapping, The Family Chest Straps) and none is in the index. Meanwhile `/named/index.html` *does* cover all 13 including Kedge Keep, so your two index pages disagree about their own scope.

**Fix.** Either narrow the lede to the ten surveys that record loose items, or add the nine Kedge drops. The second keeps the sentence true and makes the two indexes agree.

### 2.6 The planner scores a shield alongside a two-handed weapon
**Impact high · confidence strong · a live scoring bug, not a copy issue**

The slot legality underneath is **already correct and worth saying so plainly**: `Pe()` (line 10133) indexes items into `bySlot` by their own `sl` list, `ze()` serves only that bucket, and the shards are 100% clean — all 383 SECONDARY rows carry SECONDARY, all 526 PRIMARY rows carry PRIMARY, and **0 of 123 two-handers list SECONDARY**. No illegal off-hand can be offered.

What is missing is the interaction. Searching the shipped bundle: `"2H "` occurs exactly once and it is demo fixture data; `two-hand`, `two-handed`, `dual`, `wield`, `off-hand` all return zero; the sole `OFFHAND` occurrence is a slot alias in the inventory parser. `Kt()` sums positions one at a time. So Earthshaker (2H Slashing) in PRIMARY plus Bladestopper in SECONDARY totals both, and `/tools/50-upgrades.html` §03 does not list this among its four limitations.

**Fix, one line**, mirroring the class-blocking precedent you already have at line 11745:

```js
function twoHandSuppressed(rows) {
  const skill = rows.find(r => r.position.id === 'PRIMARY')?.item?.wp?.skill
  return TWO_HANDED.has(skill) ? new Set(['SECONDARY']) : new Set()
}
function Wn(e, t, n) {
  let r = new Set(Un(e, n).map(e => e.position))
  for (const p of twoHandSuppressed(e)) r.add(p)      // <- the one line
  return Kt(Hn(e).filter(e => e.position !== t && !r.has(e.position)))
}
```

That covers three surfaces at once because they all route through `Wn` — whole-loadout totals (line 20624), the marginal baseline (20625), and the candidate-scoring baseline (18341, 22873). The auto-fill generator at 11861 builds its own totals locally and needs its own guard.

**Ship it as a dismissible banner, not a hard block,** and say why in the copy: the rule is inherited from classic EverQuest and is **unmeasured on Legends**. No log in my 138 shows a two-handed primary; both inventory dumps are one character with a one-hander. The Legends-side support is indirect — eqlwiki's Game Mechanics Dual Wield section compares "the stronger arrangement… against the two-handed weapon", which presumes the rule without stating it. **Do not add a dual-wield class gate**; the geometric rule is safe and the class rule is genuinely unsettled.

### 2.7 Forty-eight effect names render literal wiki markup on screen
**Impact medium · confidence certain**

48 `fx[].n` entries across 48 items carry unescaped markup as their name. Thelvorn ships:

```json
{"k":"proc","n":"<span class='itemeff'>Dismiss Summoned</span>","d":"Combat, Casting Time: Instant","lv":45}
```

The app renders `e.n` as a plain JSX child, so React escapes it and it **shows literally**: Thelvorn's paperdoll line currently reads `Effect: <span class='itemeff'>Dismiss Summoned</span>, Dismiss Summoned`. A recursive scan finds markup at `fx[].n` and nowhere else, and 0 HTML-entity leaks anywhere — one parser, one field. I re-counted today: **48**, on your live shards.

Two corrections to an earlier read of this, both of which make the fix safer: **all 48 have a same-kind twin carrying the same effect name, so nothing loses an effect if the markup rows are dropped**; but a plain dedupe on `(k, n, d, lv)` after stripping tags collapses only **43 of 48**, because five twins differ in payload — Staff of Writhing's clean twin carries `Rate +75%` the markup row lacks, Red Dragon Tooth's clean twin carries `lv: 1` where the markup row has "at Level 1" inside `d`.

**Fix.** Strip tags in the effect parser, then **merge rather than dedupe**: "prefer the entry with a populated `lv`, then the longer `d`" resolves all five without a human. Separately, 4 items list one effect name under two different `k` (click + proc); those need a human read of the source page, since click and proc are different lanes.

### 2.8 Anthemion and Shadow Rage also drop in the Plane of Fear
**Impact medium · confidence certain · `/sets/`**

Both blocks read "— The Plane of Hate. TIER M". Every other set on the page reads both planes.

**M.** In `wl44-swap-boundary.log` the zone line at 22:15:35 on Fri Jul 31 is `You have entered The Plane of Fear 2 (Adaptive).` and the next zone line is not until 23:34:31 — I checked the full sequence, no intervening change. Inside that window:

- `You looted an Anthemion Jerkin +2 from a tentacle tormentor's corpse and stored it in your Dragon Hoard` (22:29:03)
- `You looted a Shadow Rage Boots +2 from a boogeyman's corpse…` (22:52:36)
- `You looted a Shadow Rage Gloves +2 from a scareling's corpse…` (22:55:16)
- `You looted a Shadow Rage Wristguard +2 from a decrepit warder's corpse…` (23:05:06)

All four mobs are on your own Plane of Fear plate as Fear sources for other sets. The Hate-only reading looks like small-sample truncation: these two sets have the fewest sightings on the page.

### 2.9 The `nodrop` contamination row asks for a screenshot you already published
**Impact medium · confidence certain · internal conflict**

`/learn/contamination.html` row `nodrop` (65 unmarked, 1 marked): *"Legends may use different wording. **Unchecked.** What would settle it: One screenshot of an item tooltip carrying the flag."* Meanwhile `/learn/still-true.html`, dated 10 Aug, already says: *"The reward reads Class: PAL, Race: ALL, **Lore Equipped, No Trade**."*

The counts are available across the 11,534 `{{Itempage}}` records: No Drop 3,292 · Lore Item 4,431 · Magic Item 5,432 · No Trade 297 · Lore Equipped 178 · Attunable 110 · NODROP 54 · Placeable 44. Three spellings of one idea coexist, and Attunable and Lore Equipped have no classic equivalent — so one convention is Legends-native and identifiable by name.

**Fix.** Change "Unchecked" to the answer with the counts, and cross-link the epic entry that supplied it. The general fault is one you already name elsewhere: a finding landed on one page and not on the page whose job it was.

### 2.10 The rest, compactly

| # | Where | What | Fix | Conf |
|---|---|---|---|---|
| a | `wp.skill` on 92 rows | Value is `Piercing`; the **client's own vocabulary is `1H Piercing`**. Corpus skill-ups: 1H Piercing **284**, 1H Blunt 130, 2H Slashing 20, Hand to Hand 8, 1H Slashing 5 — and **zero** bare `Piercing`. `classes.json` agrees (`1H Piercing` ×12, `Piercing` ×0). Your normalizer runs *away* from the client vocabulary here: McMannus Clan Dagger arrives as `1H Piercing` (preserved in `skillRaw`) and is normalized down. | Source `Piercing` → `1H Piercing`; `2H Piercing` unchanged. Vocabulary only — **moves no weapon between skills**, and I explicitly do not claim which of the 92 are one- vs two-handed (several are LARGE PRIMARY-only spears; the corpus cannot settle it). Leave the 11 `Throwingv1/v2` `skillRaw` rows alone — that normalizer is working. | certain |
| b | The Index slot filter | `fS.has(i.s)` tests the single canonical slot, not the recorded list. **57 rows record "Secondary" in `sl`; the filter reaches 12.** Misses Stiletto of the Bloodclaw, Flaming Fist, Barbed Leather Whip, Bronze Rapier, The Artist's Brush. | Test `sl`. Add "offhand-legal" with a **third state** — 30 of 87 weapon rows carry no `sl` at all, and must show "not recorded", never "no". | certain |
| c | `meta.json → weaponSkill.suspectRule` | The rule is printed on screen beside `suspectCount: 4`, and applied literally it selects **5** — the four plus **Bloodclaw Mace** ("claw" inside "Bloodclaw", MNK explicit). You are right to exclude it; the rule string just doesn't reproduce its own count. | Add a word boundary: `/\b(fist\|knuckle\|claw\|cestus\|ulak\|fistwrap)/i`. Reproduces 4 exactly. Do **not** swap to a size/weight shape test — I ran it, it misses Brass Knuckles and picks up Efreeti Scimitar and Fool's Gold Stein. | certain |
| d | `/dungeons/lowerguk` | Caption above the drop tables: *"No session in this zone has been parsed, so nothing here is a count."* The measured section lower on the same page reports Hoptor Thaggelum at 62.5 avg / 127 max with six drops. | Narrow it to the tables it governs: *"nothing in these tables is a count; the measured section below is a single run and still supports no rate."* Also: the Hate plate writes "Magi P\`Tasa" in the roster and "Magi P\`tasa" in the measured table (client uses lowercase t); `/named/` writes "Cazic Thule" where the client, the Fear plate and `/learn/difficulty` all use "Cazic-Thule". | certain |
| e | 32 Kunark rows, `av: true` | `/tools/50-upgrades.html` §01 says *"3,653 of what survives are here on era alone; the other 10 have no era placing them."* The 32 fall in neither bucket. **There is no policy violation** — all 32 pass `era.policy`'s second clause (12 `eqlsource-id`, 11 `measured-drop`, 9 `live-export`) and I checked every one. The code is right; the prose has no sentence for them. | Widen §01's second clause to cover era *rank*, not only era absence, and pair the era chip with "shipped on Tier M existence evidence". Two sentences. | certain |
| f | `contamination.json → dmg-bonus.classic` | *"Classic printed a Dmg Bonus line… derived from character level and weapon delay"* merges two cases. In classic EQ the **one-handed** bonus was a function of level alone; delay entered only for two-handers. eqlwiki's Game Mechanics page names the old formula outright: `floor((Level - 25) / 3)`. | One clause. And add the new signature in §3.1.4 while you are in the file. | certain |
| g | `contamination.json → haste-stacking.findings[0]` | *"Either the scorer was fixed or the scanner's pattern no longer matches."* **It was fixed.** `dn(e,t){ let n = Math.max(t,e)-t; return {counted:n, wasted:e-n} }` at line 11127, called as `dn(t, r.existing?.haste ?? 0)` with the incumbent computed by `Wn()` with the candidate's position excluded; `Kt()` takes the max on the totals side (`o>t.haste&&(t.haste=o)`). The two halves agree. | State it positively and name the function. This is currently the **only row on that page you can close**, and a scanner that can say "fixed, here is the code" is far more persuasive than one that only counts hits. (`haste-pct` is untouched and stays open.) | certain |

### 2.11 Four things I checked and did **not** call wrong

Recorded so nobody re-runs them, and because two of them are places where a hasty audit would have handed you a false error.

- **`/items/` "435".** Correct. 441 rows = 435 + 6 families. My first parse said 440; that was my bug.
- **The difficulty page's "about 12%".** I measure 12.6% on 459 deduplicated upgradeable drops with a known zone tier, and **zero** below the floor. The rule holds. (§3.5 has a refinement, not a correction.)
- **The Lord Nagafen measured row.** It is evidently a selection, not an inventory — Gauntlets of Fiery Might is in your own sightings and on the plate elsewhere but not in that row. Its omissions are not errors.
- **The weapon-skill distrust card**, which reports Monk fist-weapon suspects rather than correcting them. That is a defensible reading of your own standard and should not change. Note only that the wiki has since been corrected *to agree with you*: `Whitened Treant Fists` revision 171348 (2026-08-21, FizzleMaster, "Corrected flags and stats") changed `Skill: 1H Blunt` → `Skill: Hand to Hand`, the category to `Hand to Hand`, the flags to `No Trade, Placeable`, and added `Dmg Bon: 13`. That single edit closes three of your open items at once, all in your favour. Re-scrape and promote; the settle line drops from four client tooltips to three.

One correction to the sentence while you are there: *"all four independent scrapes"* cannot hold for jmoyers, whose only skill data for this item is inside the `statsBlock` string, and whose 2026-08-22 snapshot **already read `Skill: Hand to Hand`**. Your provenance record names jmoyers' role as "statsBlock", so that is a field you hold and did not consult.

And a better `classic` explanation than the one you have: eqlwiki Game Mechanics, "Miscellaneous Details for Legends", carries the bullet **"All Hand to Hand weapons are now 1H Blunt weapons"**, sitting among items dated to a 2013 patch and a 2016 patch, under the wiki's own header warning *"These need to be verified to be true on EQLegends."* The rule that produces your catalogue's shape is present on the wiki, is classic, and is marked unverified — which is your scanner's thesis, stated by the wiki itself.

---

## 3. Gaps you already name that I can close now

### 3.1 The damage bonus — the headline

You state this gap in four places, and the settle condition you wrote has already been met, by someone else, on a page a per-item scraper never touches.

> **§03:** "Damage bonus is absent. A client window shows one, no source carries it per item, and it appears to be derived from level and weapon type rather than stored on the item."
> **Planner card:** "The live client shows a Dmg Bon line and no source in this project carries it per item, so this planner prints nothing there. A dry streak is a ceiling, not a zero…"
> **`contamination.json` settle:** "Two client tooltips for the same weapon at different character levels would show whether it is stored or derived. Until then it cannot be computed, so it is not printed."

**Your read of the *shape* was right and is now confirmed. It is derived from level and weapon type. Here are the coefficients.**

#### 3.1.1 The formula (T5) and why it earns belief

eqlwiki `Game Mechanics`, section "Main Hand Damage Bonus on EverQuest Legends" → "Working Legends Damage Bonus Formula", added **2026-08-11** by user Maergoth (rev size 41269→43724):

```
Damage Bonus Raw = Hand Modifier × max(Character Level, Weapon Damage)
                   × (min(Weapon Delay, 50) / 40) × (Character Level / 100)
Hand Modifier: One-Handed 0.8 · Two-Handed 1.1
```

This is wiki prose — **T5 by your own rule** — and it says of itself *"It should not yet be described as the exact server formula."* The same section publishes 14 rows it labels "Confirmed Legends Observations… directly observed in-game", including **exactly the test your settle line asks for**: the same 24-delay one-hander at four character levels, L32→5, L48→12, L49→12, L50→13. One weapon, four levels. That answers stored-vs-derived on its own.

It is also, character for character, the same shape my own repo carries. My first commit with `HandMod` is 2026-08-23. The wiki predates me by twelve days. **I am not claiming this as a derivation and neither should you.**

#### 3.1.2 T2 corroboration: 19 statblocks, 18 already in your catalogue

I extracted `Dmg Bon:` from the jmoyers `statsBlock` field today — the exact field your own provenance record says you ingest from that repo — over all 11,534 keys. **20 hits: 19 spelled `Dmg Bon:`, one spelled `Dmg Bonus:`.** Evaluated against the published formula with `floor()`:

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
| Whitened Treant Fists | Hand to Hand | 14 | 28 | 13 | 14 | **13** |
| Efreeti Mace | 1H Blunt | 10 | 30 | 15 | **15** | 14 |
| Spiroc Battle Staff | 1H Blunt | 8 | 30 | 15 | **15** | 14 |
| Spiroc Wingblade | 1H Slashing | 15 | 38 | 18 | 19 | **18** |
| Blade of Abrogation | 1H Slashing | 20 | 39 | 19 | **19** | 18 |
| Efreeti War Axe | 2H Slashing | 12 | 28 | 19 | **19** | 18 |
| Efreeti War Staff | 2H Blunt | 10 | 30 | 20 | **20** | 19 |
| Efreeti War Maul | 2H Blunt | 15 | 35 | 24 | **24** | 23 |
| Skycleaver | 2H Slashing | 30 | 35 | 24 | **24** | 23 |
| Efreeti Wind Staff | 2H Blunt | 12 | 36 | 24 | **24** | 23 |
| Efreeti Zweihander | 2H Slashing | 24 | 45 | 30 | **30** | 29 |

**19 of 19 fit, at level 49 or 50.** All six two-handers fit at 50. Of the thirteen one-handers, seven fit at 50, four at 49, two at both. Fit counts for other constants: **0.8 → 19/19. 0.75 → 11/19. 0.69 → 6/19** (and the six are the two-handers, so 0.69 fits **0 of 13** one-handers).

The level split is not a free parameter I invented to rescue a fit. **eqlwiki's own independently-published level-49 observations include 1H delay 22→10 and delay 23→11 — two of these rows unchanged.** This is also why a single-level fit looks like failure, and why earlier passes (mine included) concluded "no constant fits": force all thirteen onto one character and there is no solution, which is a fact about the batch, not about the formula.

Solving the feasible bands under truncation:
- The six 2H rows at L50 force the two-handed modifier into **[1.0971, 1.1022)** — a 0.5%-wide band containing 1.10.
- The seven L50-consistent 1H rows force the one-handed modifier into **[0.8000, 0.8205)**. Note the lower endpoint: **0.8 is the smallest value that fits.** Anything below fails, which is exactly why a lower constant looks plausible on any single row.

#### 3.1.3 M corroboration: your own client window

`it-PRIMARY.json` → Earthshaker → `sdc`: *"observed in a live client window at +10 — Base Dmg 74, Delay 70, Ratio 1.057, Strength 16, Stamina 16, SV Void 10."*

`1.10 × max(50, 74) × (50/40) × 0.50 = 50.875 → 50`, and your `meta.json` records the client showing **50**.

This row also proves the formula takes **tier-upgraded** damage, not base: at +0 Earthshaker is 37, `max(50,37)=50` gives 34, and only the upgraded 74 gives 50. Your catalogue holds exactly one Earthshaker window and it is the +10 one, so there is no tier ambiguity to resolve.

#### 3.1.4 What to ship

**Two cheap, better-sourced things before any derivation.** Refresh the `jmoyers/everquest-companion` pin (`meta.json.provenance` pins `d25455e`; the snapshot I read is `fd5e5bb`, dated one day after your build) or re-scrape eqlwiki directly, and in the statsBlock parser that already extracts DMG and Atk Delay, add:

```js
const m = /Dmg\s*Bon:\s*(\d+)/i.exec(statsBlock)
if (m) wp.db = Number(m[1])          // T2, harvested
```

**Harvest `Dmg Bon:` only. Treat `Dmg Bonus:` as a suspect source value** — that is the second authoring convention and it is unreliable: `silver dagger of destruction` prints 6 on a 20-delay one-hander (against Sphinx Claw's 10 at the same delay), and a Butcherblock hammer prints 113 on a 45-delay two-hander against Efreeti Zweihander's 30. Same two-conventions phenomenon you already document for tradeability flags.

**Do not put it in `wp.bonus`.** That key is taken — line 9979, `let s = L(n?.bonus ?? t.AC_BONUS); s && (a.bonus = s)`; `wp.bonus` is a **shield's AC bonus**. It happens to be unpopulated on all 3,663 rows today (I verified: 0), which is precisely why it is easy to walk into. Use `wp.db`.

**Then the derived arm, as one pure function:**

```ts
// eqlwiki `Game Mechanics` § Working Legends Damage Bonus Formula (T5 prose),
// corroborated by 19 Itempage statsBlocks (T2) and one client window (M).
const TWO_HANDED = new Set(['2H Slashing','2H Blunt','2H Piercing'])
const MELEE = new Set([...TWO_HANDED,'1H Slashing','1H Blunt','Piercing','1H Piercing','Hand to Hand'])

export function derivedDmgBonus(skill, dmg, delay, level) {
  if (!MELEE.has(skill)) return null
  const hand = TWO_HANDED.has(skill) ? 1.1 : 0.8
  return Math.floor(hand * Math.max(level, dmg) * (Math.min(delay, 50) / 40) * (level / 100))
}
```

Inputs you already hold: `wp.skill`, the tier-upgraded damage `Gt()` already computes, `wp.dly`, and a level.

**Where it applies: main hand only.** `Kt()` (line 10984) attaches the weapon object only when `position === 'PRIMARY'` or `'SECONDARY'`; set the bonus on `weapons.primary` and leave `weapons.secondary` alone. Measured off-hand bonus is **0** (M). Any Slot needs no change — it never populates `weapons`, so your copy *"Any Slot takes any wearable item — a worn position, not a hand, so weapon damage scores nothing here"* stays true. Compute it at `Kt`, not in `Gt` (which has no level and no position) and **not** in `zn()` at line 11681 — `zn` feeds the row subtitle builder, the compare map, *and* the planar-set stat summation at line 17673, which would add damage bonuses across a set.

**Where it renders.** The Weapons card, lines ~20061–20085, as a third term: `74/70 dmg/dly · ratio 1.057 · Dmg Bon 50`. And in the set diff, because on a big two-hander the bonus is **not constant across +0..+10** — Earthshaker's climbs 34 → 50 with no other term moving, once upgraded damage passes character level.

**Two caveats belong in the note, because the wiki states them itself:** the rounding rule below level 50 is unsettled (its own L32 and L48 24-delay rows are off by one under truncation), and the `max(Level, Damage)` branch has not been isolated in-game. Both are invisible at level 50 with sub-50 damage, which is nearly every row you ship. At level 1 the formula returns 0 for almost everything, and `Ze()` defaults every class to level 1 — so **treat level 1 as "not set", print `—`, and say "set a level"**. Printing 0 would break your own absent-is-not-zero rule.

**Badge it honestly and it still reads well:** *"Tier 5 formula, Tier 2 corroboration"* — a formula published on eqlwiki's Game Mechanics page, which exactly reproduces 19 printed `Dmg Bon` figures on eqlwiki item pages and your own +10 Earthshaker window. On the 18 harvested rows the badge reads *"Tier 2 · eqlwiki statblock"*.

**The build assertion is the best part.** Those 18 become an anchor set. Assert on every build that each harvested figure reproduces from the formula at L49 or L50. It passes 18/18 today, it runs in public exactly like the contamination scanner, and it turns the `dmg-bonus` signature from "nothing to mark" into a real marked/unmarked count. If a rescrape breaks it, you learn at build time and the row is named.

**And the sentences are not equally wrong.** `contamination.json`'s scoped *"no source **in this project** carries it per item"* is defensible as of its scan date and needs a date attached. `meta.json`'s unscoped *"No source carries it per item"* is the one that is now plainly false. Fix them separately. Also: *"jmoyers has it on 1 item only"* is a statement about a field you did not read — jmoyers' *structured* stats array carries no damage-bonus key on any of 11,534 items (I checked every key), because the figure lives only in the raw `statsBlock` string.

**One new signature worth adding in the same commit.** `dmg-bonus-table`, group `changed`. Two eqlwiki **class pages** carry a section headed "Primary Hand Damage Bonuses" giving a flat level-only table — *"Level 28: 1 … Level 46: 7, Level 49: 8, Level 52: 9, Level 55: 10, Level 58: 11"* — with the line *"This is the same for all melee classes."* It is a straight classic import: it runs to levels 52, 55 and 58, which a level-50 game cannot reach. At level 50 it yields a flat **8** for every one-hander, against observed figures of 5, 7, 9, 10, 10, 11, 12, 13, 13, 15, 15, 18, 19 (T2) and a client reading of 13 (M). And it is **unevenly marked in exactly the way your scanner exists to catch**: the Monk page carries it under a red banner reading *"This is not yet confirmed for EverQuest Legends"*; the Warrior page carries the identical table bare. One marked, one unmarked, and that is the whole population. It is the first signature you could close on the day you ship it.

### 3.2 Haste — I can close half of it, and I should tell you which half

Your contamination page names haste as its one known-changed mechanic and asks for a screenshot. **I cannot give you that screenshot and neither can my corpus.** What I can do is fix the question, which is worth more than a wrong answer.

**Closable now (§2.1):** the *units*. Legends' stat is called Attack Speed, its unhasted baseline is 100, and it is printed in percent — M, off a client character panel: `Attack Speed %  100`. Corroborated T2 by 52 "Increase Attack Speed by N%" spell effects. Both of your cited sources write haste in percent. So a "+41%" item figure is **Legends' own unit, not a classic import**, and the `haste-pct` row's premise can be retired.

**Not closable, and the corpus could not have contained it:** stacking. No character in my 138 logs wears two hasted items. Your planner already says exactly this about itself, correctly.

**Your settling test needs replacing, and the replacement is better.** Your planner already names a workable one-item version verbatim: *"a Legends item tooltip showing its haste line beside the character's Attack Speed reading, on a character wearing that item and nothing else hasted."* The **two-item** version separates the stacking models outright — read Attack Speed with one hasted item, then with a second:

| model | 41% + 21% reads |
|---|---|
| additive | **162** |
| highest-only | **141** |
| compounding | **171** |

Far enough apart that one screenshot pair decides it, and it is the question eqlwiki (*"only the item with highest haste % counts"*) and EQL Tools (*"item + spell + overhaste stack up to the cap"*) actually disagree about.

**Do not take my 1.900 as evidence for anything** — see §1.3(2). A percentage that divides delay and a flat stat of 190 against a base of 100 predict the identical swing rate, so no swing-rate measurement can separate them. Your note is correct as it stands and asks for precisely the right thing.

### 3.3 The upgrade curve deserves the green light you are giving only the base values

> **`meta.json → dataReliability.stats`:** "AC/attributes/saves/dmg/delay reproduce the client exactly on every Tier 0 sample." · **Sources card:** "This is the one green light on the page, and it is narrow."

It is narrower than it needs to be. Your five `sdc` capture records also validate the **upgrade curve**, which is far more load-bearing — a base value is applied once, the curve is applied to every one of 1,713 statted rows at eleven tiers. I re-derived every upgraded field against your shipped engine: **22 of 22 exact**, across all five records.

- Bone-Clasped Girdle +4 — AC 4→8, HP 75→105, MANA 75→105, STR/STA/DEX 7→11 (6)
- Bladestopper +6 — AC 25→40, HP 50→80, STA 15→24 (3)
- Cloak of Flames +7 — AC 10→17, HP 50→85, AGI 9→16, DEX 9→16, **HASTE 36→43**, SV Fire 15→25 (6)
- Earthshaker +10 — DMG 37→74, STR 6→16, STA 6→16, **SV Void → 10** (4)
- Whitened Treant Fists +1/+2/+3 — DMG 15, 16, 18 from base 14 (3)

**Two rules fall out that nothing else in the field settles.**

**Haste takes the flat +1/tier rule, not the scaled one.** 36+7 = 43, where the scaled rule gives **61**. That is an 18-point gap, so a reader recomputing by hand concludes your planner is broken when it is right. *(This one corrects me: my `EQUIPMENT-TRUTH.md` presents the 10%/tier rule without exception, because it was validated on an item with no HASTE. Your engine is right and my doc is not.)*

**The +1/tier floor is confirmed where it actually binds** — three items, seven fields: Bone-Clasped's STR/STA/DEX 7→11 at +4 (percentage gives 9), Cloak's AGI/DEX 9→16 at +7 (gives 15), Earthshaker's STR/STA 6→16 at +10 (gives 12). Three independent items is a much better claim than one.

**And it closes a conflict two other sites still list as open.** eqlwiki `Item Upgrade System`, live and verbatim: *"Weapon damage is increased at +5% per Tier."* Your Whitened Treant Fists capture reads 14/15/16/18 at +0..+3; +5%/tier predicts 14/14/15/16. The +3 reading refutes it outright — even granting the page's own mid-tier accumulation rule, +5% cannot exceed 20% cumulative at tier 3, and 18 from a base of 14 requires 28.6%. EQL Tools lists the identical question as open on its upgrades page: *"the wiki says +5%, this site's tools use +10%. One weapon read at two tiers settles it."* **Your Earthshaker window (37→74 at +10) is that reading.** Publishing the closure is a contribution outward, not a correction inward.

**Fix.** Split the confidence note in two — base values (what it says now) and the curve (22/22 across five windows, with the two rules only these captures settle) — and add one line closing the +5% question. Three sentences, and it converts a modest disclaimer into the strongest single claim on the site. Your landing page already carries the best version of this for one item (*"nine of nine predictions exact… and the synthetic SV Void at 10, a rule that appears in no documentation"*), so this is aggregating a claim you already make well.

### 3.4 Three more you can close, briefly

**Publish the derived Void save rule.** Read out of the bundle (`Ft()` line 10852, `Wt()` 10929): at tier n>0, an item carrying at least two distinct stats from `{STR STA INT AGI DEX CHA WIS SV_FIRE SV_COLD SV_POISON SV_MAGIC SV_DISEASE}` gains `SV Void = n`, maxed against any upgraded base Void. Validates **2 of 2** — Earthshaker +10 → 10 (your window), Midnight Clad Straps +6 → 6 (a client tooltip in my `EQUIPMENT-TRUTH.md`). It is a genuinely good piece of reverse-engineering that currently exists only in minified code, and it is exactly the derived-rather-than-sourced number you are scrupulous about labelling everywhere else. Name the untested edge in the same card: an item with fewer than two qualifying stats derives no Void, and no capture in either project covers that case. *(Half a correction to me: my `EQUIPMENT-TRUTH.md` §2 says the catalogue "knows only the classic five" — wrong, Darkspun Shroud carries VOID 1 and Anthemion Armbands VOID 2. Its second half survives in weaker form: base Void exists on 2 rows, the derived value depends only on tier and on having two qualifying stats, so it **does not discriminate between items and should not be ranked on**.)*

**Document the empty ATTACK column.** `statKeys` publishes `ATTACK` and `Kt()` sums it (`t.attack += e.flat.ATTACK ?? 0`), but nothing says why it is always zero. **0 of 3,663 rows carry it — I verified across all 19 shards — and that is correct rather than missing.** In the whole 11,534-record wiki snapshot exactly **two** items carry an Attack line: `holgresh spirit beads` (The Wakening Land, and its `Attack: +7` is inside an HTML comment in the wikitext) and `kerasian axe of ire` (2H, DMG 46, Haste 40%, Attack +40). Both are quarantined by your own era policy — I checked them against your catalogue. Worn ATK is a designed channel living entirely behind unshipped expansions. One `dataReliability.attack` card with confidence `structurally-absent` converts an unexplained empty column into a documented fact. It matters more than it looks: ATK enters melee damage through `Wrath = Offense + ((2×STR)−150)/3 + WornATK + SpellATK`, and +104 ATK is worth +11 to +13% of total DPS in my model — so the one stat with the most leverage on what your planner is for cannot be bought at any price in this era.

**Say the weapon-damage upgrade divergence out loud.** Two functions ten lines apart: `At(e,t)` (line 10822) is `e<=10 ? e+tier : e+floor(e*Ot(t)/10)` — algebraically identical to the `value + max(tier, floor(value·0.1·tier))` rule your captures validate. `jt(e,t)` (line 10831) is `e+floor(e*Ot(t)/10)` with **no +1/tier floor at all**, and `Gt()` sends `wp.dmg` through `jt` while every other scaled stat goes through `At`. No capture distinguishes them, because both captured weapons have base DMG above 10. But **265 of the 431 melee weapons in your catalogue — 61.5% — have base DMG below 10**, and under `jt` their damage does not move at +1 at all; a 9-damage weapon reaches 19 at +10 under the floor rule instead of 18, a 3-damage weapon reaches 13 instead of 6. The upstream is ambiguous rather than silent: eqlwiki's Item Upgrade System states the floor as a rule about *stats* and then carves weapon damage into its own percentage bullet. **One line in "What it will not tell you" is the right move, not a code change.** One client window settles it and it is cheap: **Efreeti Standard at +1 or higher** (3 dmg / 10 delay, already in your catalogue). *(My repo has the mirror of this: `model4.py` line 67 applies the floor to weapon damage, which turns Efreeti Standard into a 13-damage off-hand at +10 and forced an empirical `OH_RATE_CAP=1.42` whose comment names Efreeti Standard by name. If `jt` is right, that cap was patching my own upgrade rule.)*

### 3.5 Data I can hand over, in your existing schemas

| What | Size | Notes |
|---|---|---|
| **name → item ID pairs for `items.v1.json`** | **279 new** | From the four `/outputfile` dumps. **79 names overlap your file and 79 of 79 IDs agree, zero conflicts** — so there is no adjudication step, only `hash` moves. Your stability note holds too: 358 distinct base names across the four dumps, none carrying more than one ID across `+N` and `(Exaltation)` forms. Named examples currently `id: null`: Crystalline Spear 11610, Eye of Innoruuk 20656, Valorium Bracers 4854, Swirlspine Belt 2471, Anthemion Skullcap 7835, Shadow Rage Helm 55601, the Apothic set (1240–1244). On the widest scope this also promotes **92 rows from era-inference to Tier M `live-export` existence** — including Thelvorn, currently one of your strongest weapons and standing on era alone. Two near-misses want a human eye, not an insert: export `Dark Reaver` (5404) vs catalogue `A Dark Reaver`; export `Guise of the Deceived` (177948) vs catalogue `Guise of the Deceiver` (2469). Generalise the `live-export` resolver from one named file to a directory. |
| Deduplicated tiered upgradeable-drop table | 459 rows | Behind the floor test in §3.6. |
| Full loot table | 1,604 rows | Zone, party token, tier, mob, item, +N, disposition. |
| New set piece/mob pairs vs `sightings.v1.json` | 58 pairs + 12 unsighted pieces | See §3.6. |
| Plane of Sky Awakened run, parsed boss by boss | 114 loot events | See §3.6. |

Per your own issue-template warning I will not attach raw logs to a public issue; happy to hand the files over directly.

### 3.6 Measured content that fills named holes

**`/raids/plane-of-sky` open question 1 is closed.** *"Anything about Sky above D0 — one logged run."* The run exists: `You have entered The Plane of Sky 1 (Awakened).` (Sat Aug 01 21:57:48, `wl44-swap-boundary.log`) opens a full progression with 114 loot events, 61 carrying a `+N`. **What it establishes, no wider than the evidence:** the ring, the key chain and the boss list are unchanged, and the loot floor behaves as in a dungeon — all 61 upgradeable drops are +1 or +2, none below the +1 floor. **It establishes nothing about HP, damage or experience scaling in Sky**; I made no such comparison. Base and Awakened runs sit in the same log by the same character, so the loot comparison is within-character and within-gear.

**The key chain is 7 of 7, and there is an eighth key you name nowhere.** Key of Swords is confirmed from the Thunder Spirit Princess's corpse in two separate runs (`--You have looted a Key of Swords from a thunder spirit princess's corpse.--`, Fri Jul 31 23:59:44; and again Sat Aug 01 22:00:07). All seven ring keys are now confirmed by a loot line naming the corpse. She also drops **Key of the Misplaced** — in both runs, seconds before the Key of Swords each time — plus a Symbol of Marr. I grepped every fetched page, all three public datasets and the planner bundle for "Misplaced": zero hits. An unnamed eighth key on the ring bears directly on your open question 4 (whether there is a tenth island). Keep open question 2 open but narrow it from "no measurement of any kind" to **"no damage figure"**: her only player-credited kill in my corpus is a fragment, and her other logged deaths are credited to a charmed pet.

**Anthemion and Shadow Rage gain five pieces.** Anthemion Skullcap (`+4 from Cleric of Innoruuk`, Hate Refined; also ID 7835 in a dump) and Anthemion Jerkin (`+2 from a tentacle tormentor`, Fear); Shadow Rage Helm (ID 55601), Gloves (55605) and Boots. New source for a listed piece: Shadow Rage Wristguard from a decrepit warder. **Your own planner corroborates:** the bundle holds **six** Shadow Rage pieces and its copy says *"Six Shadow Rage pieces are in this catalog because a live client holds them and the owner named the set."* The sets page shows three. Slots are inferred from names and empty slots, not measured — the dumps carry no worn-slot field for these rows.

**The "Dropped by" lines need the hedge your efreeti table already has.** Sixteen of eighteen set blocks list exactly six sources. Against your own `sightings.v1.json` that six is a **truncation, not a total** — Lustrous Russet has 12 distinct source mobs in the dataset, Rune Etched and Midnight Clad 15 each. A reader planning a farm around a six-entry list concludes a piece has one camp when your own data knows several. *(This corrects my own first pass, which read the six as complete and offered "nine new sources" — most of those nine were already in your data, below the cut.)*

**Two efreeti items on no page, dataset or bundle:** Efreeti War Club from Noble Dojorn (`--You have looted an Efreeti War Club +1 from Noble Dojorn's corpse.--`, Sat Aug 01 22:59:58) and Efreeti War Maul from the Hand of Veeshan (23:29:25). **One sighting each** — the line appears in two overlapping fixture files at the identical timestamp, which is one event, not two. Four new source pairs for items already on the table: Noble Dojorn → Efreeti War Spear; Overseer of Air → Efreeti Belt; the Hand of Veeshan → Efreeti War Spear and Golden Efreeti Chestplate.

**The island "Drops" lines want the same hedge.** The belt and bracelet line is **zone-wide, not island-specific**: eleven distinct pieces appear across 214 deduplicated Sky loot events, and **all eleven also drop from the soul/essence trash family**. Six came off bosses on two or more different islands. Five appear on no page, in no dataset and nowhere in the bundle: Belt of the Pine, Belt of Transience, Bracelet of Cessation, Bracelet of Exertion, Bracelet of Quiescence — as do Weight of the Gods, Stein of Flowing Ichor and Jester's Mask. Where the page is right it is right: Whitened Treant Fists is listed on island 6 and did drop from Bazzzazzt.

**Orb of Tishan drops from Lord Nagafen** — two distinct events, `+1` (Fri Jul 31 18:03:58) and `+4` (20:02:39) — and appears **nowhere on eqlsource**: not `/items/`, not the Nagafen plate, not `sightings.v1.json`.

**The loot floor rule holds, and the pooled figure hides a gradient worth publishing.** On 459 deduplicated upgradeable drops with a known zone tier: **zero below the floor, 58 above = 12.6%**, landing on your "about 12%". Per tier: D0 34/142 = 23.9% · D1 19/84 = 22.6% · D2 3/105 = 2.9% · D3 2/48 = 4.2% · **D4 0/80 = 0.0%**. Your "three drops settle it" survives the gradient — at D0, the worst tier for it, the floor value still turns up 76.1% of the time, so three drops identify the tier 98.6% of the time. **One caution against overclaiming:** no dropped item anywhere in the corpus exceeds +4 (while merges reach +8 in a log line and +9 in the dumps), but that +4 is a *design* ceiling is **not separable from D4 being the current maximum tier** — +5 could only ever arrive as an above-floor roll at D4.

**The client prints loot in four grammatical forms and you quote one.** Across 1,604 distinct loot events: `…and sold it for N platinum` / `…for free` **1,062 (66.2%)** · `--You have looted X from Y's corpse.--` **321 (20.0%)** · `…to create <item> +N` **140 (8.7%)** · `…and stored it in your Dragon Hoard` / `…your currency` / `…your tradeskill depot` **81 (5.0%)**. Restricted to the 485 events carrying a `+N` — the only ones your floor procedure uses — your quoted "to create" form is **101 (20.8%)** and the undocumented autosell family is **285 (58.8%)**. Grepping every page I fetched for "sold it for", "stored it in", "Dragon Hoard", "tradeskill depot" and "You have looted": zero hits. A reader building a parser from `/learn/difficulty` keys on the form carrying a fifth of the evidence, and the missing share is not random — autosold and hoarded items are the ones the player did not keep. All four forms name the mob and carry the dropped `+N`.

**The zone line carries a third token you never show.** The full shape is `<zone>[ - Solo|Group][ N (Name)]`: `You have entered Nagafen's Lair - Group 3 (Fused).`, `The Plane of Hate - Solo 4 (Refined).`, `The Permafrost Caverns - Solo.` — 55 such lines, Solo 52 / Group 3. Your rule for the bare form still holds, and treating those rows as tier 0 produced **zero** floor violations. The gap is that `/learn/difficulty` splits every scaling figure into "multiplayer tuning" and "solo" columns without telling the reader the zone line already carries the token. You parse it elsewhere — `sightings.v1.json` sessions carry `"zone": "Nagafen's Lair - Group"`. **One stated limit:** that the token *selects* between the two scaling columns is my inference, not something I measured, so present the token and leave the mapping alone. Two parser traps worth a sentence: `" - "` is not a safe delimiter (`Neriak - Foreign Quarter`, `Neriak - Commons`), and `You have entered an area where levitation effects do not function.` matches the zone-line pattern exactly and fires 15 times.

**Lower Guk's client zone name appears on no page.** It is `The Ruins of Old Guk` (identified by the mobs killed there — the dead-side clan ladder and named roster of your own plate — not by name similarity; `The City of Guk` is Upper Guk). **Correction to my own first pass:** I claimed a reader could not join a log to a survey by any published field. False. The Hole plate's subtitle already reads "The Ruins of Old Paineel"; `sightings.v1.json` uses client names throughout; `/tools/faction-impact.html` publishes the full list including party tokens. What is genuinely missing is the link — no field maps a client zone name to a survey, and Lower Guk is the one plate that names it nowhere. Add `zone_line` to the `zones.v1.json` row schema (your data page's own promise permits it) and a "Zone line" row beside "/who name". The values already exist inside data you publish.

**Three `/items/` rows the wiki has withdrawn.** `Blackened Mithril Boots`, `Exceptional Ratman Blood`, `Kobold Foot Bones` all open with `{{Delete}}`, and the latter two carry a second marker: `{{: Does Not Exist}}`. Exceptional Ratman Blood's own dropsfrom block lists Dragon Necropolis and Plane of Mischief — post-classic zones — beside The Hole, which is the classic-import signature. **Counter-caution so this does not become a false errand:** `{{Delete}}` **alone is not evidence an item is absent from Legends.** `Small Ringmail Belt` carries `{{delete}} not relevent in EQ legends` and is demonstrably live — `You looted a Small Ringmail Belt +1 from a Teir\`Dal shadowknight's corpse and sold it for 2 platinum`, plus two more sightings, one carrying the Legends-only `+N` suffix. **The reliable signal is the pair `{{Delete}}` + `{{Does Not Exist}}`.** Badge the two rather than deleting them.

**The wider Delete sweep, and why it must be a flag and not a filter.** `api.php?action=query&list=embeddedin&eititle=Template:Delete&eilimit=500` returns 298 pages; exact-name join to your catalogue gives **145 still shipping**, 137 graded `sd: "tier-2"`. Of those, 112 carry `{{delete}} not relevent in EQ legends`, **23 carry a "Replaced by/with X in EQL" reason, and all 23 named replacements are also in your catalogue** — so the planner offers the dead item and its live successor side by side, same slot, same class: Rheumguls 35/43 vs Khyldorn the Blood Drinker 36/43 (SHD); Wu's Tranquil Fist dly27 vs Wu's Fist of Mastery dly22 (MNK); Rod of Warding Winds dmg15 vs Rod of the Protecting Winds dmg35 (ENC); Ebonsting 11/20 vs Thornstinger 12/19 (ROG). The cleanest single example: **Griffon Wing Spauldors** is a wiki *redirect* page (`#REDIRECT [[Griffon Wing Spaulders]]` + `{{Delete}}`) and ships as a full statted SHOULDERS/ROG tier-2 row, while the correctly-spelled **Griffon Wing Spaulders** ships separately as an existence-only row with `statsUnknown` and id 2703 — the same item twice, once with stats under a misspelling and once with its stats withheld under the right name. **Badge the 23 as superseded (the highest-value half, needing no judgement), list the 112 for a human pass, and never filter on the template** — its reason string is editorial wiki prose, not structured data, which is precisely why it should flag rather than filter. One case needs a decision either way: Cloak of Leaves (Sky) [BACK, DRU] is replaced by Spiroc Banisher Focus [PRIMARY/SECONDARY, DRU] — a different slot, so dropping it empties the Druid BACK list rather than substituting into it.

**Permafrost Caverns has no survey and a full five-tier campaign in my corpus.** `The Permafrost Caverns - Solo.` then `- Solo 1 (Awakened)`, `2 (Adaptive)`, `3 (Fused)`, `4 (Refined)`, reached from Permafrost Keep. 105 kill/loot events, a populated roster, an outer zone with its own named mobs, and Lady Vox's drop table measured. You are not silent on the zone — `/tools/faction-impact.html` lists it and `sightings.v1.json` carries Permafrost sessions — so the gap is a survey plate, not a blind spot, and `/learn/difficulty`'s Lady Vox reference would then link somewhere.

**Two corpus-hygiene notes you should apply to anything I hand you.** Five fixture files are byte-identical (`e2e-maps`, `e2e-planner`, `e2e-telemetry`, `e2e-toast`, `e2e-voice`) and `wl43` is largely contained in `wl44`. Deduplicating on `(timestamp, disposition, item, mob)` takes 1,866 loot lines to **1,604 distinct events** — a 14% inflation in every raw count. Conclusions are robust; the n's are not. And **mob names repeat within a fight** (one Frost Storm cluster prints three hits on `a revultant rat`), so distinct-name counting undercounts AE targets badly.

---

## 4. The two general scraping hazards

**This is the most transferable thing in the brief.** Both are properties of eqlwiki's page structure, not of any one spell or class, and any scraper on this project is exposed to both. Each has already cost me a published error — one a 7× damage figure, one a completely inverted AOE ranking.

### The principle underneath both

> **A structured field is a container, not a provenance. The tier attaches to the named field, not to the fact that a field exists.**

Your `/sources.html` Tier 2 definition — *"Infoboxes, NPC tables, item tables, coordinate records… Machine-shaped fields that somebody entered from the live game"* — describes the container. Both hazards below are cases where the container is machine-shaped and the contents are not what the container promises. It is the exact mirror of the sentence you already have on `/learn/still-true.html` (*"a tier 5 sentence inside a tier 2 container is the most dangerous object in this ecosystem"*) — this is the same object one layer down, in the data rather than in the narrative.

Three consequences worth one line under Tier 2, and worth repeating on `/data/index.html` since the whole point of publishing machine-readable data is that other people's scrapers will read one field and not the other:

1. **A citation says which field on which page.** "eqlwiki says" is not a citation, which you already know; "the eqlwiki spell page says" is not one either.
2. **A base value and a maximum are two different citations.**
3. **A template parameter whose contents are prose is Tier 5, however machine-shaped its wrapper.**

### 4.1 Level scaling lives on CLASS pages; spell pages carry only the base

**T2 against T2, 7.1× apart, on the same three spells.** Bard's three passive point-blank AE songs:

| Song | Spell page `SpellSlotRowSmart` | Class page `RadSpellRow2 max=` (header: "Max Effect") |
|---|---|---|
| Chords of Dissonance | `Decrease Hitpoints by 2 per tick` | `-14 HP/tick` |
| Denon's Disruptive Discord | `Decrease Hitpoints by 4 per tick` | `-16 HP/tick` |
| Selo's Chords of Cessation | `Decrease Hitpoints by 2 per tick` | `-27 HP/tick` |
| **total** | **8/tick** | **57/tick** |

Verified in the cache today: `class-Bard.wikitext` lines 180, 626, 1622; the three spell pages' own slot rows.

**The reason this is a hazard and not a curiosity: the spell-page field is *capable* of expressing level scaling and does not do it here.** On the same song, the spell page's own notation reads `Decrease Attack Speed by 17% (L48) to 20% (L60)` while the class page's max column reads `-25% Atkspd`. So the field carries scaling for attack speed and omits it for the hitpoint lines, and **neither page anchors its number to a level**. A scraper reading spell pages gets a number with no level attached and does not know it. A scraper reading class pages gets a different number with no level attached.

**And I must be plain that the magnitude is unsettled, because this is where I got it wrong twice.** My repo has treated 57/tick as the level-50 answer. **It is not established.** A Tier M reading refutes both as the *observed* number: `r3-song-shared-message.log` prints **19 lines of `has taken 8 damage from your Denon's Disruptive Discord`** — exactly twice the spell page's 4 and exactly half the class page's 16. The correct statement is: *two structured wiki fields disagree by 7× on Bard passive AE damage, neither states its level, and the one measured value matches neither.* Publish the disagreement; do not pick.

The hazard generalises immediately. Every class page on eqlwiki carries a `RadSpellRow2` table with a `max=` column, and every spell page carries a `SpellSlotRowSmart` base. Any spell whose damage or effect scales with level has two numbers in two places on two page types, and no scraper reading one of them can tell.

### 4.2 Target caps, wave counts and gates live in the `description` field, which most scrapes drop

**This one produced a completely inverted AOE ranking in my own work,** and I recorded the retraction: `DDD.md` §1 — *"I previously wrote 'no AE spell in the game states a target cap, so damage scales linearly with the pull, unbounded.' That is false."* The cause was reading the `effects` field, which my local spell database carries, and never fetching `description`, which it does not.

Selection rule so this is reproducible: eqlwiki `{{Spellpagesmart}}` pages whose `target_type` contains `AE` and with at least one class at level ≤ 50. That is **72 spells, 49 of them damage-bearing**. Eleven state a numeric target cap. Every string below verified in the cache today.

| Spell | Type | Cap | Verbatim |
|---|---|---|---|
| Invoke Lightning | Targeted AE | **4** | "up to 3 others nearby (outdoor only spell)" |
| Pillar of Fire | Targeted AE | **4** | "at most 4 creatures in the vicinity of your target" |
| Column of Lightning | Targeted AE | **4** | "several (up to 4) creatures" |
| Lightning Strike | Targeted AE | **4** | "up to 3 others nearby… at most 4 targets. Only castable outdoors." |
| Circle of Force | Targeted AE | **4** | "Hits up to 4 creatures max" |
| Gravity Flux | Targeted AE | **4** | "Only hits 4 mobs max" |
| Infectious Cloud | Targeted AE | **4** | "to all beings **[4 targets]** in a small area around your target" |
| Denon's Desperate Dirge | Targeted AE | **8** | "up to 8 enemies" |
| Entrancing Lights | PB AE | **8** | "up to 8 nearby creatures" (mez) |
| **Tremor** | PB AE | **24** | "as many as **24 others** nearby" |
| Earthquake | PB AE | **25** | "up to 25 nearby creatures" |

**Three mechanics that must never share a column with those, because collapsing them publishes a wrong number:**

- **Total-hits caps (a different mechanic).** Cascade of Hail, Pogonip and Avalanche each read: *"up to a maximum of 4 targets hit… Note: Rain nukes are limited to 4 hits total. Either you can hit the same mobs 3 times, you can hit 2 mobs twice each, or you can hit 4 mobs once each."* A single-target Avalanche cast lands 3 waves × 125 = **375**. A field labelled `targetCap: 4` tells a reader the opposite of the truth about that case.
- **Gates.** Outdoors-only: Invoke Lightning, Lightning Strike, Lightning Blast, Sunbeam, Harmony. Mob-*level* gates (not target caps): Color Flux/Shift/Skew, Mesmerization, Entrancing Lights (level 55), Harmony (40).
- **Inference.** Lightning Blast states no number: *"2.04 damage per mana on a single target, 8.15 damage per mana on a full quad. Outdoors only."* The 4 comes from the word "quad" and from 8.15 ÷ 2.04 = 3.99. Good inference, still an inference — it belongs in its own key with its reasoning, never merged into the cap.

**Fourteen damage-bearing AE spells at level ≤ 50 state no cap of any kind** — the whole Wizard storm line (including Frost Storm), every Magician rain, both Shaman rains, Icestrike, Supernova, Upheaval, the Word Divine line. **Your own discipline applies exactly: a dry streak is a ceiling, not a zero.** `capState: "unstated"` is not `"uncapped"`.

**Four traps a naive extractor walks into, every one a real page I verified today:**

| Trap | Page | What happens |
|---|---|---|
| `AoE range: 25` | Energy Storm | reads a **radius** as a target cap, identical in shape to Earthquake's real 25 |
| `farming large groups of up to 25 lower level mobs` | Supernova | reads a **worked example** as a cap |
| `[4 targets]` | Infectious Cloud | **misses a real cap** — no cap word present at all |
| `%T enemies` | Sacred Word | a client template token, never substituted |

That last one deserves its own line on the page: it is direct evidence that the **client** carries a target count for Sacred Word and the wiki transcription lost it. So `capState: "unstated"` is demonstrably a *transcription* state and not a game state, for at least one spell.

**And the tier discipline is the crux.** The `description` parameter is a structured container holding prose. `Gravity Flux`'s also contains *"Two different incompatible versions of this spell exists in game"* and *"Please confirm damage at various levels."* `Avalanche`'s contains a mana-efficiency argument. Nine of the capped pages open with `<noinclude>{{Classic Era}}</noinclude>`. **Every cap is T5 and must carry the verbatim string it came from, so a reader can see the prose and disagree.**

### 4.3 The same field can hold three different numbers

Same hazard, third form, and it is why any dataset here should ship damage as three separately-tiered fields rather than one:

| Spell | `description` (T5) | slot row (T2) | measured (M) |
|---|---|---|---|
| Earthquake | 214–246 | `214 (L31) to 246 (L39)` | **246** |
| **Frost Storm** | **250** per wave | **512** | **741** per wave |

Earthquake's three readings agree. Frost Storm's are 250, 512 and 741 — a 2.96× spread, and the measured value matches none of them. (`p4-pet-buff-kill-credit.log`: three waves at +1s, +4s, +7s after the cast, each 741; crits at 2246 and 2059, ×3.03 and ×2.78, consistent with the measured ×3.00 spell-crit constant; the 391 and 116 lines are partial resists.) The Druid rain line's description and slot row agree exactly (27/27, 62/62, 125/125), so the disagreement is a property of the Wizard storm pages, not of the field. **Nobody currently publishes the fact that they disagree.** That alone is a contribution.

---

## 5. What I can build, ranked

Four deliverables across three design briefs, all specced to the point of runnable code and all sitting in `/home/user/sky-ledger/` and `$S/tdm/`. Ranked by *value per unit of risk to your standard*, which is not the same as by interest.

### 1. The 50 Upgrades upgrade path — build this first

Additions only, to a tool you already ship, in priority order: **P1** the damage bonus (§3.1); **P2** the two-hander one-liner (§2.6); **P3** the proc-socket layer; **P4** `DMG_BONUS` as a weightable EP key at weight 0; **P5** the upgrade-divergence sentence; **P6** six small fixes.

**Why first.** It closes a gap the tool names about itself, it fixes numbers that are wrong today, every change survives your sourcing standard rather than routing around it, and nothing in it introduces a model output. P1 alone converts a `0` on your stat card into 18 sourced figures plus a badged derivation with a build-time assertion behind it.

Three things I would specifically **not** do, and the reasoning matters more than the conclusions:

- **Do not fold the bonus into `RATIO`.** I tested it. Because the bonus is additive and barely moves with delay, adding it to dmg/delay promotes **Rusty Two Handed Hammer 124 places**, Abandoned Orc Shovel 126, Micah 140. Ratio stops being even a rough proxy the moment a delay-independent term is inside it. eqlwiki offers a "Normalized Primary Score" for exactly this comparison; it is fine to *show* and bad to *rank on*.
- **Do not ship a DPS number.** It would be the first figure on the site that no source carries and no client window prints — a model output in the same typography as a scraped stat, on a page whose whole argument is that those are different kinds of thing.
- **Do not touch the cap-aware scorer.** `Wn()` builds the baseline from the rest of the set with this position emptied and class-blocked items dropped; `fn()` clips attribute gains at 510 and resist gains at 1000 against what you already have; `dn()` scores only the excess haste over the best already worn. **That is genuinely rarer than it sounds and it is the strongest thing in the engine.** A worked example on the tools page — a ring that looks better in isolation and scores lower in a set already near the attribute cap — would be the best single argument for using this planner over any other.

For scale on why `DMG_BONUS` is worth a lever even at weight 0: at level 50, +10, main hand, under the measured chain, the bonus is worth **+32.3%** on Cudgel of the Fool, **+32.2%** on Earthshaker and **+14.9%** on Thelvorn. Those percentages are robust — swing rate, haste, stance and multi-attack all cancel out of the ratio. **The good news, and it belongs in the copy: your ordering is not broken.** Ranking all 425 PRIMARY-capable melee weapons at +10 by ratio and by modelled main-hand damage, they agree **8 of 10 in the top ten and 20 of 25 in the top twenty-five**. What ratio cannot do is tell a reader *how much* a swap is worth.

### 2. The parse-convention converter

A Learn page plus a small pure-JS module: a registry of what each shipped meter divides by, with file:line citations, and a converter that translates what can be translated and **refuses, with a reason, on what cannot**.

**Why second.** It is the safest thing here — it names four community tools and their fields and corrects nobody — and it closes an error that is invisible, recurring and expensive. `jos437-finishing-blow.log`, one file, one character: **265 wall-clock / 483 engaged / 581 best-60s / 678 best-30s**. Highest ÷ lowest = **2.56×**. All four are Tier M off the same file. No convention is wrong; the comparison is.

Four Legends log tools ship, and between them they print **nine** distinct rate figures over **four** denominator families using **three** gap constants: `eql-meter` `fight/mod.rs:347` (elapsed) and `:326` (3s peak); `EQBuddy` `SessionStats.cs:1692` (active, 10s gap, extended by group activity) and `:1684` (elapsed); `everquest-companion` `combat.ts:383` (elapsed) and `:379-385` (active, 3s cap); `eql-log-reader` `eql_combat_tracker.py:765` (active, 10s cap) and `:1151` (rolling 10/30/60).

**The refusal is the most valuable behaviour in the tool.** I re-derived engaged DPS under four active-time rules over 29 qualifying fights. The active family is effectively one convention: a 3s cap and a 6s split agree to within ±8%, median exactly 1.00; a 10s cap reads 5% lower. But **ELAPSED↔ACTIVE is not convertible** — the ratio runs 0.26 to 1.00 across the corpus, because it is a property of how much downtime a log happens to contain, not of the fight. Publishing the 0.883 median as a constant would be the exact false precision the tool exists to prevent.

**Burstiness table (half-open windows, `[t₀, t₀+w)`), n=29:**

| w | median | p25 | p75 | fights below 1.0 |
|---|---|---|---|---|
| 3 | 3.11 | 2.40 | 3.72 | 0 |
| 10 | 1.89 | 1.50 | 2.19 | 0 |
| 30 | 1.42 | 1.18 | 1.62 | 3 |
| 60 | 1.22 | 1.03 | 1.36 | 3 |

Two things I found while writing it that you should have even if the tool never ships. **The window boundary rule is itself a convention worth 17%** — log timestamps are one-second, so `t−t₀ ≤ 10` spans eleven distinct seconds and `< 10` spans ten, and my own `tools/convention.py` uses the inclusive form, which is why the figures I have been quoting (1.23 / 1.47 / 2.06) are 1–9% high at short windows. Ship the half-open ones. And **the "fights below 1.0" column is not an error and must ship** — a best-60s reading can come out *below* active-time DPS on a bursty fight shorter than the window.

**What must travel with it:** n=29, the spread and not just the median, and the honest limit — all 138 logs come from one upstream fixture directory and are essentially one player across class swaps. **These are not 29 independent samples of "an EverQuest Legends fight."** The single largest improvement available is not more logs, it is logs from other people.

**Scope note for you:** the string "DPS" does not appear on any eqlsource page I fetched, so this corrects nothing you publish. Your difficulty tables do put damage-to-kill and fight seconds side by side (D4 Master Yael, 234,249–242,060 over 587s), and dividing gives 412 — a raid-wide wall-clock rate that will not match any meter's default reading of the same fight. One clause beside that table, and one bullet on `/learn/reading-the-plans.html`, would cover it even without the tool.

### 3. The AE target-cap dataset

`ae-caps.v1.json` as a fifth file on `/data/`, plus a thin reference page. One row per AE spell at level ≤ 50 with **separate** fields for target cap, total-hits cap, wave count, indoor/outdoor gate and mob-level gate, each carrying the verbatim source string and its own tier.

**Why third, not higher.** The content is excellent and squarely inside your own stated motive (*"every tool re-transcribes the same wiki pages and inherits the same 1999 errors doing it"* — this is precisely such an error, caught and documented). But `/tools/index.html` draws a line: *"Client-mined numbers, spellbook diffing, AA planning and 3D zone geometry belong to other tools."* A 72-row cap table is not spellbook diffing, but it is adjacent, and you may reasonably read it as the thin end. **Offer it as a dataset with the reader as a thin layer over it, and let the decision be yours.** Every open row on it is closable by one screenshot or one pull, which is the shape `/learn/still-true.html` already uses.

### 4. The trio damage model — last, and here is why

`/tools/swing-value.html` plus `engine/trio-damage.js`. It is the most interesting thing I have and the least ready, and I would rather say that than lead with it.

**The one design decision, and the measurement that forces it: the tool prints deltas and refuses to print a DPS number.** I computed the same main-hand lane eight ways, varying the three choices this project has not settled:

| quantity | spread across eight forms |
|---|---|
| the **level** (Thelvorn +10 lane DPS) | **134.0 → 153.7, a 14.7% spread** |
| the 2H-vs-1H **delta** | −20.7% → −22.8%, **2.1 points** |
| the damage-bonus **delta** | +31.8% under both crit forms — **exactly identical** |

The crit form cancels out of a ratio to the last decimal. Swing rate, haste, stance and multi-attack cancel too. **A delta is a far better-founded object than a level, and it is what a gear planner actually needs.**

**And the level is not merely uncertain, it is wrong in a known direction.** `HANDOFF.md` §1: the model's *floor* — worst of 560 trios, raid mitigation — sits at **1.51× the measured median per character**, and **162 of 213 logged raid fights fall below it**. Turning off the two largest assumptions together still leaves 2.61×. Every number this chain has produced was a ceiling printed as an estimate.

Three more reasons it goes last. Its most consequential constants are open, not merely imprecise: whether **STR converts to damage at all** is contradicted between three of my own files; raid mitigation cannot be resolved by this instrument (seven properly-paired boss fights span 0.41–2.01); Striker stance is not a flat multiplier and its own crit test refutes one. Its ability lanes miss by **−41% to +9% individually** against the one character where gear, level and stance are all pinned, while their total lands at +0.1% — that is cancellation, not agreement. And putting a model's credibility in front of you on the same page as four corrections to that model is not a good trade.

**But the half of it you need is ready and is exactly what P4 wants.** `deltaFor(before, after, ctx)` is a pure function, it plugs into `Wn(state, position, ctx)` — which already builds the "before" side of a delta with the position emptied and class-blocked items dropped — and it runs only for PRIMARY/SECONDARY under the same `weaponCounts` guard you already use. Four lines of adapter. If any of the model ships, ship that.

---

## 6. The measured constant table

Everything, with tiers, as a reference you can adopt. **M** = measured here · **T1–T5** = your ladder · **D** = derived (not a tier; it inherits the worst tier of its inputs) · **OPEN** = I refuse or band rather than choose.

### Swing outcome
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| P(land) | 0.5765 | **M** | n = 21,122 and n = 23,013 swing attempts |
| miss | 36.18% | **M** | same |
| active-defence avoidance | 6.17–6.29% | **M** | dodge 2.67 / parry 2.31 / block 0.98 / **riposte 0.00** |
| Strikethrough (RNG) | +30% | T2 | acts on the avoidance bucket only, never the miss roll → ~+2.4% total DPS |

### The roll
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| **U = 2·DMG + 1** | base-roll maximum | **M** | two weapons identified from their own histograms: Thelvorn +8 DMG 36 → 84.2 predicted vs 86 measured; Whitened Treant Fists +4 DMG 19 → 39.0 vs 40. The rival `2(2·DMG+1)` is off by +83%/+95% |
| E[rx] base | 0.967 at Wrath 365 | **D** | back-solved from one identified main hand. **Fit path not recorded and entangled with the crit form — OPEN** |
| raid mitigation factor | 0.73 | **OPEN** | seven paired boss fights span 0.41–2.01, median 0.91. Cannot resolve a 0.73 |
| eqlwiki's published weighted-d20 | — | **REFUTED** | simulated twice at 400k draws: U-shaped, P(1) 16–37%, P(10) 1.3–2.5%, P(20) 26–59%, against a measured 2.16 / 23.08 / 5.99. **Its mean is right and its shape is wrong. Do not code it.** |

### Crit
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| melee crit | **1.70×** on the rolled part only, at **12.72%** of landed hits | **M** | five weapons |
| Berserker crit rate / Warrior crit damage | +0.06 / +0.30 | T2 | enter as a *ratio* against baseline (1.0386 / 1.0596), never as absolutes |
| **spell and proc crit** | **exactly 3.00×** at 12.2% | **M** | ten independent spells, exact to 3 s.f. — Puma Maw 517/172, Condemnation 729/243, Dismiss Undead 432/144, Lifebite 126/42, Frost Storm 2246/741. The constant is itself evidence Destructive Fury 3 applies to spells: ×2.0 base +100% *of the bonus* = exactly 3.00 |
| — but not universal | — | **M** | Earthquake 0/39, Smiting Strike 0/658, Scream of Death 0/29 never crit |

### Damage bonus — corrected this session
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| **B = HandMod × max(Level, DMG) × (min(delay,50)/40) × (Level/100)**, main hand only, floor() | — | **T5 formula + T2 ×19 + M window** | eqlwiki Game Mechanics, added 2026-08-11 |
| Hand modifier | **0.8 (1H) · 1.1 (2H)** | same | 19/19 statblocks at L49/L50; 2H band [1.0971, 1.1022); 1H band [0.8000, 0.8205) |
| off-hand bonus | **0** | **M** | measured 0 on the offhand and on every skill lane |
| ~~0.69 (1H)~~ | **wrong** | — | fits 0 of 13. See §1.3 |

### Rates and haste
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| Double Attack / Triple Attack | 56% / 14.2% conditional | **M** | |
| main-hand chain | **1.520**, CI [1.465, 1.569] | **M** | |
| off-hand chain | 1.4911 — **the off hand never triples** | **M** | P(≥3) 0.0017 vs 0.0406 main, a 24× gap |
| dual-wield success | 0.88 | **M** | separable because haste is identical in both hands |
| Frenzy | **2.918 attempts per activation**, P(3) > P(2) | **M** | not a DA/TA chain; one hit per activation understates Berserker by roughly half |
| haste cap at 50 | **75, band [75, 85]** | **OPEN** | eqlwiki's Legends-authored caps table (T5, but its 51–60 row cannot be a P99 import) and EQL Tools (T3) **agree**. Monk `Unbound Alacrity` +3/6/10% is T2 and "10% of 75" vs "75+10 points" differ by 2.5 |
| worn haste stacking | max-not-sum | **assumed** | classic behaviour + a named guide. **No character in my corpus wears two hasted items** |
| haste unit | Attack Speed %, baseline 100 | **M + T2** | client panel `Attack Speed %  100`; 52 "Increase Attack Speed by N%" spell effects |

### Stances — all eight, measured off a bash lane that floors at exactly 1 damage
| Stance | dmg | acc | rate | Tier |
|---|---|---|---|---|
| **offensive** | **×2.00** | ×1.081 | ×1.00 | **M** |
| balanced | ×1.00 | ×1.00 | ×1.00 | **M** |
| defensive | ×1.00 | ×0.95 | ×1.00 | **M** |
| **berserker** | ×1.00 | ×1.01 | **×1.90** | **M** |
| evasive | ×1.00 | ×1.00 | ×1.00 | **M** (incoming hit rate ×0.08) |
| mage hunter | ×1.00 | ×0.97 | ×1.00 | **M** |
| ranged | ×1.00 | ×1.081 | ×1.00 | **M** (grants DA/TA to the bow, no damage multiplier) |
| **striker** | **unknown** | ×1.00 | ×1.00 | **OPEN — not a flat multiplier; its own crit test refutes one** |

Offensive applies **before** the crit and also scales the damage bonus. The parity test: non-crit damage is even **100.00%** of the time under Offensive (760/760 once killing blows are excluded) against ~55% in every other stance, and endpoints double exactly on the same weapon in the same file (86→172, 89→178, 184→368). **Offensive does not touch procs or spells** (Puma Maw 172 → 172). Berserker never clearly beats Offensive: ×1.90 rate against ×2.00 × ×1.081 = ×2.16, intervals overlapping.

The client writes the stance in plain text, so no inference is required: `You assume a defensive stance.` ×180 · balanced ×154 · offensive ×146 · berserker ×128 · evasive ×56 · mage hunter ×41 · striker ×8 · ranged ×1, across 37 of 138 files. Attributing every melee line to the stance in force, **Offensive produced 121,596 of 339,052 melee damage points, 35.9%**, from roughly 18% of the time. (The time split depends on an accounting choice about time after the last attributable event; publish the damage share and the raw counts, and the time split only with its rule stated.)

### Wrath
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| **Wrath = Offense + ((2·STR)−150)/3 + WornATK + SpellATK** | — | **D** | |
| Offense caps at 50 | WAR 210 · MNK 230 · ROG 210 · RNG 210 · BER 210 · PAL/SHD/BRD/BST/SHM/CLR/DRU 200 · ENC/MAG/NEC/WIZ 140 | **M-validated** | eqlbase, **21/21 against skill plateaus visible in the logs**. eqlwiki's class-page skill tables measured **35% accurate (130/373 cells) and were rejected** — prefer eqlbase for skills and caps |
| Spell ATK | 61 | T2 | |
| Ranger Hunter Attack Power | **+104** | T2 | 26 ranks × 4, cost 0 AA, level 8 — worth **+11 to +13% of total DPS typically, +19% on a raid boss** |
| Worn ATK | **0** | **M** | 0 of 2,263 catalogued; 2 of 11,534 wiki items, both quarantined |
| STR modifier | 120 | **OPEN** | assumes a 255 STR cap; a client panel in this project reads **INT 295**. eqlwiki adds `if STR < 75: modifier = 0`, a clause my chain omits. **Decides whether STR converts to damage at all** |

### Ability lanes — measured, and individually the worst part of my model
| Lane | pre-stance mean | rate med / max | owners |
|---|---|---|---|
| kick | 58.50 | .32 / .54 | BST MNK RNG WAR |
| bash | 71.15 | .33 / .54 | PAL SHD WAR |
| strike | 35.05 | .27 / .50 | MNK |
| **smite** | 31.30 **+417 flat rider** | .17 / .31 | PAL — the rider fires 658/658 landed smites, is **not** stance-doubled and **never** crits |
| frenzy | 57.21 | .47 / .72 | BER |
| backstab | 178.69 | .29 / .47 | ROG — ×0.20 from the front |

**Against the one fully-pinned character these miss by −41.2% (strike), −19.2% (bash), −10.4% (smite), +8.7% (kick) while the total lands at +0.1%.** That is cancellation, not agreement.

### Procs, pets and defensive
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| **procs are per-minute, not per-swing** | ~2.4 PPM, band 2.1–2.7 | **M** | exposure test ΔlogLik **+8.19**; correlation of PPM with swing rate **−0.03**. **Haste and multi-attack buy zero extra procs.** *(Honest caveat: a split-half stability test I wrote to discriminate goes 4–3 with the largest sample against — Smiting Strike, 91 segments / 616 fires, is more stable per-swing. Strong enough to model on, not strong enough to hand you as a contamination row.)* |
| proc lanes | **1 two-handed · 2 dual-wielding · +1 Ranger bow · 0 from armour** | **M + D** | An Exaltation carries its **source item's** slot restriction onto the host. Re-verified on your catalogue: **146 items carry a proc effect; of the 91 that carry a slot, 91 of 91 are PRIMARY/SECONDARY/RANGE and 0 are armour.** Control test: a spell-damage line falls within 1s of an ordinary swing 20.9% of the time and within 1s of an `(Exaltation)` message **16.9% — below chance**; Golden Efreeti Boots 0 of 25 |
| Exaltation ladder | Slot 1/2 Ornamentation +0 · Slot 7 Focus +1 · Slot 8 Click +2 · Slot 9 Worn +3 · Slot 10 Proc +4 | **M** | **66/66 rows** from four inventory dumps; matches your shipped `zr` exactly |
| damage shield | exactly **1.00 tick per landed incoming hit**, ~17.5 DPS/attacker, ~0.13 mana/s | **M** | does not stack, does not scale with gear, **zero unless you are tanking** |
| charm pet / summoned pet | 66.8 / 17.5–31 DPS | **M** | |
| Spirit of the Puma (SHM 50) | 154 dmg at 400% rate mod ≈ 8 procs/min ≈ **25 DPS self, 127 group-wide across five melee** | **M** | "huge" is a group statement, not a per-character one |
| **the player tanks, not the pet** | bosses aimed 1,318 melee attempts at the player and 59 elsewhere (4.3%); on Nagafen 186:1 | **M, narrow** | **Read only as "the log owner took the boss melee in these fights."** Pets appear in 11 of 138 logs and nothing establishes a pet was ever on a boss with taunt up. This is *not* "a pet cannot hold a boss" |

### Spells and AE
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| target caps | see §4.2 | **T5 in a T2 container** | 11 of 72 AE spells at ≤50 state one; 3 more state a total-hits cap |
| rain/storm waves | land in waves | **M + T5** | one Frost Storm cast → three damage lines three seconds apart; three waves land in the same second on three different targets |
| **no spell-damage focus can boost any area spell** | — | **T2** | Improved Damage I/II/III and all Gallenite variants carry `Limit Target: Exclude Caster AE / Exclude Caster PB / Exclude Target AE`. Mana and haste focuses carry no target-type limit: Jolum Superior Abatement −15% mana and Naki Superior Pernicity +15% spell haste both apply to DDD |
| Denon's Desperate Dirge (BRD 43) | base 315, 800 mana, 3.00s cast, **recast 0.00**, Targeted AE, **cap 8**, Singing skill, Magic resist | **T2** | player screenshot rank 0 → X: damage 315→504 (×1.60), mana 800→640 (×0.80), resist 0→−150 |
| Symphonic Aura (AA, verbatim) | five songs auto-pulse; eligibility is exactly *"no mana cost, no cooldown, non-targeted area of effect"*; selects from the final spell gem backwards | **T2** | |
| Instrument Mastery vs Singing Mastery | **two disjoint +60% systems** | **T2** | Brass/Percussion/String/Woodwind vs the Singing skill. A model with one Bard multiplier is wrong |
| charm caps | ENC 51 any · BRD 51 any (18s song) · NEC 51 undead · DRU 49 animal · SHM 33 animal | T2 | |
| Shaman AA Cannibalization | consumes 1,924 health → 1,066 mana, 3-min refresh; castable version 1.25s cast + 1.5s recast, 0 mana, −50 HP → +28 mana at 50 | T2 | |

### Items and slots
| Constant | Value | Tier | Evidence |
|---|---|---|---|
| worn positions | **23 positions over 18 slot types, two Any Slots, no Charm** | **M** | matches your model exactly |
| ANY | removes the **position** restriction, not the **class** restriction | **M** | proved by intersecting three simultaneously-worn chest pieces' class lists down to one class |
| upgrade rule (stats) | `value + max(tier, floor(value·0.1·tier))` | **M** | validated 5/5 against a client tooltip including both cases where the percentage and the +1/tier floor disagree; **22/22 across your five capture records** |
| upgrade rule (haste, regen family) | flat **+1 per tier** | **M** | Cloak of Flames 36 → 43 at +7, where the scaled rule gives 61 |
| upgrade rule (weapon damage) | 10%/tier; **whether the +1 floor applies is unchecked** | **M / OPEN** | 37→74 at +10 settles 10% over 5%; 265 of 431 melee weapons are below 10 base damage where the two rules diverge |
| Void save | derived = upgrade tier, if ≥2 qualifying stats | **D, 2/2** | Earthshaker +10 → 10, Midnight Clad Straps +6 → 6 |
| weapon slot legality | a weapon may go off-hand only if its slot list contains SECONDARY | **T2** | **219 of 431 melee lack it; 214 are `["PRIMARY"]` exactly.** Aldryn and Thelvorn — the two best 1H weapons, both PAL, both 20/26 — are **both** PRIMARY-only and cannot be paired |
| weapon skill vocabulary | client says **1H Piercing**, not `Piercing` | **M** | 284 skill-up lines vs 0 bare |

### Measurement convention — worth its own tool
| Constant | Value | Tier |
|---|---|---|
| best-60s / engaged · best-30s / engaged · best-10s / engaged | **1.22 · 1.42 · 1.89** (half-open windows), n=29 | **M** |
| the same, inclusive windows (what my earlier notes quote) | 1.23 · 1.47 · 2.06 | **M** |
| worst single-file spread across four readings | **4.27×** (`w48-special-lane-reset.log`); median 1.76× | **M** |
| elapsed ↔ active | **not convertible**; ratio 0.26–1.00 across the corpus | **M** |
| four shipped meters, four denominators | see §5.2 for file:line | **M** |

---

## 7. What is still open, and the cheapest in-game test for each

Ordered by value ÷ cost. The first one takes thirty seconds and moves the best AOE spell in the game by 2.4×.

### 7.1 Amplification — start here

**The disagreement, verified in the cache today, on one page:**

| Field | Reading |
|---|---|
| `description =` (T5) | *"Focuses the power of your voice, causing all songs that use the singing skill to increase in power by **10%**."* |
| `SpellSlotRowSmart 1` (T2) | *"Increase singing skill by **0.7%**"* |
| Player reports (T4/anecdote) | **100%** |

That is a **14× spread between two fields on the same wiki page**, and a **2.4× swing on DDD's damage** depending which is right. It is also, note, a perfect instance of §4's principle: which field you cite *is* the citation, and the page cannot tell you which one it means.

**The test: cast DDD once with Amplification up and once without, in the same fight on the same target. Read the two damage lines.** Thirty seconds. The three hypotheses are 10%, 0.7% and 100% apart — no parsing subtlety, no denominator question, no sample size. I would run this before anything else on this list.

### 7.2 The rest

| Open question | Cheapest test | Cost | Why it matters |
|---|---|---|---|
| **Does worn haste stack?** | Read Attack Speed with one hasted item worn, then with a second. Additive 162 / highest-only 141 / compounding 171 on a 41+21 pair | one screenshot pair | The only genuine eqlwiki-vs-EQL-Tools conflict; settles your contamination row and your planner's assumption at once |
| **Does the +1/tier floor apply to weapon damage?** | **Efreeti Standard at +1 or higher** (3 dmg / 10 delay, already in your catalogue). Shipped rule says 3/3/3 at +1/+2/+3; floor rule says 4/5/6 | one tooltip | 265 of 431 melee weapons are in the band where the two rules disagree. Also settles whether my `OH_RATE_CAP=1.42` was patching my own bug |
| **What is Striker stance?** | One bash lane floored at exactly 1 damage, in Striker, for 200 swings — the same instrument that gave the other seven | one session | The only stance with no number. My model refuses to price it |
| **Does STR convert to damage at all?** | One client Statistics panel at two known STR values | one screenshot pair | Decides whether STR gear is worth anything. Currently contradicted between three of my own files, your planner's 510 assumption, and eqlwiki's `STR < 75 → 0` clause |
| **Frost Storm: 250, 512 or 741?** | One client spell tooltip at level 50 | one screenshot | Three sources, three numbers, 2.96× apart, and the measured one matches none |
| **Bard passive AE: 8 or 57 per tick?** | One client song tooltip at 50, or a level-50 Bard log with all three songs up | one screenshot | 7× on the class's whole passive contribution. Neither wiki field states a level and the one measured reading (8) matches neither |
| **Is any "unstated" AE spell genuinely uncapped?** | Supernova or Frost Storm into a pull larger than 8, counting distinct damage lines from one cast | one field trip | **The highest-value single field test on the AE table.** The largest AE pull anywhere in my 138 logs hit **four** mobs, so no cap of 4 or above is confirmed *or* refuted by measurement — the corpus genuinely could not have contained the answer |
| **Tremor 24 vs Earthquake 25** | One pull of 25+ with each | one field trip | Two adjacent numbers on two pages describing the same mechanic. Ship both as written and flag the discrepancy rather than smoothing it |
| **Sacred Word's `%T`** | One cast into a crowd, or the client's own string file | one screenshot | Proves `unstated` is a transcription state, not a game state |
| **Two-handers and the off hand** | One client paperdoll with a two-hander equipped | one screenshot | The rule I am asking you to implement in §2.6 is classic-inherited and unmeasured on Legends. Ship it as a banner until this exists |
| **The `Garduk` / `Arydryidriyorn` windows** | *(my problem, not yours)* Publish the readings or drop the tier-M claim | — | A tier-M grade on a constant whose parse is not in the repo does not meet the standard I am applying to you |
| **Which measured body is which Sky island** | One `/loc` per island | one field trip | Also settles whether the soul/essence family is island-4 specific, the weakest joint in the zone-wide belt finding |
| **Do Anthemion and Shadow Rage have a seventh slot?** | — | — | Genuinely unknown. Your planner holds six Shadow Rage pieces; your sets page shows three; I add three more |
| **Is +4 a design ceiling or an artefact of D4?** | Not separable from this corpus | — | +5 could only ever arrive as an above-floor roll at D4, and D4's above-floor rate is 0/80 |
| **Does a pet ever hold a boss?** | — | — | I measured "the log owner took the boss melee in these fights." The aggro claim is a different claim and I am not making it |

---

### Closing note on shelf life

Five days separated your last build (2026-08-26) from the wiki state I read (2026-08-29). In those five days one editor rewrote roughly forty Plane of Sky item pages against a live client — changing flags, changing skills, adding damage bonuses — **in your favour every time**. Three of your open questions closed themselves while nobody was looking, and three of the items in this brief exist only because of that.

The lesson is not "re-scrape more often." It is that a signature should carry a **re-check date**, not only a scan date, and that a sentence in the present tense about what all sources currently say is exactly the claim a wiki edit falsifies quietly. Your `contamination.json` already gets this half right — its scoped *"no source **in this project** carries it per item"* is defensible as of its scan date and needs only a date attached, while `meta.json`'s unscoped version is the one that is now plainly false. They are not equally wrong and they should not be fixed with the same edit.

Everything above is reproducible from the paths in §1. Where I have asserted you are wrong I have quoted you and shown the evidence; where I might be the wrong one I have said so in §1.3 and in the OPEN rows of §6. Happy to hand over the four inventory dumps, the 279 ID pairs, the 1,604-row loot table and the parsed Sky run whenever you want them — directly, not on a public issue.