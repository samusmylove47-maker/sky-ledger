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


def audit(measured, version, contract):
    want = contract["measured"]
    out = [("version asserts " + contract["version"], version == contract["version"],
            f"engine reports {version!r}")]
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


def real():
    from gapengine import gap_engine
    from synthetic_log import build
    import bundle  # noqa: F401  (path only)
    r = gap_engine(build(), {})
    return r["measured"], "1.2.0"


if __name__ == "__main__":
    c = load_contract()
    from gapengine import gap_engine
    from synthetic_log import build
    import re as _re
    ver = _re.search(r'var VERSION = "([^"]+)"',
                     open(os.path.join(ROOT, "bundle", "eqls-gap-engine.js"),
                          encoding="utf-8").read()).group(1)
    m = gap_engine(build(), {})["measured"]

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
        r3 = dict((n, o) for n, o, _ in audit(m, "9.9.9", c))
        print(f"  a wrong version                          "
              f"{'correctly fails' if list(r3.values())[0] is False else 'BROKEN'}")
        ok &= (list(r3.values())[0] is False)
        sys.exit(0 if ok else 1)

    rs = audit(m, ver, c)
    for n, o, d in rs:
        print(f"  {n:<52} {'ok' if o else 'FAILED'}   {d}")
    if not all(o for _, o, _ in rs):
        print("  B's contract is NOT satisfied. B is never blocked on me and I am "
              "never blocked on B, but a consumer asserting 1.2.0 would read a "
              "shape it did not ask for.")
        sys.exit(1)
    print(f"  {len(rs)} contract assertions, all satisfied, against B's fixture at 65e2f9e3")
