# Response to Reviewers — Revision 4

**Manuscript:** *The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior*

The revision changes the measurement architecture, formal claims, simulations, power analysis, BCI workflow, supplementary data, and reproducibility package. We also found and corrected an additional simulation defect that affected both the submitted engine and the first revision: the nominal grammar-partition factor was computed but never used. We describe that correction explicitly below rather than treating the original grid as valid.

The simulation results in the enclosed manuscript are final and regenerate from `python reproduce_all.py`. The replacement BCI analysis is execution-gated. The original BCI estimates are withdrawn, and no replacement estimate is asserted until `bci_pipeline.py` completes on all nine subjects and `validate_bci_output.py` passes. Bracket tokens in Section 6 are populated mechanically by `populate_bci_manuscript.py` from the validated JSON.

## Reviewer 1

### Comment 1. BCI preprocessing, low decoder performance, and published benchmarks

**Response.** We agree. The original empirical results are withdrawn. The replacement analysis is subject-specific and trains on session T, tunes only within T, and evaluates session E once. Supplementary Code S1b now:

- resolves training and evaluation sessions semantically rather than by lexical order;
- accepts either six source-run objects or the one-session-concatenated representation used by some MOABB releases and verifies six source runs from cue structure;
- rejects organizer-provided `bad_*` annotations explicitly through MNE Epochs and reports all, retained, and excluded trials by subject, session, and true class;
- uses exactly 22 EEG channels and excludes all EOG channels;
- fixes the primary epoch at 0.5–2.5 s after cue onset, or 2.5–4.5 s in absolute trial time;
- specifies an 8–30 Hz zero-phase MNE FIR filter with `firwin` design and writes resolved filter length, transition settings, sampling rate, software versions, and channel order to the result JSON;
- fits one-vs-rest CSP with Ledoit–Wolf regularization and shrinkage LDA, choosing 4, 6, or 8 CSP components by five-fold cross-validation on T only;
- reports per-subject accuracy and Cohen’s kappa;
- includes a separate nine-band FBCSP-style robustness decoder whose CSP and feature selection occur within T-session folds.

The robustness decoder is not called an exact reproduction of Ang et al. (2012). Their mean evaluation kappa values of .503 for OVR-CSP and .569 for OVR-FBCSP are benchmark context rather than exact fixed-window targets because their competition procedure used time-resolved predictions and maximum-over-time evaluation. Section 6.5 now states that Ang et al. do not provide the complete per-subject confusion matrices needed to reconstruct corrected MI, `B_min`, class-level F1, or `V_eff` from the publication alone.

**Location.** Sections 6.1–6.5; Supplementary Code `bci_pipeline.py`; `BCI_RUNBOOK.md`.

**Execution status.** Executed. All nine subjects were processed by both decoders under a pre-evaluation design freeze, and the results populate Section 6.1 (methods, including the Ledoit-Wolf CSP covariance and per-subject artifact counts), Table 3a (per-subject accuracy, kappa, corrected MI, Holm-adjusted p, B_min), Table 3b with per-subject curves in Supplementary Table S8, and Figures 2 and 4. The primary decoder's mean kappa of .494 sits beside the Ang et al. (2012) OVR-CSP context value of .503, with the protocol differences stated in Section 6.1.

### Comment 2. Pooled analysis, confidence intervals, and MI bias correction

**Response.** We agree. The pooled subject-level row and all operating-system interpretations of the pooled confusion matrix have been removed. A reference-only micro-average may appear in Supplementary Table S8 and is explicitly labeled as not corresponding to any subject-specific operating BCI.

Equation 7 now uses the observed-support first-order correction:

`I_MM = I_plugin − (K_YZ − K_Y − K_Z + 1)/(2N ln 2)`.

The full-support simplification `(K_Y−1)(K_Z−1)/(2N ln 2)` is stated separately. Corrected estimates are not truncated at zero. The BCI reporting shell requires, per subject and decoder, the plug-in estimate, correction amount, corrected estimate, class-stratified 10,000-resample interval, raw 5,000-permutation p-value, and Holm-adjusted p-value. Low-information subjects are not compared from point estimates alone.

**Location.** Sections 2.2, 6.2, 7, and 14; Table 3a; Supplementary Table S8; `bci_pipeline.py`.

### Comment 3. Episode duration and comparability with ITR

**Response.** We agree. The original 3 s feature-window denominator is withdrawn. The revised analysis estimates each subject’s full cycle from all 282 within-source-run inter-cue intervals across the six evaluation runs. The code rejects both a single-run estimate and intervals spanning run boundaries. `B_min` and conventional Wolpaw ITR are reported using the same full-cycle denominator. The manuscript distinguishes externally paced onset-to-next-onset duration from self-paced onset-to-resolution-or-timeout duration.

**Location.** Sections 2.1–2.2 and 6.1; `bci_pipeline.py`; `BCI_RUNBOOK.md`.

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

**Response.** Section 5.7 reports channel-specific sample counts, metric-scale effects, test statistics, empirical size, and Monte Carlo uncertainty. Section 2.3 describes `.80` as a simulation reference threshold rather than a universal usability criterion. Section 6.2 requires the full subject-level `V_eff` curve from .40 through .90 rather than a pooled headline.

### Minor Comment 1. Inconsistent 400 versus 1,000 run counts

**Response.** Section 5.4 now reports the actual counts: 400 runs for core/null/counterexample profiles; 300 per matched-base configuration; 100 paired runs per grid cell; 1,000 agents in the covariance analysis; and 1,000 replications per power cell.

### Minor Comment 2. Inconsistent Miller–Madow terms

**Response.** Equation 7, the worked example, code, and empirical reporting shell now use the same observed-support correction. The full-support values are .175 bits for 12×12, N=500 and .0225 bits for 4×4, N=288. The estimator remains first-order; residual bias is reported and permutation tests are used for null inference.

## Additional defect identified during revision: inert grammar-partition sweep

During the revision audit, we identified an additional defect. In both the submitted engine and the first revision, the nominal 60/40, 70/30, and 80/20 grammar-partition parameter was computed but never used. Held-out evaluation was hard-coded at .50. The original 1,440-cell grid was therefore 480 substantive configurations repeated three times.

We removed the split parameter entirely from `SimConfig` and from the grid. The Bernoulli engine models correctness on training-labelled versus held-out-labelled trial types; it does not represent individual combination identities, so a unique-combination partition cannot affect its behavior. The manuscript protocol still specifies an 80/20 grammar partition for real experiments, while the simulation states explicitly that this is an assumed protocol property rather than an engine factor. The 480 substantive cells were rerun with 100 paired replications each. A future explicit-combination engine could study partition balance, but that is a different model and is not introduced in this revision.

## Additional precision correction: common random numbers

The prior revision incorrectly said the two focal agents shared the base channel “exactly” while using different seed offsets. The revised engine now uses common random numbers. Within every Memorizer/Compositional pair, ground-truth intents, base response uniforms, and episode durations are identical. Base accuracy, MI, `B_min`, and `V_eff` are therefore exactly equal in Table 1, the matched-base sweep, and every grid cell.

## Defects disclosed during revision remain on the record

Three implementation defects identified and corrected during this revision
program remain disclosed rather than silently repaired:

1. **Inert grammar-partition sweep** (detailed above): the nominal 60/40,
   70/30, 80/20 split parameter was computed but never used; the parameter
   was removed and the 480 substantive cells rerun.
2. **Base-channel contamination:** earlier engine revisions allowed
   specialized-channel trials to enter the base confusion matrix. The
   revised engine isolates the channels ("Specialized trials never enter the
   base confusion matrix," Revision Audit section 1) and the released test
   suite enforces the isolation.
3. **Class-Biased implementation error:** the earlier Class-Biased null
   deviated from its declared response rule. The corrected implementation
   matches the analytic value implied by the rule (simulated .565 versus
   analytic .566 at Zipf s = 1, Section 5.6), and a released test pins the
   agent to that analytic value.

## Reproducibility package

The package now includes deterministic Data S2 with `forced_commit_error`, revised Protocol S4, a color-vision-safe Figure 5, tests for channel isolation and estimator behavior, a clean-state quick path, a SHA-256 manifest, the BCI validator, the BCI manuscript-population script, and a runbook. `python reproduce_all.py --quick` does not depend on cached grid or power output. The full simulation package regenerates all simulation-based manuscript quantities from seed 42.


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
