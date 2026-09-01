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

## P-3 — the meter cannot see six of its own damage verbs  ← THE ONE THAT MOVES NUMBERS

**Change:** add `claw` to `AUTO_VERBS`; add `frenzy`, `smite`, `cleave`, `reave` to
`LANE_VERBS` with ceilings; widen `MELEE` and `MISS` accordingly. **Do not add
`shoot`** — see below.
**File:** `gapengine.py`, and the mirror

Measured over **117 logs, 282,615 stamped lines**, with the verb left open:

```
verb      lines    damage    in the regex?
claw      1,052    51,288    NO
frenzy      727    39,498    NO
smite       699    21,219    NO
cleave       62     2,417    NO
reave        30     1,438    NO
shoot         9        78    NO

2,579 lines, 115,938 damage — 19.98% of first-person melee lines
```

58 logs affected. **In two of them, 100% of the character's melee damage is invisible.**
The same six are missing from the `You try to <verb>` pattern, so lane **attempt** rates
are under-counted too.

**And it contradicts the model in the same repository:** `model4.LANE_OWNER` owns six
lanes with rates and means for all six; `gapengine.LANE_CEILING` has four. **`frenzy`
(Berserker, 0.72/s) and `smite` (Paladin, 0.31/s) are in the model and invisible to the
meter** — for those two classes the lane analysis is blind to their signature ability
and reports no gap because it observes no attempts.

**Filing is measured, not guessed**, because a misfiled verb corrupts a denominator,
which is worse than the gap. Inter-arrival medians:

```
known AUTO   slash 2.0s   pierce 2.0s   punch 2.0s   crush 3.0s
known LANE   strike 4.0s  backstab 5.0s  bash 5.0s   kick 5.0s
─────────────────────────────────────────────────────────────
claw   2.0s  -> AUTO        frenzy 6.0s  -> LANE
smite  9.0s  -> LANE        reave 10.5s  -> LANE
cleave 26.0s -> LANE
shoot        -> n < 20. REFUSED, not classified. Archery is plausibly its own lane and
                9 lines is not enough to say. Leave it out; it is 78 damage.
```

`frenzy` and `smite` landing as lanes **corroborates `model4.LANE_OWNER` from a
different direction** — that table was built from other evidence and the cadence
measurement agrees without being told.

**A ceiling is still needed for the four new lanes.** `model4.LANE_RATE_MAX` has
`frenzy 0.72` and `smite 0.31`; **`cleave` and `reave` have none anywhere**, so either
ship them as counted-but-uncapped (no gap claimed) or leave the ceiling absent — the
engine already records `coverage.ceiling_exceeded` and refuses a rate it cannot bound.
**Do not invent a ceiling for them.**

**What it changes for you:** `damage_dealt`, `dps`, `hits_counted`,
`auto_attack_attempts`, `melee_seconds` and `lanes` all move on any log containing
these verbs — **up to 20% more melee damage counted**. This is the only one of the
three that changes a number a reader sees.

**Evidence:** `HANDOFF.md` §67.

---

## What I need from you when you re-pin

1. **Say which of the three you take.** They are independent; P-3 alone is defensible
   if the others complicate the rebuild.
2. **The version.** Your guard asserts exact equality, so name the version you want and
   I will ship that rather than guessing — and I will not bump again without you.
3. **`cleave` and `reave` ceilings** — if the rebuild has evidence for either, tell me
   and I will use it. Otherwise they ship uncapped and the engine says so.

I cannot message you; the Director carries this both ways. **This file is the artifact
— read it here rather than a summary of it.**
