# Sky Ledger

A Plane of Sky class-unlock tracker for EverQuest Legends that sits on top of the game.

Track the tests you care about, see what each missing piece drops from, and get told
which quests you can hand in right now — without alt-tabbing.

---

## Fastest start (no install)

Open `SkyLedger.html` in **Chrome or Edge on desktop**.

1. In game: `/log on`
2. In the app: **Follow a log file** → pick `eqlog_<Character>_<Server>.txt`
3. Pick your trio, tick the tests you want, hit **Show overlay**
4. Put the game in **Windowed** or **Borderless** mode and drag the browser window over it

The file picker gives the page permission to re-read that one file. It polls once a
second and reads only the bytes that are new, so a 1.5-million-line log costs nothing
after the first pass. Nothing is uploaded — there is no server.

Firefox and Safari can't follow a file live. Drop the log onto the panel instead for a
one-off read, and re-drop to refresh.

Log location is usually:
`C:\Users\Public\Daybreak Game Company\Installed Games\EverQuest Legends\Logs`

---

## Proper overlay (Electron)

The browser build can't pass clicks through to the game and can only fake transparency.
The Electron shell fixes both.

```
npm install
npm start          # run it
npm run dist       # build a portable .exe into dist/
```

Keep `SkyLedger.html`, `main.js`, `preload.js` and `package.json` in the same folder.

| | |
|---|---|
| `Ctrl+Shift+O` | show / hide |
| `Ctrl+Shift+L` | click-through — the panel stops eating clicks |
| drag the title bar | move |
| slider in the dock | transparency, 15%–100% |

Both hotkeys are global, so they work while the game has focus. Position, size,
opacity and click-through are remembered between runs.

Exclusive fullscreen draws over every window, including this one. Use Borderless.

---

## What it does that other Sky trackers don't

**It knows a piece can only be spent once.** 29 of the 128 turn-in items are wanted by
more than one test, and every wind rune is wanted by several. Holding one Djinni War
Blade does not make three quests ready. Sky Ledger treats every held item as a pool,
spends each unit on the test closest to completion, and marks contested pieces with ⚠
showing how short you are.

**It measures drop rates from your own log.** No site publishes community drop rates for
Sky — we checked every one we could find. So the app doesn't print one. It prints what
your log has seen: drops over kills of that named mob, with the sample size attached.

**A dry streak is a ceiling, not a zero.** Nine kills with no drop reads `<28% · 0/9`,
not `0%`. Zero successes in nine trials is not evidence of a 0% rate — it's evidence the
rate is under about 28%, and the bound tightens every time you kill it again. Printing
0% would tell you to stop farming something you should keep farming.

**It only counts kills you could have looted, and it asks the client, not the killer.**
`X has been slain by Y!` fires for every death in earshot — other groups, other people's
pets, even NPCs killing each other. Count all of them and every rate reads too low. But
the killer's *name* is not the answer either: the client prints `You gain party
experience!` a line or two **before** the kill, and that is its own statement that the kill
was yours — a mob can land the killing blow on a kill you were credited for. Sky Ledger
uses both signals: experience credit, **or** you / your pet / someone grouped with you at
that moment. On a real 986k-line log that is 1,205 kills counted and 63 it could not
place — and it tells you about the 63.

**It tells you what it threw away.** The strip above the dock shows kills excluded, bag
sales whose contents the client never names, and trades it refused to guess at. It hides
itself when there is nothing to admit.

**Ready tests sort to the top** with the exact dialogue to say and the NPC to say it to.

**The transparency slider is continuous.** Every other tool offers a menu of fixed steps.
Sky is a bright zone; the value that works in Lower Guk blinds you here.

---

## Wind runes

The client names all fifteen (`dbstr_us.txt` ids 75–89) and they match this tool's dataset
exactly. They are **ordinary bag items**, so an `/outputfile inventory` dump at a banker
counts them for you along with everything else you hold.

Set them by hand in **Setup → Wind runes** only if you have no dump. Runes drop zone-wide
from any mob, so a log that started after you farmed them cannot see what you already hold —
and for the same reason no drop rate can be measured for them.

## Whose kills count

A drop rate is drops over **kills whose corpse you could have opened**. The app works this
out on its own: it watches for `X has joined the group.` / `has left the group.` and the
raid equivalents, and it learns your pet's name the first time your pet speaks.

You only need the **Whose kills count** box in setup if you started logging *after* you
grouped up — the client never re-lists a group you have already joined, so those kills
would otherwise be excluded. Type the names in and it re-reads the log from the top.

Anything it cannot place is excluded and reported, never quietly folded in.

---

## Honest limits

**Kill-line patterns are now verified against the client itself.** `You have slain %1!`,
`%1 has been slain by %2!` and `%1 died.` are strings 12113, 12114 and 12112 in the
client's own `eqstr_us.txt`, read straight out of the install. `Your pet has slain %1!`
(440) is handled too. See `CLIENT-TRUTH.md` for the full table and how to re-check it.

**`X died.` names no killer, so it is never counted as your kill.** It is rare — 10 lines
in 986,514 — and it is reported in the excluded count rather than guessed at.

**Zone detection understands Legends instancing.** Planar zones arrive as
`The Plane of Sky 3 (Fused)` — a bare `<n> (<Tier>)` or `- Group <n> (<Tier>)` suffix that
classic EverQuest never had and that appears in no client string file. If Sky Ledger ever
fails to notice you are in Sky, the exact text the client printed is in the tooltip on the
zone name in the provenance strip; that is the string to report.

**The log only knows what happened while it was running.** Anything looted before
`/log on` is invisible. The inventory dump (`/outputfile inventory` at a banker) covers
that, wind runes included — it is a snapshot of your bags, so Sky Ledger takes the larger
of the two counts rather than adding them, and one item never reads as two.

**Autosell and upgrade combines are accounted for.** A line ending *"and sold it for…"* or
*"…to create a …"* means the item never reached your bags, so it isn't counted as held —
but it *is* counted toward the drop rate, because the drop still happened. An autosell
filter eating quest pieces would otherwise silently deflate every rate you see.

**A sold bag is a hole the log cannot fill.** `You receive … for the contents of your bag.`
never names what was inside. Those items may still show as held. The provenance strip says
so rather than pretending otherwise — empty the bag by hand if it matters.

**A closed trade is not proof of a turn-in.** Walk the wrong class's pieces to the wrong
giver and they're handed straight back, one refusal per item, and the trade still closes.
Refusals are only counted when the line names *your* character.

**Five classes carry a `?`.** Ranger, Rogue, Shadow Knight, Shaman and Wizard have no
confirmed Legends-era reward stat blocks. Their *turn-ins* are current; the stat numbers
may still be classic. Marked in setup and in the tooltips.

**Two items have contradictory sources** between the references, marked ⚑ in the panel:

- *Efreeti Great Staff* — eqlsource lists the efreeti set (islands 1.5 / 4 / 8);
  eqlegendstools lists Eye of Veeshan on island 8.
- *Efreeti Statuette* — eqlsource lists soul / essence griffons on island 4;
  eqlegendstools lists the efreeti set.

Three more are marked ✧ as *resolved*: Gem of Invigoration, Crown of Elemental Mastery
and Golden Hilt all drop from island 7 sphinx and drakes. eqlsource flagged the first as
unconfirmed; eqlegendstools names it, and the two agree on the other two.

---

## Credit

Quest data extracted from **eqlsource.com** and cross-checked against
**eqlegendstools.com** (FlammHammer) and **loadoutlegends.com**. Counts agree
independently at 95 tests, 222 turn-in slots, 128 unique items — and 222 matches
**EQBuddy**'s figure too.

The log-line edge cases that break naive counting — the autosell tail, combine
consumption, upgrade-tier suffixes, and handbacks naming the player — were identified by
**sowoky** in eqltools.com's `sky-core`. Reimplemented here, not copied, and the debt is
worth stating plainly: those three cases are the difference between a tracker that works
and one that quietly lies. Two of them turn out to appear in **no client string file at
all** — they are composed server-side — so they could only ever have been found the way
sowoky found them, by reading a real log. Confirmed here at 602 and 79 occurrences.

Message formats are verified against the client's own `eqstr_us.txt` rather than inherited
from 1999-era EverQuest. `CLIENT-TRUTH.md` lists every string ID so any claim in this tool
can be re-checked with one `grep`.

Fan tool. Not affiliated with Daybreak Game Company, Game Jawn or Darkpaw Studios.
