#!/usr/bin/env python3
"""check_drift.py -- the fixture must not drift from what the engine emits.

A shipped a page against my fixture on 30 Aug and the page could not render
`materiality`, because the hand-written fixture had already diverged from the
engine. The gate I wrote that day compared DELTA KEYS and MEASURED KEYS and then
printed "fixture shape matches engine output".

It compared two of the five structures a consumer renders. Refusals, coverage and
the top-level key set were not checked at all -- and refusals are precisely the
fields A's page renders, and precisely where A found a false count on 31 Aug.
Matched-pair proven before this rewrite: adding a `severity` key to every refusal
in the engine left the old gate printing "shape matches".

That is A's own 31 Aug shape, in my tree: an instrument that returned the right
answer in the wrong words, and was read for the verdict. The fix is both halves --
compare everything a consumer renders, AND say what was compared, so the sentence
cannot outrun the check again.

Run:  python3 fixtures/check_drift.py
      python3 fixtures/check_drift.py --selftest
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "fixtures", "sample-report.json")
REAL = os.path.join(ROOT, "fixtures", "real-report-shara.json")
MAKER = os.path.join(ROOT, "fixtures", "make_fixture.py")
# The REAL report had no maker until 1 Sep 2026. It was a committed artifact that
# no tool produced, and it had gone stale in a VALUE this gate does not compare:
# `months_seen: ["Aug"]`, the list form B's contract rejected and both engines
# stopped emitting on 31 Aug. Key-set comparison read clean over it for a day.
# Both sides of this comparison are now engine output, so neither can drift.
MAKER_REAL = os.path.join(ROOT, "fixtures", "make_real.py")

# Keys the fixture carries for the reader that the engine never emits.
FIXTURE_ONLY = {"_fixture", "_never", "_regenerate", "_why",
                "_context_is_caller_supplied"}
MEASURED_ONLY = {"_register"}


def keys_of(rows):
    return set().union(*[set(r) for r in rows]) if rows else set()


def compare(fx, rp):
    """Every structure a consumer renders. Returns [(what, ok, detail)]."""
    return [
        ("top-level keys", set(fx) - FIXTURE_ONLY == set(rp),
         f"{sorted(set(fx) - FIXTURE_ONLY ^ set(rp)) or 'same'}"),
        ("delta keys", keys_of(fx["deltas"]) == keys_of(rp["deltas"]),
         f"{sorted(keys_of(fx['deltas']) ^ keys_of(rp['deltas'])) or 'same'}"),
        ("measured keys", set(fx["measured"]) - MEASURED_ONLY == set(rp["measured"]),
         f"{sorted((set(fx['measured']) - MEASURED_ONLY) ^ set(rp['measured'])) or 'same'}"),
        ("refusal keys", keys_of(fx["refusals"]) == keys_of(rp["refusals"]),
         f"{sorted(keys_of(fx['refusals']) ^ keys_of(rp['refusals'])) or 'same'}"),
        ("refusal reason vocabulary",
         {r["reason"] for r in fx["refusals"]} <= {r["reason"] for r in rp["refusals"]},
         f"fixture uses {sorted({r['reason'] for r in fx['refusals']})}"),
        ("coverage keys", set(fx.get("coverage", {})) == set(rp.get("coverage", {})),
         f"{sorted(set(fx.get('coverage', {})) ^ set(rp.get('coverage', {}))) or 'same'}"),
        # `context` gets a DIFFERENT predicate, and getting this wrong once is why the
        # note is here. gapengine.py:198 passes the caller's dict through untouched, so
        # comparing the fixture's context keys against another caller's report compares
        # two CALLERS, not the engine -- the same wrong-quantity fault this file exists
        # to fix. The real hazard is a consumer treating a caller-supplied field as
        # guaranteed, so what is checked is that the fixture DECLARES them.
        ("context keys are declared caller-supplied",
         set(fx.get("_context_is_caller_supplied") or []) == set(fx.get("context", {})),
         f"declared {sorted(fx.get('_context_is_caller_supplied') or [])}, "
         f"present {sorted(fx.get('context', {}))}"),
    ]


def passthrough_holds():
    """What the engine actually does with `context` -- BOTH arms.

    On 31 Aug 2026 three parties published "the engine reads NOTHING from context"
    -- the Director, then B adopting it, and me refuting it under a subject nobody
    read. It is false, and nothing here tested it. The accurate statement is that
    the engine consumes no context VALUE, while it DOES deep-copy the object and
    DOES honour a caller-supplied `marker_raw`.

    A fact three people got wrong and no check covered is exactly what a gate is
    for. Four probes, and the last two are the ones that were being argued about.
    """
    sys.path.insert(0, ROOT)
    from gapengine import gap_engine
    LOG = ["[Sat Aug 30 20:00:00 2026] ATTN CLAUDE: FROM-THE-LOG",
           "[Sat Aug 30 20:00:01 2026] You slash a rock golem for 50 points of damage."]
    sentinel = {"zz_sentinel": [1, {"deep": True}], "source": "probe"}

    caller = dict(sentinel)
    got = gap_engine([], caller)["context"]
    if got != sentinel:
        return False, f"context not echoed: {got!r}"
    if caller != sentinel:
        return False, f"the CALLER's dict was mutated: {caller!r}"
    if gap_engine(LOG, {})["context"].get("marker_raw") != "FROM-THE-LOG":
        return False, "a marker in the log is not parsed into context"
    honoured = gap_engine(LOG, {"marker_raw": "FROM-THE-CALLER"})["context"]["marker_raw"]
    if honoured != "FROM-THE-CALLER":
        return False, f"a caller-supplied marker_raw was OVERWRITTEN: {honoured!r}"
    return True, ("echoed verbatim; caller's dict unmutated; log-derived marker parsed; "
                  "caller-supplied marker honoured -- so context IS read, and no "
                  "context VALUE is consumed")


def load(regenerate=True):
    if regenerate:
        subprocess.run([sys.executable, MAKER], check=True, capture_output=True)
        subprocess.run([sys.executable, MAKER_REAL], check=True, capture_output=True)
    return json.load(open(FIXTURE)), json.load(open(REAL))


if __name__ == "__main__":
    fx, rp = load()

    if "--selftest" in sys.argv:
        print("== check_drift self-test: every structure must be able to FAIL ==")
        ok = True
        import copy

        def mut(label, f2, r2, expect):
            global ok
            if (f2, r2) == (fx, rp):
                print(f"  {label:<44} BROKEN -- mutation was a no-op"); ok = False; return
            got = dict((n, o) for n, o, _ in compare(f2, r2)).get(expect)
            if got is None:
                print(f"  {label:<44} BROKEN -- '{expect}' not reported"); ok = False
            elif got:
                print(f"  {label:<44} BROKEN -- '{expect}' still passed"); ok = False
            else:
                print(f"  {label:<44} correctly fails '{expect}'")

        f = copy.deepcopy(fx); f["refusals"][0]["severity"] = "hard"
        mut("a key added to every refusal", f, rp, "refusal keys")
        f = copy.deepcopy(fx); f["refusals"][0]["reason"] = "brand_new_reason"
        mut("a refusal reason the consumer cannot style", f, rp, "refusal reason vocabulary")
        f = copy.deepcopy(fx); f["coverage"]["new_block"] = 1
        mut("a coverage block the page cannot render", f, rp, "coverage keys")
        f = copy.deepcopy(fx); f["deltas"][0]["materiality"] = None; del f["deltas"][0]["materiality"]
        f["deltas"][0]["new_field"] = 1
        mut("a delta field the page cannot render", f, rp, "delta keys")
        f = copy.deepcopy(fx); f["measured"]["new_metric"] = 1
        mut("a measured metric the page cannot render", f, rp, "measured keys")
        f = copy.deepcopy(fx); f["totally_new"] = {}
        mut("a whole new top-level structure", f, rp, "top-level keys")
        f = copy.deepcopy(fx); f["context"]["new_ctx"] = 1
        mut("an undeclared context field", f, rp, "context keys are declared caller-supplied")
        if not all(o for _, o, _ in compare(fx, rp)):
            print("  the real pair does not pass"); ok = False
        else:
            print(f"  the unmutated fixture and engine output still pass all {len(compare(fx, rp))}")
        okp, why = passthrough_holds()
        if not okp:
            print(f"  context pass-through does not hold: {why}"); ok = False
        sys.exit(0 if ok else 1)

    rs = compare(fx, rp) + [("context: echoed, unmutated, marker honoured",) + passthrough_holds()]
    for n, o, d in rs:
        print(f"  {n:<40} {'ok' if o else 'DRIFT'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  A PAGE BUILT ON THIS FIXTURE WOULD RENDER THE WRONG FIELDS")
        sys.exit(1)
    print(f"  {len(rs)} checks -- {len(rs)-1} structures a consumer renders, plus a "
          f"4-arm probe of what the engine does with `context`. The old gate compared 2.")
