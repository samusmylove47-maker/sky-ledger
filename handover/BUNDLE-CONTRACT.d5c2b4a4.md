# The bundle contract — what this site needs from the gap engine

**Written by Session A, 31 August 2026, so Session E can build to it tonight.**
It specifies the *artifact*, not the engine. E owns everything inside the
function; this document owns the boundary it arrives through.

Where this contradicts a ruling, the contradiction is named in §5 rather than
resolved silently.

---

## 1. One file, and it is the whole artifact

**`eqls-gap-engine.<sha256[:8]>.js` — a single file, no imports, no sibling
assets, no source map required.**

One file rather than several for a reason this repository has already paid for:
the site copies third-party builds under a content hash and serves them from
`public/app/`, and every additional file is another thing that can be stale
independently. `_build/lockouts.py` and `_build/skyledger.py` both do this, and
both were written after a stylesheet went stale in readers' caches while the site
believed it had shipped.

**Not an ES module.** A classic script, because the pages that will load it are
generated HTML with no bundler, and `type="module"` changes the loading semantics
of every page that carries it. If E strongly prefers a module, say so and I will
adapt the loader — but the default is the one that costs the site nothing.

## 2. The global, and the signature

```js
window.EQLSGapEngine = {
  version: "1.4.2",          // semver string, and see §6
  gapEngine(lines, context)  // exactly E's §21.2 signature
}
```

`gapEngine(lines: string[], context: Context) -> Report`, returning the shape in
E's §21.3 — `measured`, `deltas`, `refusals`, `coverage`.

**One global, one property for the function and one for the version.** Nothing
else on `window`. The page reads both and asserts the version before it calls
anything.

**`lines` is an array of already-decoded strings, one per log line, in file
order, with line endings removed.** The decoding is mine — see §4 — and E should
assume nothing about the file that produced them.

## 3. What it must not do, and why each one is here

- **No `fetch`, no `XMLHttpRequest`, no `WebSocket`, no `sendBeacon`, no
  `EventSource`.** The site's claim is that a reader's log never leaves their
  machine, and after 30 August that claim rests on the artifact having no
  transmit path rather than on a promise. A single request would make the
  sentence false on a page that prints it.
- **No DOM access.** No `document`, no `window` beyond its own registration.
  The engine computes; the page renders. E's §21.2 already says pure, and this
  is the same statement from the consuming side.
- **No timers.** No `setTimeout`, `setInterval`, `requestAnimationFrame`. A
  synchronous call that returns a `Report` is the whole interaction.
- **No storage.** No `localStorage`, `sessionStorage`, `IndexedDB`, no cookies.
  The reader's figures exist for the length of one function call.
- **No `eval`, no `new Function`.** The site ships a strict-ish CSP posture and a
  dynamically-evaluated string is the one thing a reader cannot audit.

**These are checkable and I will check them**, with the same instrument D built:
`analysis/audit-self-contained.js` at `523fac0` or later, run against the bundle
before it is committed. The site already refuses to publish a page that fetches
another origin; the bundle gets the same treatment.

## 4. WHO DECODES: this site does, and the method is measured

**The site decodes. E receives strings and never sees a byte.**

This is the section that contradicts the order, and the contradiction is D's
measurement rather than my preference.

**The order says the windows-1252 fallback belongs in the decode path. There is
no windows-1252 fallback — anywhere.** D measured it across the whole Lockouts
repository: no occurrence of `1252`, `latin1`, `iso-8859` or `TextDecoder` in any
`.js` file, and every reader in `analysis/` opens with `{ encoding: 'utf8' }`
with nothing catching a decode failure. `lockoutCore.js` takes strings and does
no IO, so it never sees bytes at all. **D's document is right and the order is
describing something that does not exist.**

**Why that matters rather than being a tidy-up.** D measured the failure mode and
I reproduced it: feeding Node the cp1252 bytes `0x93 0x94` inside a stamped line
does **not** throw. It substitutes `U+FFFD`, one per bad byte, and the line still
starts with `[` so the stamp still parses. A byte in a player name becomes a
replacement character *inside a key*, silently, with no counter firing.

**The browser is better than Node here, and that is why this belongs to me.**
Measured, 31 August:

| decoder | result on `0x93 0x94` |
|---|---|
| `new TextDecoder('utf-8')` | `"[Tue ��]"` — silent corruption |
| `new TextDecoder('utf-8', {fatal: true})` | **throws `TypeError`** |
| `new TextDecoder('windows-1252')` | `"[Tue “”]"` — correct |

**It is a detector with a matched pair, which is the property that makes it
trustworthy rather than merely available.** D's framing, and it is better than
calling it a fallback: `{fatal: true}` returns *both* of its answers — it throws
on the bad input and passes the good one. Measured here, both directions:

| input | `{fatal: true}` |
|---|---|
| the cp1252 bytes | **throws `TypeError`** |
| valid UTF-8 (`[Tue ok]`) | **passes** — the control |

A detector only shown to fire is the fault that invalidated D's own
self-containment auditor for a day, when it could not return YES for any page
with a local stylesheet. This one is shown by a pair.

The site will:

1. Decode with `new TextDecoder('utf-8', {fatal: true})` — **as the first decode
   of the raw bytes, before anything else touches them.**
2. On `TypeError`, decode again with `new TextDecoder('windows-1252')`.
3. **Report which path was taken** in the page's own output, because a log that
   needed the fallback is a fact about the reader's file that they are entitled
   to know, and because a silent recovery is how the original fault hid.
4. **Count `U+FFFD` in the result and report that too, on both paths.**

### The ordering in step 1 is load-bearing, and getting it wrong disables the detector silently

**D flagged this and I measured it before writing it down.** The natural
implementation — decode, then validate — does not work, and it fails in the
direction that looks fine:

```
raw cp1252 bytes  --> TextDecoder('utf-8')            "[Tue ��]"   no throw
                  --> re-encode, then {fatal: true}   PASSES
                      ...while two U+FFFD remain in the data
```

Once a lossy decode has run, the replacement characters **are legitimate
`U+FFFD`** and the byte stream really is valid UTF-8. `{fatal: true}` is then
telling the truth about the wrong thing. **A correct detector, applied one step
too late, stops detecting and reports success.**

So: `{fatal: true}` sees the *bytes*, never a string that something else has
already decoded. That is a constraint on the implementation, not a preference,
and it is why step 1 says so explicitly.

**Step 4 exists because neither decoder can catch everything.** If the log file
already contains `U+FFFD` as legitimate encoded bytes — E measured six such in
its own corpus, where a strict decode passes and a round-trip passes — then no
decoder can distinguish that from clean input, because at the byte level it *is*
clean input. Counting them and printing the count is the only honest instrument
left, and it costs one line.

**Exposure, measured by D and not by me, and the two halves do not imply each
other.** D enumerated 279,172 key-field values across roughly 57.7 MB of the
Lockouts corpus and found **zero** non-ASCII. So this may never fire on real
logs. That is a fact about D's corpus; mine is that the host can detect and
recover if it ever does. Neither result makes the other unnecessary.

**E should assume nothing and check nothing about encoding.** If a `U+FFFD` ever
reaches the engine it is my defect, not E's, and step 3 is what will make it
visible rather than mysterious.

## 5. Where this contradicts the order

Recorded rather than resolved quietly, per the standing rule that a measurement
beats a ruling and the contradiction goes in the commit subject.

- **"the windows-1252 fallback belongs there"** — there is no such fallback in
  any repository. §4 specifies one for the first time rather than relocating an
  existing one. D found this; I reproduced the Node behaviour and measured the
  browser's, which is the half that makes it fixable.

## 6. How the version is pinned, and why twice

**Two independent pins, because they fail differently.**

1. **The filename carries a content hash** — `eqls-gap-engine.<sha256[:8]>.js` —
   and the site serves it from `public/app/` under that name, exactly as it
   serves the Sky Ledger and the lockout tracker. A hashed URL is what stops a
   reader's cache serving yesterday's engine after a merge. This site has the
   scar: an unversioned stylesheet went stale in returning readers' browsers and
   the whole redesign was invisible to anyone who had visited before.
2. **The bundle declares `version` and the page asserts it.** The hash pins the
   *bytes*; the semver pins the *contract*. If E ships a breaking change to the
   `Report` shape, the hash changes either way — but only the semver says whether
   the page still knows how to render it.

**The page refuses to render on a major-version mismatch** and says so in the
page rather than throwing. `_build/build31.py` already refuses to build from data
not marked `_fixture`; this is the same rule at the other end.

**A copy step, on the pattern already here.** `_build/gapengine.py` will find a
sibling checkout, copy the bundle under its hash, write `assets/gap-engine-app.json`
with the hash, byte count and version, and **exit cleanly when the repo is
absent** so a rebuild works on a machine without it. That is how
`_build/lockouts.py` and `_build/skyledger.py` both work, and it carries the same
consequence, stated here so nobody diagnoses it later as a bug: **every engine
release needs a commit in this repository.** Nothing on a build machine reaches
across to E's tree.

## 7. What the page does with a `Report`, so E knows what is read

Everything in E's §21.3 is rendered. Specifically:

- **`measured` and `deltas` are two visually distinct registers**, because they
  are two kinds of claim.
- **`measured.dps` never appears without `dps_window`.** A DPS figure without its
  window is not a measurement, and four shipped meters use four denominators.
- **Every `delta` prints its value beside the baseline it is a difference
  against**, in the same sentence, so the claim survives being excerpted. A bare
  `+98.4` travels to an overlay or a share card meaning nothing.
- **`refusals` render with the same weight as `deltas`** — same heading level,
  same treatment, adjacent rather than below — and `scripts/check.py` fails the
  build if any refusal in the data is missing from the page.
- **`coverage.inputs_assumed` is printed as a source of error**, not as a
  footnote.

## 8. What A does not need, so E does not build it

- No streaming or progress callback. A synchronous call is fine; if a log is
  large enough to block, tell me and I will move the call to a worker — that is
  my problem and it does not change this contract.
- No configuration object beyond `context`.
- No error-message formatting. Throw, and the page will present it.
- No styling, no HTML, no strings intended for display beyond what already sits
  in `Report` — `statement`, `detail`, `what_would_settle_it`.
