# SOURCING AUDIT — every load-bearing constant, against the eqlsource standard

**Established:** 29 August 2026
**Prompted by:** the player's warning that this project leans too hard on eqlwiki.com.

I went and read the standard rather than arguing. The audit below applies it to my own
numbers. **One constant fails outright, and it happens to be right anyway for a reason that
has nothing to do with its citation.**

---

## 1. What the standard actually says

From `eqlsource.com/sources.html`, verbatim where quoted:

| Tier | What |
|---|---|
| **M** | **Measured combat logs.** *"First-hand instrument data, parsed rather than remembered. It outranks every read source for what it directly measures, and generalises to nothing beyond its stated conditions."* |
| **1** | Official patch notes. *"Anything published after a wiki page's last edit supersedes that page."* |
| **2** | **Structured wiki data** — *"Infoboxes, NPC tables, item tables, coordinate records on eqlwiki. Machine-shaped fields that somebody entered from the live game."* |
| **3** | Named community guides |
| **4** | Aggregators (EQL Build Forge, EQ Legends Tools) |
| **5** | **Wiki prose** — *"Large parts are a Project 1999 import, sometimes word for word... quoted only when marked as classic, never as Legends fact."* |

**The critical point is that the split runs through eqlwiki, not around it.**

> *"A wiki page's infobox and its NPC and item tables are usually live Legends data, while
> its narrative sections — Dangers, Benefits, Traveling — are imported prose from before the
> game existed."*

Five of the ten surveyed zone pages **began as Project 1999 imports**. So "eqlwiki says" is
not a citation. *Which field on which page* is the citation.

### The contamination scanner names exactly one mechanic as known-changed

`eqlsource.com/learn/contamination.html`, verbatim:

> **haste-pct** — **Classic:** Haste was a percentage that divided weapon delay.
> **Legends:** Legends uses a flat value on an attack-speed stat. EQL Tools documents it;
> **eqlwiki still carries the classic formula**, so the two best sources in the field
> disagree. **What would settle it:** One screenshot of a Legends haste tooltip.

---

## 2. The one constant that fails

**`HASTE_CAP = 75`, taken from eqlwiki's Haste Guide.** That is a guide page — prose, tier 5
— and it carries the exact classic percentage-divides-delay formula the scanner flags. It is
the single named contaminated pattern in the field, and I used it as though it were fact.

**Re-derived from measurement alone, with no wiki involved:**

```
jos437-finishing-blow.log · main hand provably Thelvorn, Blade of Light, delay 26
439 slash attempts / 395 s engaged            = 1.111 attempts/s   (TM)
multi-attack chain, measured separately       = 1.520              (TM)
unhasted rate  = (10/26) × 1.520              = 0.585 attempts/s
EFFECTIVE ATTACK-SPEED MULTIPLIER             = 1.111 / 0.585 = 1.900
```

| what the model used | multiplier | error vs measured |
|---|---|---|
| `model3.py`'s 175 | 2.75 | **+44.7%** |
| eqlwiki Haste Guide 75 (+10 Monk) | 1.85 | **−2.7%** |
| **measured** | **1.900** | — |

**The number survives at −2.7%; the justification does not.** And the player's own client
panel reads **`Attack Speed %  100`** unhasted — the flat attack-speed *stat* eqlsource says
Legends uses, not a delay-dividing percentage. So the mechanic is as eqlsource describes and
eqlwiki has it wrong; my model got a nearly-right number from a wrong source.

**Fix applied:** the constant is re-anchored on the measurement. `1.900` measured, expressed
as an attack-speed stat of 190 against the client's unhasted 100. The Haste Guide citation
is struck.

---

## 3. Everything else, classified

| Constant | Source | Tier | Verdict |
|---|---|---|---|
| Offensive Stance ×2.00 | parity test, 760/760 even non-crit | **M** | clean |
| `U = 2·DMG + 1` | two identified weapons vs their histograms | **M** | clean |
| `B`, HandMod ~~0.69~~ **0.80** /1.10 | ~~two client windows~~ **whose readings are not in this repository, so the M grade was false**. Re-derived 29 Aug from 9 eqlwiki `Game_Mechanics` observations + the `Efreeti Standard` statblock, both re-fetched | **T5 formula, T2 + M corroboration** | **corrected — `handmod.py`** |
| land 0.5765 / miss / avoid | 21,122 and 23,013 swing attempts | **M** | clean |
| multi-attack 1.520, offhand never triples | 3,179 deduped rounds | **M** | clean |
| melee crit 1.70 @ 12.72% | five weapons, crit maxima | **M** | clean |
| spell/proc crit 3.00× | ten independent spells | **M** | clean |
| procs are per-minute | exposure test, ΔlogLik +8.19 | **M** | clean |
| damage shield 17.5/attacker | 1.00 tick per landed incoming hit | **M** | clean |
| charm pet 66.8 DPS | pet damage inside the owner's engaged segments | **M** | clean |
| item upgrade +10%/tier — **percentage term** | 5/5 our tooltip + 5/5 Session B's weapon captures | **M** | clean, and now corroborated across two repositories |
| item upgrade — **+1/tier floor term** | ~~same tooltip~~ | ~~**M**~~ → **ungraded** | **REGRADED 31 Aug.** All ten captures tie between floor and no-floor; the floor is reachable only below base 10 and no capture sits there. Dropped from `model4.py`. `verify_upgrade.py` |
| best-30s / engaged = 1.46 | 30 fights | **M** | clean |
| Exaltation proc sockets fire from weapons only | control test at 20.9% baseline | **M** | clean |
| **haste** | ~~eqlwiki Haste Guide~~ → re-measured | ~~5~~ → **M** | **fixed above** |
| Offense caps at 50 | eqlbase, validated **21/21** against skill plateaus visible in logs | 4 → **M-validated** | clean — **and eqlwiki's class-page tables were already rejected here, at 35% accuracy (130/373 cells)** |
| Symphonic Aura, Singing/Instrument Mastery | eqlwiki AA page, structured harvest | **2** | acceptable |
| DDD 315 / 800 mana / 8 targets | eqlwiki spell **infobox** | **2** | acceptable |
| **Bard passive songs 57/tick** | eqlwiki **class-page spell table** | **2** | **acceptable but UNCROSS-CHECKED — see §4** |
| DDD 3,000 per target | wiki-hosted guide | 3 | already flagged in `BUILD-LISTS.md` |
| Amplification ×2.0 | player report | Report | already flagged |
| mote rank 10 ×2.0 | back-solved | Derived | already flagged |
| stance endurance charges | one eqlwiki page transcluded three times | 2, single-source | already flagged |
| weapon upgrade +5%/tier conflict | eqlwiki Item Upgrade System | 2 vs **M** | **CLOSED 31 Aug** — Session B's `14 → 15/16/18 at +1/+2/+3` refutes +5%/tier outright (it cannot exceed +20% cumulative at tier 3; 14 → 18 needs 28.6%) and refutes compounding at +10. 10%/tier linear wins 10/10. `verify_upgrade.py` |

**The audit comes out mostly clean, and not by luck** — the project's method has been to
measure first and read second. Of roughly thirty load-bearing constants, one was sourced
from wiki prose, and the standard caught it.

---

## 4. The one open exposure this creates

**The AOE ranking now rests on a tier-2 figure I could not cross-check.**

Bard's three passive songs at 57 damage per tick come from the **eqlwiki Bard class page's
spell table**. That is a structured field, so tier 2 by the standard — but it is the same
*page type* whose skill-cap tables my own offense audit measured at **35% accuracy**.

I tried to get a second reading and could not: eqlbase.com renders its spell list
client-side, so the values are not in the fetched HTML. **So the strongest AOE result in
this project has one source and no corroboration.**

Two things keep this from being fatal:

- It is a **spell** table, not a skill-cap table. The 35% figure was measured specifically on
  skill caps, which are a known classic import; spell tables carry Legends-specific level
  ranges that a P99 import would not have.
- The player independently reports the effect in game — *"she single-handedly blows up
  entire packs of monsters in a few seconds"* — which is corroboration of the magnitude even
  though it is not a number.

**What would close it:** stand in a pack with the three songs up and nothing else running,
and read one damage tick. Five seconds, and it converts the whole AOE list from tier 2 to
tier M.

---

## 5. Rule adopted going forward

1. **Never cite "eqlwiki" as a source.** Cite the field: *"eqlwiki Bard class page, spell
   table, `effects=` column"* or *"eqlwiki Haste Guide, prose"*. The first is tier 2; the
   second is tier 5 and may not be used as Legends fact.
2. **A wiki guide page is prose.** Haste Guide, Travel Guide, Bard Guide — all tier 3 at
   best, tier 5 if the page began as a P99 import.
3. **Any mechanic on the contamination list is presumed classic until measured.** Right now
   that is haste; the list is expected to grow.
4. **Prefer eqlbase for skills and caps** — it validated 21/21 against log plateaus where
   eqlwiki's class tables managed 35%.
5. **A number that only one source carries gets said out loud**, as §4 does.

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
