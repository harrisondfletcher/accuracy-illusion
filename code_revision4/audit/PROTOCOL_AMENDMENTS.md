# Protocol amendments — recorded before E-session performance access

Recorded: 2026-09-08 (UTC). Per handoff §2, these amendments are methodological
corrections adopted BEFORE the final E evaluation. None is a BCI finding.
No E-session decoding performance has been computed at the time of recording.

## A1. Artifact exclusion: explicit source-mask policy (replaces annotation path)

**Defect (verified in source):** `bci_pipeline.py:104` instantiates
`BNCI2014_001(artifact_handling="ignore")`; pinned moabb 1.7.1
`datasets/bnci/base.py` line 402 returns immediately in "ignore" mode, creating
no annotations, so `reject_by_annotation=True` at `bci_pipeline.py:294` rejects
zero trials. Retention would silently report 1.0 for every subject.
**Additional trap (verified):** even `artifact_handling="reject"` with default
`artifact_interval=None` creates zero-duration BAD annotations at the *trial
trigger* (base.py lines 420-427); the analysis epoch spans trigger+2.5 s to
trigger+4.5 s and does not overlap a zero-duration mark at trigger+0 s, so
rejection could still be zero.
**Amendment:** production data path is a direct local-MAT adapter (handoff
§6.2). Organizer flags are read from `run.artifacts` per trial and applied as
an explicit boolean retention mask. Decisive gate: set equality of
flagged-trial UIDs and excluded-trial UIDs (gate A1), identical across both
decoders and all nine filter bands (gate A2).
**Consequence for tests:** `tests/test_core.py::test_bci_pipeline_is_explicit_and_cross_representation`
asserts the pre-amendment implementation strings (e.g. `reject_by_annotation=True`
present, `artifact_handling="reject"` absent). The test is amended to assert the
new explicit-mask contract instead. This is a test-of-spec change tracking the
amendment, not a gate relaxation.

## A2. Event anchor: direct MAT trigger, tmin=2.5 / tmax=4.5

The adapter supplies trigger-anchored events (`run.trial - 1`, verified pinned
converter behavior). Epoch bounds are therefore 2.5-4.5 s relative to the
trigger = 0.5-2.5 s post-cue (handoff §6.1, path row 1). At 250 Hz inclusive
MNE endpoints: cue = s0+500, first epoch sample = s0+625, last = s0+1125,
n = 501. Anchor proof recorded per trial in the ledger; impulse-fixture test
covers missing-offset and double-offset failures.

## A3. Training CV: six-fold leave-one-source-run-out (replaces 5-fold shuffle)

`fit_primary`/`fit_fbcsp` used `StratifiedKFold(5, shuffle=True)`. Replaced by
`LeaveOneGroupOut` with the six T source-run identities as groups (handoff §2
row 14, §8.1). Every fitting fold is checked for all four classes. Tie rule:
smallest CSP component count / smallest feature count (declared grid order).

## A4. Permutation test: plug-in statistic, within-run scheme

`evaluate_decoder` permuted predictions globally and used the *corrected* MI as
the statistic. Amended per §10.3: statistic is plug-in MI; permutation swaps
labels within each source E run only (preserving run-specific class counts);
Phipson-Smyth (1+exceedances)/(B+1) retained; exceedance count recorded.
The v4 global scheme may be reported as a separately named sensitivity with its
own predeclared seed; never selected post hoc.

## A5. Bootstrap: run-and-class stratification, shared indices across decoders

Class-only strata amended to (E source run x true class) strata (§10.2).
Bootstrap index streams are derived from a subject-level seed independent of
decoder so paired decoder differences use identical resamples. Previous code
seeded primary and fbcsp differently (`+100*subject` vs `+100*subject+1`),
precluding paired resampling.

## A6. Seed derivation

`numpy.random.SeedSequence(master=42, per-subject/decoder/operation integer
codes)`; no Python `hash()`. CLI `--seed` implemented (did not exist).

## A7. ITR reference: no silent below-chance clipping

`itr_bits_per_trial` silently returned 0.0 below chance. Amended: record
`itr_bits_formula` (true formula value, defined with 0log0=0 conventions) and
a separately named `itr_bpm_clipped_at_chance` field with its rule (§10.5).

## A8. Interfaces implemented (did not exist; §13.1)

`--mat-dir`, `--phase preflight|train-smoke|evaluate`, `--run-dir`, `--seed`,
`--resume` on the pipeline; `--mode preflight|smoke|final`,
`--source-manifest`, `--report` on the validator; `tools/acquire_bnci_mat.py`.
Invalid flags fail (argparse default). Validator recomputes metrics from
prediction CSVs (was field-presence only, 83 lines).

## A9. Output schema extensions (§11)

Added: schema_version, result_kind (smoke|final), design_fingerprint,
source_code_sha256, data_files (name/source/bytes/sha256),
analysis_freeze_utc, run_started_utc/run_completed_utc, permutation_scheme,
permutation_exceedances, bootstrap_scheme, inference_seed, per-class
precision/recall/support, K_y/K_z/K_yz already present; strict JSON
(allow_nan=False). Existing `subjects -> decoders` layout preserved.

## A10. Performance-based admission gates removed

No kappa floor, no MI floor, no minimum significant-subject count anywhere in
pipeline or validator (handoff §2 row 1, §12). Low performance triggers the
§15 audit ladder; valid unfavorable results are admitted.

## A11. Duration estimand

All 282 within-run inter-trigger intervals per E session computed from source
`run.trial` sample coordinates BEFORE artifact exclusion; anchors never mixed
(fixed offset cancels within-run); no gap-threshold inference (six source
records preserved by identity); intervals stored individually with UIDs.
(The prior implementation's 10-second gap heuristic for concatenated sessions
is removed along with the MOABB loading path.)

## A12. Clean-subset scope + all-scheduled sensitivity (§7.3)

Primary analysis = organizer-clean trials. Prespecified sensitivity: frozen
decoders predict all valid scheduled E epochs (flagged included); second
confusion matrix + MI reported as `all_scheduled_sensitivity`. No refit or
selection between the two.

## A13. Environment note

Pinned stack resolved exactly on Python 3.12.13 (moabb 1.7.1, mne 1.12.1,
scikit-learn 1.8.0, numpy 2.3.5, scipy 1.17.0, matplotlib 3.10.8,
pytest 9.0.2); `pip check` clean. Installed moabb sources byte-identical to
fetched v1.7.1 tags (hashes in RUNLOG). No substitutions.

## A14. Package identity

Supplied zip differs from the handoff-inspected package (RUNLOG §"Package
identity discrepancy"). CLI surfaces and file tree match the handoff's audit;
proceeding with per-file hash inventory at git baseline
3fa8077a203cf6618dbd60f0a5690c7355576b12.
