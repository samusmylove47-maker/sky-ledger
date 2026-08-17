# CLIENT TRUTH — what the EverQuest Legends client actually says

**Established:** 15 August 2026
**Method:** direct read of the shipped client string tables plus a 986,514-line
real Legends log. Nothing here is inferred from classic EverQuest, eqlwiki, or
any rival site. Every row can be re-checked with one `grep`.

This file exists because Sky Ledger's premise is that a number without its
source is a number that can lie. These are the sources.

---

## 1. Where the truth lives

| File | Size | What it is |
|---|---|---|
| `eqstr_us.txt` | 454 KB | The client's message string table. Header `EQST0004`, **7,120 entries**, one per line as `<id> <format string>`. `%1 %2 %3` are substitution slots. |
| `dbstr_us.txt` | 9.8 MB | Item / AA / effect string database. `^`-delimited fields. |
| `eqlsstr_us.txt` | 19 KB | **Launcher and login only.** No gameplay strings. A dead end — recorded so nobody spends an afternoon on it again. |
| `Logs/eqlog_<Char>_<Server>.txt` | — | The real corpus. 986,514 lines over 11–14 Aug 2026. **Never enters Plane of Sky** — see §3.4. |
| `<Char>-Inventory.txt` | 37 KB | A real `/outputfile inventory` dump. Five columns: `Location, Name, ID, Count, Slots`. |

All are inside the game install, which is **read-only, always**. Everything
below was produced from copies.

### The methodological finding

Two of the tails Sky Ledger depends on **do not exist in `eqstr_us.txt` at
all**, yet occur 602 and 79 times in the real log:

```
 and sold it for ...      autosell on pickup
 to create a ...          loot consumed by an upgrade combine
```

They are composed server-side. **The string table is necessary but not
sufficient.** Anyone mining only `eqstr_us.txt` would conclude these phrasings
were invented; anyone mining only a log would miss the message families they
happen not to have triggered. Ground truth is the two together.

This also independently vindicates sowoky's edge cases in eqltools' sky-core,
which were previously taken on trust.

---

## 2. The message families Sky Ledger reads

Every pattern in `engine.js` `RX`, with the client ID that governs it.

| Purpose | Client ID | Format string | Status |
|---|---|---|---|
| Loot from a corpse | **467** | `--You have looted %1 %2 from %3.--` | verified |
| Another player loots | 466 | `--%1 has looted %2 %3 from %4.--` | correctly ignored |
| Corpse naming | 1223 | `%1's corpse` | verified |
| Offer in a trade | **10012** | `You offered %1 %2 to %3.` | verified |
| Trade completed | **9122** | `You complete the trade with %1.` | verified |
| Trade completed, unnamed | **9123** | `You complete the trade.` | **now handled** |
| NPC hands it back | **1105** | `I have no need for this, %3. You can have it back.` | verified — `%3` is the **player**, not the item |
| Item destroyed | **8080** | `You successfully destroyed %1 %2.` | verified |
| Sold to a merchant | **1361** | `You receive%1 from %2 for the %3(s).` | verified — note no space after `receive`; `%1` carries its own |
| Sold a whole bag | **799** | `You receive %1 from %2 for the contents of your bag.` | **now handled** as a known unknown |
| Zoning | **12357** | `You have entered %1.` | verified |
| Not a zone | 6372 | `You have entered an area where levitation effects do not function.` | **now rejected** |
| Not a zone | 12009 | `You have entered an Arena (PvP) area.` | **now rejected** |

### Kills

| Purpose | Client ID | Format string | Status |
|---|---|---|---|
| You killed it | **12113** | `You have slain %1!` | verified verbatim |
| Someone killed it | **12114** | `%1 has been slain by %2!` | verified verbatim |
| Nobody named | **12112** | `%1 died.` | verified — but **unattributable** |
| Your pet killed it | **440** | `Your pet has slain %1!` | **now handled** — was missing entirely |
| You died | **12106** | `You died.` | **now excluded** — was booked as a kill of a mob named "You" |
| You died | **12107** | `You have been slain by %1!` | now counted as your death |
| Killer unknown | 12115 | `%1 has been slain by an unseen hand!` | unattributable |

**The three kill patterns the previous session flagged as unverified guesses
are correct, verbatim.** `HANDOFF.md` §6 is closed. The inference happened to
be right — but it was right by luck, and what was actually wrong sat one layer
underneath it, in *who gets credit*.

### Group and raid roster — how "yours" is learned

| Client ID | Format string |
|---|---|
| **1399** | `%1 has joined the group.` |
| **12005** | `%1 has left the group.` |
| **12004** | `You have joined the group.` |
| **12001** | `You have been removed from the group.` |
| **12002** | `Your group has been disbanded.` |
| **5059** | `%1 joined the raid.` |
| **5063** | `%1 has left the raid.` |
| **5083** | `You have joined the raid.` |
| **5062** | `You were removed from the raid.` |
| **5071** | `Your raid was disbanded.` |

Your pet identifies itself: every pet-chatter string ends `, Master.`
(IDs 438, 489, 490, 1130, 1131, 1132, 1133, 1138), so the first line a pet
speaks teaches the ledger its name.

---

## 3. Two things only the log could prove

### 3.1 Legends instances its zones, and classic EverQuest did not

Real zone lines from the corpus:

```
You have entered The Plane of Fear 4 (Refined).
You have entered The Plane of Hate - Group 3 (Fused).
You have entered Nagafen's Lair - Group 1 (Awakened).
You have entered The Ruins of Old Paineel 1 (Awakened).
```

Tiers observed: **Awakened · Adaptive · Fused · Refined**, in both a bare
`<n> (<Tier>)` and a `- Group <n> (<Tier>)` form.

These suffixes appear in **no client string file** — they are composed
server-side. A tool testing `zone === "Plane of Sky"` therefore never fires
inside an instance, which is where the zone is actually played. Sky Ledger now
normalises the base name and keeps the tier.

This is precisely the class of error this project exists to catch: a
1999-shaped assumption that survives because nobody checked the current
client. We shipped one ourselves.

### 3.2 A drop-rate denominator built from `%1 has been slain by %2!` counts strangers

That string fires for **every** death in earshot regardless of who landed it —
including other players, NPC-versus-NPC kills, and players dying to mobs.
Replaying the corpus through the pre-fix engine:

```
kill events credited : 1274
landed by a stranger :  540   (42%)
```

It also books other players' deaths as mob kills — `Ffossip has been slain by
Amygdalan warrior!` counted a kill of a "mob" named Ffossip.

An inflated denominator reads every rate **systematically low**, which is a
fabricated number. Sky Ledger now credits a kill only when you, your pet, or a
current group/raid member landed it, and **reports what it excluded** rather
than discarding it silently. On the same corpus: 982 credited, 286 excluded.

---

## 3.3 The client says outright whose kill it was — and it is not the killer's name

The single most consequential finding. The client prints an experience line
**1–4 lines before** the kill line:

```
[17:18:40] You gain party experience! (0.592%)
[17:18:40] You receive 6 platinum, 9 gold, 9 silver and 3 copper from the corpse.
[17:18:40] An ire ghast has been slain by an elite dragoon!
```

A **mob** landed the killing blow. The experience and the corpse were still
ours. Any rule keyed on the killer's *name* throws that kill away.

| Client ID | Format string |
|---|---|
| **138** | `You gain experience!%1` |
| **139** | `You gain party experience!%1` |
| **15603** | `You receive no experience for defeating this creature as you are in a raid.` |
| **12072** | `You receive %1 from the corpse%2.` |

Measured on the reference corpus: **222 of 286 kills (78%) that roster-based
attribution discarded carried experience credit** — an ~18% low bias on every
denominator, which reads every drop rate too **high**.

The rule is therefore a **union**: a kill is yours if the client awarded
experience for it, *or* if you, your pet, or a current group/raid member landed
it. Neither signal alone is sufficient — 128 kills in the corpus print
`You have slain X!` with no experience line at all (trivial cons).

This also matters because **the raid roster cannot be learned from a log**. The
corpus contains 22 raid-experience lines and *zero* raid roster lines. Where the
roster is blind, experience is the only signal there is.

Result on the corpus: credited 982 → **1,205**, unattributed 286 → **63**.

## 3.4 The fifteen wind runes — and a correction

From `dbstr_us.txt`, ids **75–89**, all fifteen carrying the description
`Used in Class quests in the Plane of Sky.`

```
Lena · Meda · Neza · Ozah · Kala · Azia · Beza · Caza
Dena · Ena · Fana · Geza · Heda · Izah · Jaka
```

**These fifteen match `sky.json`'s fifteen rune items exactly** — an independent
client-side validation of that slice of the dataset.

**A correction, recorded because the mistake is instructive.** Those dbstr
entries sit in a field type used for alternate currency, and the text
`Wind Rune` appears **zero** times in the 986k-line reference log. That looked
like proof runes were currency and could never be counted from a file, and it
was written up here as fact.

It was not proof. **That log never entered Sky** — `sawSky` is false throughout;
it covers Fear, Hate and Nagafen. The silence said nothing at all, and the
inference should never have been drawn from it.

A real `/outputfile` dump settles it. Runes are **ordinary bag items** with
stack counts, item ids 177775–177789:

```
General 2-Slot2   Wind Rune Ozah   177778   3   10
General 5-Slot6   Wind Rune Neza   177777   5   10
```

So they are tracked like any other item, an inventory dump counts them, and a
completion requires them like every other piece. The hand-entry panel remains
for players with no dump, since runes drop zone-wide and a log begun after
farming them cannot see what is already held.

**The lesson generalises:** absence of evidence in one corpus is not evidence of
absence. The corpus has to be capable of containing the thing before its silence
means anything — and this one demonstrably was not.

## 3.5 Trades that end without delivering

Offers sat in the pending map until *some* trade closed with that NPC. With no
cancellation handling, one offer survived **11,000 lines and two hours** before
attaching itself to an unrelated trade.

| Client ID | Format string |
|---|---|
| **1450** | `You have cancelled the trade.` |
| **1448** | `%1 has cancelled the trade.` |
| **1449** | `The trade has been cancelled.` |

In the reference corpus this booked **5 items as delivered that never left the
bags**, and a fabricated item set on a trade to a quest giver can tick a Sky
test complete. Offers are now cleared on cancellation, on zoning, and after a
staleness bound.

A related case: the handback line (**eqstr 1105**) names the **player**, not the
item, so on a *partial* bounce there is no way to know which piece came back.
Delivering all of them marked a test complete that was never turned in and
forgot a piece still in the bags. The ledger now records nothing for such a
trade and discloses it.

## 3.6 Other message families now handled

| Client ID | Format string | Why it matters |
|---|---|---|
| **1460** | `You received a %1 from %2.` | how every quest reward arrives |
| **6471 / 6472** | `%1 hands you the %2 that was sent from %3.` | parcels — a guildmate can post you a Sky piece |
| **15518** | `You have successfully merged two items together to create a new item: %1` | eats **two** of the base item; 197 in the corpus |
| **8067** | `You receive %1 from %2 for the %3.` | the *singular* merchant sale; 1361 only matches the `(s)` plural |
| **12108** | `You have been slain by an unseen hand!` | your death, previously uncounted |

Also: Legends key-ring variants print as `Gold Plated Koshigatana (Exaltation)`
alongside the plain name, so the parenthetical is stripped like the `+N` tier —
otherwise the two land in different buckets and holdings drift.

## 4. Leads not yet followed

- `dbstr_us.txt` holds **15 contiguous entries (IDs 75–89)** whose lore reads
  `Used in Class quests in the Plane of Sky.` — a client-side list of Sky quest
  items, checkable against our 128. Worth chasing.
- The zone archive is `airplane.s3d` / `airplane_obj.s3d` in the install root,
  which is `HANDOFF.md` §7 priority 5 (island geometry). Untouched.
- `Logs/Sky.txt` is a **skybox renderer error log**, nothing to do with the
  Plane of Sky. Recorded so it is not mistaken for a lead again.
- `spells_us.txt` (38 MB) and `spells_us_str.txt` are present and unread. They
  settle the flat-vs-percentage haste question in `HANDOFF.md` §5.

---

*Fan project. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw
Studios. The game install was read, never written.*
