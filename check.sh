#!/bin/sh
# check.sh — the single named entry point for this repository's checks.
#
# HONEST LABEL, per Session D: "A GUARD IS NOT A GATE UNTIL SOMETHING FAILS
# BECAUSE OF IT."
#
# UPDATED 31 Aug 2026. The line above said "this repository has no CI", and that
# was true when it was written and is not now. PR #1 merged, master became the
# front door, and .github/workflows/check.yml runs this script on every push and
# pull request against a FRESH CLONE. So this is a gate for anything arriving by
# pull request. It is still a guard for a human running it locally.
#
# It becomes a gate in one further place, not built yet: inside gapEngine(),
# where HANDOFF.md §21.6 puts it. There, a claim that fails cannot reach a
# caller, because the engine will not emit it.
#
# The CI job runs every --selftest BEFORE this script, so a suite that cannot
# fail is caught before its passing verdict is trusted.
set -e
# set -o pipefail is not POSIX sh; emulate its effect by never piping a check.
# D measured this defect on 30 Aug: `cmd | head -3; echo $?` reports head's status,
# not cmd's, and `set -e` does not stop a failing pipeline. This script contains no
# pipelines for exactly that reason. If you add one, capture the status explicitly.
fail=0
echo "== the three weapon shards must be present and match their pins =="
# FIRST, because everything below that touches a weapon depends on them and they
# are NOT COMMITTED. Measured 31 Aug on a fresh clone: check.sh failed here with
# FileNotFoundError, having passed for days on an untracked file that happened to
# sit on one container's disk. See fetch_shards.py's header.
# FETCH FIRST, then self-test. Measured on a fresh clone 31 Aug: running the
# self-test first fails, because its final assertion reads shards that do not
# exist yet. A gate whose own proof depends on the state it is about to create.
python3 fetch_shards.py || fail=1
python3 fetch_shards.py --selftest || fail=1
echo
echo "== every file the README points a reader at must exist =="
python3 check_readme.py --selftest || fail=1
python3 check_readme.py || fail=1
echo
echo "== derived-claim validator: self-test (must reject all bad claims) =="
python3 derived_check.py --selftest || fail=1
echo
echo "== derived-claim validator: the committed claims =="
python3 derived_check.py derived || fail=1
echo
echo "== reproducers must still run =="
# A reported the inverse fault on 31 Aug: a check branch that FIRED AND REPORTED
# NOTHING, so the session that tripped it debugged the wrong repository. This loop
# had a milder form of it -- it discarded stdout and stderr, so a failing reproducer
# printed the word FAILED and no reason. On failure the output is now shown.
# verify_upgrade.py takes --fast here (56 of 560 trios, ~12s vs ~2min). Stated, not
# silent: the script prints which mode it ran and the full proof is one flag away.
for f in "handmod.py" "validate_jos437.py" "verify_upgrade.py --fast"; do
  printf '  %-24s ' "$f"
  out=$(python3 $f 2>&1) && echo ok || {
    echo "FAILED -- its output follows, so you debug YOUR file and not this script:"
    echo "$out" | sed 's/^/      /'
    fail=1
  }
done
echo
echo "== my scanner must still cover the contract I ship against =="
python3 bundle/check-contract.py --selftest || fail=1
python3 bundle/check-contract.py || fail=1
echo
echo "== the bundle's bytes must be what this tree says they are =="
python3 bundle/check-integrity.py --selftest || fail=1
python3 bundle/check-integrity.py || fail=1
echo "== the shipped bundle must obey BUNDLE-CONTRACT section 3 =="
node bundle/check-bundle.js || fail=1
echo
echo "== B's hand-written contract for the measured block must be satisfied =="
python3 check_contract.py --selftest || fail=1
python3 check_contract.py || fail=1
echo
echo "== no committed file may hard-code an absolute path outside itself =="
# Added 1 Sep. model4.py carried REPO="/home/user/sky-ledger" and a fresh clone with
# ZERO shards of its own imported it and loaded 515 weapons and 1,973 spells -- all
# from that path. fetch_shards.py fetches the shards INTO THE CLONE and verifies them
# against their pins, and model4 then read a different copy: a gate verifying bytes the
# consumer does not use, green on both machines for days.
python3 check_paths.py --selftest || fail=1
python3 check_paths.py || fail=1
echo
echo "== the Director's raid dataset must be pinned, and its absence must be LOUD =="
# Added 1 Sep. residual.py's default data path was an absolute scratchpad path
# carrying ONE SESSION'S UUID, and the file is committed nowhere -- so the published
# 4.59x ratio and the 71.9 DPS measured median rested on a file that exists on one
# container. That is fetch_shards.py's fault, still live in two more files.
# ABSENT exits 0 on purpose: nothing on a fresh clone can restore a file with no
# source, and a suite that is red for a reason nobody can fix teaches its reader to
# ignore it. DRIFTED is fatal -- substituted bytes silently move every figure.
python3 residual.py --check || fail=1
echo
echo "== every model input NO log can supply must be swept, or declared unsweepable =="
# The list is IMPORTED from percharacter.INPUTS, never retyped, so adding an ASSUMED
# input to the audit demands a sweep here. The full sweep is minutes and has no place
# in a 13-second suite; this arm is the list agreement only.
python3 sensitivity.py --check --selftest || fail=1
echo
echo "== ROUND-TRIP: build a log from known parameters, recover them, measure the error =="
# Added 1 Sep. 50 generated logs, parameters chosen before the engine sees them.
# It tests the ARITHMETIC and the EXCLUSIONS, not the grammar -- the generator writes
# lines in the shape the parser reads, so a line the real client writes differently is
# invisible in both directions. That question is answered by the 117 REAL logs, not
# here. It found a live defect on its first run (D-6) and that row is DECLARED, so the
# suite stays green on a known gap while any UNDECLARED failure is fatal.
python3 simulate.py --selftest || fail=1
python3 simulate.py || fail=1
echo
echo "== the per-character audit must classify every model input, and refuse below n=30 =="
# Added 1 Sep. Critical-path task 2, and deliberately the AUDIT rather than a fitted
# per-character model: pointing model4 at a real log found that the log does not carry
# most of what the model needs. This reports each input as OBSERVED / REFUSED /
# ASSUMED and suppresses any observed-vs-model ratio whose precondition -- the stance
# -- is not established.
python3 percharacter.py --selftest || fail=1
python3 percharacter.py || fail=1
echo
echo "== the MAKE ME BIS ranker must enforce every ruling it was built to =="
python3 rank.py --selftest || fail=1
echo
echo "== every number in the measured block must name the population it is over =="
# Added 1 Sep. `measured` carried THREE populations in one block with no labels --
# in_window (dps, damage_dealt), all_lines (spells_landed, resists, crit_rate) and
# melee_time (lanes) -- so a consumer combining two got a share of nothing. B's
# contract names the exact division: sum(spells_landed[*].damage_total) over
# damage_dealt gives 202% on the log this engine was built against, 324% on the
# short one. No value moved; the report now states its populations and publishes
# the totals, and this fails if a new key is added without declaring one.
python3 check_window.py --selftest || fail=1
python3 check_window.py || fail=1
echo
echo "== every timestamp pattern in this tree must accept a space-padded day =="
# Added 1 Sep. A fixed-width day discards the line BEFORE any parse, where nothing
# downstream can report it. Two hand-sweeps for this fault ran the same day and both
# were defective -- one returned zero everywhere, mine matched a literal and missed
# amp.py. So this does not grep for a shape: it EXTRACTS every timestamp regex and
# RUNS it against a space-padded line.
python3 check_timestamps.py --selftest || fail=1
python3 check_timestamps.py || fail=1
echo
echo "== a self-hit must never reach damage_dealt, in either engine =="
# Added 1 Sep, relayed by D and CHECKED rather than accepted. A self-hit written
# without a `by <spell>` clause cannot match the SPELL shape and fell through to
# MELEE, where there was no guard -- emitted as ordinary OUTGOING damage. Zero
# instances in 189,460 lines, so the corpus CANNOT test it: the input is crafted and
# the file carries its own positive control.
python3 check_selfhits.py --selftest || fail=1
python3 check_selfhits.py || fail=1
echo
echo "== the unconditional refusals must survive ANY input, in both engines =="
# Added 31 Aug. gap_engine([]) returned `refusals: []` because both engines built
# the list AFTER the `if not hits` early return -- so the engine went silent about
# what it refuses exactly when it knew least, including a privacy refusal whose own
# text reads "refused in all cases".
python3 check_refusals.py --selftest || fail=1
python3 check_refusals.py || fail=1
echo
echo "== the unreported-findings index must still be true of the tree =="
# Added 1 Sep under R74. An index of findings is an artifact nothing produces --
# the exact shape that went stale inside the drift gate for a day. Each row cites a
# VERBATIM FRAGMENT and this fails when the fragment is gone.
python3 check_unreported.py --selftest || fail=1
python3 check_unreported.py || fail=1
echo
echo "== every outbound document must be reachable from the watched file =="
# Added 1 Sep, and it is NOT my finding. Session 0 described the new Auditor's failure:
# FIVE communications went into five NEW files while the watched file sat untouched --
# a full day of output invisible, and the session did not know, because it had been told
# a file was watched but never which one.
# I went to answer and found the same defect here. TO-SESSION-C-mailbox.md and
# TO-SESSION-C-verb-census.md were named ZERO times in HANDOFF.md, and my attempt to
# message C about them FAILED, so they reached C only if C happened to browse.
# A WATCHED FILE IS AN ADDRESS, NOT A CONTAINER. Store anywhere; name it in the address,
# or it does not exist to a reader following the only path they were given.
python3 check_reachable.py --selftest || fail=1
python3 check_reachable.py || fail=1
echo
echo "== the peer mailbox must carry a poll record, and name files that exist =="
# Added 1 Sep. Session C reaches me by SendMessage; I cannot call it (verified: the
# cloud credential is refused for cross-session delivery). Git already carries the
# content -- two full rounds in an hour, zero content failures. What failed was
# ADDRESSING: I named `master` for a file that was on a branch 60 commits ahead, and C
# would have fetched an empty ref with no way to tell that from my never having
# written. So every open message must name a file that EXISTS ON THE BRANCH THE
# MAILBOX DECLARES.
# The poll verdict is a closed set including UNREACHABLE, which is the point of the
# field: a failed look recorded as "nothing new" is an instrument reporting on a look
# it never took. UNREACHABLE passes as readily as NOTHING-NEW, for the same reason
# HELD passes check_holds.py.
# Hermetic only -- `mailbox.py --poll` touches the network and is never a gate.
python3 mailbox.py --selftest || fail=1
python3 mailbox.py || fail=1
echo
echo "== a claim about the distance between two moving refs must be recomputed =="
# Added 1 Sep. My STATUS block said "my branch is an ancestor of master, 0 commits
# ahead". True the day it was written, stale on the next push, and it kept asserting
# itself through sixty commits -- until I read it and, on its authority, told Session C
# that the reply I had written for C was on master. IT WAS NOT. C would have fetched
# master, found nothing, and had NO WAY TO TELL THAT FROM MY NEVER HAVING WRITTEN IT:
# a false negative that reads exactly like silence.
# The claim is a FLOOR because `origin/master..HEAD` counts the commit being written,
# so an exact number would have to predict its own commit. FAIL-CLOSED: an unresolvable
# base ref REFUSES, because an instrument reporting "fine" when it could not look is
# the fault this repository has caught more than any other.
python3 check_refclaims.py --selftest || fail=1
python3 check_refclaims.py || fail=1
echo
echo "== no document may claim a time that has not happened yet =="
# Added 1 Sep on a clock tick, because between 16:01Z and 16:25Z I wrote TWELVE
# timestamps into this tree -- the Director's polled channel, B's handover, and two
# shipped Python files -- dated 16:30Z through 18:05Z. All in the future. I estimated
# elapsed time from how much work I had done instead of running `date`, in the same
# four commits whose subject lines are about not asserting unsourced values.
# A timestamp is a number. Fault shape (8): having the measurement and not reading it.
# It fired on its own self-test fixtures on the first run -- a true positive on a
# false target, exactly as check_timestamps.py did -- so the exemption is asserted at
# an EXACT count in both directions rather than capped: a cap raised whenever it binds
# is not a cap, and skipping this file would blind the scanner to itself.
python3 check_timeclaims.py --selftest || fail=1
python3 check_timeclaims.py || fail=1
echo
echo "== measuring a held patch must not leak it into the shipped engine =="
# recovery.py runs the engine TWICE -- as shipped and with P-3's verb set widened in
# memory -- so the two populations are identical by construction rather than by my
# reasoning about them. That makes it a tool that PATCHES THE LIVE ENGINE, which is
# only safe if the patch cannot escape: the self-test asserts the constants are back
# after a normal run AND after the engine raises mid-patch, and then BREAKS the leak
# detector on purpose to prove it can fail. Hermetic; the corpus run is not a gate.
python3 recovery.py --selftest || fail=1
echo
echo "== the verb census must find a verb no hand-written list contains =="
# Added 1 Sep. The finding it exists for was measured BY HAND over a population I
# never inspected: 416 log files, of which 277 were duplicate copies and only 5
# carried the name the EverQuest client writes. Two of the six "missing verbs" I was
# about to ship had ZERO occurrences outside other projects' generated fixtures.
# A share is only a share against the population its numerator came from, and a
# measurement with no script is one nobody can re-run to find that out.
# Only the SELF-TEST runs here: it is hermetic (tempfile), while the census itself
# reads a corpus outside this repository and must never become a gate that a fresh
# clone cannot satisfy.
python3 verbcensus.py --selftest || fail=1
echo
echo "== the engine's non-pattern conditions must still be load-bearing =="
# Added 3 Sep. Session C audited this engine by TRANSLITERATING it -- preserving "the four
# patterns and the match order verbatim" -- and reported a defect that does not exist,
# because the guard that prevents it is an `if` AFTER the match, outside every pattern.
# TRANSLITERATING AN IMPLEMENTATION PRESERVES ITS PATTERNS AND LOSES EVERYTHING THAT IS
# NOT ONE. So this answers "what else?" by MEASUREMENT, since reading is the instrument
# that failed: it disables each non-regex condition and reports which published fields
# move. 9 of 10 are load-bearing, and none is visible in a regex.
# It patches the live engine, so the self-test proves every constant is restored AND
# breaks its own leak detector to show that check can fail.
python3 conditions.py --selftest || fail=1
python3 conditions.py > /dev/null || fail=1
echo
echo "== every LIVE item in the Director channel must carry an end condition =="
# Added 3 Sep on the Director's ruling. Asked for a status report, I checked the list
# instead of recalling it and found FOUR items marked [OPEN] that were all closed -- one
# for eleven hours after its substance was settled. The retirement-arm fault in my own
# outbound, on the day I built retirement arms for five other mechanisms: section 79
# enumerated six declaration mechanisms and DID NOT INCLUDE THE D-LIST. I checked the
# instruments and not the inbox.
# The closed set is a CONTRACT -- the Director binds itself to this vocabulary when it
# rules. PATCH-READY and GATE-EXISTS are evaluated; AWAITING-RULING, SEQUENCED and
# ADVISORY are honest UNCHECKABLEs, legal and COUNTED, because a channel where every item
# is unverifiable satisfies every other check and is worth nothing.
python3 check_dclaims.py --selftest || fail=1
python3 check_dclaims.py || fail=1
echo
echo "== every withheld patch must be declared, with a ground from a closed set =="
# Added 1 Sep. A claim that STOPS work does not announce itself the way a claim that
# starts work does. Four items were held in this tree; ONE was in a machine-checked
# closed set (REPIN NEEDED) and three were prose in commit bodies, visible to no
# instrument. The GROUND is a closed set for the same reason the state is: I held
# these three for nine hours on "B is offline", which was false the whole time and
# which my own hourly output refuted. Availability is not a legal ground.
# HELD is a PASSING state on purpose -- a gate that punishes an honest hold teaches
# its author to delete the declaration to get green.
python3 check_holds.py --selftest || fail=1
python3 check_holds.py || fail=1
echo
echo "== the JS bundle and the Python engine must agree field for field =="
python3 bundle/parity.py || fail=1
echo
echo "== the fixture must not drift from what the engine emits =="
# WIDENED 31 Aug. The version here until tonight compared DELTA KEYS and MEASURED
# KEYS -- two of the five structures a consumer renders -- and then printed
# "fixture shape matches engine output". Refusals, coverage and the top-level key
# set went unchecked, and refusals are exactly the fields A renders and exactly
# where A found a false count the same night. Matched-pair proven: adding a
# `severity` key to every refusal in the engine left the old gate saying "matches".
# A's shape, in my tree -- the right answer in the wrong words, read for the verdict.
python3 fixtures/check_drift.py --selftest || fail=1
python3 fixtures/check_drift.py || fail=1
echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED. Nothing ships."
  exit 1
fi
echo "All checks pass. Note: passing here prevents nothing on its own — see the"
echo "header. This is a guard until the engine calls the validator in-process."
