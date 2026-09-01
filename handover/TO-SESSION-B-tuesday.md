# TO SESSION B — three engine patches held for Tuesday's rebuild

**Written for B to read directly, not relayed.** The Director asked for this in one
place it can hand over on Tuesday; a finding that ships only in one place has not been
reported, and a paraphrase of a patch is not a patch.

**Nothing here is shipped.** The gap engine on `claude/eq-legends-class-analysis-q68111`
is **1.5.0**; B consumes **1.4.0** (`02543ec8`, 30,220 bytes) and that seam is stable
and correct. These three land together in **one** bump when B re-pins during the
Tuesday rebuild.

**Why together and why then:** a third re-pin four days before B rewrites the thing
that consumes the bundle serves nobody, and Tuesday is a re-pin B is doing anyway.
**That ground does not depend on anyone's availability** — an earlier version of this
hold rested on my believing B was offline, which was false; see §68 of `HANDOFF.md`.

**All three are conservative failures today.** Nothing wrong is being emitted while
they wait: the stance classifier *refuses* rather than asserting, the lane counter
over-counts an attempt that never occurs in a real log, and the missing verbs are
absent rather than wrong. Only P-3 changes numbers a reader sees.

---

## P-1 — the stance constant is calibrated on the wrong population

**Change:** `STANCE_EVEN_SHARE_OFFENSIVE` `0.93` → `0.993`
**File:** `gapengine.py`, and the mirror in `bundle/eqls-gap-engine.js`

`validate_jos437.py` records jos437 as *"provably Offensive (93.6% even damage)"*. The
classifier measures **99.3%** on the same file. Both are right — **they are over
different populations**:

```
0.9932  n=732  all melee, non-crit, KILLING BLOWS EXCLUDED   <- what the classifier uses
0.9387  n=832  every melee line, NO EXCLUSIONS               <- where 0.93 came from
```

The constant is the unfiltered figure; the code compares it against a filtered one. It
is the same defect as the 202% share, inside the classifier.

**What it changes for you:** `measured.stance_inferred` becomes identifiable on logs
that currently return `null`. It does **not** rescue the two real player logs — Shara
0.636 and Kenkyo 0.615 are further from 0.993 than from 0.93 and remain `null`, which
is correct until the owner supplies a stance screenshot alongside a log.

**Evidence:** `HANDOFF.md` §63. Source log `jos437-finishing-blow.log` in
`jmoyers/everquest-companion @ fd5e5bb`.

---

## P-2 — `_lanes` counts a self-hit as an auto-attack attempt

**Change:** apply the existing `SELF_TARGETS` guard inside `_lanes`, not only `_hits`
**File:** `gapengine.py`, and the mirror

`hit` is in `AUTO_VERBS`, and `_lanes` reads the raw events, so the self-target guard
added on 1 Sep reached `_hits` and never reached `_lanes`. Minimal probe — two real
swings and two self-hits:

```
_hits    outgoing hits kept        2   correct
_lanes   auto_attack_attempts      3   should be 2
```

**What it changes for you:** `measured.auto_attack_attempts` drops by the number of
self-hit melee lines, and `melee_seconds`' run set can shorten. **`melee_seconds` is
the denominator every lane rate divides by**, so a lane rate can move.

**Impact today: nil.** Zero `You hit yourself` **melee** lines in 189,460 lines of real
log — the spell form (`… by Cannibalize`) is common and already excluded correctly.

**Found by** `simulate.py` on its first run. **Evidence:** `HANDOFF.md` §66.

---

## P-3 — the meter cannot see damage verbs it is emitting  ← THE ONE THAT MOVES NUMBERS

### *** CORRECTED 1 Sep 16:16Z, BEFORE SHIPPING. THE PATCH BELOW IS SMALLER THAN THE ONE I FIRST SENT YOU, AND ONE PART OF IT WAS WRONG. ***

The first version of this section told you to add **six** verbs on evidence from
"117 logs, 282,615 stamped lines". I re-ran that measurement as a committed script
(`verbcensus.py`) instead of by hand, and the population was not what I said it was.

```
472  .txt/.log files named
416  open as EQ logs
139  UNIQUE by sha256          <- 277 were duplicate copies of each other,
                                  the same samples vendored into three trees
  5  named eqlog_<Char>_<server>.txt, the shape the EverQuest client writes
  1  of those five is literally named ..._fixture.txt
```

**So ~96% of the corpus behind the original claim is other projects' generated test
files.** They are perfectly good software fixtures and they are not evidence about
what EverQuest emits. R159: this is the KIND-of-claim question, and I got it wrong
in my own favour — the six-verb finding was the largest thing I had, and I did not
ask what the files were before counting them.

**What survives when the population is named.** Verbs seen in client-named logs:

```
verb     client-named logs                         synthetic only    VERDICT
frenzy   128 lines  9,047 dmg   Kenkyo                    607        ADD
smite     70 lines  1,647 dmg   Kenkyo                    640        ADD
cleave    20 lines    841 dmg   Shara (the owner's log)     0        ADD, uncapped
shoot      9 lines     78 dmg   Testchar_FIXTURE            0        REFUSE
claw       0 lines      0 dmg   -- none, anywhere       1,057        DROP
reave      0 lines      0 dmg   -- none, anywhere          36        DROP
```

**`claw` and `reave` have ZERO occurrences in any client-named log.** Every line
either verb has ever appeared on is in another project's generated fixture. I told
you to put `claw` in `AUTO_VERBS` on the strength of 1,057 lines and a 2.0s cadence;
all 1,057 are synthetic and the cadence is a property of somebody's generator.
**Do not add them.** If the rebuild has a real capture with either verb, that is new
evidence and I will take it.

**`cleave` is the strongest item here and it is the smallest.** 20 lines, 841 damage,
in `eqlog_Shara_rivervale_20260829_full.txt` — the owner's own capture, committed in
this repository, 181,325 stamped lines. Not a sample, not a fixture, not mine.

**Corrected size of the defect,** on client-named logs (5 files, 189,469 stamped
lines, 1,413 first-person melee lines):

```
269 lines invisible / 1,413   = 19.04% of first-person melee LINES
13,189 damage    / 67,095     = 19.66% of first-person melee DAMAGE
```

The number I published before was **19.98%, and it was a LINE share quoted where a
DAMAGE share is what a DPS meter is wrong by.** Those are two different quantities
and on the mixed corpus they diverge hard — 19.83% of lines but only 12.12% of
damage, because the synthetic verbs hit softer than the real ones. On the client-named
population they happen to agree at ~19%. Both are now reported, each against the
population its numerator came from.

**Change:** add `frenzy`, `smite`, `cleave` to `LANE_VERBS`; widen `MELEE` and `MISS`.
Do **not** add `claw`, `reave` or `shoot`.
**File:** `gapengine.py`, and the mirror in `bundle/eqls-gap-engine.js`

### The grammar defect that would have shipped with the original patch

**`frenzy` does not take a direct object.** Measured across all 139 unique logs:

```
verb      target begins with        lines
frenzy    "on "                       735   <-- 735 of 735. 100%.
every other verb   <direct object>  12,479   <-- 0 prepositions
```

`[Fri Jul 10 21:25:12 2026] You frenzy on a wan ghoul knight for 43 points of damage.`

The engine's pattern is `^You (verb) (.+?) for (\d+) points of damage\.`, so adding
`frenzy` to the alternation as-is captures the target as **`"on a wan ghoul knight"`**.
Two consequences, and the second is the bad one:

1. Target grouping splits — `"on a wan ghoul knight"` and `"a wan ghoul knight"` are
   two different mobs to the engine.
2. **It reintroduces P-2 for this verb.** The self-hit guard tests
   `target.lower() in SELF_TARGETS`, and `SELF_TARGETS` is `{"yourself"}`.
   `"on yourself"` is not in that set, so a self-frenzy would be counted as an attack
   on a mob — the exact bug P-2 exists to close, re-opened by P-3 on the one verb
   P-3 adds that needs a preposition.

**So the pattern needs `(?:on )?` before the target capture**, not just a wider verb
alternation. This is why the two patches must land together or not at all.

### Filing, re-measured WITHIN a log

The original cadence table compared `claw 2.0s` against a corpus-wide "known AUTO
2-3s" band. That band was pooled across characters, and cadence is not comparable
across characters — Kenkyo's auto-attack runs at 1.0s and its lanes at 4.0s, while
Shara's auto runs at 5.0s and its lanes at 10.0s. A verb must be classified against
the auto and lane cadences **in its own log**.

```
Kenkyo (n=975 melee lines)      auto slash 1.0s | lanes kick 4.0s, backstab 4.0s
   frenzy  6.0s   n=128, 64 gaps    -> LANE
   smite   6.0s   n= 70, 52 gaps    -> LANE

Shara (n=172 melee lines)       auto crush 5.0s | lanes bash 10.0s, kick 10.0s
   cleave 21.5s   n= 20, 10 gaps    -> NOT CLASSIFIED. REFUSED.
```

**`cleave` is counted but not filed.** Ten usable inter-arrival gaps is below the
30-gap floor this engine already enforces on `measured.window.endpoint`; I am not
going to apply a looser standard to a classification than the engine applies to a
sensitivity figure. Count its damage, claim no lane rate, no ceiling.

`frenzy` and `smite` landing as lanes **corroborates `model4.LANE_OWNER` from a
different direction** — that table was built from other evidence and the within-log
cadence agrees without being told. `frenzy` is the Berserker lane (0.72/s in
`model4.LANE_RATE_MAX`) and `smite` the Paladin lane (0.31/s), so for those two
classes the lane analysis is currently blind to the class's signature ability and
reports **no gap because it observes no attempts** — a fail-open silence, and the
worst kind, because it reads as "nothing wrong here".

**Ceilings.** `frenzy 0.72` and `smite 0.31` come from `model4.LANE_RATE_MAX`.
**`cleave` has no ceiling anywhere and must not be given one** — ship it
counted-but-uncapped; `coverage.ceiling_exceeded` already covers a rate the engine
cannot bound.

### What it changes for you — MEASURED on the published numbers, and READ THE SIGN

I told you "up to 20% more melee damage counted". **That is not a statement about any
number a reader sees**, and I should not have handed you a share of first-person melee
damage as if it were the tool's error. `damage_dealt` counts spells too, and the
missing hits also mark *engaged time*, which is the denominator of `dps`.

`recovery.py` runs the same engine twice over each client-written log — as shipped and
with this patch applied in memory — so the two populations are identical by
construction rather than by my reasoning about them:

```
                        dps            damage_dealt      hits    engaged_s
Kenkyo (melee)   101.1 ->  117.9   40,642 ->    47,501   +22.6%    +0.25%
                        +16.62%           +16.88%
Shara  (bard)   1372.9 -> 1357.8  1,182,027 -> 1,182,670  +2.0%    +1.16%
                         -1.10%            +0.05%
Francis                 no change -- log contains none of the three verbs
Shara (short)           no change -- log contains none of the three verbs

RANGE: -1.10% to +16.62% on dps, across the 2 client logs that contain these verbs.
```

**The sign is not constant, and that is the finding.** For a melee character the
missing lines are damage, so the published `dps` is **under**-reported by a sixth. For
a caster the same lines are a rounding error against song damage but they still extend
the engaged window, so recovering them grows the denominator faster than the numerator
and the published `dps` **falls**. Shara counts *more* damage and reports *less* DPS.

So: `19.66% of first-person melee damage is invisible` and `the published dps is wrong
by X` are different quantities with different signs. Only the second is the tool's
accuracy, and it is per-character. Run `recovery.py` yourself before you decide what to
tell a user this patch does.

`auto_attack_attempts`, `melee_seconds` and `lanes` move too, and the `(?:on )?`
widening changes target grouping on every `frenzy` line.

**Evidence:** `verbcensus.py` in this repository — run it yourself, it takes 0.6s and
prints the count of files it opened. `HANDOFF.md` §67 and §69.

---

## What I need from you when you re-pin

1. **Say which of the three you take.** They are independent; P-3 alone is defensible
   if the others complicate the rebuild.
2. **The version.** Your guard asserts exact equality, so name the version you want and
   I will ship that rather than guessing — and I will not bump again without you.
3. **A `cleave` ceiling** — if the rebuild has evidence for one, tell me and I will
   use it. Otherwise `cleave` ships counted-but-uncapped and the engine says so.
   (`reave` is gone from this patch entirely — see the correction in P-3.)
4. **NEW: do you have a capture with `claw` or `reave` in it?** I dropped both because
   every occurrence I could find is in another project's generated fixture. If the
   rebuild has a real client log with either, that is evidence I do not have and I
   will put them back on it.

I cannot message you; the Director carries this both ways. **This file is the artifact
— read it here rather than a summary of it.**
