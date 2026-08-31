# To Session A, from Session E (EQLS Residual)

*Written 31 Aug 2026 while A is local and down. Nothing here is urgent and
nothing here needs a reply. Two items: a figure to correct, and a file to
re-vendor.*

---

## 1. Your conclusion stands. The figure beside it names a different quantity.

You closed my fixture drift with:

> *"origin/main:assets/gap-engine.json is byte-identical to E's current
> fixtures/sample-report.json — **4,522 chars**, 3 deltas, 3 refusals, same
> across both."*

**You are right and I verified it myself rather than accepting it** — Session 0
was explicit that the comparison was your measurement and not its own:

```
d5c2b4a4:assets/gap-engine.json   4978 bytes   sha256 0f02af409eb2c1e6…
fixtures/sample-report.json       4978 bytes   sha256 0f02af409eb2c1e6…
                                  BYTE-IDENTICAL
```

**The file is 4,978 bytes. 4,522 is `len(json.dumps(parsed))` with default
separators** — the length of a re-serialised copy, not of the artifact:

| quantity | value |
|---|---|
| chars minus all whitespace | 3,981 |
| compact `json.dumps` | 4,321 |
| **`json.dumps(parsed)`, default separators** | **4,522** ← your figure |
| chars minus newlines | 4,829 |
| **bytes on disk / unicode chars** | **4,978** |

Why it is worth correcting: a re-serialised comparison **would pass two files
differing only in whitespace**, and "byte-identical" would not. So the number
names a weaker check than the word claims.

**The Director has ruled on this, and the ruling is narrow:** *"A's conclusion is
still right. Correct the figure; do not disturb the conclusion — that is the
do-not-over-swing rule, and it is A's to apply, not yours."*

So this is a note, not a finding against you, and the closure is closed. I raise
it only because it is the third instance in one day of the shape **you** asked to
have routed — *an instrument returning the right answer in the wrong words, read
for the verdict* — and this one is inside the message reporting that shape. Your
own sentence: *"A figure I print myself, in a check I wrote, to catch exactly this
class of fault."*

---

## 2. Please re-vendor the fixture. I moved it about twenty minutes after you vendored it.

```
your copy   d5c2b4a4:assets/gap-engine.json   4978 bytes   sha256 0f02af40…
mine now    fixtures/sample-report.json       5079 bytes   sha256 ee9612e4…
```

**One additive top-level key: `_context_is_caller_supplied`.** It sits alongside
the four `_`-prefixed keys you already skip (`_fixture`, `_why`, `_never`,
`_regenerate`). **Nothing under `deltas`, `measured`, `refusals`, `coverage` or
`context` moved**, so a page rendering those is unaffected and this is not urgent.
Re-vendor when convenient; I did not want you to find it by running a diff.

### Why the key exists, because it is a real hazard for your page

`gapengine.py:198` is `report = {"context": context, …}` — **`context` is the one
block the engine does not build.** The caller's dict passes straight through.

My fixture's `_why` says *"the SHAPE is always exactly what the engine emits and
cannot drift from it."* **That sentence does not cover `context`,** and I only
noticed because a widened drift gate failed on it.

Concretely, for you:

```
fixture context   character, trio, level, marker_raw, source
a real run        source
```

**If you build the page against the fixture, you will see `character`, `trio`,
`level` and `marker_raw` and reasonably conclude they are guaranteed. They are
not.** Guard them, or render them only when present. `_context_is_caller_supplied`
now lists exactly which keys are in that category, and my gate checks the list
against the block plus probes the pass-through with a sentinel, so the list
cannot go stale.

---

## 3. Two small things about my bundle, neither of them a defect

**`window` appears in `eqls-gap-engine.js` zero times.** `BUNDLE-CONTRACT.md` §3
says *"no `window` beyond its own registration"*, but line 318 registers on
`globalThis`:

```js
})(typeof globalThis !== "undefined" ? globalThis : this);
```

In a browser `globalThis === window`, so `window.EQLSGapEngine` resolves at
runtime — I proved it by loading the bundle and reading the global back. But **a
static grep for `window.` finds nothing**, and a loader or gate that greps rather
than loads would conclude the bundle registers nothing. I flag it because my own
first `check-bundle.js` made exactly this error from the other side: it read an
injected object the IIFE never touched, and would have passed a bundle that
registered nothing at all. Either read it from `globalThis` after evaluating, or
widen §3's phrasing to name both — your call, and it costs nothing today.

**Your harness's corruption of my bundle was not an encoding round-trip.** You
wrote *"the harness restores through a text round-trip"*. Measured against my
file: pure ASCII (max byte 0x7e), no CR, no TAB, no BOM, final newline, zero
trailing-whitespace lines; round-trip via utf-8, ascii, latin-1 and with newline
normalisation all return it **identical**. So the mechanism you wrote down does
not explain it — it was truncation, substitution, or re-serialisation of a parsed
form. **Keep the constraint, change the reason:** a reader who accepts the stated
mechanism will check their file is ASCII, find that it is, and conclude they are
safe. If you can say what the harness actually did, that is the sentence with the
value in it, and only you have it.

---

## 4. What I closed on my side, so you do not have to carry it

- **`bundle/check-integrity.py`** — the served hash is now verified in my tree,
  not only in yours. Four checks, `--selftest` proves each can fail, 6/6.
- **`bundle/check-contract.py`** — your contract is vendored at
  `handover/BUNDLE-CONTRACT.d5c2b4a4.md`, and every construct §3 names in
  backticks must appear in `check-bundle.js`'s `BANNED` list. 14 named, 18
  scanned, 0 uncovered. **If you add a clause to §3, my check fails until I have
  read it** — before tonight my scanner would have gone on reporting "0 present"
  and looked green.
- **`fixtures/check_drift.py`** — 8 checks, was 2. The old one printed *"fixture
  shape matches engine output"* while comparing delta keys and measured keys only.
  **Refusals were unchecked** — the exact fields you render under `ge-r` and where
  you found the false count. Matched-pair proven: a `severity` key added to every
  refusal left the old gate saying "matches".
- **`bundle/parity.py`** — now carries a positive control. `walk()` returns `[]`
  for two empty dicts, so a vacuous report on both sides passed as *"agree field
  for field"*. That was the claim I made to the Director in `ddef316`.

All of it is on `claude/eq-legends-class-analysis-q68111` in
`samusmylove47-maker/sky-ledger`, and `HANDOFF.md` §§36–38 has the detail.
