# Revision Audit V4

## Status

**Simulation manuscript:** complete and regenerated.

**BCI empirical insertion:** execution-gated. The original BCI results are withdrawn. No replacement BCI value is asserted in the current manuscript. Section 6 is populated only from a validated `results/bci_real_application_v4.json`.

## 1. Simulation architecture

- Removed the inert grammar-partition factor from `SimConfig`, the grid, and all result cells.
- The engine now states its actual abstraction: Bernoulli correctness on training-labelled and held-out-labelled trials, without combination identities.
- The real-study protocol may assume an 80/20 grammar partition; that value is not represented as a simulation parameter.
- The 480-cell grid varies only `|Z|`, base correctness `p`, Zipf exponent, and total trial count.
- Fixed `n_base_override` allocation so the uncertainty count is computed from the realized base count.
- Specialized trials never enter the base confusion matrix.
- Memorizer and Compositional paired runs use common random numbers, producing exact equality of every realized base metric.

## 2. Final simulation results

At `|Z|=12`, `N=1000`, 400 runs:

- Memorizer and Compositional base accuracy: `.849935` for both.
- Corrected MI: `2.572421` bits for both.
- `B_min`: `4.747720` bits/min for both.
- `V_eff(.60)`: `11.7875` for both.
- `V_eff(.80)`: `10.435` for both.
- `C_2`: `.082227` versus `.855563`.
- `R`: `.161225` versus `.349750`.
- `U`: `0` versus `.217178`.

Matched-base sweep:

- Aggregate-accuracy gaps: `4.7–9.9` percentage points.
- `C_2` gaps: `41.6–86.4` points.
- Base `B_min` gap: exactly zero at every level.

Grid:

- 480 cells, 100 paired runs per cell.
- Minimum `C_2` Cohen’s `d`: `1.799` at `N=100`, `2.724` for `N>=200`.
- Median `C_2 d`: `11.476`.
- Minimum `R d`: `.528` at `N=100`, `1.321` for `N>=500`.
- Maximum paired base `B_min` difference: `0`.
- Finite-run `B_min` monotonicity: 79/80 series; manuscript does not claim perfect empirical monotonicity.

## 3. Power and inference

- `C_2`, `R`, and `U`: two-sided Fisher exact tests.
- `B_min`: two-sided system-label permutation conditional on the pooled joint table.
- 1,000 Monte Carlo replications per cell.
- 1,000 system-label permutations per `B_min` replication.
- Wilson 95% Monte Carlo intervals reported.
- Empirical `B_min` size: `.039–.057`.
- `Delta p=.05`: power `.665` at 500, `.823` at 750, `.929` at 1,000 base trials/system.
- `Delta p=.03`: power `.798` at 2,000.
- Population `Delta B_min` at a .5-min cycle: `.120`, `.369`, `.628`, and `1.339` bits/min for `Delta p=.01,.03,.05,.10`.

## 4. Formal corrections

- Observed-support Miller–Madow correction used everywhere; no zero truncation.
- Equal-MI construction uses beta first-block diagonal `.81`, avoiding threshold equality; `q=.5467007423005`, MI `1.1524153202` for both matrices, and `V_eff(.80)=4` versus `2`.
- `C_k` is behavioral held-out generalization, not proof of an internal grammar.
- Repair null is protocol-specific; `1-(1-1/K)^n` is only the independent-uniform simulation null.
- `U` is uncertainty selectivity, not calibration, and is accompanied by coverage and error-stratum counts.
- Functional-independence propositions hold under fixed ontology, duration distribution, alpha, and beta.
- Synthetic covariance is reported as generator-specific, not as general empirical dimensionality.
- MI is described as a non-injective scalar functional of a joint distribution.
- Perfect decoding reaches `log2|Z|` only under a uniform intent distribution.
- Noise proof uses `P_Y(y)/|Z|`, not a uniform joint distribution.
- `I/log2|Z|` is a normalized maximum-entropy fraction, not Shannon channel capacity.
- No universal measurement-error division by `(1-epsilon)^2` is asserted.

## 5. BCI replacement analysis

`bci_pipeline.py` now:

- resolves T/E by semantic labels;
- supports either six source-run objects or one concatenated object per session;
- verifies 288 cues/session, six source runs, and 282 within-run E-session intervals;
- performs explicit MNE FIR filtering and logs the resolved specification;
- rejects organizer `bad_*` annotations explicitly;
- uses exactly 22 EEG channels and excludes EOG;
- fixes the primary epoch at .5–2.5 s post-cue;
- selects primary CSP components within T only;
- evaluates E once;
- fits an FBCSP-style robustness decoder with CSP and feature selection inside T folds;
- reports subject-specific accuracy, kappa, MI components, `B_min`, ITR, per-class F1, `V_eff`, intervals, permutation p-values, Holm adjustment, exclusions, predictions, and matrices;
- measures full-cycle duration from all 282 within-source-run cue intervals;
- never reports a pooled matrix as an operating BCI.

Execution is governed by `BCI_RUNBOOK.md`, checked by `validate_bci_output.py`, and inserted by `populate_bci_manuscript.py`.

## 6. Supplementary and package integrity

- Data S2 is present and machine-generated.
- Protocol S4 is present and uses metric-specific trial planning.
- Figure 5 uses per-system trial counts, an empirical-size row, a color-vision-safe scale, and an .80 contour.
- Core tests pass.
- `python reproduce_all.py --quick` requires no cached grid/power result.
- Full reproduction writes a SHA-256 manifest.

## 7. Remaining publication gate

Before resubmission:

1. Run both BCI decoders on all nine subjects in the pinned environment.
2. Pass `validate_bci_output.py`.
3. Populate the manuscript mechanically.
4. Generate Figures 2, 4, and the supplementary FBCSP-style confusion figure.
5. Replace future-tense BCI language in the response letter with actual results.
6. Archive JSON, prediction CSVs, console log, environment lock, and code commit.


---

## Addendum (2026-09-09): BCI real-data application executed

The replacement analysis promised in this revision has now been executed and
independently validated. Design frozen 2026-09-09T03:37:41Z
(fingerprint eabbe1298c88) before any evaluation-session
decoding; all methodological amendments were recorded pre-evaluation in
audit/PROTOCOL_AMENDMENTS.md (notably: direct local-MAT loading with explicit
organizer artifact masks after the annotation-based path was shown to reject
zero trials; six-fold leave-one-source-run-out tuning; within-run
plug-in-MI permutation; run-by-class stratified bootstrap).

Primary decoder (fixed-window OVR-CSP + shrinkage LDA), nine subjects:
mean accuracy 0.620, mean kappa
0.493, corrected MI
0.087-1.195
bits, B_min 0.65-8.92
bits/min at the measured 8.043-s full trial cycle. The specified independence
test rejected after Holm adjustment for all nine subjects under both
decoders. FBCSP-style robustness decoder: mean accuracy
0.692, mean kappa
0.591. No pooled operating-system claim is
made. C_k, R, and behavioral U remain unmeasured by design (Section 6.4).
Full evidence: final result JSON, prediction CSVs, trial ledger, independent
validation report, and FINAL_BCI_COMPLETION_REPORT.md in the
release archive.
