# BCI Correction and Execution Protocol V4

## Purpose

This document converts Reviewer 1’s BCI objections into an executable analysis. It also identifies which original claims are withdrawn and which outputs are permitted after the replacement run.

## 1. Withdrawn original analysis

The original BCI section is not treated as a weak baseline. It is withdrawn because four defects jointly invalidate its headline interpretation:

1. decoder performance was far below the relevant published context;
2. the source of the analysis window was not reproducibly established;
3. `B_min` used the feature window rather than the full trial cycle;
4. a pooled confusion matrix across subject-specific decoders was interpreted as though it were an operating system.

No original BCI number is carried forward.

## 2. Source data and immutable split

Dataset: MOABB `BNCI2014_001`, corresponding to BCI Competition IV Dataset 2a.

- nine subjects;
- four classes: left hand, right hand, feet, tongue;
- one training session T and one evaluation session E per subject;
- 288 trials per session, 72 per class before exclusions;
- six source runs per session;
- 22 EEG and three EOG channels at 250 Hz;
- cue onset at trial time 2 s; imagery extends through 6 s.

The analysis is subject-specific. T is used for every fit, hyperparameter decision, and feature-selection decision. E is evaluated once. No subject pooling is used for an operating-system estimate.

## 3. Session and run verification

MOABB versions may expose six Raw objects or a single concatenated Raw object per session. The pipeline therefore verifies source structure from the cue stream:

- six Raw objects: each must contain 48 cues;
- one concatenated Raw: it must contain 288 cues and five between-run gaps;
- either representation must yield exactly 282 within-source-run inter-cue intervals.

Session names are resolved by the strings `train` and `test`/`eval`, not by lexical sorting.

## 4. Artifact handling and channels

The pipeline obtains the source recordings from MOABB but performs preprocessing explicitly with MNE.

- Organizer-provided `bad_*` annotations are rejected by `mne.Epochs(reject_by_annotation=True)`.
- An all-trial epoch set is also constructed with rejection disabled.
- All, retained, and excluded counts are written by subject, session, and true class.
- Exactly 22 EEG channels are selected by channel type.
- EOG channels never enter filtering, CSP, or classification.
- Channel order is asserted across runs and sessions.

Clean-trial throughput is reported together with retention. A deployment sensitivity analysis should treat rejected trials as erasure outcomes when they would consume cycle time in actual use.

## 5. Primary fixed-window decoder

Preprocessing:

- epoch: 0.5–2.5 s after cue onset, or 2.5–4.5 s in absolute trial time;
- band-pass: 8–30 Hz;
- filter: MNE FIR, zero phase, `firwin`, automatic length and transitions;
- log: resolved tap count, sampling rate, transition settings, software versions, and channel list.

Classifier:

- one-vs-rest CSP;
- Ledoit–Wolf covariance regularization;
- shrinkage LDA;
- candidate CSP components per binary classifier: 4, 6, 8;
- selection criterion: mean Cohen’s kappa in five-fold stratified cross-validation on T;
- final model refit on all clean T trials and applied once to clean E trials.

The primary analysis is a fixed operating window. It is not tuned on E and is not compared as though it were identical to a maximum-over-time competition score.

## 6. FBCSP-style robustness decoder

Nine frequency bands are used: 4–8, 8–12, 12–16, 16–20, 20–24, 24–28, 28–32, 32–36, and 36–40 Hz.

Within every T-session cross-validation fold:

1. fit binary one-vs-rest CSP for every class and band;
2. retain four CSP components per class-band model;
3. concatenate the resulting features;
4. select 16, 32, 64, or 96 features by mutual information on the fold’s training data only;
5. fit shrinkage LDA;
6. score kappa on the fold’s held-out T data.

The selected feature count is refit on all T data and E is evaluated once. This is called **FBCSP-style** because it does not reproduce every feature-selection and temporal-evaluation detail of Ang et al. (2012).

## 7. Full-cycle duration

For each subject, `tau_bar` is the mean of all 282 within-source-run inter-cue intervals in E. Intervals crossing run boundaries are excluded. The 2-s feature epoch and the original 3-s analysis window are never used as the throughput denominator.

`B_min = I_MM / tau_bar`, with `tau_bar` in minutes.

The conventional Wolpaw ITR is calculated with the same cycle time and reported only for comparison, with its uniform-class and symmetric-error assumptions stated.

## 8. MI estimation and inference

For every subject and decoder, save:

- complete 4×4 confusion matrix;
- plug-in MI;
- occupied supports `K_Y`, `K_Z`, `K_YZ`;
- first-order correction `(K_YZ-K_Y-K_Z+1)/(2N ln 2)`;
- corrected MI without truncation;
- class-stratified 10,000-resample interval;
- 5,000-permutation independence p-value using `(b+1)/(B+1)`;
- Holm-adjusted p-value across nine subjects, separately for each decoder;
- accuracy and kappa with bootstrap intervals;
- `B_min`, conventional ITR, class precision/recall/F1, and `V_eff(.40-.90,30)`.

A subject is described as carrying measurable information only under the preregistered confirmatory criterion. Point estimates near zero are not compared without intervals and adjusted p-values.

## 9. Figures and tables

- Table 3a: primary fixed-window subject-level results.
- Table 3b: primary `V_eff` threshold sensitivity.
- Supplementary Table S8: both decoders, exclusions, correction amounts, software versions, and reference-only micro-average.
- Figure 2: subject accuracy versus full-cycle `B_min` with intervals, plus the threshold curve.
- Figure 4: all nine primary row-normalized confusion matrices.
- Supplementary figure: all nine FBCSP-style matrices.

No fold range is reported when the minimum corrected information rate is non-positive or statistically indistinguishable from zero.

## 10. Commands

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

## 11. Final acceptance decision

Do not submit the BCI results when any of the following occurs:

- session/run/channel/timing assertion failure;
- unexpected artifact count or class imbalance without explanation;
- any E-label use in tuning;
- primary performance remaining near the withdrawn kappa of .29 without a resolved cause;
- unexplained divergence between the primary and FBCSP-style confusion structure;
- unpopulated manuscript tokens;
- a figure or table not reproducible from the final JSON and prediction CSVs.
