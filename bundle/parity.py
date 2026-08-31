#!/usr/bin/env python3
"""parity.py -- run gapengine.py and the JS bundle over the same log and diff.

Two implementations of one measured mechanic is a witness. I control both, so
this does not test the mechanic -- it tests the PORT, which is where a
transcription error would otherwise sit unseen behind identical-looking output.
"""
import json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gapengine import gap_engine

log = sys.argv[1] if len(sys.argv) > 1 else "corpus/corpus/everquest-companion/tests/fixtures/jos437-finishing-blow.log"
lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
py = gap_engine(lines, {"source": "parity"})

driver = """
const fs=require('fs');
(0,eval)(fs.readFileSync(process.argv[2],'utf8'));
const lines=fs.readFileSync(process.argv[3],'utf8').split(/\\r?\\n/);
process.stdout.write(JSON.stringify(globalThis.EQLSGapEngine.gapEngine(lines,{source:'parity'})));
"""
open("/tmp/_drv.js", "w").write(driver)
js = json.loads(subprocess.run(["node", "/tmp/_drv.js", "bundle/eqls-gap-engine.js", log],
                               capture_output=True, text=True, check=True).stdout)

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
print(f"  log: {os.path.basename(log)}")
print(f"  PY dps={py['measured']['dps']} deltas={len(py['deltas'])} refusals={len(py['refusals'])}")
print(f"  JS dps={js['measured']['dps']} deltas={len(js['deltas'])} refusals={len(js['refusals'])}")
if d:
    print(f"  {len(d)} DIFFERENCE(S):")
    for x in d[:20]: print(f"    {x}")
    sys.exit(1)
print("  PARITY: the two implementations agree field for field.")
