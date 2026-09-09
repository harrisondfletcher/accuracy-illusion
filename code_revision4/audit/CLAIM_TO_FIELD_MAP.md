# Claim-to-field map (BCI population)

Input: `bci_real_application_v4.json` sha256 `5b8075d274a57153421ba078212df9554bc48e8609d42d6684c1c08b6915da38`

| Sentence/block id | JSON fields or calculation | Kind |
|---|---|---|
| Front-execution-status | status, result_kind, analysis_freeze_utc | descriptive |
| S6-intro | status, result_kind, design_fingerprint, analysis_freeze_utc | descriptive |
| S6.1-loader | dataset.data_path_mode, config.artifact_policy, subjects.*.artifact_accounting | descriptive |
| S6.1-artifact-counts | artifact_accounting.*.n_clean/n_dropped, decoders.primary.true_support_per_class | descriptive |
| S6.1-cv | config.cv_scheme, subjects.*.decoders.*.training_only_tuning | descriptive |
| S6.1-duration | subjects.*.evaluation_cycle, evaluation_within_run_intervals_sec | descriptive |
| S6.2-shell | config.bootstrap_scheme, config.permutation_scheme, decoders.*.mi_perm_p_holm | descriptive |
| S6.3 | decoders.primary.confusion_matrix (row-normalized cells) | descriptive |
| S15.4 | decoders.primary.b_min_bpm, veff_curve, mi_perm_p_holm | descriptive |
| Abstract-BCI | decoders.primary.accuracy, b_min_bpm, mi_perm_p_holm | descriptive |
| S6.2-fbcsp-persistence | paired replay of prediction CSVs; decoders.*.accuracy/kappa/mi_corrected_bits | descriptive |
| S8-tables | decoders.fbcsp.*, artifact_accounting, all_scheduled_sensitivity, veff_curve; paired replay | descriptive |

Numeric tokens in every listed block are inserted programmatically from the listed fields; connective prose is manually written. The exploratory near-matched-accuracy contrast in the validated summary paragraph is labeled exploratory with its selection rule disclosed in the text.
