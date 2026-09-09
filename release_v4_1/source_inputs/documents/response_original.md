# Response to Reviewers — Revision 4

**Manuscript:** *The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior*

The revision changes the measurement architecture, formal claims, simulations, power analysis, BCI workflow, supplementary data, and reproducibility package. We also found and corrected an additional simulation defect that affected both the submitted engine and the first revision: the nominal grammar-partition factor was computed but never used. We describe that correction explicitly below rather than treating the original grid as valid.

The simulation results in the enclosed manuscript are final and regenerate from `python reproduce_all.py`. The replacement BCI analysis has also been executed on all nine subjects under the frozen design described below. Both predeclared decoders completed, the final output passed 713 validation checks with zero failures, and Section 6, its figures, and Supplementary Table S8 were populated mechanically from the validated result JSON. The original BCI estimates remain withdrawn and are not reused.

## Reviewer 1

### Comment 1. BCI preprocessing, low decoder performance, and published benchmarks

**Response.** We agree. The original empirical results were withdrawn and the replacement analysis was executed from the 18 official BNCI 001-2014 MAT files. The production path reads the MAT records directly so that source-run identity, one-based trigger indices, class labels, and organizer artifact masks are explicit and auditable. Each session is required to contain six 48-trial task runs, 22 EEG plus 3 EOG channels, and 250-Hz sampling. The fixed analysis window is 0.5-2.5 s after cue onset (2.5-4.5 s after the MAT trial trigger); exactly 22 EEG channels enter the decoders and EOG is excluded.

The primary model is an 8-30 Hz fixed-window one-vs-rest CSP plus shrinkage LDA decoder. Its CSP component count (4, 6, or 8) is selected using six-fold leave-one-source-run-out cross-validation entirely within session T, then the model is refit on all clean T trials and applied once to E. A separate nine-band FBCSP-style robustness decoder performs all CSP fitting and mutual-information feature selection inside the same T-only folds. Organizer artifact flags are applied explicitly as a trial mask; a frozen-model all-scheduled sensitivity includes flagged E trials without refitting.

The executed primary decoder obtained mean accuracy 0.620 and mean kappa 0.493; the FBCSP-style decoder obtained 0.692 and 0.591. These are contextualized against Ang et al. (2012), who report mean evaluation kappa .503 for OVR-CSP and .569 for OVR-FBCSP under a different causal, time-resolved, maximum-over-time competition procedure. We therefore use those values as context rather than acceptance targets. The final package includes all per-subject confusion matrices and the complete prediction records.

**Location.** Sections 6.1-6.5; Supplementary Table S8; Supplementary Code `bci_local_data.py` and `bci_pipeline.py`; `BCI_RUNBOOK_FINAL.md`.

### Comment 2. Pooled analysis, confidence intervals, and MI bias correction

**Response.** We agree. The pooled subject-level row and all operating-system interpretations of the pooled confusion matrix were removed. Table 3a now contains nine subject-specific primary-decoder rows; the robustness results are in Supplementary Table S8. A micro-average, if retained for reference, is explicitly identified as a descriptive aggregation rather than an operating BCI.

Equation 7 uses the observed-support first-order correction, `I_MM = I_plugin - (K_YZ - K_Y - K_Z + 1)/(2N ln 2)`, with the correction recomputed for each subject and each resample and no truncation at zero. Final descriptive intervals use 10,000 resamples stratified by evaluation source run and true class. Confirmatory independence inference uses 5,000 within-run label permutations with plug-in MI as the statistic and p=(b+1)/(B+1), followed by Holm adjustment across the nine subjects separately within each decoder family. All nine subject tests rejected the specified independence null after Holm correction under both decoders (raw p=1/5001 for every subject; Holm-adjusted p=9/5001=.00180). We do not interpret this as a between-subject test.

**Location.** Sections 2.2, 6.2, 7, and 14; Table 3a; Supplementary Table S8; `bci_pipeline.py`.

### Comment 3. Episode duration and comparability with ITR

**Response.** We agree. The original 3 s feature-window denominator was withdrawn. For each subject, the replacement analysis computes the mean of all 282 within-source-run inter-trigger intervals across the six E runs before artifact exclusion. The 18 MAT files share the same pseudorandom trigger schedule, yielding a mean cycle of 8.043 s (SD 0.271; range 7.58-8.48 s). `B_min` and the conventional Wolpaw ITR reference are both reported using this full-cycle denominator. Under the primary decoder, corrected MI spans 0.087-1.195 bits and full-cycle `B_min` spans 0.65-8.92 bits/min.

**Location.** Sections 2.1-2.2 and 6.1-6.2; `bci_pipeline.py`; Supplementary Table S8.

### Comment 4. Section 4.3 was asserted rather than constructed

**Response.** We agree. Proposition 3 now states the general non-identifiability result: holding the base joint distribution and duration distribution fixed does not constrain behavior on disjoint held-out compositional trials. Section 4.3 also supplies explicit 4×4 matrices under a uniform prior. Agent alpha has diagonal .85 and uniform .05 errors. Agent beta has first-block diagonal .81 and second-block diagonal `q = .5467007423005`; both have MI `1.1524153202` bits to numerical precision, while `V_eff(.80)` is 4 versus 2. The text no longer infers compositional generalization from single-intent error geometry.

**Location.** Proposition 3 and Section 4.3; `results/equal_mi_matrices.json`.

### Comment 5. Power claims, replication count, resampling count, and effect-size definition

**Response.** We agree. The original power study was invalid because its nominal parameter changed while the compared programmed agents differed on multiple channels. It has been replaced completely.

Each panel now perturbs one metric-specific parameter while holding the other channels equal, uses 1,000 Monte Carlo replications, reports a zero-effect empirical-size row and Wilson interval, and indexes sample size by the observations entering that metric. `C_2`, `R`, and `U` use two-sided Fisher tests. `B_min` uses the same two-sided system-label permutation test recommended for confirmatory analysis, conditional on the pooled joint table, with 1,000 label permutations per replication and `(b+1)/(B+1)` p-values. Table 2e reports both `Δp` and the corresponding population `ΔB_min`.

The revised results distinguish detecting an extreme chance-versus-.86 compositional contrast from resolving smaller differences. A .10 difference around `C_2=.50` requires about 400 held-out trials per system; a .05 difference requires approximately 1,600. For `B_min`, `Δp=.05` reaches power .665, .823, and .929 at 500, 750, and 1,000 base trials per system, respectively; `Δp=.03` reaches .798 at 2,000. Empirical size for the `B_min` permutation procedure ranges .039–.057.

**Location.** Section 5.7; Tables 2a–2e; Figure 5; Supplementary Table S7; `power_v3.py`.

### Comment 6. Directed non-implications, circularity, and empirical non-redundancy

**Response.** We narrowed and formalized the claim. “Irreducible” now means functional independence under fixed ontology, duration distribution, and `V_eff` thresholds: for each reported quantity, two systems can agree on the other four and differ on that quantity. Proposition 4 proves that claim by channel construction plus the explicit equal-MI/different-`V_eff` and equal-`V_eff`/different-MI pairs.

The programmed agents are described as a separability demonstration, not empirical validation. A separate continuously parameterized synthetic population reports the observed covariance matrix and eigenvalues. The text explicitly states which near-zero correlations follow from independently sampled latent parameters and makes no claim that real communicative behavior is intrinsically four-dimensional. Incremental validity against downstream task completion is reserved for prospective empirical work.

**Location.** Sections 3.4–3.5, 5.1, 14, and 15.1.

### Comment 7. The original uncertainty measure confounded abstention with follow-up informativeness

**Response.** We agree. Equation 6 is replaced by uncertainty selectivity:

`U = P(A=1 | E=1) − P(A=1 | E=0)`,

where `A` is abstention and `E` is the observed error on a forced commitment elicited before outcome feedback. After abstention, the forced commitment uses the same unchanged stimulus, no added task-relevant information, and a fixed short delay. `U` is Youden’s J for a binary abstention signal. It equals zero for random abstention and can be negative for anti-selective abstention. It is not estimable if either error stratum is empty.

Because always-abstaining and never-abstaining systems can both have `U=0`, the manuscript and protocol require joint reporting of abstention rate and commitment coverage, both conditional abstention rates, and both stratum counts. The construct is described as selectivity/discrimination, not probabilistic calibration. Graded confidence is evaluated with risk–coverage/AURC, with calibration assessed separately by a proper score.

**Location.** Sections 2.6, 3.3, 11.5, and 13; Protocol S4; `metrics_u.py`.

## Reviewer 2

### Major Comment 1. State what each metric requires from an experimental design

**Response.** Table 0 now lists the ground truth, trial structure, and additional design element required for every metric. Section 6.4 applies that table to IV-2a: the dataset can support only the base-channel measures; absent compositional, induced-error, and abstention channels are reported as not measurable, not as zero.

### Major Comment 2. Clarify the meaning and scope of “irreducible”

**Response.** Section 3.4 distinguishes functional independence, covariance under one synthetic generator, and application-specific computability. The abstract no longer implies that all five measures are required in every application or uncorrelated in realistic populations.

### Major Comment 3. Report trial allocation, null tests, and threshold sensitivity

**Response.** Section 5.7 reports channel-specific sample counts, metric-scale effects, test statistics, empirical size, and Monte Carlo uncertainty. Section 2.3 describes `.80` as a simulation reference threshold rather than a universal usability criterion. The executed Section 6.2 reports the complete primary-decoder threshold curve: subjects with at least one qualifying class number 9/9, 8/9, 7/9, 5/9, 4/9, and 0/9 at alpha=.40,.50,.60,.70,.80,.90. The FBCSP-style sensitivity yields 9/9, 9/9, 7/9, 7/9, 5/9, and 3/9, demonstrating that `V_eff` is decoder-dependent as well as threshold-dependent.

### Minor Comment 1. Inconsistent 400 versus 1,000 run counts

**Response.** Section 5.4 now reports the actual counts: 400 runs for core/null/counterexample profiles; 300 per matched-base configuration; 100 paired runs per grid cell; 1,000 agents in the covariance analysis; and 1,000 replications per power cell.

### Minor Comment 2. Inconsistent Miller–Madow terms

**Response.** Equation 7, the worked example, code, and empirical reporting shell now use the same observed-support correction. The full-support values are .175 bits for 12×12, N=500 and .0225 bits for 4×4, N=288. The estimator remains first-order; residual bias is reported and permutation tests are used for null inference.

## Additional defect identified during revision: inert grammar-partition sweep

During the revision audit, we identified an additional defect. In both the submitted engine and the first revision, the nominal 60/40, 70/30, and 80/20 grammar-partition parameter was computed but never used. Held-out evaluation was hard-coded at .50. The original 1,440-cell grid was therefore 480 substantive configurations repeated three times.

We removed the split parameter entirely from `SimConfig` and from the grid. The Bernoulli engine models correctness on training-labelled versus held-out-labelled trial types; it does not represent individual combination identities, so a unique-combination partition cannot affect its behavior. The manuscript protocol still specifies an 80/20 grammar partition for real experiments, while the simulation states explicitly that this is an assumed protocol property rather than an engine factor. The 480 substantive cells were rerun with 100 paired replications each. A future explicit-combination engine could study partition balance, but that is a different model and is not introduced in this revision.

## Additional precision correction: common random numbers

The prior revision incorrectly said the two focal agents shared the base channel “exactly” while using different seed offsets. The revised engine now uses common random numbers. Within every Memorizer/Compositional pair, ground-truth intents, base response uniforms, and episode durations are identical. Base accuracy, MI, `B_min`, and `V_eff` are therefore exactly equal in Table 1, the matched-base sweep, and every grid cell.

## Reproducibility package

The package now includes deterministic Data S2 with `forced_commit_error`, revised Protocol S4, a color-vision-safe Figure 5, tests for channel isolation and estimator behavior, a clean-state quick path, a SHA-256 manifest, the executed BCI pipeline, trial-level predictions, the final BCI JSON, the independent validator, and deterministic manuscript-population scripts. The final BCI validator passed 713 checks with zero failures; the core test suite reports 39 passing tests. `python reproduce_all.py --quick` does not depend on cached grid or power output, and the simulation artifacts remain unchanged by the BCI completion.


