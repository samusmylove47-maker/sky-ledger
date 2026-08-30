#!/usr/bin/env python3
"""derived_check.py -- the gate for derived claims. Session E.

A tier grades a SOURCE. A derived number has no source; it has a DERIVATION.
Giving it a tier would let it inherit trust it never earned -- the same fault as
the Sky tracker's per-page boolean, one level up. So derived claims live in their
own envelope, carry a `D` badge, and pass this gate or they do not ship.

Binding, per the Director's ruling of 30 Aug 2026:
  * a RECOMMENDATION is a published claim and a stronger one than prose, so it
    passes the same gate as any other derived claim and then some;
  * a claim whose kind is `ceiling` may NEVER be displayed as a target;
  * a finding that survives with the log removed belongs to eqlegendstools.com
    and we link to it (`docs/BACKLOG.md`, "Deliberately not doing").

And following `skydata.py`'s precedent: **`verified` is DERIVED and cannot be
typed.** A claim that carries the field at all is rejected.

    python3 derived_check.py [dir]      -> exit 0 clean, 1 on any failure
    python3 derived_check.py --selftest -> proves the gate rejects what it must
"""
import json, os, re, sys, glob

TIERS = {"M", "T1", "T2", "T3", "T4", "T5", "D"}
TIER_RANK = {"M": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4, "T5": 5, "D": 6}
KINDS = {"ceiling", "floor", "estimate"}
REQUIRED = ["id", "claim", "model", "inputs", "assumptions", "kind",
            "residual", "stops", "falsifier", "requires_log"]

# A falsifier has to name something checkable. These are the phrases that look
# like a falsifier and are not one.
BANNED_FALSIFIER = [
    "more data", "further testing", "additional research", "needs review",
    "if it turns out", "time will tell", "unknown", "tbd", "n/a",
]

def _err(out, cid, msg): out.append(f"{cid}: {msg}")

def check_claim(c, out):
    cid = c.get("id", "<no id>")

    for f in REQUIRED:
        if f not in c or c[f] in (None, "", [], {}):
            _err(out, cid, f"missing required field `{f}`")

    if "verified" in c:
        _err(out, cid, "carries a typed `verified` field. Verified is DERIVED, "
                       "never typed -- skydata.py's rule, one level up.")

    # 1. the model, by name AND commit, so a stranger can run it
    m = c.get("model") or {}
    if not isinstance(m, dict) or not m.get("file") or not m.get("commit"):
        _err(out, cid, "`model` needs {file, commit}: 'our damage model' is not a model, "
                       "a file and a hash a stranger can run is")
    elif not re.fullmatch(r"[0-9a-f]{7,40}", str(m["commit"])):
        _err(out, cid, f"model.commit {m['commit']!r} is not a git hash")

    # 2. every input carries its own tier, and the claim is only as good as its worst
    ins = c.get("inputs") or []
    worst = None
    for i, inp in enumerate(ins):
        if not isinstance(inp, dict):
            _err(out, cid, f"input[{i}] is not an object"); continue
        if inp.get("tier") not in TIERS:
            _err(out, cid, f"input[{i}] {inp.get('name','?')!r} has tier "
                           f"{inp.get('tier')!r}, not one of {sorted(TIERS)}")
        else:
            r = TIER_RANK[inp["tier"]]
            worst = r if worst is None else max(worst, r)
        if not inp.get("source"):
            _err(out, cid, f"input[{i}] {inp.get('name','?')!r} names no source. "
                           "Never invent a number.")
        if inp.get("value") is None:
            _err(out, cid, f"input[{i}] {inp.get('name','?')!r} has no value")
    if ins and worst is not None:
        inv = {v: k for k, v in TIER_RANK.items()}[worst]
        c["_worst_input_tier"] = inv
        if worst >= TIER_RANK["T3"] and not c.get("badge"):
            _err(out, cid, f"worst input is tier {inv}; a claim below T2 prints a badge")

    # 3. the assumptions a reader would never guess, and which way each one pushes
    for i, a in enumerate(c.get("assumptions") or []):
        if not isinstance(a, dict) or not a.get("text") or a.get("direction") not in ("inflates", "deflates", "unknown"):
            _err(out, cid, f"assumption[{i}] needs {{text, direction: inflates|deflates|unknown}}. "
                           "An assumption whose direction is not stated is not disclosed.")

    # 4. ceiling / floor / estimate -- and a ceiling is never a target
    k = c.get("kind")
    if k not in KINDS:
        _err(out, cid, f"kind {k!r} must be one of {sorted(KINDS)}")
    if k == "ceiling" and c.get("never_display_as_target") is not True:
        _err(out, cid, "kind is `ceiling`, so `never_display_as_target` must be true. "
                       "Binding: the ceiling is a denominator, never a target.")
    if k != "ceiling" and c.get("never_display_as_target") is True:
        _err(out, cid, "`never_display_as_target` is set on a non-ceiling claim; "
                       "say what you mean or drop it")

    # 5. the residual, component-wise where the claim decomposes
    r = c.get("residual")
    if isinstance(r, dict):
        if r.get("not_measured"):
            if not r.get("why"):
                _err(out, cid, "residual.not_measured needs `why`")
        else:
            for f in ("value", "n", "direction"):
                if r.get(f) in (None, ""):
                    _err(out, cid, f"residual needs `{f}` (or not_measured + why)")
            if r.get("direction") not in ("over", "under", "mixed", None):
                _err(out, cid, "residual.direction must be over|under|mixed")
            if c.get("decomposes") and not r.get("components"):
                _err(out, cid, "claim decomposes, so the residual must too. A total "
                               "residual hides cancellation: a model can land at +0.1% "
                               "while its parts run -41% to +20%.")
    else:
        _err(out, cid, "`residual` must be an object")

    # 6. where it stops
    if isinstance(c.get("stops"), str) or not (c.get("stops") or []):
        _err(out, cid, "`stops` must be a non-empty list of conditions outside which "
                       "the number is not claimed at all")

    # 7. what would falsify it, named specifically
    f = str(c.get("falsifier", ""))
    if len(f) < 25:
        _err(out, cid, "`falsifier` is too short to name anything checkable")
    for b in BANNED_FALSIFIER:
        if b in f.lower():
            _err(out, cid, f"`falsifier` contains {b!r}, which is not a falsifier")

    # THE CATALOGUE TEST -- the Director's boundary, as a build failure.
    # `internal_only` is the one exemption and it is narrow: a claim that never
    # reaches a reader is not shipping, so the boundary does not bite. It was added
    # 30 Aug 2026 because the gate's first run against a real claim rejected this
    # repo's own trio-DPS ceiling -- correctly. That ceiling is computable from a
    # catalogue and a chain with no log at all, so as a SHIPPING finding it belongs
    # to eqlegendstools.com. As an internal denominator it is ours and never shown.
    if c.get("internal_only"):
        if c.get("is_recommendation"):
            _err(out, cid, "internal_only and is_recommendation are contradictory")
        if c.get("displayed"):
            _err(out, cid, "internal_only claim marked as displayed")
        if not c.get("internal_only_reason"):
            _err(out, cid, "internal_only needs a reason: what it is used FOR, "
                           "given it is never shown")
    elif c.get("requires_log") is False and not c.get("link_out"):
        _err(out, cid, "requires_log is false, so this survives with the log removed. "
                       "It belongs to eqlegendstools.com -- set `link_out` to the tool "
                       "we link to instead of shipping it. (docs/BACKLOG.md)")
    if c.get("requires_log") is True and not c.get("internal_only"):
        if not any(i.get("from_log") for i in ins):
            _err(out, cid, "requires_log is true but no input is marked from_log; "
                           "the catalogue test is asserted, not shown")
    if c.get("is_recommendation") and c.get("requires_log") is not True:
        _err(out, cid, "a recommendation that does not require a log is a Gear Upgrade "
                       "Finder. It ships only as a ranked delta against an observed baseline.")

    # retractions are struck in place, never deleted
    if c.get("retracted") and not c.get("retracted_reason"):
        _err(out, cid, "a retracted claim keeps its reason in place")

def derive_status(c):
    """`verified` is derived, never typed. This is the only thing allowed to set it."""
    if c.get("retracted"): return "retracted"
    worst = c.get("_worst_input_tier")
    if c.get("marked_against"): return "contested"
    if worst and TIER_RANK.get(worst, 9) <= TIER_RANK["T2"]: return "supported"
    return "unsupported"

def run(d):
    out, claims = [], []
    files = sorted(glob.glob(os.path.join(d, "*.json")))
    if not files:
        return [f"{d}: no claims found -- an empty gate passes nothing"], []
    seen = set()
    for fp in files:
        try:
            c = json.load(open(fp, encoding="utf-8"))
        except Exception as e:
            out.append(f"{fp}: unreadable ({e})"); continue
        if c.get("id") in seen:
            out.append(f"{fp}: duplicate id {c.get('id')!r}")
        seen.add(c.get("id"))
        check_claim(c, out)
        c["_status"] = derive_status(c)
        claims.append((fp, c))
    return out, claims

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import copy
        base = json.load(open("derived/chain-swing-rate.json", encoding="utf-8"))
        cases = [
            ("a ceiling that could be shown as a target",
             {"kind": "ceiling", "never_display_as_target": False}),
            ("a typed `verified` field", {"verified": True}),
            ("an input with no source", {"inputs": [{"name": "x", "value": 1, "tier": "M"}]}),
            ("a recommendation computable without a log",
             {"is_recommendation": True, "requires_log": False, "link_out": None}),
            ("a falsifier that says 'more data'", {"falsifier": "more data would help settle this"}),
            ("an assumption with no stated direction",
             {"assumptions": [{"text": "best-in-slot gear"}]}),
        ]
        bad = 0
        for label, patch in cases:
            c = copy.deepcopy(base); c.update(patch); c["id"] = "selftest"
            errs = []; check_claim(c, errs)
            ok = bool(errs)
            print(f"  [{'REJECTED' if ok else 'ACCEPTED — GATE IS BROKEN'}] {label}")
            if ok: print(f"        {errs[0][:110]}")
            else: bad += 1
        print(f"\nself-test: {len(cases)-bad}/{len(cases)} bad claims rejected")
        sys.exit(1 if bad else 0)

    d = sys.argv[1] if len(sys.argv) > 1 else "derived"
    errs, claims = run(d)
    for fp, c in claims:
        print(f"  {c['_status']:<12} {c.get('kind','?'):<9} {c['id']}")
    if errs:
        print(f"\n{len(errs)} FAILURE(S):")
        for e in errs: print(f"  - {e}")
        print("\nNothing ships. Fix the claim, not the gate.")
        sys.exit(1)
    print(f"\n{len(claims)} claim(s) pass the gate.")
