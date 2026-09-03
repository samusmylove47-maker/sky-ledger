# Damage-family boundary for Session D — and the coordination mechanism already exists

**Session E, 3 Sep 18:39Z.** `handover/TO-SESSION-D-damage-boundary.md`,
`samusmylove47-maker/sky-ledger @ claude/eq-legends-class-analysis-q68111`, **not on
`master`**. The Director convened this; D is local and reads what the Director carries.

## The short version

**D can widen most of it freely, starting now, and the recalibration cannot be silent
because it is already gated.** I proved that rather than asserting it — see the bottom.

## What actually couples us, measured

**One file of mine reads anything D produces:** `residual.py`, against
`assets/raids-measured.json`. Everything else I publish — the gap engine, the DPS meter,
`verbcensus`, `recovery`, `simulate` — parses log files directly and is **completely
untouched by anything D does to its regexes.**

`residual.py` computes, per record:

```
measured DPS  =  damage_low  x  our_damage_share_pct  /  seconds  /  distinct observers
```

Two of those four terms come from D's parse, and **they behave completely differently
under widening**, which is where the boundary is:

```
damage_low   MONOTONE. A regex can only ADD matches, never remove them, so this can
             only go UP. And 143 of 213 records already carry damage_is_floor: TRUE.
share        NOT MONOTONE. It is our damage over total damage, both from D's parse.
             Widening moves the numerator, the denominator, or both, in either
             direction -- and it MULTIPLIES straight into the published figure.
```

## The boundary

### GREEN — widen freely, tell nobody, I will see it

**Any family that adds damage attributed to a NAMED actor, where the affected records
carry `damage_is_floor: true`.** That is **143 of 213** records.

A floor rising is a floor doing its job. My ratio moves monotonically toward
conservatism — measured goes up, so model-over-measured goes down, so **every gap claim I
publish gets smaller, never larger.** Nothing I have published is falsified by a floor
tightening; that is what declaring it a floor was for.

### AMBER — widen, and name the records; I re-run one command

**Any family touching the 70 records with `damage_is_floor: false`.** There the figure is
asserted complete, so a rise contradicts the assertion rather than tightening it. The fix
is cheap — `python3 residual.py` and I republish — but it is a correction, not a
tightening, and it should be labelled as one.

**Sharpest sub-case: the 5 records that are `gold: share == 100%` AND not floor-marked.**
Those are the only ones where I claim both completeness and full attribution. Any widening
there directly falsifies a published figure.

### RED — do not widen without a coordinated re-measure

**1. Anything that moves `our_damage_share_pct`.** It is a ratio of two D-parsed
quantities and it multiplies into every published DPS. Median across the corpus is
**24.1%** (range 2–100), so most figures are already dominated by this term. Adding
damage for OTHER players lowers our share; newly attributing damage to ours raises it.
**Both directions, unbounded, straight into the output.**

**2. Anything that adds damage with NO named owner** — unattributed damage shields,
environmental, ticks with no actor. That inflates the **denominator** of `share` with
nothing in the numerator, so it lowers every figure of mine **for a reason that is a
parsing artifact rather than a fact about the fight.** This is the one I would most like
D to hold, and it is a small class.

## AND THE RECALIBRATION CANNOT BE SILENT — I PROVED IT

The Director's stated trade was *"I would rather D widen nothing and know why, than widen
correctly and leave your figures silently recalibrated."*

**In this case that trade is not needed, because the silence it fears is already
impossible.** `residual.py` pins the dataset:

```
DATA_SHA256 = "11823ae7b43509fe..."   DATA_BYTES = 207239   DATA_RECORDS = 213
```

I modified one record's `damage_low` by +1000 and ran the check:

```
residual.py --check  ->  EXIT 1
[FAIL] the dataset is present and its bytes DO NOT MATCH the pin. Every figure
downstream is a function of these bytes; a human decides whether the published
numbers move.
```

Then restored it and confirmed the tree clean. **`residual.py` is in `check.sh` twice, so
the moment D regenerates that dataset my suite goes red with a message that already says a
human decides.** That is the coordination mechanism, it predates this conversation, and it
fires.

## So I would argue with the trade, in one direction only

**"Absent and declared beats present and unaccounted" is right, and it does not apply to
the 143 floor-marked records — because `damage_is_floor` IS the accounting.** Holding
those back does not preserve a true figure; it preserves a knowingly-low one while a
better one exists. The declaration was made precisely so the number could improve without
anyone being misled.

**Where the trade IS right: the RED class.** Unowned damage moving a share is present-and-
unaccounted in exactly the sense meant, and I would rather D hold it indefinitely than
widen it and have me discover it as a shifted number.

## What I need from D, and it is one thing

**When you widen, say which of the three classes it lands in, and for AMBER give me the
record ids.** Not a merged parser, not a review — a label. My pin will catch the change
either way; the label is what turns a red suite into a five-minute re-run instead of an
investigation.

---

*Session E, 3 Sep 18:39Z. Every figure above is read out of the committed dataset at run time:
213 records, 143 floor-marked, 70 not, 19 at 100% share, 5 both. `residual.py` prints all
of it.*
