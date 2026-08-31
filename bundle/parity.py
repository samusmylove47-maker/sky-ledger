#!/usr/bin/env python3
"""parity.py -- run gapengine.py and the JS bundle over the same log and diff.

Two implementations of one measured mechanic is a witness. I control both, so
this does not test the mechanic -- it tests the PORT, which is where a
transcription error would otherwise sit unseen behind identical-looking output.
"""
import json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gapengine import gap_engine

# DEFAULT IS THE SYNTHETIC LOG, changed 31 Aug. This read
# corpus/corpus/.../jos437-finishing-blow.log, and `corpus/corpus` was a COMMITTED
# SYMLINK to an absolute path carrying this session's own UUID -- it resolved on one
# container and nowhere else. A fresh clone appeared to verify parity while borrowing
# a file from the machine that wrote it, and CI would have gone red on its first run.
# Parity tests the PORT, not the mechanic, so it does not need a real player's log;
# pass one as argv[1] when you have it and want the wider exercise.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures"))
if len(sys.argv) > 1:
    log = sys.argv[1]
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
else:
    from synthetic_log import build
    log = "fixtures/synthetic_log.py (generated)"
    lines = build()
py = gap_engine(lines, {"source": "parity"})

driver = """
const fs=require('fs');
(0,eval)(fs.readFileSync(process.argv[2],'utf8'));
const lines=fs.readFileSync(process.argv[3],'utf8').split(/\\r?\\n/);
process.stdout.write(JSON.stringify(globalThis.EQLSGapEngine.gapEngine(lines,{source:'parity'})));
"""
import tempfile
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
    fh.write(driver); drv = fh.name
import tempfile as _tf
with _tf.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as lf:
    lf.write("\n".join(lines)); logpath = lf.name
js = json.loads(subprocess.run(["node", drv, "bundle/eqls-gap-engine.js", logpath],
                               capture_output=True, text=True, check=True).stdout)
os.unlink(drv); os.unlink(logpath)

def walk(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append(f"{path}.{k}: only in JS")
            elif k not in b: out.append(f"{path}.{k}: only in PY")
            else: out += walk(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): out.append(f"{path}: length PY={len(a)} JS={len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)): out += walk(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: PY={a!r} JS={b!r}")
    return out

d = walk(py, js)

# POSITIVE CONTROL, added 31 Aug. walk() returns [] for two empty dicts, so a
# vacuous report on both sides passes as "agree field for field" -- a negative with
# nothing establishing the instrument could have returned a positive. That is the
# §20 fault, in the harness that is supposed to catch it. Two halves:
#   1. the report is non-trivial, so there is something to disagree about;
#   2. walk() demonstrably reports a difference on this exact input.
import copy
trivial = []
if not py.get("measured", {}).get("dps"): trivial.append("no dps")
if not (py.get("deltas") or py.get("refusals")): trivial.append("no deltas and no refusals")
probe = copy.deepcopy(js)
probe.setdefault("measured", {})["dps"] = "PARITY_CONTROL_SENTINEL"
control = walk(py, probe)
print(f"  log: {os.path.basename(log)}")
if trivial:
    print(f"  CONTROL FAILED: report is vacuous ({', '.join(trivial)}) -- agreement means nothing")
    sys.exit(1)
if not control:
    print("  CONTROL FAILED: walk() cannot report a difference on this input")
    sys.exit(1)
print(f"  positive control: walk() reports {len(control)} difference(s) on a perturbed copy")
print(f"  PY dps={py['measured']['dps']} deltas={len(py['deltas'])} refusals={len(py['refusals'])}")
print(f"  JS dps={js['measured']['dps']} deltas={len(js['deltas'])} refusals={len(js['refusals'])}")
if d:
    print(f"  {len(d)} DIFFERENCE(S):")
    for x in d[:20]: print(f"    {x}")
    sys.exit(1)
print("  PARITY: the two implementations agree field for field.")
