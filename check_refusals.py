#!/usr/bin/env python3
"""check_refusals.py -- the unconditional refusals must survive ANY input.

Found 31 Aug 2026 while answering the Director's question about the engine's
context surface. `gap_engine([])` returned `refusals: []`.

Both implementations built the refusal list at the END of the function, after
`if not hits: return report`. So a log with no outgoing damage lines -- a support
character's log, a log for the wrong character, a file that failed to decode, an
empty file -- produced a Report with NO refusals. The engine went silent about
what it refuses exactly when it knew least, and a page rendering `refusals` would
have shown nothing.

The worst of the three is `engaged_time.comparison`, whose own detail reads
"refused in all cases" -- a privacy refusal ruled on 30 August that was not, in
fact, unconditional. `worn.stats` and `item.selection` are equally facts about
what a log can never show, and equally independent of the log.

This is a gate, not a guard: it runs both implementations over inputs designed to
reach the early return and asserts the three survive.

    python3 check_refusals.py
    python3 check_refusals.py --selftest   prove it can FAIL
"""
import json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "fixtures"))
from gapengine import gap_engine, ALWAYS_REFUSED

REQUIRED = {r["lane"] for r in ALWAYS_REFUSED}

# Inputs chosen to reach the `if not hits` early return, plus one that does not.
CASES = {
    "empty log": [],
    "only blank lines": ["", "  ", ""],
    "log with no outgoing damage": [
        "[Sat Aug 30 20:00:00 2026] You have entered the Plane of Sky.",
        "[Sat Aug 30 20:00:04 2026] Shara begins to cast a spell.",
        "[Sat Aug 30 20:00:09 2026] a sand giant hits YOU for 61 points of damage.",
    ],
    "unparseable bytes as text": ["\ufffd\ufffd\ufffd", "not a log line at all"],
    # A continuous fight across a MONTH BOUNDARY. Until 31 Aug 2026 `t` was
    # day_of_month*86400, which runs backwards at the rollover and split one fight
    # into two engagements with double the engaged seconds and half the dps.
    "a fight crossing 31 Aug -> 1 Sep": (
        [f"[Sun Aug 31 23:59:{s:02d} 2026] You slash a rock golem for 50 points of damage."
         for s in range(20, 60, 2)] +
        [f"[Mon Sep 01 00:00:{s:02d} 2026] You slash a rock golem for 50 points of damage."
         for s in range(0, 40, 2)]),
    "a real engagement (control: must ALSO carry them)": None,   # filled below
}


def js_refusals(lines):
    drv = ('const fs=require("fs");(0,eval)(fs.readFileSync(process.argv[2],"utf8"));'
           'const l=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));'
           'process.stdout.write(JSON.stringify('
           'globalThis.EQLSGapEngine.gapEngine(l,{source:"refusal-check"}).refusals));')
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(drv); d = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(lines, f); j = f.name
    out = subprocess.run(["node", d, os.path.join(ROOT, "bundle", "eqls-gap-engine.js"), j],
                         capture_output=True, text=True, check=True).stdout
    os.unlink(d); os.unlink(j)
    return {r["lane"] for r in json.loads(out)}


def audit(py_fn, js_fn, cases):
    out = []
    for name, lines in cases.items():
        py, js = {r["lane"] for r in py_fn(lines)["refusals"]}, js_fn(lines)
        missing_py, missing_js = REQUIRED - py, REQUIRED - js
        ok = not missing_py and not missing_js and py >= REQUIRED and js >= REQUIRED
        detail = f"PY {len(py)} JS {len(js)}"
        if missing_py: detail += f"  PY MISSING {sorted(missing_py)}"
        if missing_js: detail += f"  JS MISSING {sorted(missing_js)}"
        if py != js:   detail += f"  PY/JS DISAGREE {sorted(py ^ js)}"; ok = False
        out.append((name, ok, detail))
    return out


# ---------------------------------------------------------------------------
# R159, added 1.5.0: the engine must say WHAT KIND OF CLAIM its silence is.
# A file that could not be READ and a character who dealt NO DAMAGE used to produce
# the same output. That is how the CRLF defect stayed quiet -- a true sentence about
# an unread file, sitting in the slot where a measurement goes.
# The case matrix above already contains both kinds, which is why this lives here
# rather than in an eighteenth checker: two unreadable inputs, three readable ones and
# one empty. Every verdict is exercised, so no arm can pass by never being reached.
EXPECT_VERDICT = {
    "empty log": "empty",
    "only blank lines": "unreadable",           # 0 of 3 stamped; blanks are not a log
    "log with no outgoing damage": "read",      # A REAL ZERO, and it must say so
    "unparseable bytes as text": "unreadable",
    "a fight crossing 31 Aug -> 1 Sep": "read",
    "a real engagement (control: must ALSO carry them)": "read",
}


def js_coverage(lines):
    drv = ('const fs=require("fs");(0,eval)(fs.readFileSync(process.argv[2],"utf8"));'
           'const l=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));'
           'process.stdout.write(JSON.stringify('
           'globalThis.EQLSGapEngine.gapEngine(l,{source:"refusal-check"}).coverage));')
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(drv); d = f.name
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(lines, f); j = f.name
    try:
        return json.loads(subprocess.run(
            ["node", d, os.path.join(ROOT, "bundle", "eqls-gap-engine.js"), j],
            capture_output=True, text=True, check=True).stdout)
    finally:
        os.unlink(d); os.unlink(j)


def audit_verdicts(py_fn, js_fn, cases):
    out = []
    for name, lines in cases.items():
        want = EXPECT_VERDICT[name]
        p = ((py_fn(lines).get("coverage") or {}).get("parse") or {}).get("verdict")
        j = ((js_fn(lines) or {}).get("parse") or {}).get("verdict")
        ok = p == want and j == want
        out.append((f"verdict: {name}", ok, f"want {want!r}, PY {p!r}, JS {j!r}"))
    # The matrix must exercise EVERY verdict, or an arm passes by never being reached.
    seen = set(EXPECT_VERDICT.values())
    out.append(("every verdict is exercised by the matrix",
                seen == {"empty", "read", "unreadable"}, f"covers {sorted(seen)}"))
    return out


if __name__ == "__main__":
    from synthetic_log import build
    CASES["a real engagement (control: must ALSO carry them)"] = build()

    if "--selftest" in sys.argv:
        print("== check_refusals self-test: it must be able to FAIL ==")
        ok = True
        # An engine that drops the refusals on empty input -- the bug as it was.
        def broken_py(lines):
            r = gap_engine(lines)
            if not any("points of damage" in l for l in lines):
                r["refusals"] = []
            return r
        res = dict((n, o) for n, o, _ in
                   audit(broken_py, js_refusals, {"empty log": []}))
        if res.get("empty log") is not False:
            print("  the pre-fix behaviour                BROKEN -- did not fail"); ok = False
        else:
            print("  the pre-fix behaviour                correctly fails")
        # A port that disagrees with its own Python.
        res = dict((n, o) for n, o, _ in
                   audit(gap_engine, lambda l: REQUIRED - {"worn.stats"}, {"empty log": []}))
        if res.get("empty log") is not False:
            print("  a JS port dropping one refusal       BROKEN -- did not fail"); ok = False
        else:
            print("  a JS port dropping one refusal       correctly fails")
        if not all(o for _, o, _ in audit(gap_engine, js_refusals, CASES)):
            print("  the real engines do not pass"); ok = False
        else:
            print(f"  the real engines carry all {len(REQUIRED)} on every case")

        # The verdict arm, proven able to fail: an engine that calls everything
        # "read" is exactly the pre-1.5.0 behaviour -- one sentence for a file it
        # could not read and a character who dealt nothing.
        def flat_py(lines):
            r = gap_engine(lines)
            r.setdefault("coverage", {}).setdefault("parse", {})["verdict"] = "read"
            return r
        res = dict((n, o) for n, o, _ in
                   audit_verdicts(flat_py, js_coverage, {"unparseable bytes as text":
                                                         CASES["unparseable bytes as text"]}))
        got = res.get("verdict: unparseable bytes as text")
        print(f"  an engine that calls everything read {'correctly fails' if got is False else 'BROKEN'}")
        ok &= (got is False)
        vs = audit_verdicts(gap_engine, js_coverage, CASES)
        if not all(o for _, o, _ in vs):
            print("  the real engines disagree on a verdict"); ok = False
        else:
            print(f"  both engines agree on all {len(CASES)} verdicts")
        sys.exit(0 if ok else 1)

    rs = audit(gap_engine, js_refusals, CASES)
    for n, o, d in rs:
        print(f"  {n:<48} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  The engine went silent about what it refuses. That is the whole product.")
        sys.exit(1)
    print(f"  {len(REQUIRED)} unconditional refusals survive {len(rs)} inputs, in both implementations")

    vs = audit_verdicts(gap_engine, js_coverage, CASES)
    for n, o, d in vs:
        print(f"  {n:<48} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in vs):
        print("  A file that could not be READ is reporting as a character who dealt "
              "NOTHING. That is the shape the CRLF defect hid behind.")
        sys.exit(1)
