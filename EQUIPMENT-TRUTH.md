# EQUIPMENT TRUTH — the worn-item model, verified against the client

**Established:** 28 August 2026
**Standing:** every row below is confirmed by a client screenshot, a real
`/outputfile inventory` dump, or both. Nothing here is inherited from classic
EverQuest.

Companion to `CLIENT-TRUTH.md`, which does the same job for the log message
families. Same rule: *a number without its source is a number that can lie.*

---

## 1. There are twenty-three worn positions, and two of them are ANY

The paperdoll is not the classic EverQuest paperdoll. A real
`/outputfile inventory` dump of a live Legends character (`Primitive`,
freeport) enumerates its worn positions as:

| Position | Count |
|---|---|
| Ear | 2 |
| Wrist | 2 |
| Fingers | 2 |
| **Any Slot** | **2** |
| Head · Face · Neck · Shoulders · Arms · Back · Range · Hands · Primary · Secondary · Chest · Legs · Feet · Waist · Ammo | 1 each |

**Total: 23 worn positions across 18 slot types.** There is **no Charm slot** —
the catalogue has no `CHARM` shard and the dump has no `Charm` row.

### The ANY slots take anything

This was previously recorded as unconfirmed. It is now confirmed twice over,
independently:

**Client screenshot.** `Midnight Clad Straps +6` — an item whose own tooltip
reads `Chest` — sitting in a slot the client labels `Any Slot`, on a character
whose actual Chest position is already filled. The neighbouring ANY position is
visible and empty, labelled `ANY`.

**Inventory dump.** The same structure, in text, on a different character:

```
Any Slot   Brigandine Tunic +1        3307     1   10
Any Slot   Midnight Clad Straps +2    177795   1   10
Chest      Red Dragonscale Armor +1   11623    1   10
```

That character is wearing **three chest pieces at once.** `Brigandine Tunic` is
`CHEST`-only, `Midnight Clad Straps` is `CHEST`-only, and the Chest position
itself holds a third `CHEST` item.

### What the ANY slots do *not* bypass

Class restriction still applies. In the dump above the three chest pieces list
`WAR BRD CLR PAL RNG ROG SHD SHM`, `DRU ENC MAG MNK NEC ROG WIZ BST`, and
`WAR BRD PAL RNG ROG SHD`. The intersection is exactly one class — **ROG** — so
that character's trio contains a Rogue. An ANY slot removes the *position*
restriction, not the *class* restriction.

### What the two ANY slots are worth

They are worth whatever the two best items your trio can legally equip are worth,
unconstrained by position. That is a real gain of two slots — but **the obvious way to
spend them does not work**, and the reason is worth recording.

Since **0 of 2,263 catalogued items carry an ATTACK stat** (re-verified on the current
catalogue; the previous count was 0 of 3,663), the naive plan is to buy Wrath through STR,
which enters at `((2 x STR) - 150) / 3` — 0.667 Wrath per point. The best legal STR item
for a `WAR / RNG / BER` trio is `Red Dragonscale Armor` (STR 20 base, **40 at +10**, and
**not LORE**, so it can be worn twice), which would be +80 STR = +53 Wrath.

**That gain is almost certainly zero in practice.** eqlwiki caps STR at 255, which pins
`StrengthModifier` at its maximum of 120. Any character geared well enough to be having
this conversation is already at the cap, so STR bought in an ANY slot converts to nothing.
The two slots are real, but they are **not** an ATK workaround. Spend them on AC, HP, mana,
resists, or a click/proc effect — their damage value is whatever that effect is worth, not
a Wrath gain.

> **Contradiction, recorded rather than smoothed over.** The client panel in section 4
> reads **INT 295**, above 255. So either the cap is per-stat, or something raises it, or
> the display is uncapped while the cap still binds internally. Until this is settled, treat
> "STR caps at 255" as the *conservative* assumption — it is the one that makes the ANY
> slots worth less, not more.

> **Also open.** Whether *worn* haste stacks across positions. The catalogue's haste ceiling
> is 41 (class-specific belts) and 36 (`Cloak of Flames`, ALL classes). If worn haste stacks,
> two ANY slots are worth a great deal; if only the highest worn source counts — the classic
> behaviour — they are not. **Do not model stacked worn haste until this is measured.**

---

## 2. The upgrade formula is confirmed against a client tooltip — ~~in full~~ in part

> **CORRECTED 31 Aug 2026.** The heading and the closing sentence of this section
> were both too strong. The tooltip confirms the **percentage** term. It does not
> test the **floor** term at all, and this section said it did. See
> `verify_upgrade.py` and `HANDOFF.md` §35.

The rule in use was `value + max(tier, floor(value × 0.10 × tier))` — ten
percent of **base** per tier, with a floor of +1 per tier. It had never been
checked against the client.

`Midnight Clad Straps` is catalogued at `AC 10, STR 13, STA 13, INT 13, WIS 13`.
The client tooltip for the **+6** copy reads:

| Stat | Base | Predicted at +6 | Client | |
|---|---|---|---|---|
| AC | 10 | 10 + max(6, 6) = **16** | 16 | OK |
| STR | 13 | 13 + max(6, 7) = **20** | 20 | OK |
| STA | 13 | **20** | 20 | OK |
| INT | 13 | **20** | 20 | OK |
| WIS | 13 | **20** | 20 | OK |

~~**Five for five, including the case where the floor and the percentage
disagree** (AC, where 10% × 6 = 6.0 ties the floor, and STR, where 7 beats it).
The formula is confirmed.~~

**Five for five on the percentage term. Zero for five on the floor term.** The
struck sentence names its own refutation and then draws the opposite conclusion:
AC *ties*, and a tie is not a disagreement. Work the five rows out both ways —
`verify_upgrade.py` prints the table — and `max(tier, …)` and plain
`floor(base × tier / 10)` give **the same answer in every row**. AC 10 → 16 both
ways, STR/STA/INT/WIS 13 → 20 both ways.

The floor term is strictly larger than the percentage term **only when the base
value is below 10**, at every tier from 1 to 10 (proved exhaustively over base
1–399 in `verify_upgrade.py` §3). `Midnight Clad Straps` has no such stat. So
this tooltip could not have returned a negative for the floor no matter what the
client did — which is the precondition failure this project keeps finding in
other people's instruments and had here in its own.

Session B holds five further client captures of the same mechanic on **weapon
damage** (14 at +0/+1/+2/+3 and 37 at +10). Those refute +5%/tier and refute
compounding, and they confirm the percentage term a second time — but their
bases are 14 and 37, so they do not reach the floor either.

**Ten captures across two repositories and not one of them is decisive.** The
percentage term is Tier M twice over. The floor term is ungraded, and
`model4.py` no longer carries it: percentage-only is the conservative branch and
it agrees with Session B's `upgrade.ts`, so one item stops getting two values
across the seam. **One client window of any sub-10-damage weapon at any tier
≥ 1 settles it.**

### The catalogue's saves are incomplete

The same tooltip reads `SV Void: 6`. The catalogue entry has **no `sv` block at
all**, and no catalogued item anywhere carries a `VOID` save — the catalogue
knows only the classic five (`MAGIC FIRE COLD POISON DISEASE`). The character
panel meanwhile shows `SV Void 111` next to those five.

**Void is a sixth, Legends-native resist that the item data does not cover.**
Any analysis that ranks items on resists is reading a truncated column. Damage
analysis is unaffected.

---

## 3. Exaltations are real, per-item, and numerous

`CLIENT-TRUTH.md` noted the `(Exaltation)` name suffix as a parsing nuisance.
The dump shows what it actually is: **augment sub-slots on every worn item**,
enumerated as `<Position>-Slot<n>`.

```
Face-Slot7       Polished Mithril Mask (Exaltation)     4505    <- same id as the item it sits in
Range-Slot7      Idol of the Underking (Exaltation)     14762   <- same id
Primary-Slot10   Thelvorn, Blade of Light (Exaltation)  27709   <- same id
Fingers-Slot7    Djarn's Amethyst Ring (Exaltation)     10366   <- same id
Fingers-Slot7    Moonstone Ring (Exaltation)            10150   <- DIFFERENT id from its host
Feet-Slot7       Golden Efreeti Boots (Exaltation)      4407    <- DIFFERENT id from its host
```

Two things follow.

**An item can be converted into an Exaltation and grafted onto a different
item.** `Golden Efreeti Boots` are not worn anywhere on that character — only
their Exaltation exists, socketed into `Lustrous Russet Boots`. The item was
consumed to produce the augment. This is the mechanism the user demonstrated
by moving `McVaxius' Horn of War (Exaltation)` onto the Cudgel.

**Sub-slot counts are per item, not per position.** Observed counts:

| Position | Sub-slots on this character's item |
|---|---|
| **Primary** | **5** (Slot2, 7, 8, 9, 10) |
| **Secondary** | **5** |
| Hands | 5 |
| Ear | 4 |
| Feet | 4 |
| Face · Arms · Legs · Wrist(a) | 3 |
| Head · Neck · Back · Chest · Waist · Wrist(b) | 2 |
| Range · Fingers | 1 |

The two Wrist items differ from each other (3 vs 2) and the two ANY items
differ from each other (2 vs 3), so the count is a property of the item.

> **This is the largest unmodelled damage channel in the project.** A weapon
> carries **five** Exaltation sub-slots. If any meaningful fraction of those can
> hold proc or worn-damage effects, the per-swing and per-minute damage of a
> geared character is not something the current model is within range of
> estimating. It was assumed to be zero. It is not zero.

### Only weapon proc sockets fire — confirmed, against my own earlier doubt

**29 August 2026.** The player states that Proc Exaltations fire **only from the primary and
secondary weapon slots**, plus the ranged slot for a Ranger — so **one proc on a two-hander,
two dual-wielding, and one on a bow.** Armour sockets do not proc.

I flagged this as contradicting the corpus, which shows six distinct Exaltation sources
firing in a single log — a bracer 96 times, a ring 60, boots, a medallion, a girdle, a mask.
**The corpus agrees with the player, and I was reading the messages wrong.**

The test is in `tools/exaltation.py`. If those were damage procs a spell-damage line would
follow, but a busy combat log has spell damage flying constantly, so the measurement needs a
control: the same ±1 s window around an ordinary melee swing.

```
CONTROL  spell damage within ±1s of an ordinary melee swing : 384/1834 = 20.9%
POOLED   same window around an (Exaltation) message          : 162/958  = 16.9%
```

**Exaltation messages are BELOW the coincidence baseline.** Per source:

| Exaltation | slot | fires | with damage | vs 20.9% baseline |
|---|---|---|---|---|
| Djarn's Amethyst Ring | FINGERS | 425 | 7% | far below |
| Idol of the Underking | RANGE | 210 | 3% | far below |
| Serpentine Bracer | WRIST | 96 | 18% | below |
| Mane Attraction | — | 69 | 28% | at chance |
| Black Alloy Medallion | NECK | 59 | 46% | above, but no damage is ever *attributed* to it |
| Golden Efreeti Boots | FEET | 25 | **0%** | a movement click, as in classic |
| **Polished Mithril Mask** | FACE | 62 | **100%** | fires on *every cast* — a spell-linked worn effect, and no damage line names it |

Not one of them is a damage source. The messages are **click and worn-effect activations**.

**What this costs the model.** The "armour proc sockets take proc lanes from 4 to 10–20,
worth +100 to +260 DPS" hypothesis in `DAMAGE-CHAIN.md` was the leading explanation for the
chain's remaining shortfall against the 900–1000 and 1200+ anchors. It is dead. And the
37.3% non-melee share of that real 426-DPS parse turns out to need no armour procs at all —
it decomposes entirely into DoTs, class spells and one class proc buff (Envenomed Bolt 30.7,
Smiting Strike 24.6, Plague 13.1, Puma Maw 12.7, and a tail).

**What it costs a build.** Proc capacity is now a hard structural gate, not a stat:

| Setup | Proc sockets that fire |
|---|---|
| Two-hander | **1** |
| Dual wield | **2** |
| Ranger with a bow equipped | **+1** |

Dual wield gains a whole proc lane over any two-hander — which weakens every
`Cudgel of the Fool` build and strengthens the Paladin-blade builds.

---

### The KeyRing is not the Exaltation library

The dump's `KeyRing / Equipment` section lists 36 items. **None of the six worn
Exaltation ids appear in it.** So the KeyRing does not store Exaltations and
they are not freely re-drawn from a library; it is a separate equipment
collection. Whether an Exaltation can be pulled back *out* of a host item
without being destroyed is **not established** — the user reports swapping them,
which suggests it can, but the dump cannot show it.

---

## 4. One character panel, read verbatim

The only direct client read of the derived stat block held by this project.
Recorded whole because a second one at a different STR would let the Wrath
formula be solved outright.

```
Avenrae — level 10, WIZ / SHM / NEC, Bristlebane

HP     1398 / 1398          STR 178    SV Poison   49
Mana   1799 / 1799          STA 197    SV Magic    62
End     596 /  596          AGI 119    SV Disease  68
AC     365 / 407 | 128      DEX 161    SV Fire     60
Attack      98 | 117        WIS 239    SV Cold     45
                            INT 295    SV Void    111
                            CHA 122
HP Regen 16   Mana Regen 34   End Regen 23   Attack Speed % 100
Weight: overall 58 / 178, equipped 16
```

**What this settles.** `INT 295` is above 255, so **Legends has no 255 stat
cap** — a classic assumption that would have silently truncated every
high-STR build. `Attack Speed % 100` is the unhasted baseline, so the haste
readout is a percentage of 100, not a bonus over it.

**What it does not settle.** `Attack 98 | 117` is a two-part readout and the
split is unexplained. With `STR 178` the strength term alone is
`((2 × 178) − 150) / 3 = 68.7`, leaving ~29 for weapon skill and worn ATK on a
level-10 caster — plausible but not solvable from one sample.
**One more panel at a different STR value closes this.**

Note also that HP 1398 / Mana 1799 at **level 10** is roughly an order of
magnitude above classic EverQuest at the same level. Any level-scaling term
carried over from classic is wrong.

---

*Fan project. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw
Studios. The game install was read, never written.*
