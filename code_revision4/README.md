# The Accuracy Illusion — Revision 4 Reproducibility Package

## Status

All simulation-based manuscript values are final and reproducible from seed 42. The original BCI results are withdrawn. The replacement BCI analysis is fully specified but remains execution-gated; no BCI estimate is asserted until its validated JSON exists.

## Simulation reproduction

```bash
python -m venv .venv-sim
. .venv-sim/bin/activate
pip install -r requirements-simulation.txt
python reproduce_all.py
```

Clean-state smoke run:

```bash
python reproduce_all.py --quick
```

Quick mode regenerates core profiles, counterexamples, matched-base results, synthetic covariance, Data S2, Figures 1/3, and tests. It does not read cached grid or power outputs.

## BCI execution

```bash
python -m venv .venv-bci
. .venv-bci/bin/activate
pip install -r requirements-bci.txt
python bci_pipeline.py \
  --subjects 1-9 \
  --decoders primary fbcsp \
  --data-path /absolute/path/to/MNE-data \
  --output results/bci_real_application_v4.json \
  --n-bootstrap 10000 \
  --n-permutations 5000
python validate_bci_output.py results/bci_real_application_v4.json
python populate_bci_manuscript.py results/bci_real_application_v4.json
python make_figures.py bci
```

See `BCI_RUNBOOK.md` before execution.

## Measurement architecture

- base single-intent trials -> `B_min`, `V_eff`
- held-out-labelled compositional trials -> `C_k`
- induced-error trials -> `R`
- uncertainty trials -> `U`

Specialized trials never enter the base confusion matrix. Memorizer and Compositional paired runs use common random numbers; their realized base confusion matrices, durations, and base metrics are exactly equal.

## Split correction

The original and first-revision engines computed a nominal grammar-partition quantity but never used it; held-out evaluation was fixed at .50. The 1,440-cell grid therefore repeated 480 substantive configurations three times. Revision 4 removes the split field entirely. The Bernoulli engine does not represent combination identities and cannot study a grammar-partition sweep. The manuscript’s 80/20 grammar partition is a real-study protocol assumption, not an engine parameter. The substantive 480-cell grid was rerun.

## Main files

| File | Purpose |
|---|---|
| `engine_v2.py` | Four-channel engine; retained filename for continuity |
| `run_simulations.py` | Core profiles, nulls, counterexamples, matched-base sweep, 480-cell grid, synthetic covariance |
| `power_v3.py` | Fisher and system-label permutation power analyses |
| `metrics_u.py` | Uncertainty selectivity, coverage, intervals, Fisher test, risk–coverage/AURC |
| `generate_worked_example.py` | Deterministic Data S2 and summary |
| `bci_pipeline.py` | Explicit subject-specific primary and FBCSP-style IV-2a analyses |
| `validate_bci_output.py` | BCI runtime/output acceptance gates |
| `populate_bci_manuscript.py` | Mechanical Section 6 insertion from validated JSON |
| `BCI_RUNBOOK.md` | BCI execution and interpretation protocol |
| `protocol/S4_protocol_checklist.md` | Adversarial protocol and metric-specific trial planning |
| `make_figures.py` | Simulation figures and validated BCI figures |
| `reproduce_all.py` | One-command simulation reproduction, tests, and manifest |
| `tests/` | Core invariance and estimator tests |

## Revision documents

- `manuscript/The_Accuracy_Illusion_v4.md/.docx`: simulation-final, BCI execution-gated manuscript.
- `RESPONSE_TO_REVIEWERS_V4.md` and `docs/Response_to_Reviewers_V4.docx`: point-by-point response draft.
- `REVISION_AUDIT_V4.md` and `docs/Revision_Audit_V4.docx`: numerical and code audit.
- `BCI_CORRECTION_AND_EXECUTION_PROTOCOL_V4.md` and matching DOCX: detailed BCI repair.
- `BCI_RUNBOOK.md` and matching DOCX: executable acceptance gates.
- `supplements/`: Tables S0-S8 and Protocol S4 in Markdown and DOCX.

## Estimator conventions

- Miller–Madow correction uses observed support: `(K_yz-K_y-K_z+1)/(2N ln 2)`.
- Bias-corrected MI is not truncated at zero for inference.
- `B_min` two-system confirmation uses system-label permutation over complete episode records.
- `U` is not estimable when either forced-commitment error stratum is empty.
- Report `U` jointly with abstention rate, commitment coverage, and both error-stratum counts.
- The repair expression `1-(1-1/K)^n` is only the simulation’s independent-uniform null.
- Synthetic covariance results are properties of the specified generator, not of communication generally.
