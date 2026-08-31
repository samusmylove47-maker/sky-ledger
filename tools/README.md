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
| `stance.py` | Parity test for Offensive Stance. Damage is even 98.8% of the time under Offensive and ~55% otherwise — the signature of a x2 applied last. |
| `lattice.py` | Support test for the roll. A 20-step lattice admits at most 20 distinct damage values per weapon/verb/target; 12 of 12 large groups exceed that, one reaching 82 distinct values over a 98-wide span. Refutes the quantised model published in this file's first draft. |

Usage — point them at a directory of `.log` fixtures:

```
python3 tools/avoid.py /path/to/fixtures/*.log
python3 tools/eng.py   /path/to/fixtures/*.log
SPELLS=/path/to/spells.json python3 tools/combo.py /path/to/fixtures/*.log
python3 tools/wrath.py
python3 tools/stance.py  /path/to/fixtures/*.log
python3 tools/lattice.py /path/to/fixtures/*.log
```

`wrath.py` needs no corpus; it is self-contained and reproduces §3 of `DAMAGE-CHAIN.md`.
