#!/bin/sh
# check.sh — the single named entry point for this repository's checks.
#
# HONEST LABEL, per Session D: "A GUARD IS NOT A GATE UNTIL SOMETHING FAILS
# BECAUSE OF IT." Until this script is invoked by something other than a human
# deciding to invoke it, derived_check.py is a GUARD. This repository has no CI
# — established by listing every root entry on both refs, not by grepping for
# the configs I could think of (Session C's correction).
#
# It becomes a GATE in exactly one place, and that place is not built yet:
# inside gapEngine(), where HANDOFF.md §21.6 puts it. There, a claim that fails
# cannot reach a caller, because the engine will not emit it.
set -e
# set -o pipefail is not POSIX sh; emulate its effect by never piping a check.
# D measured this defect on 30 Aug: `cmd | head -3; echo $?` reports head's status,
# not cmd's, and `set -e` does not stop a failing pipeline. This script contains no
# pipelines for exactly that reason. If you add one, capture the status explicitly.
fail=0
echo "== derived-claim validator: self-test (must reject all bad claims) =="
python3 derived_check.py --selftest || fail=1
echo
echo "== derived-claim validator: the committed claims =="
python3 derived_check.py derived || fail=1
echo
echo "== reproducers must still run =="
for f in handmod.py validate_jos437.py; do
  printf '  %-24s ' "$f"
  if python3 "$f" >/dev/null 2>&1; then echo ok; else echo FAILED; fail=1; fi
done
echo "== the shipped bundle must obey BUNDLE-CONTRACT section 3 =="
node bundle/check-bundle.js || fail=1
echo
echo "== the JS bundle and the Python engine must agree field for field =="
python3 bundle/parity.py corpus/corpus/everquest-companion/tests/fixtures/jos437-finishing-blow.log || fail=1
echo
echo "== the fixture must not drift from what the engine emits =="
python3 - <<'DRIFT' || fail=1
import json, subprocess, sys
subprocess.run([sys.executable, "fixtures/make_fixture.py"], check=True, capture_output=True)
fx = json.load(open("fixtures/sample-report.json"))
rp = json.load(open("fixtures/real-report-shara.json"))
fk = set().union(*[set(d) for d in fx["deltas"]]) if fx["deltas"] else set()
rk = set().union(*[set(d) for d in rp["deltas"]]) if rp["deltas"] else set()
bad = False
if fk != rk:
    print(f"  DRIFT in delta keys: {fk ^ rk}"); bad = True
if set(fx["measured"]) - {"_register"} != set(rp["measured"]):
    print(f"  DRIFT in measured keys: {set(fx['measured']) ^ set(rp['measured'])}"); bad = True
print("  fixture shape matches engine output" if not bad else "  A PAGE BUILT ON THIS FIXTURE WOULD RENDER THE WRONG FIELDS")
sys.exit(1 if bad else 0)
DRIFT
echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED. Nothing ships."
  exit 1
fi
echo "All checks pass. Note: passing here prevents nothing on its own — see the"
echo "header. This is a guard until the engine calls the validator in-process."
