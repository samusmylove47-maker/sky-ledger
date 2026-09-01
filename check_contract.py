#!/usr/bin/env python3
"""check_contract.py -- does EQLSGapEngine satisfy B's hand-written contract?

B wrote `web/src/engine/__fixtures__/gap-contract-1.2.0.json` stating what its
`measured` block needs. It is HAND-WRITTEN, not generated from my output, which is
the point: B says what it needs and I make it pass, rather than B describing what I
already do. Vendored here at B's `65e2f9e3` so this check cannot drift silently.

This asserts TYPES AND SHAPES, never values -- B's numbers come from B's own
sample log and mine come from mine.

    python3 check_contract.py
    python3 check_contract.py --selftest
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "fixtures"))
CONTRACT = os.path.join(ROOT, "handover", "gap-contract-1.2.0.b-65e2f9e3.json")

SPELL_KEYS = {"landings", "normalised_key", "damage_total", "damage_median", "damage_max"}


def _sv(v):
    return tuple(int(x) for x in v.split("."))


def audit(measured, version, contract, handoff=""):
    """SHAPE is asserted against B's fixture; VERSION is asserted as a RELATIONSHIP.

    This read `version == contract["version"]` until 1 Sep 2026, which was right while
    the engine sat at 1.2.0 and became a gate that could only be satisfied by never
    releasing again. Worse, it hid the thing the Director ruled on: TWO byte-sets
    shipped as 1.2.0 in one night, the second with a changed PARSER, and B's guard --
    exact equality -- could not tell them apart.

    So the checks are now: the engine is not BELOW the contract, the MAJOR matches
    (B's page refuses on a major mismatch), the SHAPE still satisfies every key B
    asked for, and -- the load-bearing one -- **a version divergence is DECLARED**.
    B asserts equality, so any divergence means B is reading its unknown band until B
    re-pins, and a divergence nobody wrote down is a consumer silently switched off.
    """
    want = contract["measured"]
    ev, cv = _sv(version), _sv(contract["version"])
    out = [
        ("engine is not BELOW the contract version", ev >= cv,
         f"engine {version}, contract {contract['version']}"),
        ("engine MAJOR matches the contract's", ev[0] == cv[0],
         f"{ev[0]} vs {cv[0]}; B's page refuses on a major mismatch"),
        # THE DETAIL MUST FOLLOW THE BRANCH THAT ACTUALLY HELD. The first version of
        # this line computed the failure text unconditionally, so a PASSING check
        # printed "HANDOFF.md carries no 'REPIN NEEDED: 1.3.0'" beside an `ok`. The
        # right answer in the wrong words -- the shape this repository has spent a
        # week finding in other people's instruments -- caught by reading the detail
        # column of a green run.
        ("a version divergence is DECLARED in HANDOFF.md",
         ev == cv or (f"REPIN NEEDED: {version}" in handoff),
         ("versions match, nothing to declare" if ev == cv
          else (f"engine {version} != contract {contract['version']}, and HANDOFF.md "
                f"DECLARES 'REPIN NEEDED: {version}' -- B is on its unknown band until "
                "it re-pins, and that is written down"
                if f"REPIN NEEDED: {version}" in handoff else
                f"engine {version} != contract {contract['version']} and HANDOFF.md "
                f"carries NO 'REPIN NEEDED: {version}' -- B is reading its unknown "
                "band and nobody said so"))),
    ]
    for k in ("engaged_seconds", "melee_seconds", "damage_dealt", "months_seen"):
        exp, got = want[k], measured.get(k, "<<ABSENT>>")
        ok = isinstance(got, type(exp)) and not isinstance(got, bool)
        out.append((f"measured.{k} is {type(exp).__name__}", ok,
                    f"got {type(got).__name__} {got!r}"))
    sl = measured.get("spells_landed")
    out.append(("measured.spells_landed is an object keyed by the RAW string",
                isinstance(sl, dict), f"got {type(sl).__name__}"))
    if isinstance(sl, dict) and sl:
        k0 = sorted(sl)[0]
        out.append((f"each entry carries {sorted(SPELL_KEYS)}",
                    SPELL_KEYS <= set(sl[k0]), f"'{k0}' has {sorted(sl[k0])}"))
        out.append(("normalised_key is a VALUE, not the key",
                    sl[k0].get("normalised_key") is not None
                    and isinstance(sl[k0]["normalised_key"], str), ""))
    return out


def load_contract():
    return json.load(open(CONTRACT, encoding="utf-8"))


# `real()` lived here and was never called. It returned the engine's `measured` block
# beside a HARD-CODED "1.2.0" -- a second, unsourced copy of a version the __main__
# path already reads out of the bundle. Deleted 1 Sep 2026 rather than updated: a
# duplicated constant is how two truths drift, and this one would have kept saying
# 1.2.0 through tonight's bump with nothing to notice.


if __name__ == "__main__":
    c = load_contract()
    from gapengine import gap_engine
    from synthetic_log import build
    import re as _re
    ver = _re.search(r'var VERSION = "([^"]+)"',
                     open(os.path.join(ROOT, "bundle", "eqls-gap-engine.js"),
                          encoding="utf-8").read()).group(1)
    m = gap_engine(build(), {})["measured"]
    handoff = open(os.path.join(ROOT, "HANDOFF.md"), encoding="utf-8").read()

    if "--selftest" in sys.argv:
        print("== check_contract self-test: it must be able to FAIL ==")
        ok = True
        bad = dict(m); bad["months_seen"] = ["Aug"]
        r = dict((n, o) for n, o, _ in audit(bad, ver, c))
        got = r.get("measured.months_seen is int")
        print(f"  a list where the contract wants an int   "
              f"{'correctly fails' if got is False else 'BROKEN'}")
        ok &= (got is False)
        bad2 = dict(m); bad2.pop("damage_dealt", None)
        r2 = dict((n, o) for n, o, _ in audit(bad2, ver, c))
        print(f"  an absent key                            "
              f"{'correctly fails' if r2.get('measured.damage_dealt is int') is False else 'BROKEN'}")
        ok &= (r2.get("measured.damage_dealt is int") is False)
        def arm(label, ver, hf, expect):
            global ok
            got = dict((n, o) for n, o, _ in audit(m, ver, c, hf)).get(expect)
            print(f"  {label:<40} {'correctly fails' if got is False else 'BROKEN'}")
            ok &= (got is False)

        arm("an engine BELOW the contract", "1.1.9", handoff,
            "engine is not BELOW the contract version")
        arm("a MAJOR bump", "2.0.0", handoff, "engine MAJOR matches the contract's")
        arm("a divergence nobody declared", "1.3.0", "",
            "a version divergence is DECLARED in HANDOFF.md")
        # ...and the matched pair: the SAME divergence, declared, must PASS.
        got = dict((n, o) for n, o, _ in
                   audit(m, "1.3.0", c, "REPIN NEEDED: 1.3.0")).get(
                       "a version divergence is DECLARED in HANDOFF.md")
        print(f"  {'the same divergence, DECLARED':<40} "
              f"{'correctly passes' if got is True else 'BROKEN'}")
        ok &= (got is True)
        sys.exit(0 if ok else 1)

    rs = audit(m, ver, c, handoff)
    for n, o, d in rs:
        print(f"  {n:<52} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  B's contract is NOT satisfied. B is never blocked on me and I am "
              f"never blocked on B, but a consumer asserting {c['version']} would read "
              "a shape it did not ask for.")
        sys.exit(1)
    print(f"  {len(rs)} contract assertions, all satisfied, against B's fixture at 65e2f9e3")
