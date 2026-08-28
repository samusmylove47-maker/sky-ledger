# FOUR RANKINGS, ON THE CORRECTED DAMAGE CHAIN

**Established:** 28 August 2026 · **Model:** `model3.py`, rankings `lists.py`
**Chain:** `DAMAGE-CHAIN.md` · **Itemisation:** `EQUIPMENT-TRUTH.md`
**Constraint:** Enchanter excluded from every list. Support buffs are assumed supplied by
a partner, so no class is credited for buffing.

These supersede everything in `BUILDS.md`.

---

## 0. The four structural facts that decide all four lists

Before any number, these are what actually sort the 455 non-Enchanter trios.

**1. Offensive Stance is x2.00 damage, and only the nine martial classes have it.**
`BER BRD BST MNK PAL RNG ROG SHD WAR` get Offensive; the seven pure casters get
Channeler only. A trio with no martial class cannot ever have the largest multiplier in
the game. Measured: damage is even 98.8% of the time under Offensive against ~55% for
every other stance (n=1,069).

**2. Weapon access is class-gated, and the gates are narrow.**

| Weapon | +10 | Who can hold it |
|---|---|---|
| `Cudgel of the Fool` | 90/52, best 2H ratio in the game | **BER only** |
| `Aldryn, Blade of the Ocean` | 40/26 | **PAL only** |
| `Thelvorn, Blade of Light` | 40/26 **+ a 226-damage proc** | **PAL only** |
| `Wu's Fist of Mastery` | 32/22 | **MNK only** |
| `Windstriker` | 90/60, best bow | **RNG only** |
| `Khyldorn the Blood Drinker` | 72/43 | **SHD only** |

The best 1H pair in the game is **both** Paladin-only — and **Paladin has no Dual Wield
skill.** So the best dual-wield build in the game *requires* PAL for the weapons plus one
of `BRD BST MNK RNG ROG WAR` to actually swing two of them.

**3. The attack chain is gated too.**
Dual Wield: `BRD BST MNK RNG ROG WAR`. Double Attack: `BER MNK PAL RNG ROG SHD WAR`.
Triple Attack: **`BER MNK RNG WAR` only.** The intersection of Dual Wield and Triple
Attack is **MNK, RNG, WAR** — a dual-wielding triple-attacker must contain one of those three.

**4. Attack power has exactly one meaningful source.**
0 of 2,263 items carry ATTACK. The best attack-power *spell* among 2,006 is +15. The
Ranger's `Hunter's Attack Power` is **+104, free, permanent**, and `Force of Nature`
(L50) adds **+20** more. Nothing else in the game comes close.

**Monk's five special skills collapse into two logged verbs** (`strike` and `kick`) across
the whole corpus — so Monk is worth two autoskill lanes, not six. Recorded because the
class page reads as though it were six.

---

## LIST 1 — TOP 10 RAID-BOSS DPS

Raid-boss mitigation (measured MitFactor 0.73, the Nagafen band), attacking from behind
so Rogue backstab is at full value, Offensive stance, haste capped.

| # | Trio | DPS | Wrath | Weapons | Why it is here |
|---|---|---|---|---|---|
| **1** | **PAL+RNG+ROG** | **567** | 464 | Aldryn + Thelvorn | The only trio that pairs the two Paladin-only blades with Backstab, the highest-damage lane measured (178.7/hit) |
| 2 | NEC+PAL+RNG | 556 | 464 | Aldryn + Thelvorn | Trades Backstab for 120 DPS of Necromancer DoT, which never stops during a long boss fight |
| 3 | MNK+RNG+WAR | 549 | 449 | Wu's Fist ×2 | Four lanes (kick/bash/strike/slam), Triple Attack, and Monk's +10% haste-cap break |
| 4 | PAL+RNG+WIZ | 543 | 464 | Aldryn + Thelvorn | Same melee core, Wizard nukes instead of a third martial |
| 5 | BER+PAL+RNG | 542 | 464 | Aldryn + Thelvorn | Berserker's free +6% crit rate on the best 1H pair |
| 6 | MNK+PAL+RNG | 542 | 464 | Aldryn + Thelvorn | The classic pick. Dual Wield + haste break + the best blades |
| 7 | PAL+RNG+WAR | 537 | 464 | Aldryn + Thelvorn | Warrior's free +30% **critical damage** and the Slam lane |
| 8 | MNK+RNG+ROG | 536 | 449 | Wu's Fist ×2 | Backstab plus Monk's lanes, without needing Paladin |
| 9 | RNG+ROG+WAR | 535 | 449 | Arydryidriyorn + Yannikil | Four lanes and the widest AA spread; held back by weak weapon access |
| 10 | MNK+RNG+SHD | 531 | 464 | Wu's Fist + Bloodmoon | Shadow Knight lifetaps ride along for 61 DPS |

**Ranger is in 10 of 10 — and that was not assumed.** It falls out of the ATK elasticity
being steepest exactly at raid-boss mitigation. At *average* mitigation Ranger appears in
8 of 10 instead. The best non-Ranger trio in the game is `MNK+NEC+WAR` at 509, so
**Ranger is worth +11.4%** over the best build that omits it.

> **Archery does not compete.** `Windstriker +10` (90/60) with `Weapon Mastery of the
> Scout` (+100% base damage) and the free double shot computes to **~204 DPS**, because
> Ranged stance forfeits Offensive's x2.00 on everything else. Archery is a mobility and
> pulling tool here, not a damage rotation. **Take Ranger for the +124 ATK, not the bow.**

---

## LIST 2 — TOP 10 TANK + CHARM PET + DAMAGE

Gates: must have **Defensive stance** (`WAR PAL SHD` — the only three classes with it) and
must have a **charm** class. With Enchanter excluded the charmers are:

| Class | Spell | Charms up to |
|---|---|---|
| **NEC** | `Cajole Undead` (L47) | **level 51** — equal to Enchanter's own ceiling |
| DRU | `Beguile Animals` (L33) | level 43, animals only |
| SHM | `Charm Animals` (L23) | level 33, animals only |

Fighting from the front, so Rogue backstab is degraded to `Chaotic Stab`.

| # | Trio | DPS | Tank | Charm | Note |
|---|---|---|---|---|---|
| **1** | **NEC+PAL+RNG** | **556** | 80 | NEC → L51 | Best damage that satisfies both gates. Paladin tanks, Necro charms to the cap, Ranger carries the ATK |
| 2 | NEC+PAL+WAR | 501 | **110** | NEC → L51 | The *durable* pick — Warrior's free 5% permanent melee mitigation plus Lay on Hands |
| 3 | PAL+RNG+SHM | 527 | 80 | SHM → L33 | Only worth it if you are farming animals |
| 4 | MNK+NEC+WAR | 509 | 88 | NEC → L51 | No Ranger; Monk's haste break and evasion instead |
| 5 | NEC+RNG+WAR | 521 | 80 | NEC → L51 | |
| 6 | PAL+SHM+WAR | 471 | **110** | SHM → L33 | Toughest body in the list |
| 7 | MNK+NEC+PAL | 505 | 88 | NEC → L51 | |
| 8 | MNK+SHM+WAR | 480 | 98 | SHM → L33 | |
| 9 | RNG+SHM+WAR | 491 | 90 | SHM → L33 | |
| 10 | BER+NEC+WAR | 500 | 80 | NEC → L51 | The `Cudgel of the Fool` entry |

**Necromancer is the answer to "charm without Enchanter."** `Cajole Undead` charms to
level **51**, matching Enchanter's `Allure` exactly — and Fear, Hate and Guk are undead
content. Druid's animal charm caps eleven levels lower.

> **If you meant your partner's Enchanter supplies the pet**, the charm gate disappears and
> this list becomes "highest-DPS trio that can tank": **PAL+RNG+ROG (567)**, then
> **MNK+RNG+WAR (549)**, then **PAL+RNG+WAR (537)**. Note all three still want Ranger.

> **Stance caveat.** These numbers are in Offensive. Actually holding a raid boss means
> Defensive, which forfeits the x2.00 — roughly halving them. A tank flexes between the
> two; the ranking does not change, the absolute numbers do.

---

## LIST 3 — TOP 10 DAMAGE PER UNIT OF WRIST

The mechanic that makes this list possible: **combat skills have no global cooldown and
fire automatically during auto-attack.** Kick, Bash, Slam, Frenzy, Strike and Backstab
all cost **zero input**. So do auto-attack, weapon procs, and stances (set once). The
entire wrist load is spell and song upkeep.

Sustaining actions per minute, derived from measured spell durations:

- **Bard: 61 of 76 songs last exactly 18.0 seconds.** Twisting four is **13.3 recasts per
  minute, forever.** Bard is the single worst class in the game for this purpose, by a
  factor of about twenty-five.
- Shaman: 3 DoTs at median 42 s → 4.2/min. Beastlord: 4 DoTs at 57 s → 1.1 each.
- Pure melee: **0.5–1.0/min** — a stance and the occasional Mend.

| # | Trio | DPS | Actions/min | DPS per action |
|---|---|---|---|---|
| **1** | **BER+MNK+WAR** | **667** | **2.0** | **222** |
| 2 | BER+RNG+WAR | 652 | 2.5 | 186 |
| 3 | **MNK+RNG+WAR** | **694** | 3.0 | 174 |
| 4 | BER+MNK+RNG | 645 | 3.0 | 161 |
| 5 | BER+PAL+WAR | 651 | 4.0 | 130 |
| 6 | BER+MNK+PAL | 639 | 4.5 | 116 |
| 7 | MNK+PAL+WAR | 634 | 4.5 | 115 |
| 8 | BER+PAL+RNG | 682 | 5.0 | 114 |
| 9 | PAL+RNG+WAR | 675 | 5.0 | 113 |
| 10 | MNK+PAL+RNG | 681 | 5.5 | 105 |

**`BER+MNK+WAR` is the rest-your-hands build.** Three classes with no damage spells at
all: every point of its 667 DPS comes from auto-attack and autoskills. It carries five
lanes (kick, bash, strike, frenzy, slam), every stance in the game including Berserker
and Striker, Triple Attack, Berserker's free **+6% crit rate**, Warrior's free **+30% crit
damage**, and Monk's **+10% haste-cap break**. You set a stance and hold your auto-attack.

**If you want the highest raw output on this list, `MNK+RNG+WAR` at 694 DPS for 3.0
actions/min** is the better pick — 4% more DPS for one extra action per minute.

For contrast: `BRD+DRU+SHD` produces 386 DPS at **26.3 actions/min** — 43% less damage
for thirteen times the wrist load.

---

## THE AOE FARMING TRIO — and a verdict on `SHD+DRU+BRD`

### First, the finding that reframes the question

Modelled as a real pull cycle (dump the mana pool, med back), against N mobs:

| N | damage shield | AE spells | melee |
|---|---|---|---|
| 8 | 38% | 9% | 53% |
| 16 | 52% | 12% | 36% |
| **32** | **64%** | **15%** | 22% |

**The damage shield is the AOE engine, not the nukes.** It is measured at exactly 1.00
tick per landed incoming hit — ~17.5 DPS *per attacker*, for ~0.13 mana/s. Area-effect
spells cost 0.6–1.0 damage per mana and are mana-starved within seconds: `Upheaval` is
618 damage for **625 mana**, and no class regenerates fast enough to sustain it.

So AOE farming is decided by three things, in order: **how many mobs you can hold**, **whether
you survive them**, and **how much mana you can manufacture** — not by which nuke you own.

The mana engines that exist, read off the spell database:

| Class | Engine | Rate |
|---|---|---|
| **SHM** | `Cannibalize` / `McMerin's Feast` — 0 mana, converts HP to mana, spammable | **~8/s** with a healer |
| NEC | `Lich` — +20 mana/tick, costs HP | 3.3/s |
| WIZ | `Harvest` — +251 mana for 1 mana | ~4/s |
| BRD | `Chorus of Clarity` — 0 mana, **group-wide** | 1.17/s |

### The verdict on your pick

`SHD+DRU+BRD` computes to **364 / 536 / 881 DPS** at N = 8 / 16 / 32 — rank **~190 of the
210 trios that can hold a pull at all**, about **71% of the leader**. Three specific reasons:

1. **No mana engine.** 4.2 mana/s against 15 for a Shaman+Wizard core. Druid has the
   second-best AE in the game and no way to pay for it.
2. **Druid's `Upheaval` is the wrong buy** — 625 mana is the most expensive AE at its
   damage tier.
3. **Weak melee floor** (191 vs 300): no Triple Attack, no Dual Wield worth having, poor
   weapon access.

### But your instinct is right about the variable that matters

The Bard's contribution to AOE is **not damage — it is pull size**, and pull size is the
one term everything else scales on linearly. If a Bard lets you hold twice what any other
trio can:

```
BRD+SHM+WAR at N=64  =  1761 DPS      vs   best non-Bard at N=32  =  1236 DPS
BRD+DRU+SHD at N=64  =  1571 DPS
```

**Bard wins outright the moment it doubles N.** I cannot measure whether it does — swarm
pulling is not in the log corpus — so that is stated as the conditional it is.

### Top 3

| # | Trio | Case |
|---|---|---|
| **1** | **BRD+SHM+WAR** | **Your build, corrected.** Keep the Bard for pull size; swap Druid → **Shaman** for `Cannibalize` (0 → 8 mana/s, the single largest AOE upgrade available) and Shadow Knight → **Warrior** for `Area Taunt` (the actual gathering tool), the free 5% permanent mitigation, and real weapons. **995 at N=32, 1761 at N=64.** 18% ahead of `SHD+DRU+BRD` at every pull size, before counting Warrior holding more. |
| **2** | **SHM+WAR+WIZ** | **The best at a fixed pull.** 15 mana/s (Cannibalize + Harvest), a 12,000 pool, and `Supernova` at 854 PBAE. **1236 at N=32** — the highest number any trio reaches without assuming Bard pull mechanics. |
| **3** | **CLR+SHM+WAR** | **The one that never dies.** Tank score 105, `Divine Aura` (18 s of invulnerability on a 10-minute timer) as an emergency button, 11 mana/s, 12,000 pool, `Upheaval`. **1131 at N=32** — 8% behind the Wizard build for a large margin of safety on a big pull. |

If you keep `SHD+DRU+BRD` as-is you are giving up about 30% for the Shadow Knight's
lifetap self-sustain, which the Warrior's mitigation and your partner's heals already cover.

---

## What would change these answers

| Unknown | Which list it moves |
|---|---|
| **Do armour Proc Exaltation sockets fire on melee swings?** (a 60-second in-game test) | All of them — worth +100 to +260 DPS, and it favours whoever has the most worn slots free |
| Whether a Bard really holds a bigger pull | The AOE top 3, decisively |
| Multi-attack (DA/TA) law — the last classic-sourced constant | ±1.5–2x on every melee lane in lists 1–3 |
| Defensive stance's damage multiplier (assumed 1.0) | The absolute numbers in list 2 and the AOE lists |
| PAL/SHD/BST Offense caps at level 50 (unpublished) | ±15 Wrath ≈ ±2% — does not reorder anything |
| Archery damage bonus on bows | Would have to roughly triple to make Ranged stance competitive |

*Fan analysis. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.*
