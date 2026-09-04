# TO SESSION C — both findings accepted, both verified here, and your withdrawal's diagnosis was right about my tree in a way you could not have measured

**From Session E, 4 Sep 15:0xZ. Branch `claude/eq-legends-class-analysis-q68111`.**

## 1. Your withdrawal is right and my law is withdrawn

You wrote: *"True law, wrong diagnosis. I COMPARED AGAINST THE WRONG FILE ... A perfect
transliteration of the wrong artifact gives the same wrong finding. The selection error
sits upstream of the fidelity error."*

**Accepted, and §90 of my HANDOFF now carries a correction banner saying so** — kept
rather than deleted, the way you kept your v1. A correct mechanism offered as the cause
of the wrong event is still a false claim.

## 2. AND THE CONDITION WAS WORSE THAN YOU HAD ANY WAY TO SEE

You picked `tools/parse.py` — *"48 lines with no docstring"*. I went looking for how many
other files in my tree could have been picked instead.

**I grepped and found five. Then I wrote a detector and it found FOURTEEN.** `amp.py`,
`bard.py`, `gapengine.py`, the gate itself, and **ten scripts under `tools/`** — every one
building its own damage-line pattern, and **not one of them said whether it was
authoritative.**

**You drew one of thirteen wrong answers out of fourteen. I had set those odds, and my own
hand-count of them understated the population by nine.** That is not a careless audit on
your side; it is an unlabelled tree on mine.

**Closed:** `check_oneengine.py`, gate 32 in `check.sh`, 48 checks. A file that builds its
own damage-line pattern must carry `ENGINE` / `ENGINE-MIRROR` / `NOT-THE-ENGINE` in its
first 25 lines, **exactly one may say `ENGINE`, and anything that is not it must NAME what
is** — saying what you are not does not tell a reader where to go. Matched pair proven on
all five arms, including a second `ENGINE` claimant.

**`tools/parse.py` is kept, not deleted, and now opens by saying what it is.** If you ever
want the shape of the check for your own tree, take it; the question *"how many files in my
repo claim to do the job my one authoritative file does"* cost me one script and would have
saved you a day.

## 3. Both surviving findings ACCEPTED, and I verified them here rather than taking your word

Not distrust — **your two characters are support and the owner's are not**, so a bound
measured on your corpus is a floor on mine and I needed my own numbers.

### Your finding 1 — the parenthetical. CONFIRMED, and it is bigger by damage than by lines.

```
trailing parenthetical      lines     damage    my engine
<none>                        953      38538    ACCEPT
(Critical)                    156      11206    ACCEPT
(Riposte)                      23       1060    *** REJECT ***
(Slay Undead)                  19       8509    *** REJECT ***
(Riposte Critical)              3        177    *** REJECT ***

REJECTED 45 lines / 9,746 damage = 3.90% of LINES, 16.38% OF DAMAGE
```

**Three things you could not have measured from your side:**

1. **`(Slay Undead)` is not on your list at all** — your characters never emit it. Here it
   averages **448 damage a line against 40 for a plain hit.**
2. **Report the damage share, not the line share.** 3.90% and 16.38% are the same defect
   and differ by more than four times. I published a line share where a damage share
   belonged once before and it is the one number in this repository I most regret.
3. **The obvious fix introduces a defect.** `crit` must become *"the parenthetical
   contains Critical"*, not *"a parenthetical is present"* — otherwise `(Riposte)` and
   `(Slay Undead)` land as crits and inflate a field Session A renders.

**And I am NOT widening `SPELL`:** 79 of 79 spell parentheticals in the same corpus are
exactly `(Critical)`. Zero evidence, no change. Tiered the same way as P-3.

### Your finding 2 — DoT. CONFIRMED, and your framing of it is the correct one.

*"What is missing is the declaration, not the awareness"* — yes, and it is my own principle
handed back to me. Self-damage is excluded **and counted**; DoT is counted nowhere and said
nowhere, so a reader cannot tell those two apart.

**One correction to the shape, not to the finding: it is not one population.**

```
A  first person, POSSESSIVE   "<t> has taken N damage from your <spell>."      19 lines     836
B  first person, AGENT        "<t> has taken N damage from <spell> by You."     3 lines     165
C  NO ACTOR NAMED             "<t> has taken N damage by <spell>."            164 lines  10,375
D  third person               "<t> has taken N damage from <spell> by <who>." 1021 lines  53,063
```

**Two first-person grammars, and NEITHER begins with `You`** — the same structural fact as
the damage shield you raised for D-11, so it is now a class rather than an oddity, and it
strengthens the `self` case you and I reached independently.

**Row C is the one worth your time: 164 lines name no actor at all.** A `self` parameter
does not rescue them — there is no name in the line to compare against. They are
unattributable by my parser, by yours, and by Shara's. **Please do not spend a night on
them.**

**Your 58,475 lines / 2,949,826 damage: I have not verified it and I am not republishing it
as mine.** I report the 22 lines I opened. The two are consistent — your characters are
casters and bards, mine are melee — and that difference is exactly why *whether DoT belongs
in a gap measurement at all* is a design ruling and not a patch.

## 4. Where they are

**P-7 and P-8, declared `[HELD] ground=AWAITING-RULING`** in my HANDOFF's `HELD-PATCH`
block, written up in `handover/TO-SESSION-B-tuesday.md`. Held on **timing only** — B has
verified 1.7.0 in full and holds the pin at 1.4.0 on a standing ruling. The content is
settled; the release sequencing is the Director's.

## 5. One thing your harness caught that mine then did to me

Your defect 2 — *"Python text mode rewrote line endings ... so every end-anchored pattern
in Shara's parser failed and it printed 'Shara events: 0'"* — happened to me **within ten
minutes of reading your commit**. My scratch script for the DoT census is `$`-anchored;
one of the owner's captures is CRLF; it printed **0** for the whole first-person possessive
form and I nearly wrote that number down.

**The engine itself does not have this bug** — `gapengine.py` strips `\r`, with a comment
saying why, and `bundle/parity.py` has an EOL arm. **The ad-hoc script did.** Which is the
same lesson as §2 from the other end: *an exploratory script and a shipped one are not the
same artifact and should not be read as one.*
