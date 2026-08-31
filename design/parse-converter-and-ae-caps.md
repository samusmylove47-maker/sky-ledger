# DESIGN BRIEF 2 of 3 — TWO REFERENCE TOOLS FOR eqlsource.com

**The Parse-Convention Converter** and **The AE Target-Cap Reference**

Written for an engineer with no context from this session. Every number carries a tier: **M** = measured from the 138-log Legends corpus or read directly from shipped source code; **T1** patch notes; **T2** structured wiki field; **T3** named guide; **T4** aggregator; **T5** wiki prose. The site's own rule applies to us: *cite the field, never the site.*

Both tools exist because a specific, invisible, recurring error is being made in this community, and in both cases the fix is a small table nobody publishes. Neither tool ships a model output. Neither predicts anything. Both are readers of what is already there.

---

---

# TOOL A — THE PARSE-CONVENTION CONVERTER

## A0. The error, stated precisely

A player quotes "I parsed 680 on that fight." A tool author compares it against a computed 483 and concludes the model is 29% low. Both numbers are correct. They are answers to different questions, and nothing in either number says which question.

The corpus contains a worked instance. `jos437-finishing-blow.log`, one file, one character, one stretch of play, four defensible readings of the same damage:

| reading | value | denominator |
|---|---|---|
| whole-file wall clock | **265** | 786 s, first damage event to last |
| active combat time | **483** | 431 s, gaps > 6 s excluded |
| best 60 s | **581** | 60 s |
| best 30 s | **678** | 30 s |

Highest ÷ lowest = **2.56×**. All four are Tier M off the same file. No convention is wrong. The error is the comparison.

Across the 29 corpus fights that qualify, the median spread between those same four readings on a *single file* is **1.76×**, and the worst is **4.27×** (`w48-special-lane-reset.log`). That 1.76 median is the figure the project brief has been carrying as "up to 1.75×" — it is a median, not a maximum, and the tool should say so.

**What the tool is.** A page with two halves: a registry saying exactly what each shipped meter divides by, with file-and-line citations; and a converter that will translate between the conventions that *can* be translated and **refuse, with a reason, on the ones that cannot**. The refusal is the most valuable single behaviour in the tool.

---

## A1. The denominator registry — Tier M, read from shipped source

Four Legends log tools ship. Between them they print **nine** distinct damage-rate figures over **four** denominator families, using **three** different gap constants and **two** different idle timeouts. Every row below was read out of the code in the committed corpus at `scratchpad/corpus/<tool>/`.

| # | Tool | Printed figure | Family | Exact definition | Citation |
|---|---|---|---|---|---|
| 1 | **eql-meter** (Rust/Tauri) | `total_dps` | ELAPSED | `total / duration`, where `duration = (ended_at − started_at).max(1.0)` — gaps included. A fight closes after 10 s with no hit. | `src-tauri/src/fight/mod.rs:347` (and `:1657`); `fn duration` `:223–226`; `const IDLE_SECS: f64 = 10.0` `:12`, applied `:1141` |
| 2 | **eql-meter** | `peak_dps` | WINDOW 3 s | `peak_rolling_dps(&timeline, 3)`, per-second buckets, divides by `(i+1).min(window)` so a short fight is handled correctly | `:326`, `:348`; fn `:1859–1884` |
| 3 | **EQBuddy** (C#) | `SessionDps` | ACTIVE, session-summed | `combatDamage / combatSeconds`. A combat segment stays live while **any nearby combat signal** arrives within `CombatGap = 10 s` — including group members hitting or being hit — with `BystanderGrace = 20 s` capping how long someone else's fight may extend your clock. | `src/EQBuddy.Core/SessionStats.cs:1692`; `CombatGap` `:15`; `BystanderGrace` `:19`; the intent comment `:9–13` |
| 4 | **EQBuddy** | `currentDps` | ELAPSED, live segment | `_combatDamage / dur`, `dur = Math.Max(1, (last − start).TotalSeconds)` | `:1684`, `:1690` |
| 5 | **everquest-companion** (Electron/TS) | `outDps` | ELAPSED, per segment | damage ÷ `durationSec` | `src/shared/combat.ts:383`, `:377` |
| 6 | **everquest-companion** | `activeDps` | ACTIVE, **gap cap 3 s** | damage ÷ `activeSec` — the field's own doc: *"Sum of active combat time (gaps between consecutive attributed damage hits capped at 3s each — standard meter convention)"* | `combat.ts:379–381`, `:384–385`; both figures rendered: `DpsCard.tsx:85`, `SegmentHeader.tsx:50–56` |
| 7 | **eql-log-reader** (Python) | fight average | ACTIVE, **gap cap 10 s** | `total / Fight.elapsed()`; `elapsed() = max(active_secs, 1.0)`; `touch()` accumulates `min(gap, ACTIVE_GAP_CAP)` | `eql_combat_tracker.py:765–769`; `touch` `:746–763`; `ACTIVE_GAP_CAP = 10.0` `:185` |
| 8 | **eql-log-reader** | rolling 10 s / 30 s, and a last-60 s column | WINDOW 10 / 30 / 60 | `rolling_sum(key, window)` | `:1151`; `ROLLING_MAX_WINDOW = 60.0` `:191`; `README.md:57` |
| 9 | **eql-log-reader** | `Fight.span()` | ELAPSED — **display only** | its own docstring: *"for the fight-timer display only; rates use elapsed()"* | `:771–774` |

Two constants that look like denominators and are not:

- **eql-log-reader `IDLE_TIMEOUT = 45.0`** (`:184`, user-selectable 5–60 s). `RELEASE_NOTES.md:248` states it outright: *"Rates still divide by ACTIVE combat time … so the timeout changes how fights are grouped, not the math."* It moves which events share a denominator, not what the denominator is.
- **eql-meter `IDLE_SECS = 10.0`** does the same job for fight boundaries.

The tool must present these separately, because a reader who changes the timeout and sees the number move will otherwise conclude the denominator changed.

---

## A2. What is convertible, and what is not — Tier M

This is the substance of the tool, and it is not what the project brief assumed.

I re-derived engaged DPS on all 29 qualifying corpus fights under four different active-time rules and compared each against a reference (gap-split at 6 s, no cap — the rule `tools/convention.py` uses).

| rule | who uses it | median vs reference | range |
|---|---|---|---|
| gap cap **3 s** | everquest-companion `activeDps` | **1.000** | 0.95 – 1.08 |
| gap split **6 s** | this project's `convention.py` | 1.000 (reference) | — |
| gap cap **10 s** | eql-log-reader `elapsed()`; EQBuddy's floor | **0.946** | 0.71 – 1.00 |
| full **elapsed** | eql-meter `total_dps`, companion `outDps` | **0.883** | **0.26 – 1.00** |

Three conclusions, and the tool is built on them:

**1. The active-time family is effectively one convention.** A 3-second cap and a 6-second split give the *same* answer to within ±8%, median exactly 1.00. A 10-second cap reads about 5% lower, worst case 29% lower on a loot-heavy log. Convert with a stated band; do not pretend to a decimal place.

**2. ELAPSED and WALL are not convertible, and the tool must refuse.** The elapsed/active ratio ranges 0.26 to 1.00 across the corpus. That ratio is a property of *how much downtime the log happens to contain* — looting, running, medding — not a property of the fight, the character or the game. There is no constant to publish, and publishing the 0.883 median as one would be the exact false precision this tool exists to prevent. A converter that outputs a number here is worse than one that says *"cannot convert: the answer depends on your downtime, which is in your log and not in this table."*

**3. Window ↔ active-time is convertible**, because both read the same damage stream and differ only in window width. That is the measured curve in §A3.

There is a fourth conclusion that only fell out when I read the window code, and it is a convention nobody names:

**4. The window *boundary rule* is itself a convention worth 17%.** Log timestamps have one-second resolution. If a "10-second window" is defined as `t − t₀ ≤ 10` it spans **eleven** distinct timestamp seconds; if `t − t₀ < 10`, ten. Measured effect on the ratio:

| window | inclusive (`≤ w`) | half-open (`< w`) | inflation |
|---|---|---|---|
| 3 s | 3.64 | 3.11 | **+17.0%** |
| 10 s | 2.06 | 1.89 | +9.0% |
| 30 s | 1.47 | 1.42 | +3.8% |
| 60 s | 1.23 | 1.22 | +0.8% |

This project's own `tools/convention.py` uses the inclusive form. **The brief's headline ratios 1.22 / 1.46 / 2.03 are the inclusive readings**, and are 1–9% high at the short windows. The tool ships the half-open figures and states the rule on the page, because "best 10 seconds" that covers eleven seconds is not a defensible reading.

---

## A3. The burstiness table — Tier M, the tool's only measured constant

Ratio of *best-w-second window DPS* to *active-time DPS*, per fight. Windows half-open `[t₀, t₀+w)`; denominator = damage ÷ summed active time with a 6-second gap split.

**Corpus:** 29 fixture logs, all 29 distinct by md5. Qualification: ≥ 120 attributed damage events and engaged DPS ≥ 40, applied to the 138-log corpus. Median span 253 s, median 398 damage events, median engaged DPS 203.

| w (s) | **median** | mean | p25 | p75 | min | max | fights below 1.0 |
|---|---|---|---|---|---|---|---|
| 3 | **3.11** | 3.16 | 2.40 | 3.72 | 1.93 | 5.42 | 0 |
| 6 | **2.27** | 2.38 | 1.95 | 2.75 | 1.53 | 3.58 | 0 |
| 10 | **1.89** | 1.88 | 1.50 | 2.19 | 1.34 | 2.56 | 0 |
| 15 | **1.73** | 1.68 | 1.35 | 1.93 | 1.14 | 2.24 | 0 |
| 20 | **1.53** | 1.57 | 1.29 | 1.84 | 1.05 | 2.04 | 0 |
| 30 | **1.42** | 1.41 | 1.18 | 1.62 | 0.97 | 1.90 | 3 |
| 45 | **1.31** | 1.28 | 1.11 | 1.45 | 0.66 | 1.66 | 2 |
| 60 | **1.22** | 1.20 | 1.03 | 1.36 | 0.57 | 1.61 | 3 |
| 90 | **1.14** | 1.11 | 1.00 | 1.21 | 0.65 | 1.50 | 5 |

**The "fights below 1.0" column is not an error and must ship.** A best-60 s reading can come out *below* active-time DPS whenever the fight is bursty and shorter than the window: `w51-round-flurry-era.log` packs 256 DPS into 59 s of active time inside a 93 s span, and no 60-second window can match that density. This is why the tool converts to a **band**, and why the p25 column is on the page and not in a footnote.

---

## A4. Honest confidence, and what would sharpen it

**What the ratios are.** A point estimate of the median of a distribution, over 29 fights, from one corpus.

**How much to trust them, item by item:**

- **The ordering is certain.** r(3) > r(6) > r(10) > … > r(90) holds on every fight individually, by construction — a smaller window can never contain less peak density than a larger one. Nothing about the corpus can overturn it.
- **The magnitudes are a rule of thumb, not a constant.** The interquartile range at w = 60 is 1.03–1.36. Quoting "×1.22" to three figures on a single unknown fight would be false precision; the honest statement is *"typically 1.0 to 1.4, median 1.22."*
- **The corpus is one player, near enough.** All 138 logs come from a single upstream fixture directory (`everquest-companion/tests/fixtures`). On the evidence of the `cw*`/`wl*` loadout-swap series and a single named inventory dump, they are essentially one character across class swaps. **These are not 29 independent samples of "an EverQuest Legends fight."** They are 29 fights by one player, and the tool must say so on the page.
- **The composition is not controlled.** Class trio, target count, buff state and content tier all move burstiness — a Wizard chaining a nuke line and a Warrior autoattacking have different curves, and the corpus cannot separate them.
- **The tail is degenerate.** At w = 90, most fights are shorter than the window, so r → 1 by arithmetic rather than by measurement. Do not extrapolate past 60.
- **One row of `convention.py` is an artefact and is excluded here.** The shipped script divides by the window width even when the fight is shorter than the window; `w49-round-triple-backstab.log` (39 s span) reports best-60/engaged = 0.65 for that reason alone. The tool's implementation divides by `min(w, span)` and **excludes** any fight whose span is under the window rather than reporting it. Exactly one of 29 rows is affected; the medians survive, but the rule must be stated because a reader re-running the script will see a number the page does not have.

**What would sharpen them, in descending order of value:**

1. **Logs from other players.** The single largest weakness is not n, it is that n is one person. Twenty fights from five characters would beat two hundred from one. The site already accepts contributed logs and already warns not to attach them publicly.
2. **Stratification by class trio and by target count.** A caster AE fight and a melee single-target fight almost certainly have different curves; pooling them is the reason the IQR is as wide as it is. This is free once (1) exists.
3. **The same fight read by two meters.** Run one log through eql-log-reader and everquest-companion and record both figures. That converts the §A2 gap-rule factors from *derived from my re-implementation* to *observed on the shipping tools*, which is a tier promotion and the cheapest real improvement available today.
4. **A `%` fight-duration control.** Restricting to fights of 120–400 s would remove the short-fight artefacts that produce the sub-1.0 rows without hiding them.

**What would NOT sharpen them:** more fixture logs from the same directory. That raises n and does not touch the thing that is actually uncertain.

---

## A5. The converter — real JavaScript

Single file, no dependencies, pure functions. Ships as `convention.js` beside the page and is also the page's own engine, so the printed table and the live answer cannot drift.

```js
// ─────────────────────────────────────────────────────────────────────────────
// convention.js — DPS parse-convention converter
//
// Tiers: every constant below is Tier M. The meter registry is read from
// shipped source (file:line on each row). The burstiness table is measured on
// 29 EverQuest Legends combat logs; see BURST.provenance.
//
// Design rule: this module returns null and a reason rather than a number
// whenever the conversion is not defined. Callers must render the reason.
// ─────────────────────────────────────────────────────────────────────────────

/** The four denominator families. */
export const FAMILY = {
  ACTIVE:  'active',   // damage ÷ summed active combat time (gap-capped or gap-split)
  ELAPSED: 'elapsed',  // damage ÷ (fight end − fight start), gaps included
  WALL:    'wall',     // damage ÷ whole-file or whole-session span
  WINDOW:  'window',   // damage in the best N-second window ÷ N
}

/**
 * Every rate figure the four shipped Legends meters print.
 * `gapCap` is in seconds; null means "no cap — gaps count in full".
 * `cite` is file:line in the tool's own repository, Tier M.
 */
export const METERS = [
  { id: 'eql-meter/total_dps',        tool: 'eql-meter',            label: 'DPS',
    family: FAMILY.ELAPSED, gapCap: null,
    cite: 'src-tauri/src/fight/mod.rs:347 (duration() :223-226, IDLE_SECS :12)' },
  { id: 'eql-meter/peak_dps',         tool: 'eql-meter',            label: 'Peak',
    family: FAMILY.WINDOW,  window: 3, bucketed: true,
    cite: 'src-tauri/src/fight/mod.rs:326, peak_rolling_dps :1859' },
  { id: 'eqbuddy/SessionDps',         tool: 'EQBuddy',              label: 'Session DPS',
    family: FAMILY.ACTIVE,  gapCap: 10, bystanderExtended: true,
    cite: 'src/EQBuddy.Core/SessionStats.cs:1692 (CombatGap :15, BystanderGrace :19)' },
  { id: 'eqbuddy/currentDps',         tool: 'EQBuddy',              label: 'Current DPS',
    family: FAMILY.ELAPSED, gapCap: null,
    cite: 'src/EQBuddy.Core/SessionStats.cs:1684' },
  { id: 'companion/outDps',           tool: 'everquest-companion',  label: 'DPS',
    family: FAMILY.ELAPSED, gapCap: null,
    cite: 'src/shared/combat.ts:383' },
  { id: 'companion/activeDps',        tool: 'everquest-companion',  label: 'act',
    family: FAMILY.ACTIVE,  gapCap: 3,
    cite: 'src/shared/combat.ts:379-385' },
  { id: 'logreader/fightAverage',     tool: 'eql-log-reader',       label: 'fight average',
    family: FAMILY.ACTIVE,  gapCap: 10,
    cite: 'eql_combat_tracker.py:765-769 (ACTIVE_GAP_CAP :185)' },
  { id: 'logreader/rolling',          tool: 'eql-log-reader',       label: 'rolling 10s/30s/60s',
    family: FAMILY.WINDOW,  window: null /* user picks 10, 30 or 60 */,
    cite: 'eql_combat_tracker.py:1151 (ROLLING_MAX_WINDOW :191)' },
]

/**
 * Best-w-second window DPS ÷ active-time DPS.
 * Measured on 29 EverQuest Legends fixture logs (all distinct by md5),
 * half-open windows [t0, t0+w), active time = gap-split at 6 s.
 * Fights whose span is shorter than w are excluded, not reported.
 */
export const BURST = {
  provenance: {
    tier: 'M', n: 29, source: 'everquest-companion/tests/fixtures/*.log',
    qualify: '>=120 attributed damage events and active DPS >= 40',
    windowRule: 'half-open [t0, t0+w); an inclusive (<= w) rule reads 17% high at w=3 and 0.8% high at w=60',
    caveat: 'one upstream fixture directory, essentially one player across class swaps',
  },
  //  w   median  p25   p75
  rows: [
    [  3,  3.11, 2.40, 3.72 ],
    [  6,  2.27, 1.95, 2.75 ],
    [ 10,  1.89, 1.50, 2.19 ],
    [ 15,  1.73, 1.35, 1.93 ],
    [ 20,  1.53, 1.29, 1.84 ],
    [ 30,  1.42, 1.18, 1.62 ],
    [ 45,  1.31, 1.11, 1.45 ],
    [ 60,  1.22, 1.03, 1.36 ],
  ],
  minW: 3, maxW: 60,
}

/**
 * Active-time DPS under a given gap rule, relative to the 6-second-split
 * reference. Tier M, same 29 fights. `lo`/`hi` are the observed range, not a
 * confidence interval — the corpus is too small and too correlated for one.
 */
export const GAP_RULE = {
  3:    { median: 1.000, lo: 0.95, hi: 1.08, note: 'agrees with the reference; treat as identical' },
  6:    { median: 1.000, lo: 1.00, hi: 1.00, note: 'the reference rule' },
  10:   { median: 0.946, lo: 0.71, hi: 1.00, note: 'reads lower; worst case on loot-heavy logs' },
}

/** Log-linear interpolation across BURST.rows. Returns null outside [3, 60]. */
export function burstRatio(w) {
  if (!(w > 0)) return null
  const R = BURST.rows
  if (w < BURST.minW || w > BURST.maxW) return null   // refuse to extrapolate
  for (let i = 0; i < R.length; i++) {
    if (w === R[i][0]) return { median: R[i][1], lo: R[i][2], hi: R[i][3], exact: true }
  }
  for (let i = 0; i < R.length - 1; i++) {
    const [w0, m0, l0, h0] = R[i], [w1, m1, l1, h1] = R[i + 1]
    if (w > w0 && w < w1) {
      const f = (Math.log(w) - Math.log(w0)) / (Math.log(w1) - Math.log(w0))
      const mix = (a, b) => a + f * (b - a)
      return { median: mix(m0, m1), lo: mix(l0, l1), hi: mix(h0, h1), exact: false }
    }
  }
  return null
}

/**
 * Convert a quoted rate from one convention to another.
 *
 * from / to: { family, window?, gapCap? }
 *
 * Returns either
 *   { ok: true,  value, low, high, exact, basis, caveats }
 * or
 *   { ok: false, reason, whatWouldHelp }
 *
 * There is no third state. A caller that renders `value` without also
 * rendering `low`, `high` and `basis` has reintroduced the error this tool
 * exists to prevent.
 */
export function convert(value, from, to) {
  const refuse = (reason, whatWouldHelp) => ({ ok: false, reason, whatWouldHelp })
  if (!(value > 0)) return refuse('Enter a rate above zero.', null)

  const undefinedFamily = f =>
    f.family === FAMILY.ELAPSED || f.family === FAMILY.WALL

  // Identity — including elapsed→elapsed, which is fine.
  if (from.family === to.family &&
      (from.window ?? null) === (to.window ?? null) &&
      (from.gapCap ?? null) === (to.gapCap ?? null)) {
    return { ok: true, value, low: value, high: value, exact: true,
             basis: 'Same convention — nothing to convert.', caveats: [] }
  }

  // The refusal that matters most.
  if (undefinedFamily(from) || undefinedFamily(to)) {
    return refuse(
      'Wall-clock and fight-elapsed rates cannot be converted by any published ' +
      'factor. The gap between them and active-time DPS is set by how much ' +
      'downtime your log happens to contain — looting, running, medding — not ' +
      'by the fight, the character or the game. On this corpus that ratio runs ' +
      'from 0.26 to 1.00, so any single constant would be wrong most of the time.',
      'Re-read the same log with a meter that prints an active-time figure ' +
      '(everquest-companion `activeDps`, eql-log-reader fight average) and ' +
      'convert from that instead.')
  }

  const caveats = []

  // Step 1 — normalise the source onto the reference active-time denominator.
  let lo = value, mid = value, hi = value
  if (from.family === FAMILY.ACTIVE) {
    const g = GAP_RULE[from.gapCap]
    if (!g) return refuse(
      `No measurement for a ${from.gapCap}-second gap rule.`,
      'Measured rules are 3 s, 6 s and 10 s.')
    mid /= g.median; lo /= g.hi; hi /= g.lo
    if (from.gapCap !== 6) caveats.push(
      `Source uses a ${from.gapCap}s gap cap; normalised by ${g.median} ` +
      `(observed ${g.lo}–${g.hi}).`)
    if (from.bystanderExtended) caveats.push(
      'EQBuddy extends its combat clock on group members\u2019 activity ' +
      '(BystanderGrace 20 s, SessionStats.cs:19). No fight in this corpus ' +
      'exercises that rule, so its effect is unmeasured and this figure is a ' +
      'lower bound on the correction.')
  } else if (from.family === FAMILY.WINDOW) {
    const r = burstRatio(from.window)
    if (!r) return refuse(
      `No measurement for a ${from.window}-second window.`,
      'Measured windows run 3 s to 60 s. Outside that the tool will not extrapolate.')
    mid /= r.median; lo /= r.hi; hi /= r.lo
    if (from.bucketed) caveats.push(
      'eql-meter aggregates into whole-second buckets before taking its 3 s ' +
      'peak (fight/mod.rs:1859); this table slides over events, so the source ' +
      'figure is if anything the lower of the two.')
  }

  // Step 2 — project onto the target denominator.
  if (to.family === FAMILY.ACTIVE) {
    const g = GAP_RULE[to.gapCap]
    if (!g) return refuse(
      `No measurement for a ${to.gapCap}-second gap rule.`, 'Measured rules are 3 s, 6 s and 10 s.')
    mid *= g.median; lo *= g.lo; hi *= g.hi
  } else if (to.family === FAMILY.WINDOW) {
    const r = burstRatio(to.window)
    if (!r) return refuse(
      `No measurement for a ${to.window}-second window.`,
      'Measured windows run 3 s to 60 s. Outside that the tool will not extrapolate.')
    mid *= r.median; lo *= r.lo; hi *= r.hi
  }

  if (lo > hi) [lo, hi] = [hi, lo]          // both legs inverted: restore order
  caveats.push(
    'Band is the interquartile range of 29 fights from one corpus, not a ' +
    'confidence interval. Three of those fights read below 1.0 against their ' +
    'own 60 s window, so a value under the low end is possible on a short ' +
    'bursty fight.')

  return { ok: true, value: mid, low: lo, high: hi, exact: false,
           basis: 'Tier M, 29 EverQuest Legends fights, half-open windows.',
           caveats }
}

/** Convenience: convert between two registry entries by id. */
export function convertBetweenMeters(value, fromId, toId, windows = {}) {
  const find = id => {
    const m = METERS.find(x => x.id === id)
    return m && { ...m, window: m.window ?? windows[id] ?? null }
  }
  const a = find(fromId), b = find(toId)
  if (!a || !b) return { ok: false, reason: 'Unknown meter figure.', whatWouldHelp: null }
  return convert(value, a, b)
}
```

### Worked example the page should carry

> Someone quotes **680** off eql-log-reader's rolling 30-second window. Your model computes a sustained figure. Are you 41% low?
>
> `convertBetweenMeters(680, 'logreader/rolling', 'companion/activeDps', {'logreader/rolling': 30})`
> → 680 ÷ 1.42 × 1.000 = **479**, band **420 – 576**.
>
> A model at 483 is inside the band and within 1% of centre. Nothing is wrong with the model. The two numbers were never the same measurement. *(This is `jos437-finishing-blow.log`: its true active-time reading is 483 and its true best-30 s is 678.)*

### Edge cases the implementation must handle

| case | behaviour |
|---|---|
| `from` or `to` is ELAPSED or WALL | **refuse**, with the downtime explanation and the "re-read with an active-time meter" suggestion |
| window outside 3–60 s | **refuse**; no extrapolation, ever |
| window between table rows | log-linear interpolation, `exact: false` |
| identical conventions | return the input unchanged, `exact: true` |
| fight shorter than the window | not the converter's problem, but the *measurement* pipeline must divide by `min(w, span)` **and exclude** the fight from the table; state the rule on the page |
| EQBuddy as source | attach the BystanderGrace caveat — unmeasured, corpus could not contain it |
| eql-meter `peak_dps` as source | attach the bucketing caveat |
| band inverts (both legs divide and multiply) | swap `lo`/`hi` before returning |
| user changes eql-log-reader's Combat timeout | page note: this regroups fights, it does not change the denominator (`RELEASE_NOTES.md:248`) |

### UI

Three controls — quoted number, source figure (a dropdown of the nine registry rows, each showing its tool and its `file:line`), target figure. One output: **a range, with the median inside it**, never a bare number. Below it, the caveat list, verbatim, always. Below that, the registry table and the burstiness table as static content, so the page is useful with JavaScript off.

The page must **not** contain a "DPS calculator". It converts a number the reader already has. It computes nothing about the game.

---

---

# TOOL B — THE AE TARGET-CAP REFERENCE

## B0. The error, stated precisely

Target caps on EverQuest Legends area spells are published in the eqlwiki spell page's `description =` template parameter. **Almost every scraper drops that parameter**, because it is prose in a page otherwise full of clean fields. Downstream, an AE spell with a stated 4-target cap is modelled as scaling linearly with the pull, and a Wizard "quad-kite" spell is ranked as though it kills eight.

This project made exactly that error and recorded it: `DDD.md §1` — *"I previously wrote 'no AE spell in the game states a target cap, so damage scales linearly with the pull, unbounded.' That is false."* The cause was reading the `effects` field, which the local spell database carries, and never fetching `description`, which it does not.

**What the tool is.** A published dataset — `ae-caps.v1.json`, a fifth file on `/data/` — plus a small reference page. One row per area spell available at level ≤ 50, carrying **separate** fields for target cap, total-hits cap, wave count, indoor/outdoor gate and mob-level gate, each with the verbatim source string it came from and its own tier.

**The single most important design decision:** those are five different mechanics and must never collapse into one `cap` column. The project brief itself collapsed two of them and got a spell family wrong as a result (§B3).

---

## B1. Scope and method

Source: eqlwiki `{{Spellpagesmart}}` wikitext, from the harvest cache committed at `corpus/EQBuddy/scripts/harvests/eqlwiki/cache/` (3,126 pages).

Selection rule, stated so it is reproducible: `target_type` contains `AE`, and at least one entry in `classes` is at level ≤ 50. That gives **72 spells**, of which **49 carry damage**. (The project brief's "34 AE spells at level ≤ 50" is a narrower damage-only filter; both counts should ship, with the rule beside each.)

Tier discipline, and it is the crux of this tool:

> The `description =` parameter is a **structured container holding prose**. The tier attaches to the *contents*, not to the wrapper. A target cap read out of `description` is **Tier 5**, however machine-shaped the template around it is.

The evidence that this is not pedantry is inside the same field. `Gravity Flux`'s description also contains *"Two different incompatible versions of this spell exists in game"* and *"Please confirm damage at various levels."* `Avalanche`'s contains a mana-efficiency argument comparing it to Firestrike. These are editorial notes, not data. And nine of the capped pages open with `<noinclude>{{Classic Era}}</noinclude>` — the wiki's own marker that the content is a classic-era record awaiting Legends verification.

So every row carries `capTier: 5` and the verbatim string, and the page says why.

---

## B2. Data table 1 — explicit numeric target caps (T5, verbatim)

Eleven spells state a number. Verbatim strings, from the `description` field of each named page.

| Spell | Type | Classes ≤ 50 | **Cap** | Verbatim source string | `{{Classic Era}}` |
|---|---|---|---|---|---|
| Invoke Lightning | Targeted AE | DRU 4, RNG 15 | **4** | *"causing damage to your target and up to 3 others nearby (outdoor only spell)"* | yes |
| Pillar of Fire | Targeted AE | WIZ 15 | **4** | *"to at most 4 creatures in the vicinity of your target"* | yes |
| Column of Lightning | Targeted AE | WIZ 24 | **4** | *"to several (up to 4) creatures in the vicinity of your target"* | yes |
| Lightning Strike | Targeted AE | DRU 31 | **4** | *"and up to 3 others nearby … This spell can hit at most 4 targets. Only castable outdoors."* | yes |
| Circle of Force | Targeted AE | WIZ 31 | **4** | *"Hits up to 4 creatures max"* (also *"several creatures"* earlier in the same string) | yes |
| Gravity Flux | Targeted AE | ENC 36, WIZ 43 | **4** | *"Only hits 4 mobs max"* | yes |
| Infectious Cloud | Targeted AE | NEC 15, SHM 15 | **4** | *"to all beings [4 targets] in a small area around your target"* | yes |
| Denon's Desperate Dirge | Targeted AE | BRD 43 | **8** | *"causes between 311 and 405 damage to up to 8 enemies"* | no |
| Entrancing Lights | PB AE | ENC 30 | **8** | *"Cause up to 8 nearby creatures to fall into an enchanted sleep"* (mez, not damage) | yes |
| Tremor | PB AE | DRU 21, CLR 34 | **24** | *"causing between 106 and 122 damage to as many as 24 others nearby"* | no |
| Earthquake | PB AE | DRU 31, CLR 44 | **25** | *"causing between 214 and 246 damage to up to 25 nearby creatures"* | no |

**Corrections to the project brief carried by this table, all verified:**

- **Tremor is 24, not 25.** Its description says *"as many as 24 **others** nearby"* — and it is a PB AE, so the caster is not among them. Earthquake, the same spell family with the same opening clause, says 25. Two adjacent numbers on two pages describing the same mechanic. Ship both as written and **flag the one-apart discrepancy on the page** rather than smoothing it; the flag is more useful than a guess.
- **Avalanche and Pogonip do not belong here at all.** See §B3.
- **Three capped spells the brief missed** — Circle of Force, Invoke Lightning, Infectious Cloud — one of which (Infectious Cloud) states its cap in square brackets, `[4 targets]`, which no plausible cap-word regex catches.
- **Lightning Strike is outdoors-only too.** The outdoor gate is not unique to Lightning Blast.

---

## B3. Data table 2 — total-hits caps (a different mechanic)

Three spells cap **hits across waves**, not targets. Collapsing this into a `cap` column would publish a wrong number.

| Spell | Class | Waves | Per-wave dmg | Cap | Verbatim |
|---|---|---|---|---|---|
| Cascade of Hail | DRU 12 | 3 | 27 | **4 hits total** | *"up to a maximum of 4 targets hit … Note: Rain nukes are limited to 4 hits total. Either you can hit the same mobs 3 times, you can hit 2 mobs twice each, or you can hit 4 mobs once each."* |
| Pogonip | DRU 22 | 3 | 62 | **4 hits total** | identical note, plus *"WARNING: This spell WILL NOT deal the final killing blow to any mob. Instead, it will just resist to infinity."* |
| Avalanche | DRU 37 | 3 | 125 | **4 hits total** | identical note |

Read the wiki's own sentence: four hits *total*, distributable as one mob hit three times, two mobs hit twice, or four mobs hit once. A single-target cast of Avalanche therefore lands 3 waves × 125 = 375, and a four-mob cast lands 125 each. **A `targetCap: 4` field would tell a reader the opposite of the truth about the single-target case.** This is why the schema has `hitsTotalCap` as its own key.

Pogonip's killing-blow warning is a genuine mechanic note that belongs on the row and appears nowhere else.

---

## B4. Data table 3 — inferred, gated, and unstated

**Inferred, never stated numerically — one spell, and it must be marked as inference:**

| Lightning Blast | Targeted AE | DRU 46 | cap **4, inferred** | *"2.04 damage per mana on a single target, 8.15 damage per mana on a full quad. Outdoors only."* |

The 4 comes from the word *quad* and from 8.15 ÷ 2.04 = 3.99. That is a good inference and it is still an inference. Ship it as `targetCap: null, targetCapInferred: 4, inferredFrom: "damage-per-mana ratio 8.15/2.04 = 3.99 and the word 'quad'"`.

**Outdoor gate (T5):** Invoke Lightning, Lightning Strike, Lightning Blast, Sunbeam, Harmony.

**Mob-level gate (T5), which is not a target cap:** Color Flux / Color Shift / Color Skew / Mesmerization / Entrancing Lights (level 55), Harmony (level 40). Only Entrancing Lights carries both a level gate and a target cap.

**Unstated — and this is a column, not an absence.** Fourteen damage-bearing AE spells at level ≤ 50 state no cap of any kind, including every spell in the Wizard storm line (Firestorm, Lightning Storm, Energy Storm, Lava Storm, **Frost Storm**), every Magician rain (Rain of Blades / Fire / Spikes / Lava / Swords), both Shaman rains (Poison Storm, Gale of Poison), Icestrike, Supernova, Upheaval and the whole Word Divine / Word of Souls / Word of Spirit line.

The site's own discipline applies exactly: **a dry streak is a ceiling, not a zero.** `capState: "unstated"` is not `capState: "uncapped"`, and the page must say so in one sentence.

Two further observations that only appear when the families are laid side by side, and that belong on the page as findings:

- **The rain mechanic is documented three different ways in the same wiki.** The Druid hailstorm line (Cascade of Hail, Pogonip, Avalanche) states the 4-hits-total rule verbatim. The Wizard storm line states nothing. The Magician rain line states nothing *and has no structured slot row at all* — its only damage figure lives in the prose. Same mechanic, three authoring states.
- **`Supernova` is the false positive to beware.** Its description contains *"farming large groups of up to 25 lower level mobs for a mana efficiency of up to 24.4 dmg/mana"*. That 25 is a worked example of a pull size, not a cap. A regex hunting `up to (\d+)` near an AE spell will pick it up and produce a cap of 25 identical in shape to Earthquake's real one. The extractor must not accept it, and the page should show it as the worked counter-example.

---

## B5. The damage columns, and why they get three values

Publishing per-target damage in this table is tempting and is where it can go wrong. On the Wizard storm line the description prose, the structured slot row and the measured client log give **three different numbers**:

| Spell | `description` (T5) | `SpellSlotRowSmart` slot 1 (T2) | measured in corpus (M) |
|---|---|---|---|
| Firestorm | 28 per wave | `Decrease Hitpoints by 41` | — |
| Lightning Storm | 75 per wave | `Decrease Hitpoints by 115` | — |
| Energy Storm | 96 per wave | `Decrease Hitpoints by 238` | — |
| Lava Storm | 128 per wave | `Decrease Hitpoints by 401` | — |
| **Frost Storm** | **250** per wave | **512** | **741** per wave |
| Earthquake | 214–246 | `214 (L31) to 246 (L39)` | **246** |

Earthquake's three readings agree. Frost Storm's three readings are 250, 512 and 741 — a 2.96× spread, and the measured value is the one that matches none of them. (`p4-pet-buff-kill-credit.log`, Tier M: three waves at +1 s, +4 s, +7 s after the cast, each printing 741; crits at 2246 and 2059, ×3.03 and ×2.78 of 741, consistent with this project's measured ×3.00 spell-crit constant. The 391 and 116 lines are partial resists.) Also note the Druid rain line's description and slot row agree exactly (27/27, 62/62, 125/125), so the disagreement is a property of the Wizard storm pages, not of the field.

**Design consequence.** The dataset's primary payload is caps, gates and wave counts. Damage ships as three separately-tiered, separately-named fields — `dmgDescription` (T5), `dmgSlotRow` (T2), `dmgMeasured` (M, mostly null) — never as one `damage`. The page prints all three where they differ and highlights the disagreement. That is a contribution: nobody currently publishes the fact that they disagree.

**A related hazard, verified, that belongs on the same page.** Bard's three passive point-blank AE songs have their per-tick damage in two structured places that disagree by 7×:

| Song | Spell page `SpellSlotRowSmart` (T2) | Class page `RadSpellRow2 max=` under a "Max Effect" header (T2) |
|---|---|---|
| Chords of Dissonance | `Decrease Hitpoints by 2 per tick` | `-14 HP/tick` |
| Denon's Disruptive Discord | `Decrease Hitpoints by 4 per tick` | `-16 HP/tick` |
| Selo's Chords of Cessation | `Decrease Hitpoints by 2 per tick` | `-27 HP/tick` |
| **total** | **8/tick** | **57/tick** |

*(`cache/class-Bard.wikitext` lines 180–189, 631–635, 1622–1631; the three spell pages' own slot rows.)*

The project brief has been treating 57/tick as the level-50 answer. **It is not established.** On the same class-page row, Cessation's attack-speed max reads `-25% Atkspd` while its spell page says *"Decrease Attack Speed by 17% (L48) to 20% (L60)"* — so the class page's "max" is not the level-60 value either, and neither field is anchored to a level. And a Tier M reading refutes both as the observed number: `r3-song-shared-message.log` prints **19 lines of `has taken 8 damage from your Denon's Disruptive Discord`** — exactly twice the spell page's 4 and exactly half the class page's 16.

So the tool ships this as an **unsettled row with three readings**, not as 57. The correct statement is: *two structured wiki fields disagree by 7× on Bard passive AE damage, neither states its level, and the one measured value matches neither.* A scraper reading only spell pages is wrong; a scraper reading only class pages is also wrong; and this is a general hazard, not a Bard quirk.

---

## B6. What the corpus can and cannot settle — stated because absence is not evidence

I tested every capped spell against the 138 logs. Maximum distinct targets observed inside a 4-second cluster:

| Spell | damage lines | clusters | max distinct targets seen |
|---|---|---|---|
| Frost Storm | 67 | 22 | 2 |
| Earthquake | 38 | 27 | **4** |
| Gravity Flux | 3 | 3 | 1 |
| Poison Storm | 3 | 1 | 1 |
| Denon's Disruptive Discord (ticks) | 19 hits + 8 resists | 21 | 3 |

**The largest AE pull anywhere in this corpus hit four mobs.** Therefore:

- No cap of 4 or above is **confirmed** by measurement, because a cap of 4 and a cap of 25 are indistinguishable when nobody pulled five.
- No cap is **refuted** either. Earthquake's 4 observed targets is consistent with its stated 25 and tells us nothing.
- **The corpus could not have contained the answer.** Under the site's own rule this is the case where absence of evidence is genuinely not evidence of absence, and the page should say so in those words.

Two measurement traps found while doing this, which belong on the page for anyone reproducing it:

- **Mob names repeat.** One Frost Storm cluster prints three hits on `a revultant rat`; distinct-name counting undercounts real targets badly. Any target-count parse needs the client's own disambiguation, which the log does not provide.
- **Passive AE songs log no cast line.** Symphonic Aura pulses print only the damage; there is no `You begin singing` to anchor a tick window to, and in the observed fight the per-target ticks are staggered across different seconds rather than landing together. A per-tick target count needs a window, and the window is a judgement call.

---

## B7. Schema — `ae-caps.v1.json`

```jsonc
{
  "version": 1,
  "generated": "2026-08-29",
  "selection": "eqlwiki {{Spellpagesmart}} pages whose target_type contains 'AE' and which have at least one class at level <= 50",
  "counts": { "spells": 72, "damageBearing": 49,
              "withTargetCap": 11, "withHitsTotalCap": 3, "inferredCap": 1, "unstated": 57 },
  "fieldTiers": {
    "description": "5 — prose inside a structured container; the tier attaches to the contents, not the wrapper",
    "slots": "2 — SpellSlotRowSmart, a structured effect row",
    "mana|casting_time|recast_time|resist|target_type": "2",
    "measured": "M — this project's 138 EverQuest Legends combat logs"
  },
  "spells": [
    {
      "name": "Lightning Strike",
      "targetType": "Targeted AE",
      "classes": [{ "class": "Druid", "level": 31 }],

      "targetCap": 4,                  // explicit, T5. null when unstated.
      "targetCapInferred": null,       // set only when derived; never merged into targetCap
      "hitsTotalCap": null,            // rain-nuke rule — a DIFFERENT mechanic
      "waves": 1,
      "outdoorsOnly": true,
      "mobLevelCap": null,
      "capState": "stated",            // stated | inferred | unstated  — never "uncapped"

      "capSourceField": "description",
      "capSourceVerbatim": "Calls down lightning from the sky, causing between 163 and 184 damage and up to 3 others nearby. (1.23 DPM) This spell can hit at most 4 targets. Only castable outdoors.",
      "capTier": "5",

      "dmgDescription": "163-184",
      "dmgSlotRow": "Decrease Hitpoints by 163 (L31) to 184 (L38)",
      "dmgMeasured": null,
      "dmgFieldsAgree": true,

      "mana": 149, "castTime": 4.50, "recastTime": 6.00, "resist": "Magic (0)", "skill": "Evocation",
      "classicEraMarker": true,        // page opens <noinclude>{{Classic Era}}</noinclude>
      "notes": []
    }
  ]
}
```

Five rules the schema enforces and the page states:

1. `targetCap` and `hitsTotalCap` are never both set, and never merged.
2. `capState: "unstated"` never means uncapped.
3. An inference lives in its own key with its reasoning.
4. Every cap carries the verbatim string it came from, so a reader can see the prose and disagree.
5. Damage is three fields, not one.

---

## B8. The extractor, and the traps it must survive

```js
/**
 * Pull cap / gate / wave facts out of an eqlwiki {{Spellpagesmart}} description.
 * Returns a partial row plus every string it matched, so a human can audit.
 * Tier of everything returned: 5. The caller must not promote it.
 */
export function parseAeDescription(desc, targetType) {
  const out = { targetCap: null, hitsTotalCap: null, waves: 1,
                outdoorsOnly: false, mobLevelCap: null,
                matched: [], rejected: [] }
  const hit = (re, fn) => {
    const m = desc.match(re)
    if (m) { fn(m); out.matched.push(m[0]) }
    return !!m
  }

  // ── REJECT FIRST. Three number-shaped things that are not target caps. ──
  //  (a) mob-level gates: "Works on mobs up to level 55"
  hit(/(?:creatures|mobs) up to level (\d+)/i, m => { out.mobLevelCap = +m[1] })
  //  (b) radii: Energy Storm's "AoE range: 25" — the same 25 Earthquake uses as a cap
  const RADIUS = /AoE range:\s*\d+/i
  //  (c) worked examples: Supernova's "farming large groups of up to 25 lower level mobs"
  const EXAMPLE = /(?:farming|groups of)[^.]*?up to \d+/i
  let scan = desc
  for (const re of [RADIUS, EXAMPLE]) {
    const m = scan.match(re)
    if (m) { out.rejected.push(m[0]); scan = scan.replace(re, ' ') }
  }

  // ── TOTAL-HITS CAP: check BEFORE target caps; the rain note also says "targets hit" ──
  if (/limited to (\d+) hits total/i.test(scan) || /maximum of (\d+) targets hit/i.test(scan)) {
    const m = scan.match(/limited to (\d+) hits total/i) || scan.match(/maximum of (\d+) targets hit/i)
    out.hitsTotalCap = +m[1]; out.matched.push(m[0])
  }

  // ── TARGET CAPS. "others" is relative to the target on a Targeted AE. ──
  if (out.hitsTotalCap === null) {
    const abs = [
      /up to (\d+) (?:nearby )?(?:creatures|enemies|mobs|targets)/i,
      /at most (\d+) (?:creatures|targets)/i,
      /\(up to (\d+)\) creatures/i,
      /(?:Only h|H)its up to (\d+) creatures max/i,
      /Only hits (\d+) mobs max/i,
      /\[(\d+) targets\]/i,                         // Infectious Cloud — no cap word at all
    ]
    for (const re of abs) if (hit(re, m => { out.targetCap = +m[1] })) break

    // "your target and up to 3 others" => 4 on a Targeted AE.
    // "as many as 24 others nearby"    => 24 on a PB AE: there is no target to add.
    if (out.targetCap === null) {
      hit(/(?:and )?(?:up to|as many as) (\d+) others/i, m => {
        out.targetCap = /Targeted AE/i.test(targetType) ? +m[1] + 1 : +m[1]
      })
    }
  }

  hit(/(three|two|four) waves/i, m => { out.waves = { two: 2, three: 3, four: 4 }[m[1].toLowerCase()] })
  hit(/[Oo]utdoors only|only castable outdoors|only works outdoors|outdoor only spell/, () => { out.outdoorsOnly = true })
  return out
}
```

**Every trap in that function is a real page, not a hypothetical:**

| trap | page | what a naive parser does |
|---|---|---|
| `AoE range: 25` | Energy Storm | reads 25 as a target cap, identical in shape to Earthquake's real 25 |
| `farming large groups of up to 25 lower level mobs` | Supernova | reads a worked example as a cap |
| `Works on mobs up to level 55` | Color Flux/Shift/Skew, Mesmerization | reads a *level* gate as a target cap |
| `potential maximum of 48 cold damage` | Icestrike | reads a *damage* maximum as a target cap |
| `[4 targets]` | Infectious Cloud | **misses** a real cap — no cap word present |
| `maximum of 4 targets hit` | Avalanche, Pogonip, Cascade of Hail | reads a hits-across-waves cap as a target cap; wrong on the single-target case by 3× |
| `up to 3 others` | Invoke Lightning, Lightning Strike | reads 3 where the answer is 4 (Targeted AE: the target counts) |
| `as many as 24 others` | Tremor | reads 25 where the answer is 24 (PB AE: no target to add) |
| `%T enemies` | Sacred Word | client template token, never substituted — the cap exists in the client string file and the wiki carries the placeholder |
| `between 14 and @1 damage` | Numbing Cold | same, on damage |
| `648 and 728 (Level 59)` | Upheaval | a level-59 figure on a level-50 game — classic residue in the description |
| `between 250 damage` | Frost Storm | malformed, one value where two are expected |

The `%T` case deserves one line on the page in its own right: it is direct evidence that the client *does* carry a target count for Sacred Word and that the wiki transcription lost it. That makes `capState: "unstated"` demonstrably a transcription state and not a game state, for at least one spell.

---

## B9. What would settle the open rows

| open question | what settles it | cost |
|---|---|---|
| Tremor 24 vs Earthquake 25 — real, or an editorial slip? | one pull of 25+ mobs with each, counting damage lines | one field trip |
| Is any "unstated" spell genuinely uncapped? | Supernova or Frost Storm into a pull larger than 8, counting distinct damage lines from one cast | one field trip; the highest-value single test on this page |
| Frost Storm 250 / 512 / 741 | a client spell tooltip at level 50 | one screenshot |
| Bard passive AE 8 vs 57 per tick | a client song tooltip at level 50, or a parse of a level-50 Bard log with all three songs up | one screenshot |
| Lightning Blast's 4 | the same spell tooltip, or a five-mob cast | one screenshot |
| Sacred Word's `%T` | the client's own string file, or one cast into a crowd | one screenshot |

Every one of those is a screenshot or a single pull. That is what makes this table worth publishing: it is a list of open questions each closable in one action, which is the shape the site's `still-true` page already uses.

---

## B10. Scope note for the site owner

`/tools/index.html` states the boundary: *"Client-mined numbers, spellbook diffing, AA planning and 3D zone geometry belong to other tools."* A 72-row AE cap table is not spellbook diffing, and it is squarely inside *"nobody in this community publishes machine-readable data … every tool re-transcribes the same wiki pages and inherits the same 1999 errors doing it"* — this is precisely such an error, caught and documented. But it is adjacent to that line and the owner may reasonably read it as the thin end. Offer it as a fifth dataset with the reference page as a thin reader over it, and let the owner decide whether the reader ships.

The converter has no such tension: it names four community tools and their fields, and it corrects nobody. It is the safer of the two to ship first.