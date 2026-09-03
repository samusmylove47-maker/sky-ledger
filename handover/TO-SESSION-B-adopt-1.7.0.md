# Adoption instructions for Session B — EQLSGapEngine 1.7.0

**Session E, 3 Sep 18:39Z.** Written for a session that cannot ask a follow-up question, so
every step is literal and every check is one you run yourself.

## THE DIRECTOR'S RECORD IS STALE. THE CURRENT STATE IS:

```
                        Director's record        ACTUAL, now
version                 1.6.0                    1.7.0
bundle hash             1c3a6701                 7ffb2a6d
gates                   28                       29
declared patches        five (P-1..P-5)          SIX (P-1..P-6)
```

**P-6 shipped after that record was written.** It came from Session C's finding that which
`You <verb>` forms a log contains is a property of the logging character's classes. Nothing
in the earlier record is wrong about P-1..P-5; it is one version behind.

## What to pin

```
file    bundle/eqls-gap-engine.js
copy    bundle/eqls-gap-engine.7ffb2a6d.js      (byte-identical, hash in the name)
bytes   38499
sha256  7ffb2a6d72634172ed6b17edbdf972c38db93f378244df21a087b3fa6dd78c0c
version EQLSGapEngine reports "1.7.0"
```

## The literal steps

```sh
# 1. fetch the branch and take the bundle
git fetch origin claude/eq-legends-class-analysis-q68111
git show origin/claude/eq-legends-class-analysis-q68111:bundle/eqls-gap-engine.js > <your vendored path>

# 2. VERIFY THE BYTES BEFORE TRUSTING ANYTHING ELSE
sha256sum <your vendored path>
# must print: 7ffb2a6d72634172ed6b17edbdf972c38db93f378244df21a087b3fa6dd78c0c
wc -c <your vendored path>
# must print: 38499

# 3. update the contract assertion
#    handover/gap-contract.b-*.json field  assertedEngineVersion
#    "1.4.0"  ->  "1.7.0"
```

## How to verify the pin took, without asking me

**Your own guard is the check.** Your contract asserts
`EQLSGapEngine.version === assertedEngineVersion` EXACTLY, and refuses a newer engine as
readily as an older one. So:

1. **Before** you change the assertion, load 1.7.0 against a contract still saying
   `1.4.0`. **Your guard must REFUSE.** If it does not refuse, the guard is not running
   and the pin is meaningless — stop there and report that, not the version bump.
2. **Then** set the assertion to `1.7.0` and load again. It must accept.

**That is a matched pair and it is the only proof that matters:** a guard that has not
been seen to refuse has not been seen to work.

## What moves when you adopt — the only question that costs you time

**ONE of the six changes a published figure. Five do not.**

```
        changes a computed value?   you must re-verify?
P-1     no  (a refusal becomes an assertion, on no real log)     NO
P-2     yes in principle, measured ZERO across 139 logs          NO
P-3     *** YES ***                                             *** YES ***
P-4     no  (one string is longer)                              NO
P-5     no  (one new list appears)                              NO
P-6     no  (two new keys under coverage)                       NO
```

**P-3, measured by running the same engine twice over the same log so the populations
match by construction:**

```
Kenkyo (melee)   dps  101.1 ->  117.9    the OLD figure was 16.62% TOO LOW
Shara  (bard)    dps 1372.9 -> 1357.8    the OLD figure was  1.10% TOO HIGH
```

**Read the sign. It is not one direction.** A missing hit is not only missing damage, it
is a missing SECOND: `dps` divides by engaged time and engaged runs are built out of hits,
so recovering a hit adds to the numerator *and* the denominator, in a ratio that depends
on how melee-heavy the character is. **There is no single "the meter was X% wrong" you can
print.** Recompute per character.

**The Director's record on this is correct and it was a correction of a convenient
sentence of mine.** I had written that all the held patches were conservative failures.
That was false for P-3 and I corrected it before it was relied on.

## New keys you will render

```
coverage.verbs_unclassified.verbs                 [ ... ]   verbs counted, filed as nothing
coverage.verbs_unclassified.blocks_lane_rates     true|false
measured.dps_window_note                          longer: says damage shields are excluded
```

`blocks_lane_rates: true` means **every `per_melee_second` below it is null because the
character's only melee verbs are ones the engine counts but does not file as
auto-attacks** — not because they had no melee time. Those are different facts and the
null looked identical for both until 1.7.0.

---

*Session E, 3 Sep 18:39Z. `check.sh` PASS 29 gates, `check_fresh.sh` PASS, parity PASS on LF
and CRLF, round-trip 700/700 exact. The full per-patch reasoning is in
`handover/TO-SESSION-B-tuesday.md`.*
