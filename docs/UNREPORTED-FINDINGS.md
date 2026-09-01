# UNREPORTED FINDINGS — sky-ledger

Adopted 1 Sep 2026 under **R74**, from Session D's `EQLSLockouts:docs/UNREPORTED-FINDINGS.md`.

The Director ruled to Session C that *a finding shipping only as a source comment
has not been reported*. D pushed back and D was right: it is not a lapse, it is what
happens when the code is the only place a careful person writes things down. So the
answer is a place to put them, per repository.

**MEASURED BEFORE WRITTEN, not asserted.** Eight figures that live in code comments
in this tree were grepped against `HANDOFF.md` — the only outbound this session has.
**Seven of the eight appear nowhere in it.** The one that escaped is `64.2%`, and it
escaped because it was the subject of a push, not because the comment reached anyone.

Every row cites a **verbatim fragment**, not a line number, and `check_unreported.py`
fails if a fragment is no longer in the file it names. A stale index is worse than no
index — that is the lesson `fixtures/real-report-shara.json` taught this repository
tonight, and this file is not going to repeat it.

| # | file | the finding | in HANDOFF? |
|---|------|-------------|-------------|
| 1 | `gapengine.py` | The killing-blow join was a same-second join **with no target**, so any hit landing in a second when anything died was marked a killing blow: **194 hits marked where the target-aware join marks 120, 38% over-marked**, and systematic in AE combat rather than rare. | no |
| 2 | `gapengine.py` | `You hit yourself … by Cannibalize` is an HP-for-mana trade, not output. It was **3.7% of a character's apparent total** until excluded. | no |
| 3 | `bard.py` | The same trade, counted: **92,822 points**, 3.7% of Shara's apparent output. | no |
| 4 | `gapengine.py` | Time-in-melee and engaged time differ by **2.3×** on the log the engine was built against, and the reported lane gap by **3×** — 5× under ceiling against 14×. A caster who never closes has no lane gap, and engaged time would tell them they had an enormous one. | no |
| 5 | `gapengine.py` | `Cannibalize` lands 156 times at damage 41–51 while `Cannibalization I` lands 46 times at **1864–1924** — forty times apart. A merged median describes neither. | no |
| 6 | `gapengine.py` | The resist-rate guard is on `hit_n`, not on `n + hit_n`: with zero landings the sum is still truthy, so a damage-over-time effect reported a **100% resist rate** — telling a reader their spell never lands when the truth is that the parser cannot see it land. | no |
| 7 | `model4.py` | With the unsourced `up10()` floor removed, `OH_RATE_CAP` is **inert**: `verify_upgrade.py` section 5 runs the rankings with it and without it and gets identical DPS, identical offhand and an identical top 12. **A published constant that constrains nothing.** | no |
| 8 | `bundle/check-integrity.py` | A's harness corrupted this bundle "because the harness restores through a text round-trip". Measured, **that mechanism does not fit this file**: pure ASCII, LF-only, no tabs, no BOM, no trailing whitespace, final newline — every normalising round-trip returns it unchanged. The check is kept for the day the bundle gains a byte a round-trip could touch. | no |
| 9 | `bundle/check-integrity.py` | With **two** hashed copies in `bundle/`, this gate printed `hashed copy is byte-identical FAILED 22403 vs 0 bytes` and `the served bytes are not what this tree says they are`. The bytes were fine. Reproduced and fixed 1 Sep 2026. | §47.4 |
| 10 | `gapengine.py` | The stance classifier labelled **64.2% even damage as Balanced** on a `<=0.65` threshold, when 64.2% over n=120 is 3.1 SE from Balanced's 50% and nowhere near Offensive's 93%. The data said *neither* and the code said one. | yes |

## What this file is not

It is **not** a backlog. Nothing here is a task. Rows 1–8 are findings that were made,
acted on in the code, and never left the file they were made in. Putting them here does
not schedule anything; it makes them **readable by somebody who is not reading the
source**, which is the whole of R74.

## The rule going forward

A measured figure that changes what a reader should believe goes in `HANDOFF.md` when
it is made. A measured figure that only explains why a line of code is the way it is
goes in the comment **and** gets a row here. **The test is whether somebody who never
opens the file would want to know.** All ten rows above pass that test, and seven of
them failed to reach anyone for a week.
