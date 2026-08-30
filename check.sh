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
echo
if [ "$fail" -ne 0 ]; then
  echo "FAILED. Nothing ships."
  exit 1
fi
echo "All checks pass. Note: passing here prevents nothing on its own — see the"
echo "header. This is a guard until the engine calls the validator in-process."
