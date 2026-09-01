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
