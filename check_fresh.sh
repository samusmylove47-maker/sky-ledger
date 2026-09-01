#!/bin/sh
# check_fresh.sh -- does this repository work on a machine that is not this one?
#
# NOT IN check.sh, on purpose: it clones, it needs the network for the weapon shards,
# and it takes ~40s. It is the release check, and it exists because three separate
# faults on 1 Sep 2026 were invisible to every in-tree gate:
#
#   §58  residual.py's dataset lived at an absolute scratchpad path, committed nowhere,
#        and the published 4.59x ratio rested on it
#   §59  making that absence tolerable in residual.py left it FATAL one import
#        downstream, in sensitivity.py, at module scope
#   §60  model4.py hard-coded REPO="/home/user/sky-ledger", so a clone with ZERO shards
#        of its own loaded 515 weapons and 1,973 spells FROM ANOTHER TREE -- while
#        fetch_shards.py fetched the shards INTO the clone and verified them against
#        their pins. A gate verifying bytes the consumer never read.
#
# THE LESSON THIS FILE ENCODES: it is not enough to clone fresh on the machine that
# HAS the files. The container-local dependency has to be REMOVED for the clone to be
# a test of anything. Every step below either removes one or proves it was removed.
#
# PROVEN ABLE TO FAIL, not merely written. The third arm was run against the PRE-FIX
# model4.py recovered from git at 1e028355, in a clone with its data files deleted:
#
#     IMPORTED -> REPO = /home/user/sky-ledger
#     weapons 515  spells 1973  - all from another tree
#
# The arm reports IMPORTED as a failure, so it fires on the exact defect it was written
# for. A guard is not a gate until something fails because of it.
#
#     sh check_fresh.sh
set -e
SRC=$(cd "$(dirname "$0")" && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0

echo "== cloning $SRC at HEAD into a directory that is not it =="
git -C "$SRC" rev-parse --short HEAD
git clone -q "$SRC" "$TMP/clone"
cd "$TMP/clone"

# POSITIVE CONTROL FIRST, and it is the one that matters. If the clone silently landed
# in the source tree, every check below would pass and prove nothing -- which is
# precisely how §60 stayed hidden. Establish the clone is elsewhere before trusting it.
echo "== control: the clone must NOT be the source tree =="
HERE=$(pwd -P)
if [ "$HERE" = "$SRC" ]; then
  echo "  CONTROL FAILED: the clone resolved to the source tree. Nothing below means anything."
  exit 1
fi
echo "  ok   clone at $HERE, source at $SRC"

echo "== the full suite, with the raid dataset made UNREACHABLE =="
# Absence must be DECLARED and non-fatal. If this goes red, absence is fatal
# somewhere -- which is exactly what §59 found one import downstream of the fix.
if EQLS_RAIDS_MEASURED=/nonexistent/removed-on-purpose.json sh check.sh > "$TMP/suite.log" 2>&1; then
  echo "  ok   check.sh PASS with the dataset gone"
  grep -c 'ABSENT' "$TMP/suite.log" > /dev/null && echo "  ok   and the absence was DECLARED, not silent"
else
  echo "  FAILED: check.sh is red when a container-local file is absent. Tail:"
  tail -20 "$TMP/suite.log" | sed 's/^/      /'
  fail=1
fi

echo "== the clone must read ITS OWN data files, not the source tree's =="
# Delete the clone's data and assert the import FAILS naming the CLONE's path. A
# success here means some module is reaching into another tree, which is §60 exactly.
rm -f sh-*.json spells.json
out=$(python3 -c "
import sys; sys.path.insert(0, '.')
try:
    import model4
    print('IMPORTED')
except FileNotFoundError as e:
    print('FAILED_ON', e.filename)
" 2>&1 || true)
case "$out" in
  IMPORTED*)
    echo "  FAILED: model4 imported with this clone's data files deleted."
    echo "          It is reading another tree. Every weapon and spell figure it"
    echo "          publishes came from somewhere other than this checkout."
    fail=1 ;;
  FAILED_ON*"$TMP"*)
    echo "  ok   model4 failed on THIS clone's path, so it reads its own tree" ;;
  *)
    echo "  FAILED: unexpected result -- $out"
    fail=1 ;;
esac

echo
if [ "$fail" -ne 0 ]; then
  echo "FRESH-CLONE CHECK FAILED. This repository does not work on a machine that is not this one."
  exit 1
fi
echo "FRESH-CLONE CHECK PASSED: clone elsewhere, dataset absent, own data files only."
