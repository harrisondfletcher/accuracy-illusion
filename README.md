# The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior

**Harrison D. Fletcher**
Submitted to *Behavior Research Methods*, March 2026.

> DOI: [assigned upon publication]

---

## What This Repository Contains

This is **Supplementary Code S1** for the manuscript. It contains everything needed to reproduce every table, figure, and statistical claim in the paper from deterministic seeds.

- **Simulation engine** — 5 agent types: random, class-biased, overproduction, memorizer, compositional
- **Parameter sweep and power analysis pipelines** — noise sweeps, matched-accuracy analyses, bootstrap power curves
- **All JSON data files** reproducing every table and figure in the manuscript
- **Figure generation scripts** — 5 publication-quality figures
- **Worked example dataset (S2)** — 800 episodes, |Z|=12, all trial types
- **Supplementary tables (S3)** — Tables S1–S7, cross-verified against JSON
- **Adversarial evaluation protocol checklist (S4)** — printable checklist for researchers

## Quick Start — Reproduce All Figures

```bash
pip install -r requirements.txt
cd src
python build_figures.py
# outputs appear in figures/
```

## Reproduce From Scratch (Full Simulation)

```bash
# Phase A: core simulation (generates table1.json, counterexamples.json, null_models.json)
cd src
python phase_a.py

# Phase B: parameter sweeps (generates sweep_noise.json, matched_c2.json)
python phase_b_sweeps.py

# Phase C: power analysis (generates power_analysis.json)
python phase_c_power.py

# Generate all figures
python build_figures.py
```

Note: Full simulation takes ~15 minutes. Pre-computed JSON files are provided in `data/json/` for convenience.

## BCI Competition IV-2a Data

The empirical application uses the publicly available BCI Competition IV Dataset 2a (Brunner et al., 2008). The processed confusion matrices and per-subject metrics are in `data/json/bci_real_application.json`. Raw EEG data is available from the original competition at: http://www.bbci.de/competition/iv/

## Deterministic Reproducibility

All simulations use deterministic seeds. The seed structure is defined in `phase_a.py` lines 10–14:

```python
SEED_OFFSETS = {"random":0, "class_biased":100000, "overproduction":200000,
                "memorizer":300000, "compositional":400000, ...}
```

Running `phase_a.py` on any machine with the same numpy version will produce identical JSON outputs.

## Simulation Parameters (Default Configuration)

| Parameter | Value |
|-----------|-------|
| Intent space \|Z\| | 12 |
| Episodes per agent N | 500 |
| Monte Carlo runs | 400 |
| p_correct (memorizer) | 0.85 |
| p_correct (compositional) | 0.90 |
| Compositional split | 80/20 training/held-out |
| Repair fraction | 20% |
| Uncertainty split | 70% easy / 30% hard |
| Bootstrap resamples (power) | 50 per cell |
| Power experiments | 20 per cell |

## Key Data Files

| File | Description | Manuscript Reference |
|------|-------------|---------------------|
| `table1.json` | 5 agents x all metrics, 400 runs | Table 1, Figure 1 |
| `counterexamples.json` | 3 CEs proving irreducibility | Table S2 |
| `null_models.json` | Zipf sweep for null models | Table S3 |
| `sweep_noise.json` | p_correct sweep 0.5–0.95 | Table S4 |
| `matched_c2.json` | Matched-accuracy analysis, 6 levels | Figure 3, Table S5 |
| `power_analysis.json` | 3 metrics x 4 delta-p x 5 N | Figure 5, Table 2 |
| `bci_real_application.json` | 9 subjects, 2,592 trials | Table 3, Figures 2 & 4 |
| `bci_confusion_matrices.json` | Per-subject confusion matrices | Table 3 |

## Repository Structure

```
accuracy-illusion/
├── src/
│   ├── phase_a.py              # Simulation engine + core data generation
│   ├── phase_b_sweeps.py       # Noise sweep + matched-accuracy analysis
│   ├── phase_c_power.py        # Bootstrap power analysis (3 metrics)
│   ├── brm_protocol.py         # Standalone unified protocol (704 lines)
│   └── build_figures.py        # Generates all 5 manuscript figures
├── data/
│   ├── json/                   # All pre-computed simulation outputs
│   └── worked_example/
│       └── S2_worked_example.csv
├── supplementary/
│   ├── S3_supplementary_tables.md
│   └── S4_protocol_checklist.md
├── figures/                    # Generated publication figures
└── tests/
    └── test_reproducibility.py
```

## License

MIT
