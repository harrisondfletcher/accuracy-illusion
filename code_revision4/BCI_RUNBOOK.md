# BCI Competition IV-2a execution, validation, and manuscript population

Section 6 is not a prose placeholder to be filled by hand. It is populated only from a completed `results/bci_real_application_v4.json` that passes `validate_bci_output.py`.

## 1. Pinned environment

```bash
python -m venv .venv-bci
. .venv-bci/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-bci.txt
```

Record:

```bash
python --version > results/bci_python_version.txt
pip freeze > results/bci_environment_lock.txt
```

The script supports MOABB representations with either six Raw objects per session or one concatenated Raw object. It does not depend on an `artifact_handling` constructor argument. Organizer-provided `bad_*` annotations are rejected explicitly through MNE Epochs.

## 2. Full run

```bash
python bci_pipeline.py \
  --subjects 1-9 \
  --decoders primary fbcsp \
  --data-path /absolute/path/to/MNE-data \
  --output results/bci_real_application_v4.json \
  --n-bootstrap 10000 \
  --n-permutations 5000
```

The first run downloads the public dataset. Preserve the console log, dataset cache, prediction CSVs, environment lock, and JSON.

## 3. Non-negotiable runtime gates

The run aborts when any gate fails.

1. All nine subjects complete.
2. Session labels resolve semantically to one training session and one evaluation/test session.
3. Each session contains 288 cue events.
4. Six source runs are verified either as six 48-cue Raw objects or as one 288-cue Raw with five between-run gaps.
5. Each subject contributes exactly 282 within-source-run inter-cue intervals to the cycle-time estimate.
6. Exactly 22 EEG channels enter every filter/CSP fit; EOG never enters the feature matrix.
7. Organizer `bad_*` annotations are rejected; all, clean, and excluded counts are reported by session and true class.
8. The primary epoch is fixed at 0.5-2.5 s after cue onset. E labels are never used to choose it.
9. Filter method, phase, design, transition settings, resolved tap count, sampling rate, package versions, and channel order are written to JSON.
10. Primary CSP component count is selected only inside five-fold T-session cross-validation.
11. FBCSP-style CSP fitting and feature-count selection occur inside T-session folds; E is evaluated once.
12. Corrected MI uses observed joint support and is not truncated at zero.
13. MI and B_min intervals use class-stratified bootstrap resampling.
14. Independence p-values use `(b+1)/(B+1)`; Holm adjustment is applied across nine subjects separately for each decoder.
15. Every decoder result includes a 4x4 confusion matrix, per-class precision/recall/F1, full V_eff curve, kappa, ITR, and correction amount.

Validate after execution:

```bash
python validate_bci_output.py results/bci_real_application_v4.json
```

## 4. Decoder interpretation

The primary fixed-window OVR-CSP decoder is compared contextually with Ang et al. (2012): mean evaluation kappa .503 for OVR-CSP and .569 for OVR-FBCSP. Those values are not exact targets because Ang et al. used time-resolved competition evaluation and maximum-over-time scoring.

If primary mean kappa remains near the withdrawn value of .29, do not populate Section 6. Debug, in order:

1. semantic T/E resolution;
2. cue-relative timing;
3. all/clean artifact counts and class balance;
4. EEG/EOG channel picks;
5. filter specification and epoch identity across bands;
6. CSP component selection and covariance regularization;
7. per-subject confusion matrices;
8. agreement or disagreement with the FBCSP-style robustness analysis.

The robustness decoder is called **FBCSP-style** unless every detail of Ang et al.'s feature-selection and temporal evaluation procedure is reproduced. It exists to test decoder dependence, not to manufacture a higher score.

## 5. Artifact-conditioned versus operational throughput

The primary table reports clean-trial performance because the competition provides artifact annotations. Also report retention by subject and class. If rejected trials would consume time or yield no command in deployment, add a sensitivity analysis treating them as erasure outcomes rather than deleting them. Do not silently equate clean-trial throughput with deployment throughput.

## 6. Manuscript population

Populate all table tokens and validated summary prose with:

```bash
python populate_bci_manuscript.py \
  results/bci_real_application_v4.json \
  --template manuscript/The_Accuracy_Illusion_v4.md \
  --output manuscript/The_Accuracy_Illusion_v4_BCI_populated.md
```

Then regenerate figures:

```bash
python make_figures.py bci
```

Before resubmission, verify that no `BCI_PRIMARY_*_START/END` table markers remain.

## 7. Reporting rules

Do not:

- report a pooled confusion matrix as an operating subject-specific BCI;
- call an intent “usable” solely because it crosses a reference F1 threshold;
- report a fold range when the smallest corrected B_min is non-positive or statistically indistinguishable from zero;
- compare low-information subjects from point estimates alone;
- describe a class-confusion pattern before inspecting all subject-level matrices;
- compare fixed-window kappa as though it were identical to maximum-over-time competition kappa;
- report the FBCSP-style decoder as an exact Ang et al. reproduction.

Table 3a contains the primary decoder. Table 3b contains threshold sensitivity. Supplementary Table S8 contains both decoders, artifact counts, support corrections, software versions, and the reference-only micro-average. Figure 2 shows subject-level accuracy against full-cycle B_min plus threshold sensitivity. Figure 4 shows all nine primary confusion matrices; the FBCSP-style matrices belong in the supplement.

## 8. Publication gate

The Section 6 results are publication-ready only when:

- `validate_bci_output.py` passes;
- prediction CSVs recreate every confusion matrix;
- figures recreate from the final JSON;
- the populated manuscript contains no token or withdrawn value;
- the response letter reports actual values rather than future tense;
- the archived package contains the JSON, prediction CSVs, log, environment lock, and code commit hash.
