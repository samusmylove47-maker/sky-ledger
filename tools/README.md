# Measurement tools

Every number in `DAMAGE-CHAIN.md` and `EQUIPMENT-TRUTH.md` that is marked *measured*
comes from one of these. They read the committed Legends log corpora published by
third-party parser projects (`jmoyers/everquest-companion`, `kpxcoolx/eql-meter`,
`DranakCorps-bot/EQBuddy`, `blastlaster/eql-log-reader`), which ship real client logs as
test fixtures.

| Script | Answers |
|---|---|
| `parse.py` | Per-channel damage totals and DPS for one log. |
| `dist.py` | Per-channel damage distributions, split normal vs critical. Source of the 3.00x spell crit multiplier. |
| `eng.py` | Wall-clock, engaged, peak-60s and peak-30s DPS. Source of the ground-truth ladder. |
| `avoid.py` | Swing outcomes across every log. Source of `G = 5.97%` and the strikethrough value. |
| `combo.py` | Infers a character's classes from exclusive spell casts, then ranks logs by measured DPS. |
| `wrath.py` | Reimplements eqlwiki's published roll algorithm and shows it does not reproduce the measured histogram. |

Usage — point them at a directory of `.log` fixtures:

```
python3 tools/avoid.py /path/to/fixtures/*.log
python3 tools/eng.py   /path/to/fixtures/*.log
SPELLS=/path/to/spells.json python3 tools/combo.py /path/to/fixtures/*.log
python3 tools/wrath.py
```

`wrath.py` needs no corpus; it is self-contained and reproduces §3 of `DAMAGE-CHAIN.md`.
