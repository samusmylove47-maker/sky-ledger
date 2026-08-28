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

They are worth whatever the two best items your trio can legally equip are
worth, unconstrained by position. Since **0 of 2,263 catalogued items carry an
ATTACK stat** (re-verified on the current catalogue; the previous count was 0 of
3,663), the damage-relevant currency in an ANY slot is STR, which enters Wrath
at `((2 × STR) − 150) / 3` — **0.667 Wrath per point of STR**.

For a `WAR / RNG / BER` trio the best legal STR item in the game is
`Red Dragonscale Armor` (STR 20 base, **40 at +10**, and **not LORE**, so it can
be worn twice):

```
2 ANY slots × 40 STR  =  +80 STR  =  +53.3 Wrath
```

For scale, the Ranger's entire `Hunter's Attack Power` AA line — 26 ranks — is
**+104 ATK = +104 Wrath**. So the two ANY slots are worth roughly **half a
Ranger's ATK line**, they cost nothing but the drops, and they stack with it.

> **Open.** Whether *worn* haste stacks across positions is unresolved, and it
> matters here: the catalogue's haste ceiling is 41 (class-specific belts) and
> 36 (`Cloak of Flames`, ALL classes). If worn haste stacks, two ANY slots are
> worth far more than 53 Wrath. If only the highest worn source counts — the
> classic behaviour — they are worth the STR and nothing more. **Do not model
> stacked worn haste until this is measured.**

---

## 2. The upgrade formula is confirmed against a client tooltip

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

**Five for five, including the case where the floor and the percentage
disagree** (AC, where 10% × 6 = 6.0 ties the floor, and STR, where 7 beats it).
The formula is confirmed.

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
