# Response to Reviewers — Revision 4.1

**Manuscript:** *The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior*

The revision addresses the measurement definitions, formal scope, simulation implementation, power analysis, and subject-specific BCI application. The original BCI estimates were withdrawn; both replacement decoders were executed under a specification frozen before evaluation-session decoding in that replacement run. We also disclose defects found during revision rather than presenting the submitted implementation as valid.

Version 4.1 is a reporting and proof-precision revision of those completed analyses. Neither BCI decoder was refitted. Previously omitted uncertainty companions were recovered by deterministic replay of the original 400 core runs per agent; every archived core summary field compared matched within numerical tolerance. The new ITR, support-correction, and FBCSP threshold tables use the frozen BCI result JSON. The original 480-cell grid and power estimates are retained.

**Location convention.** References below identify manuscript sections and exact line ranges in the companion `The_Accuracy_Illusion_v4_1_SOURCE_LINES.txt`. These are source-text lines, not Word page-layout line numbers; the source index reproduces the delivered Markdown verbatim. Supplementary tables are identified by their stable labels.

## Reviewer 1

### Comment 1. BCI preprocessing, low decoder performance, and published benchmarks

**Response.** We agree that the original analysis did not sufficiently establish pipeline validity or reproducibility. It was withdrawn. The replacement uses all 18 official BNCI MAT files, with explicit source-run identity, trigger origins, organizer artifact flags, and T/E session labels. The analysis is subject-specific: all fitting and selection use T, followed by evaluation on E. Exactly 22 EEG channels enter the decoder; the three EOG channels are excluded. The fixed epoch is .5–2.5 s after cue onset, equivalent to 2.5–4.5 s after the source trial trigger.

The primary decoder applies an 8–30 Hz zero-phase FIR filter independently within each continuous source run. Both primary and filter-bank CSP estimate class-wise covariance from concatenated training epochs with Ledoit–Wolf shrinkage and no trace normalization. LDA uses automatic shrinkage. Primary component counts of 4, 6, or 8 and filter-bank feature counts of 16, 32, 64, or 96 are selected inside six-fold leave-one-source-run-out cross-validation on T, with all learned transforms fitted within the training folds.

Organizer flags exclude 224 of 2,592 evaluation trials, ranging from 5 to 73 exclusions per subject. Every evaluation class retains 53–72 observations and therefore satisfies beta=30. S8 reports training and evaluation counts and class-specific exclusions. Frozen-decoder all-scheduled sensitivity includes flagged E trials without refitting.

The primary decoder has mean accuracy .620 and mean kappa .493; the FBCSP-style decoder has .692 and .591. Ang et al.'s published OVR-CSP and OVR-FBCSP kappa values (.503 and .569) are contextual benchmarks, not exact targets, because their temporal evaluation differs. The implemented filter-bank decoder is explicitly called FBCSP-style rather than an exact replication. All confusion matrices and prediction records are retained. The published Ang report lacks the complete subject-level matrices needed to reconstruct the suite, so our fully reported stronger-decoder reanalysis addresses the underlying robustness concern.

**Location.** Sections 6.1–6.5; manuscript source L336–L393; Tables 3a–3b; Supplementary S8a–S8i; executed BCI code.

### Comment 2. Pooling, confidence intervals, and MI correction

**Response.** The pooled operating-system claim was removed. Estimates and inference are subject-specific. The observed-support first-order correction is recomputed for each subject and bootstrap resample, with no zero truncation. S8h now displays the plug-in MI, correction amount, corrected MI, and support dimensions.

Descriptive intervals use 10,000 resamples within evaluation source-run-by-class strata. Confirmatory independence tests use plug-in MI with 5,000 within-run label permutations and p=(b+1)/(B+1), followed by Holm adjustment over nine subjects separately by decoder. All nine tests reject the specified within-subject null under both decoders (adjusted p=9/5001=.00180). These results are not interpreted as between-subject significance. The S1/S8 illustration is explicitly exploratory and includes its selection rule.

Both primary and FBCSP-style per-subject vocabulary curves are now printed in S8e, rather than only summarized across subjects or stored in JSON. The threshold is a reference criterion, not an externally established usability boundary.

**Location.** Sections 2.2, 6.2, and 7; manuscript source L348–L380; Table 3a; S8d, S8e, and S8h.

### Comment 3. Episode duration and ITR comparability

**Response.** The original feature-window denominator was withdrawn. The replacement full-cycle mean uses all 282 within-source-run trigger intervals across the six E runs before artifact exclusion. Fixed cue offsets cancel in these differences; inter-run gaps do not enter the mean. The mean cycle is 8.043 s, not the two-second decision epoch or the original three-second denominator.

Table S8d now prints conventional Wolpaw ITR beside B_min for both decoders, using this common duration. The uniform-prior/symmetric-error assumptions of the conventional ITR are explicit. The all-file trigger-schedule assertion is supported by the supplied `TRIGGER_SCHEDULE_AUDIT.json`, which compares all 18 file identities using the archived 5,184-trial ledger. That reporting-stage audit is identified as a ledger reconstruction, not a new reading of the raw EEG binaries.

**Location.** Section 6.1; manuscript source L346–L347; S8d and S8g; timing-audit JSON.

### Comment 4. Section 4.3 required an explicit construction

**Response.** Proposition 3 now states the base-to-held-out nonrecoverability construction, including its behavioral-channel assumptions. Section 4.3 supplies explicit four-class matrices. The first matrix has diagonal .85 and .05 off-diagonal probabilities. The second has a first-block diagonal .81 and a second-block parameter q defined by the entropy equality, numerically q=.5467007423005. Both have population MI 1.1524153202 bits at the displayed precision, but population vocabulary counts at alpha=.80 are four and two. A converse example fixes the vocabulary count and varies population MI. No compositional performance is inferred from the geometry of the base errors.

Version 4.1 distinguishes these population identities from finite-sample corrected estimates. Equal population MI need not give equal Miller–Madow corrections when the matrices have different observed supports. Proposition 1 also now includes the additional replacement channel establishing monotonicity for every pair epsilon1<epsilon2, not only comparison with zero noise.

**Location.** Sections 3.4 and 4.2–4.3; manuscript source L190–L217; Propositions 1, 3, and 4.

### Comment 5. Power, replication, and effect-size definitions

**Response.** The submitted power experiment mixed programmed agent identity with the nominally varied accuracy parameter. It was replaced. Each panel now perturbs one metric-specific parameter, holds the other channels equal, uses 1,000 Monte Carlo replications, and reports a zero-effect size check and Wilson Monte Carlo intervals. Trial counts refer to observations entering the metric and, for two-system comparisons, are per system.

C2, R, and U use two-sided Fisher tests. B_min uses the two-sided system-label permutation procedure conditional on the pooled table, with 1,000 label permutations per replication and finite-permutation correction. Its exactness requires the stated exchangeability null; equality of a scalar information rate alone is not asserted to imply exchangeability. The zero-effect simulation uses a common generating distribution.

The revised tables distinguish an extreme chance-versus-.86 contrast from small effects. A .10 C2 difference around .50 requires approximately 400 held-out trials per system. For B_min, a .05 base-accuracy difference has power .665, .823, and .929 at 500, 750, and 1,000 base trials per system. The corresponding population difference is .628 bits/min at the simulated .5-minute cycle. Empirical size of the B_min procedure ranges .039–.057. Newly printed S7e–S7g expose the already archived uncertainty-error-fraction sensitivities and compositional-presence Monte Carlo intervals; no power simulation was rerun for this reporting revision.

**Location.** Sections 5.7 and 7; manuscript source L268–L322; Tables 2a–2e; Figure 5; S7a–S7g.

### Comment 6. Non-implications, circularity, and empirical non-redundancy

**Response.** We distinguish functional nonrecoverability from statistical independence and from criterion validity. Proposition 4 is now explicitly a population-level construction for the nondegenerate four-class reference design with alpha=.80, adequate planned support, fixed duration, and the specified class of behavioral channels. It is not claimed for every threshold, ontology, sample allocation, or restricted learning architecture. The proof gives witnesses for each metric, rather than relying on an unexpanded symmetric-construction assertion.

The programmed agents establish controlled separability, not discovered human/animal mechanisms. A separate population of 1,000 continuously parameterized synthetic agents reports covariance and its dependence on the generator. The text disclaims general empirical dimensionality. As requested, the discussion addresses incremental validity against an external criterion: a prospective study would test whether specialized measures add prediction of downstream task completion beyond base performance. IV-2a does not elicit Ck, R, or U, so it cannot establish that validity. We do not replace missing specialized observations with zero.

**Location.** Sections 3.4–3.5, 6.4, 14, and 15.1–15.4; manuscript source L137–L173; Propositions 3–4; Table 1a.

### Comment 7. Uncertainty selectivity and follow-up confounding

**Response.** The follow-up-resolution measure was replaced by U=P(A=1|E=1)−P(A=1|E=0), where E is the observed error of a forced commitment elicited before feedback on the same unchanged stimulus. It is not inferred from a difficulty label. U is selectivity/discrimination, not probabilistic calibration. Random abstention has population U=0; anti-selective behavior can produce negative values. A sample with an empty error or non-error stratum is not estimable, rather than assigned zero.

Because always-abstaining and never-abstaining systems can both have U=0, reporting includes abstention rate, commitment coverage, both conditional abstention rates, and both stratum counts. S1b–S1c now fulfill this requirement for the actual core experiment. We replayed the same 400 seeded runs per agent with the unchanged archived engine to recover these fields and checked every previously reported core summary field. The Compositional core runs have mean error/non-error counts 16.70/133.30 out of 150 uncertainty trials, with mean conditional abstention rates .444/.226; these yield mean U=.217. No core run has a non-estimable U. Data S2 is explicitly a separate worked example.

**Location.** Sections 2.6 and 5.5; manuscript source L89–L98; Table 1; S1b–S1c; core uncertainty CSV and reconstruction report.

## Reviewer 2

### Major Comment 1. Experimental requirements

**Response.** Table 0 identifies required ground truth, trial structure, and additional design elements for each measure. Section 6.4 applies this directly: IV-2a supports the base channel only. This is a limitation of the observations collected, not a zero score on unelicited behavior.

**Location.** Sections 2.7 and 6.4; manuscript source L99–L120; Table 0.

### Major Comment 2. Meaning of irreducibility

**Response.** Section 3.4 defines the restricted population-level nonrecoverability result and distinguishes it from covariance and application-specific computability. Scope qualifications now appear in the abstract, theorem, and discussion, and finite-sample corrections are treated separately.

**Location.** Section 3.4; manuscript source L137–L154.

### Major Comment 3. Allocation, null tests, and threshold sensitivity

**Response.** The channel allocation and actual run counts are explicit. Power is indexed by channel observations rather than a global minimum. Both decoder-specific threshold curves are printed by subject in S8e. The primary counts of subjects with at least one qualifying class are 9, 8, 7, 5, 4, and 0 at thresholds .40–.90; FBCSP-style counts are 9, 9, 7, 7, 5, and 3. Every evaluation class meets the fixed support requirement. Alpha=.80 is a reference threshold, not a universal usability criterion.

**Location.** Sections 5.2, 5.4, 5.7, and 6.2; manuscript source L224–L241; Tables 2a–2e and 3b; S8e.

### Minor Comment 1. Inconsistent replication counts

**Response.** Section 5.4 reports the actual counts: 400 core/null/counterexample runs, 300 runs per matched-base condition, 100 paired runs per grid cell, 1,000 covariance-population agents, and 1,000 replications per power cell. The 2,000 core runs replayed for S1b–S1c are the original seeds, not additional independent evidence.

**Location.** Section 5.4; manuscript source L238–L241.

### Minor Comment 2. Miller–Madow inconsistency

**Response.** Sample estimates use the observed-support first-order correction consistently. The full-support subtraction terms are approximately .175 bits for K=12,N=500 and .0225 bits for K=4,N=288. S8h prints the actual subject/decoder terms. Population examples are now explicitly excluded from the sample-correction convention. Residual small-sample bias remains disclosed.

**Location.** Section 7; manuscript source L394–L406; S8h.

## Additional implementation defects disclosed during revision

**Inert grammar-partition factor.** In the submitted engine and the first revision, nominal 60/40, 70/30, and 80/20 settings did not affect generated trials. The nominal 1,440-cell grid therefore did not represent 1,440 distinct conditions. The factor was removed; the corrected 480-condition grid was run with 100 paired replications per cell. The Bernoulli engine distinguishes training-labelled and held-out-labelled trial types but does not instantiate actual combination identities. The real-study grammar protocol and the simulated held-out evaluation allocation are now distinguished explicitly.

**Cross-channel contamination.** The previous base confusion matrix included specialized compositional, repair, and uncertainty episodes, allowing those behaviors to alter the quantities described as base-channel measures. The revised engine restricts B_min and V_eff to base episodes; each specialized metric uses its own channel. The affected simulation profiles and power analyses were regenerated during the earlier substantive revision.

**Class-Biased agent mismatch.** The previous favored classes were not aligned with the high-probability Zipf classes as the manuscript description implied. The revised specification uses the three most frequent intents. The results now report the observed .565 accuracy at s=1, consistent with the analytic .566 expectation under that rule, rather than retaining the unsupported .72 claim.

**Exact matched-base control.** Matching parameters under different random seeds does not produce identical realized base samples. The revised engine uses common random numbers for the paired Memorizer and Compositional base channel. Their sample-level equality is identified as a design control, not an empirical discovery.

## Final reporting and format corrections

The abstract is within 250 words. The Open Practices Statement appears immediately before References and distinguishes the local analysis freeze from public preregistration. Stale unpopulated-BCI instructions were removed. ITR and both decoder threshold curves are readable tables. The missing set-difference operator is encoded as editable mathematics, and table rows are kept intact in the Word versions. The reporting audit lists all additional mathematical qualifiers, including the exchangeability-null and measurement-error clarifications, without changing an executed BCI estimate.
