from pathlib import Path
import json, re, shutil, math, hashlib
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT
msrc=OUT/'source_inputs/documents/manuscript_original.md'
ssrc=OUT/'source_inputs/documents/supplement_original.md'
rsrc=OUT/'source_inputs/documents/response_original.md'
m=msrc.read_text();s=ssrc.read_text();r=rsrc.read_text()
changes=[]
def replace(old,new,label):
 global m
 assert old in m,label
 m=m.replace(old,new,1);changes.append(label)
def section(start,end,new,label):
 global m
 a=m.index(start);b=m.index(end,a)
 m=m[:a]+new.strip()+'\n\n'+m[b:];changes.append(label)
# Title, status, and concise abstract.
m=m.replace("**Harrison D. Fletcher**\nIndependent Researcher, Santa Rosa, California\nCorresponding author: harrisondfletcher@gmail.com", "**Harrison D. Fletcher**\n\nIndependent Researcher, Santa Rosa, California\n\nCorresponding author: harrisondfletcher@gmail.com")
replace('Version 4, September 2026.','Version 4.1, September 2026.', 'Version identifier changed to 4.1; empirical analyses retained.')
section('**Data and code availability.**','## Abstract', '''**Data and code availability.** Simulation code, the executed BCI code and prediction records, and revision-specific reporting scripts are supplied in the accompanying reproducibility releases. The project repository is https://github.com/harrisondfletcher/accuracy-illusion. The Open Practices Statement identifies the distinction between the project repository and the versioned materials accompanying this revision.
''','Replaced the execution-status box with a concise availability statement; kept withdrawn-analysis history in the response letter.')
abstract='''Aggregate accuracy does not identify all properties of communicative behavior. We introduce five measures organized into four experimental channels: information rate from mutual information and full episode duration, thresholded effective vocabulary, held-out compositional generalization, recovery after induced misunderstanding, and uncertainty selectivity from abstention and observed forced-commitment errors. Reference-design constructions establish that no population measure is recoverable from the other four under the stated conditions. In simulations, Memorizer and Compositional agents have identical realized base channels by construction, yet differ by 42–86 percentage points on held-out generalization while aggregate accuracy differs by 5–10 points. A 480-cell grid varies ontology size, base accuracy, class imbalance, and trial count. Metric-specific power analyses use 1,000 replications and empirical-size checks; a .10 compositional difference requires approximately 400 held-out trials per system, while a .05 base-accuracy difference reaches .82 power at 750 base trials under the specified system-label permutation test. Uncertainty results include abstention coverage and error-stratum summaries. In a completed nine-subject BCI Competition IV-2a application, primary-decoder information rates span 0.65–8.92 bits/min and mean kappa is .493; an FBCSP-style decoder yields mean kappa .591. All nine subject-specific independence tests reject after Holm adjustment under each decoder. At F1 ≥ .90, no subject retains a qualifying class under the primary decoder, whereas three retain at least one under FBCSP-style decoding. The dataset cannot measure the three specialized channels. Code, data, and design requirements are provided.'''
assert len(abstract.split())<=250,len(abstract.split())
a=m.index('## Abstract');b=m.index('**Keywords:**',a)
m=m[:a]+'## Abstract\n\n'+abstract+'\n\n'+m[b:]
changes.append(f'Abstract shortened to {len(abstract.split())} whitespace-delimited words; corrected threshold counts and scoped the population proof.')
# Local mathematical precision; all changes explicitly logged.
replace('We define each formally, prove its properties, prove that no measure is a function of the others, state the design element each requires,', 'We define each formally, establish its stated properties and reference-design nonrecoverability, state the design element each requires,','Scoped introductory nonrecoverability claim to the construction actually proved.')
replace('The second demonstrates compositional structure that the first does not. No standard metric distinguishes these cases.', 'The second provides evidence about held-out compositional behavior that the first task does not elicit. Equal aggregate scores alone do not distinguish these experimental conditions.','Narrowed the introductory accuracy example to the information supplied by its design, without an unsupported claim about all standard metrics.')
replace('The plug-in estimator is biased upward in finite samples; all reported values are bias-corrected by Eq. 7 (Section 7) and are not truncated at zero.', 'Here I denotes population mutual information; substitution of the empirical joint distribution gives the plug-in estimator. Reported sample estimates use the first-order correction in Eq. 7 (Section 7) and are not truncated at zero. Population constructions in Sections 3–4 do not include a finite-sample correction.','Distinguished population MI in proofs from sample estimates and their corrections.')
replace('Report B_min with a bootstrap 95% confidence interval (10,000 resamples, stratified by design strata where present, bias correction applied inside each resample) and, for confirmatory inference, the permutation procedure appropriate to the design (Section 7).', 'Report B_min with a descriptive bootstrap 95% interval (10,000 resamples, with bias correction recomputed within each resample). Resampling must respect the design, including relevant strata, pairing, and clustering. Confirmatory inference uses a permutation scheme with justified exchangeability for the specified null (Section 7).','Clarified design-respecting resampling and permutation-null assumptions.')
replace('held-out set U = G \\ T,',r'held-out set $\mathcal{U}=G\smallsetminus T$,','Repaired the set-difference expression using editable mathematical markup.')
replace('combination ∈ U)   (4)','combination ∈ 𝒰)   (4)','Separated the held-out-set symbol from uncertainty selectivity U.')
replace('Chance baseline = 1/|responses|.', 'Under an independent uniform-response null with one correct answer per item, the baseline is 1/|responses|; other response or scoring designs require an explicit null.','Qualified the compositional chance baseline to its actual null model.')
replace('Report U with a Newcombe hybrid-score interval or a stratified bootstrap, together with abstention rate, commitment coverage, n_{e=1}, and n_{e=0}.', 'Report U with a Newcombe hybrid-score interval or a design-respecting stratified bootstrap, together with abstention rate, commitment coverage, both conditional abstention rates, n_{e=1}, and n_{e=0}.','Completed the uncertainty reporting contract.')
# Replace Section 3.4, preserving the original theory but restricting the proof.
section('### 3.4 What "irreducible" means','### 3.5 Covariation',r'''### 3.4 What "irreducible" means

We use *irreducible* to mean nonrecoverability of one population measure from the remaining four over a specified class of behavioral channels. Proposition 4 establishes this result for the reference design below; it is not a claim for every ontology, threshold, sample allocation, or restricted agent architecture. In particular, a thresholded count can become constant under a degenerate design. Functional nonrecoverability is distinct from statistical independence and from a requirement that every empirical application measure all five quantities.

For the population constructions, F1 is computed from the joint probabilities and support eligibility is fixed by the planned allocation. Write $F1_P(z)=2P(z,z)/[P_Y(z)+P_{\widehat Z}(z)]$ and $V_{\mathrm{eff}}^{\mathrm{pop}}(\alpha,\beta)=\sum_z\mathbf{1}\{F1_P(z)\geq\alpha,\ n_z^{\mathrm{plan}}\geq\beta\}$. This is the population counterpart of the observed count in Eq. 3, not a finite-sample estimator. Let the common episode-duration distribution have a finite positive mean $\mu_\tau$, so that population $B_{\min}=I/\mu_\tau$.

**Proposition 3 (base MI does not determine held-out generalization).** Fix a base-channel joint distribution $P(Y,\widehat Z)$, its episode-duration distribution, and a nonempty held-out trial set. Suppose each held-out trial permits a correct and an incorrect response, and the admissible behavioral-channel class allows separate response laws on base and held-out trials. For every $c\in[0,1]$, a channel in this class has base distribution P and $C_k=c$.

*Proof.* Retain P and the duration law on base trials. On each held-out trial, emit a correct response with probability c and an incorrect response with probability $1-c$. The base law, MI, and information rate remain fixed, while the held-out correctness probability is c. This constructs a behavioral channel; it does not establish how a particular learning mechanism acquires it. *End of proof.*

**Proposition 4 (functional nonrecoverability in the reference design).** Fix four equiprobable base intents, $\alpha=.80$, a planned allocation $n_z^{\mathrm{plan}}\geq\beta$ for every intent, and a common positive finite mean episode duration. Allow unrestricted stochastic response laws on the four protocol channels, with correct and incorrect responses available on held-out and repair trials and both uncertainty error strata having positive probability. For each population quantity $M\in\{B_{\min},V_{\mathrm{eff}}^{\mathrm{pop}},C_k,R,U\}$, two admissible channels agree on the other four quantities and differ on M. Therefore none of these five population quantities is a function of the other four over this channel class.

*Proof.* To vary $C_k$ or R, fix the base joint law and all other channel laws, and change only the corresponding correctness or recovery probability. To vary U, fix the other channel laws and the uncertainty error probability at one half. An abstention signal independent of error has $U=0$; a signal equal to the error indicator has $U=1$. Both uncertainty strata remain nonempty at population level, and no other reported population quantity changes. These constructions use the explicitly allowed independent specification of channel laws, not disjoint sampling alone.

For $V_{\mathrm{eff}}^{\mathrm{pop}}$, use the two four-class matrices in Section 4.3. Their population MI values are equal, their duration means are equal, and their thresholded counts are four and two. Hold the specialized channel laws fixed. For $B_{\min}$, use symmetric four-class matrices with diagonal probabilities .85 and .95 and uniform off-diagonal errors. Both have $V_{\mathrm{eff}}^{\mathrm{pop}}(.80,\beta)=4$, but their MI values are approximately 1.152 and 1.634 bits. Hold the duration and specialized-channel laws fixed. Each construction gives two channels with the same remaining four quantities and a different target quantity. *End of proof.*

Finite-sample estimates need not satisfy the equalities in the population constructions. In particular, the Section 4.3 matrices have different joint supports and hence can receive different first-order finite-sample corrections. Estimation and uncertainty are treated in Section 7. The matched-base simulation establishes a separate, exact sample-level equality by reusing the same realized base records.
''','Replaced Proposition 4 with the demonstrated nondegenerate reference-design population theorem; added explicit witnesses, assumptions, and estimator distinction.')
replace('To see how the measures covary when nothing forces them apart, we simulated', 'To describe covariation under a continuously parameterized generator rather than only the programmed archetypes, we simulated','Removed a misleading characterization of the synthetic covariance design.')
# Monotonicity proof.
old='*Proof.* The joint distribution becomes P_ε(y, ẑ) = (1 − ε) P₀(y, ẑ) + ε P_Y(y)/|Z|, the second term being the product of the Y-marginal and the uniform distribution on Ẑ (the joint is uniform only when Y is uniform). Ẑ(ε) is obtained from Ẑ by a channel that does not depend on Y, so by the data processing inequality I(Y; Ẑ(ε)) ≤ I(Y; Ẑ). At ε = 1, Ẑ is independent of Y. *End of proof.*'
new=r'''*Proof.* The joint law is $P_\epsilon(y,\widehat z)=(1-\epsilon)P_0(y,\widehat z)+\epsilon P_Y(y)/|Z|$. For $0\leq\epsilon_1<\epsilon_2\leq1$, apply to the $\epsilon_1$ output another independent uniform-replacement channel with probability

$$\delta=\frac{\epsilon_2-\epsilon_1}{1-\epsilon_1}.$$

Its retained-original weight is $(1-\delta)(1-\epsilon_1)=1-\epsilon_2$, so the resulting channel is exactly the $\epsilon_2$ channel. Thus $Y\to\widehat Z_{\epsilon_1}\to\widehat Z_{\epsilon_2}$ is a Markov chain and data processing gives $I(Y;\widehat Z_{\epsilon_2})\leq I(Y;\widehat Z_{\epsilon_1})$. At $\epsilon=1$ the output is independent of Y, so MI is zero. *End of proof.*'''
replace(old,new,'Completed Proposition 1 with the arbitrary intermediate-noise comparison.')
replace('**C_k.** C_k ∈ [0, 1]; chance = 1/|responses|; values below chance indicate systematic misapplication and are diagnostically informative.', '**C_k.** C_k ∈ [0, 1]. The independent uniform-response reference is 1/|responses| under the conditions in Section 2.4. A sample estimate below that reference requires uncertainty assessment before interpreting systematic misapplication.','Aligned the C_k bounds paragraph with the explicit chance model.')
replace('and Agent beta has the same MI to numerical precision.', 'and Agent beta has the same MI at the ten decimal places reported. Exact equality refers to the unique root q in (.5,.81) of the entropy equation, rather than to an arbitrary rounding of that root.','Defined exact equality through the entropy root while preserving the displayed numerical example.')
replace('Thus neither MI nor V_eff is a function of the other under fixed thresholds.', 'Thus neither population MI nor the support-eligible population vocabulary count determines the other in this reference design.','Aligned Section 4.3 with the restricted population theorem.')
replace('so that base accuracy equals p exactly.', 'so that the population base correctness probability is p; realized sample accuracy fluctuates around it.','Distinguished the generator correctness parameter from realized accuracy.')
replace('the default N = 1,000 gives 500 base trials, satisfying β·|Z| = 360.', 'the default N = 1,000 gives 500 base trials, exceeding the aggregate lower bound β·|Z| = 360; actual per-class eligibility is still checked.','Clarified that total support alone does not guarantee per-class support under random allocation.')
old=m[m.index('**Table 1.**'):m.index('\n\n| | Random',m.index('**Table 1.**'))]
new='''**Table 1.** Metric profiles at default parameters (|Z| = 12, N = 1,000, 400 runs). Mean (SD). Reference values are C₂=.083 under uniform response, R=.160 under the independent-uniform two-attempt simulation null, and U=0 under abstention-error independence. Every run contains 150 uncertainty trials. U was estimable in all 400 runs for every agent. Supplementary Tables S1b–S1c report abstention, commitment coverage, conditional abstention rates, and error-stratum counts for these same core runs. Data S2 is a separate worked example, not the source of the core-run denominators.'''
replace(old,new,'Pointed Table 1 to the recovered core-run uncertainty companion tables, not the separate S2 example.')
# BCI edits preserve all empirical numbers and selection history.
section('## 6. Empirical Application: BCI Competition IV-2a','### 6.1 Data, preprocessing, and decoders', '''## 6. Empirical Application: BCI Competition IV-2a

We report a subject-specific replacement analysis of BCI Competition IV Dataset 2a. Both predeclared decoders were executed for all nine subjects. The analysis specification was frozen before evaluation-session decoding in this replacement run; its timestamp, design fingerprint, pre-evaluation amendments, and validation records are provided in the supplementary release. The response letter documents why the original analysis was withdrawn.
''','Moved revision history and implementation fingerprint out of the main BCI opening; retained explicit replacement-run scope.')
old=m[m.index('`bci_pipeline.py` reads the 18'):m.index('\n\nThe primary decoder',m.index('`bci_pipeline.py` reads the 18'))]
new='''The pipeline reads the 18 official BNCI MAT files directly, preserving the six source task runs per session. The decision window is 0.5–2.5 s after cue onset, equivalent to 2.5–4.5 s after the source trial trigger. Exact sample coordinates and timing checks are documented in Supplementary S8. Organizer artifact flags are applied identically to both decoders. They exclude 224 of 2,592 scheduled evaluation trials, ranging from 5 to 73 exclusions per subject (1.7%–25.3%). Evaluation samples therefore contain 215–283 trials, with 53–72 observations per class; every class meets β=30. Subject- and class-specific training and evaluation counts are reported in S8. Exactly 22 EEG channels enter the decoders; the three EOG channels are excluded.'''
replace(old,new,'Added evaluation exclusion totals and class-support range; shortened main-text implementation prose.')
old=m[m.index('The primary decoder uses a fixed'):m.index('\n\nA separate FBCSP-style',m.index('The primary decoder uses a fixed'))]
new='''The primary decoder uses the fixed post-cue window and an 8–30 Hz zero-phase MNE FIR filter with `firwin` design, applied independently to each continuous source run before epoching. Both decoders use class-wise concatenated training epochs for CSP covariance estimation with Ledoit–Wolf shrinkage and no trace normalization (`reg="ledoit_wolf"`, `cov_est="concat"`, `norm_trace=False`); LDA uses automatic covariance shrinkage. The primary one-vs-rest classifier selects 4, 6, or 8 CSP components by six-fold leave-one-source-run-out cross-validation within T. All fitting occurs inside the training folds, score ties select the smaller component count, and the selected model is refit on clean T before E is evaluated. Resolved filters, software versions, channel order, and tuning details are archived in the result JSON.'''
replace(old,new,'Kept explicit executed covariance regularization and tuning while removing log-style prose.')
replace('Conventional Wolpaw ITR is reported beside B_min for comparison, with its uniform-class and symmetric-error assumptions stated; the unclipped formula value is recorded alongside the conventional below-chance-zero presentation.', 'Supplementary Table S8d compares conventional Wolpaw ITR and B_min using the same full-cycle denominator. ITR assumes uniform class priors and symmetric errors; the source JSON also retains the unclipped formula and its below-chance-zero presentation.','Corrected the ITR cross-reference to a newly populated readable table.')
old=m[m.index('**Validated BCI result summary.**'):m.index('\n\nNo pooled row',m.index('**Validated BCI result summary.**'))]
new='''**BCI result summary.** Mean accuracy and kappa are .620 and .493 for the primary decoder and .692 and .591 for the FBCSP-style decoder. The specified within-run independence null is rejected after Holm adjustment for all nine subjects under both decoder families (raw p=1/5001; adjusted p=9/5001=.00180). These are within-subject tests, not tests of differences between subjects. As an exploratory illustration, S1 and S8 have accuracies .779 and .775 and information rates 8.92 and 7.43 bits/min. This pair was selected to maximize the B_min gap among pairs within .03 accuracy whose independence tests rejected; the selection and the two subject-specific tests do not establish a significant between-subject difference.'''
replace(old,new,'Removed the nonexistent remaining-subjects phrase and preserved the exploratory pair-selection disclosure.')
replace('No pooled row is permitted as an operating-system claim. A micro-average may appear in Supplementary Table S8 only, labeled as a descriptive aggregation of heterogeneous subject-specific systems.', 'No pooled confusion matrix is interpreted as an operating subject-specific BCI. All reported operating-system estimates are subject-specific.','Replaced residual editing instructions about pooling with the executed reporting statement.')
replace('Complete per-subject V_eff curves appear in Supplementary Table S8.', 'Complete per-subject V_eff curves for both decoders appear in Supplementary Table S8e.','Added explicit reference to both decoder threshold tables.')
old=m[m.index('The FBCSP-style decoder is reported in Supplementary Table S8 with the same fields.'):m.index('\n\n### 6.3',m.index('The FBCSP-style decoder is reported in Supplementary Table S8 with the same fields.'))]
new='''The FBCSP-style results and paired descriptive contrasts are reported in Supplementary S8. Accuracy is higher under FBCSP-style decoding for seven of nine subjects; S2 and S9 are the exceptions. Threshold dependence changes with the decoder: at F1 ≥ .90, the primary decoder has no qualifying class in any subject, whereas FBCSP-style decoding retains at least one class in S1, S3, and S7. The complete subject-level curves, rather than one threshold, characterize this decoder dependence. The paired intervals are descriptive and are not multiplicity-adjusted between-decoder hypothesis tests.'''
replace(old,new,'Clarified decoder-specific threshold results and separated descriptive contrasts from confirmatory within-subject tests.')
replace('All MI values in this paper, simulated and empirical, use Eq. 7 on observed support and are not truncated at zero.', 'All reported sample MI estimates use Eq. 7 on observed support and are not truncated at zero. The population examples in Sections 3–4 use the MI functional without a sample-size correction.','Removed the conflict between population matrices and the blanket correction statement.')
replace('For two independent systems, pool complete episode records and permute system labels; for paired systems, swap decoder outputs within episodes. These tests capture finite-sample bias in the null itself.', 'For two independent systems with exchangeable complete episode records under the null, pool the records and permute system labels. For paired systems under a within-pair exchangeability null, swap the paired records while preserving their pairing and relevant design strata. Such tests are exact under their exchangeability nulls, not under equality of the scalar B_min alone. The zero-effect simulation in Section 5.7 satisfies the stronger common-distribution null. The permutation reference captures the statistic\'s finite-sample behavior under that null.','Clarified the null required by system-label permutation without changing any executed test.')
replace('The central methodological contribution is not any single measure — MI has existed for 75 years — but the demonstration that no measure in the suite is a function of the other four (Proposition 4), together with the specification of what each requires of a design (Table 0).', 'The central methodological contribution is not any single measure, but the reference-design construction showing that none of the five population quantities is recoverable from the other four over the stated behavioral-channel class (Proposition 4), together with the design requirements for each measure (Table 0).','Propagated the theorem scope into the discussion.')
replace('The definitions reference no application domain. Table 0 states what each measure requires. The BCI application is designed to demonstrate both halves after its execution gates pass: base-channel measures are computable from subject-specific confusion matrices, whereas the three specialized measures remain not measurable because the paradigm lacks their design elements.', 'The definitions reference no application domain, but their computability depends on experimental design. The completed BCI application illustrates both points: base-channel measures are computed from subject-specific confusion matrices, whereas the three specialized measures remain unmeasured because IV-2a lacks the required manipulations. This application does not establish cross-domain criterion validity for the complete suite.','Removed obsolete future-tense execution language and retained domain-validity limits.')
replace('The original empirical claims were withdrawn rather than repaired rhetorically, and the replacement analysis has now been executed under a frozen design.', 'The replacement empirical analysis was executed under the frozen design described in Section 6.','Removed rhetorical revision-history wording from the discussion.')
# No new arbitrary 300-trial R threshold not directly in supplied grid.
replace('δ_R = 0.10 requires n_R ≈ 300;', 'δ_R = 0.10 has power .63 at n_R=200 and .91 at n_R=400;', 'Replaced an untested interpolated R planning threshold with the actual tested cells.')
# Formal measurement-error caveat, logged rather than silently imported.
section('## 9. Measurement Error','## 10. Separating Conditioning from Representation',r'''## 9. Measurement Error

Ground-truth labeling is not error-free. Let $Y_{\mathrm{true}}$ denote the latent true label and $\widetilde Y$ the recorded label. Under a nondifferential labeling channel satisfying $\widetilde Y\perp\widehat Z\mid Y_{\mathrm{true}}$, the Markov relation $\widehat Z\to Y_{\mathrm{true}}\to\widetilde Y$ gives $I(\widetilde Y;\widehat Z)\leq I(Y_{\mathrm{true}};\widehat Z)$ by data processing. This population result does not imply that every finite-sample estimate decreases, and it does not hold for arbitrary differential labeling mechanisms.

There is no universal multiplicative correction: attenuation depends on the labeling channel. Where labeling error is material, report sensitivity analyses under explicit alternative labeling mechanisms or model the error process as a nuisance component (Archer et al., 2014). Accuracy-based C_k and R can be biased in either direction by erroneous outcome labels; their direction cannot be inferred from the MI inequality. For U, error-outcome misclassification independent of abstention conditional on the true outcome attenuates selectivity when the recorded outcome retains positive discrimination; differential or label-inverting error can behave differently. Inter-rater agreement documents reliability but does not by itself identify a true labeling-error rate.
''','Made the existing measurement-error argument mathematically explicit; removed unsupported universal accuracy attenuation. No empirical calculation changed.')
# Table comparison is scoped to scalar scores, not impossibility of established task-specific accuracies.
replace('**Table 4.**', '**Table 4.** Information supplied by an aggregate base-channel score versus the protocol-separated suite. Task-specific accuracy can measure held-out performance or recovery when those trials are actually collected; the contrast concerns what can be inferred from the base score alone.','Scoped the comparison table to base-channel scalar reporting.')
replace('| Penalizes intent confusion | Partial | Yes | Yes |','| Preserves intended-label correctness as a separate criterion | Yes | No: invertible label permutations preserve MI | Yes, through base accuracy and class-level F1 |','Corrected the MI-versus-label-correctness row without changing the proposed suite.')
# Declarations + Open Practices: no invented street address, phone, DOI, or registration.
section('## Declarations','## References', '''## Declarations

**Funding.** None.

**Competing interests.** None declared.

**Ethics approval.** Not applicable to the reported simulations and secondary analysis of the public benchmark; no new participants were recruited.

**Consent to participate and consent for publication.** Not applicable to this secondary analysis.

**Availability of data and materials.** Synthetic data, trial-level BCI prediction records, and supplementary results accompany the reproducibility releases. Raw EEG recordings are available from the official BNCI 001-2014 dataset source.

**Code availability.** The accompanying releases contain the simulation and executed BCI code. This reporting revision adds scripts and source hashes for the uncertainty summaries, expanded BCI tables, and timing audit.

**Author contributions.** H.D.F. conceived the framework and is responsible for the analyses and manuscript.

## Open Practices Statement

The materials supporting this revision are supplied in the accompanying simulation and BCI reproducibility releases, together with the Version 4.1 reporting supplement. They include synthetic worked-example data, simulation outputs and code, executed BCI configuration and environment records, prediction CSVs, the trial ledger, and reporting scripts. The project repository is https://github.com/harrisondfletcher/accuracy-illusion; the versioned accompanying releases, rather than an unversioned project page, identify the numerical sources of this revision. Raw BCI data are available from the official BNCI 001-2014 source (https://bnci-horizon-2020.eu/database/data-sets/001-2014/).

No public preregistration is claimed for these analyses. The replacement BCI analysis specification was frozen on September 9, 2026, before evaluation-session decoding in that replacement run; its design fingerprint and pre-evaluation amendments are archived. This local analysis freeze is not presented as a public preregistration. The subject-pair illustration in Section 6.2 is explicitly exploratory. The Version 4.1 additions are post-execution reporting corrections and deterministic reconstruction of already specified simulation runs, not new confirmatory studies.
''','Added structured declarations and the Open Practices Statement immediately before References; did not invent a public registration or claim the new release was uploaded.')
replace('S1 core profiles;', 'S1 core profiles and uncertainty companions;', 'Updated supplement inventory for the recovered uncertainty tables.')
replace('S8 subject-level primary and FBCSP-style BCI results plus a reference-only micro-average after execution.', 'S8 executed primary and FBCSP-style results, ITR comparisons, artifact counts, both threshold curves, and timing evidence.', 'Updated supplement inventory to the actual completed contents.')
replace('Fig. 2 subject-level accuracy, full-cycle B_min, and V_eff threshold sensitivity after BCI execution;', 'Fig. 2 subject-level accuracy, full-cycle B_min, and V_eff threshold sensitivity;', 'Removed obsolete after-execution language from figure inventory.')
replace('Fig. 4 per-subject BCI confusion matrices after execution;', 'Fig. 4 per-subject BCI confusion matrices;', 'Removed obsolete future execution phrase from confusion-figure inventory.')
# Essential equations as editable display mathematics.
equations={
'I(Y; Ẑ) = Σ_{y,ẑ} P(y, ẑ) log₂ [P(y, ẑ) / (P(y) P(ẑ))]   (1)':r'$$I(Y;\widehat Z)=\sum_{y,\widehat z}P(y,\widehat z)\log_2\frac{P(y,\widehat z)}{P_Y(y)P_{\widehat Z}(\widehat z)}.\qquad(1)$$',
'B_min = I(Y; Ẑ) / Ē[τ(e)]   (2)':r'$$B_{\min}=\frac{I(Y;\widehat Z)}{\mathbb{E}[\tau(e)]}.\qquad(2)$$',
'V_eff(α, β) = |{ z ∈ Z : F1(z) ≥ α and n(z) ≥ β }|   (3)':r'$$V_{\mathrm{eff}}(\alpha,\beta)=\left|\{z\in Z:F1(z)\geq\alpha,\ n(z)\geq\beta\}\right|.\qquad(3)$$',
'C_k = P(correct response | combination ∈ 𝒰)   (4)':r'$$C_k=P(\text{correct response}\mid\text{combination}\in\mathcal{U}).\qquad(4)$$',
'R = P(correct intent communicated within n turns | misunderstanding induced)   (5)':r'$$R=P(\text{correct intent within }n\text{ turns}\mid\text{misunderstanding induced}).\qquad(5)$$',
'U = P(a = 1 | e = 1) − P(a = 1 | e = 0)   (6)':r'$$U=P(a=1\mid e=1)-P(a=1\mid e=0).\qquad(6)$$',
'Î_corrected = Î − (K_YẐ − K_Y − K_Ẑ + 1) / (2N ln 2)   (7)':r'$$\widehat I_{\mathrm{MM}}=\widehat I_{\mathrm{plugin}}-\frac{K_{Y\widehat Z}-K_Y-K_{\widehat Z}+1}{2N\ln2}.\qquad(7)$$',
'D = I(Y; Ẑ) / log₂|Z|   (8)':r'$$D=\frac{I(Y;\widehat Z)}{\log_2|Z|}.\qquad(8)$$'
}
for old,new in equations.items():
 assert old in m,old
 m=m.replace(old,new)
for old,new in [('δ_C \\ n_U','δ_C / n_U'),('δ_R \\ n_R','δ_R / n_R'),('δ_U \\ n_A','δ_U / n_A'),('Δp \\ n_S','Δp / n_S')]:m=m.replace(old,new)
m=m.replace('N ∈ {100, …, 2,000}','N ∈ {100, 200, 500, 1,000, 2,000}').replace('p ∈ {0.50, …, 0.95}','p ∈ {.50, .60, .70, .80, .90, .95}')
# Supplement: retain supplied values and add machine-exported fields.
s=s.replace('— Revision 4','— Revision 4.1',1)
s=s.replace('All simulation tables are machine-generated from seed 42. Table S8 is an execution-gated BCI shell and must be replaced only from a validated `bci_real_application_v4.json`.', 'Simulation values are retained from the archived seed-42 analyses. Tables S1b–S1c add deterministic reconstructions of the same 400 core runs per agent; the reconstructed original summary fields match the archive within numerical tolerance. Table S8 reports the completed BCI analysis. New BCI displays are exported from the archived result JSON without refitting either decoder.')
u=json.loads((OUT/'evidence/CORE_UNCERTAINTY_REPORT.json').read_text())['summaries']
core=['random','class_biased','overproduction','memorizer','compositional']
display={'random':'Random','class_biased':'Class-Biased','overproduction':'Overproduction','memorizer':'Memorizer','compositional':'Compositional'}
# Transpose original S1 for readable portrait/landscape flexibility.
s1_start=s.index('## Table S1.');s1_end=s.index('## Table S2.',s1_start)
fields=[('accuracy_base','Base accuracy',3),('mi','MI, bits',3),('b_min','B_min, bits/min',3),('veff_60','V_eff(.60)',2),('veff_80','V_eff(.80)',2),('c2','C2',3),('r','R',3),('u','U',3)]
def ms(a,k,n=3):d=u[a][k];return f'{d["mean"]:.{n}f} ({d["sd"]:.{n}f})'
s1=['## Table S1. Core agent profiles','', '### Table S1a. Existing metric profiles','', '400 runs per agent; |Z|=12, total N=1,000, 500 base trials per run. Cells are mean (sample SD) across runs. These are the original numerical profiles, reorganized for readability.', '', '| Measure | Random | Class-Biased | Overproduction | Memorizer | Compositional |','|---|---:|---:|---:|---:|---:|']
for k,label,n in fields:s1.append('| '+label+' | '+' | '.join(ms(a,k,n) for a in core)+' |')
s1+=['','Reference values: C2=1/12 under uniform response; R=1−(11/12)² under the simulation\'s independent-uniform two-attempt receiver null; U=0 under abstention-error independence.','', '### Table S1b. Uncertainty selectivity and operating behavior','', 'Each original core run contains 150 uncertainty trials. Conditional rates are computed within each run, then summarized; they are not ratios of pooled counts. Commitment coverage equals one minus the abstention rate. Cells are mean (sample SD) across the same 400 runs.','', '| Agent | U | Abstention rate | Commitment coverage | P(A=1 given E=1) | P(A=1 given E=0) |','|---|---:|---:|---:|---:|---:|']
for a in core:s1.append('| '+display[a]+' | '+' | '.join(ms(a,k) for k in ['u','abstain_rate','commitment_coverage','u_tpr','u_fpr'])+' |')
s1+=['','### Table S1c. Forced-commitment denominators','', '| Agent | Error count, mean (SD) | Error count range | Correct count, mean (SD) | Correct count range | Non-estimable U runs |','|---|---:|---:|---:|---:|---:|']
for a in core:
 d=u[a];s1.append(f'| {display[a]} | {ms(a,"u_n_err",2)} | {d["u_n_err"]["min"]:.0f}–{d["u_n_err"]["max"]:.0f} | {ms(a,"u_n_ok",2)} | {d["u_n_ok"]["min"]:.0f}–{d["u_n_ok"]["max"]:.0f} | {d["u"]["n_nan"]}/400 |')
s1+=['', 'The complete per-run denominators and conditional rates are in `evidence/core_uncertainty_runs.csv`; source hashes, summary comparisons, and aggregation definitions are in `evidence/CORE_UNCERTAINTY_REPORT.json`. These records reconstruct the original seeded core runs using the unchanged archived engine. Data S2 is a different illustrative dataset.','']
s=s[:s1_start]+'\n'.join(s1)+'\n'+s[s1_end:]
s=s.replace('## Table S8. BCI execution-gated supplementary report'+s.split('## Table S8. BCI execution-gated supplementary report')[1].split('## Supplementary Table S8 (executed):')[0], '')
s=s.replace('## Supplementary Table S8 (executed): FBCSP-style robustness decoder and decoder contrasts','## Table S8. Executed subject-specific BCI results\n\n### Table S8a. FBCSP-style robustness decoder')
s=s.replace('### Paired decoder contrasts (FBCSP minus primary; identical bootstrap resamples)','### Table S8b. Paired decoder contrasts (FBCSP minus primary)\n\nIntervals use identical bootstrap resamples of the shared evaluation trials. They are descriptive, not multiplicity-adjusted confirmatory between-decoder tests.')
s=s.replace('### Artifact exclusions by subject and session (organizer flags)','### Table S8c. Artifact exclusions by subject and session (organizer flags)')
s=s.replace('### All-scheduled sensitivity (frozen decoders, flagged epochs included)','### Table S8f. All-scheduled sensitivity (frozen decoders, flagged epochs included)')
s=s.replace('### Full V_eff threshold curves per subject (primary decoder)','### Table S8e. Full V_eff threshold curves\n\n**Primary decoder.** Counts use alpha values shown and beta=30; all evaluation classes satisfy the support requirement.')
bci=json.loads((OUT/'source_inputs/bci/bci_real_application_v4.json').read_text())
subjects=[f'S{i}' for i in range(1,10)]
def table(rows,head):return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(row)+' |' for row in rows])
itr_rows=[]
for sub in subjects:
 for dec in ['primary','fbcsp']:
  d=bci['subjects'][sub]['decoders'][dec]
  itr_rows.append([sub,'Primary' if dec=='primary' else 'FBCSP-style',str(d['N']),f'{d["mi_corrected_bits"]:.3f}',f'{d["b_min_bpm"]:.2f}',f'{d["itr_bpm"]:.2f}'])
itr='''### Table S8d. Information-rate comparison\n\nBoth rates use the same measured full cycle of 8.043148936 s. B_min uses the subject's observed joint distribution and first-order MI correction. Conventional Wolpaw ITR uses accuracy, four equiprobable classes, and symmetric errors; it is a reference calculation, not a second measurement of the same error geometry. Every observed accuracy exceeds .25, so the stored formula and below-chance-clipped ITR agree here.\n\n'''+table(itr_rows,['Subject','Decoder','n','Corrected MI, bits','B_min, bits/min','Wolpaw ITR, bits/min'])+'\n\n'
s=s.replace('### Table S8e.',itr+'### Table S8e.',1)
fb_rows=[]
for sub in subjects:
 d=bci['subjects'][sub]['decoders']['fbcsp'];fb_rows.append([sub]+[str(d['veff_curve'][str(a)]) for a in [.4,.5,.6,.7,.8,.9]])
fb='''**FBCSP-style decoder.** The same thresholds and support rule apply.\n\n'''+table(fb_rows,['Subject','.40','.50','.60','.70','.80','.90'])+'\n\n'
s=s.replace('### S8 methods note:',fb+'### Table S8g. Methods note:',1)
s=s.replace('is released as `TRIGGER_SCHEDULE_AUDIT.json`.', 'is provided as `evidence/TRIGGER_SCHEDULE_AUDIT.json`. This reporting-stage audit recomputes the schedule comparison from the archived trial ledger; it does not claim to have reread the MAT binaries. It carries the ledger and result hashes, all six trigger vectors per file, all within-run interval vectors, and comparisons for all 18 file identities.')
# Move all-scheduled sensitivity after the curves for natural table order.
a=s.index('### Table S8f.');b=s.index('### Table S8d.',a)
block=s[a:b];s=s[:a]+s[b:];pos=s.index('### Table S8g.');s=s[:pos]+block+s[pos:]
# Add explicit S7 heading, power .10/.35 material is only in JSON reference, not readable original tables.
s=s.replace('All cells use 1000 Monte Carlo replications.', '## Table S7. Metric-specific power\n\nAll cells use 1000 Monte Carlo replications.',1)
s=s.replace('Cells: 480 (|Z| in {6,12,24,48} x p in {.5,...,.95} x Zipf s in {0,.5,1,1.5} x N in {100,...,2000})','Cells: 480 (|Z| in {6,12,24,48} x p in {.5,.6,.7,.8,.9,.95} x Zipf s in {0,.5,1,1.5} x N in {100,200,500,1000,2000})')
s=s.replace('Eigenvalues: [2.262, 1.033, 0.973, 0.626, 0.106]; cumulative variance: [0.452, 0.659, 0.854, 0.979, 1.0].','Pearson-correlation eigenvalues: [2.262, 1.033, 0.973, 0.626, 0.106]; cumulative variance: [0.452, 0.659, 0.854, 0.979, 1.0]. The displayed matrix above contains Spearman correlations. This distinction is preserved from the analysis.')
# More S8 export: support correction and all 72 class F1 / precision / recall documented; modest size.
rows=[]
for sub in subjects:
 for dec in ['primary','fbcsp']:
  d=bci['subjects'][sub]['decoders'][dec]
  rows.append([sub,'Primary' if dec=='primary' else 'FBCSP',f'{d["mi_plugin_bits"]:.6f}',f'{d["mi_mm_correction_bits"]:.6f}',f'{d["mi_corrected_bits"]:.6f}',f'{d["K_y"]}/{d["K_z"]}/{d["K_yz"]}'])
s+='\n### Table S8h. Observed-support MI correction components\n\n'+table(rows,['Subject','Decoder','Plug-in MI','Subtraction term','Corrected MI','Ky / Kz / Kyz'])+'\n\nAll MI quantities are in bits. Corrections are subject- and decoder-specific; rounded displays may differ in their last digit. Full precision remains in the source JSON.\n'
# Add concise metadata in supplement, not huge table of package versions.
sv=bci.get('software_versions',{})
s+='\n### Table S8i. Execution and reporting provenance\n\n'
s+='The executed BCI configuration uses 10,000 run-by-class stratified bootstrap resamples and 5,000 within-run label permutations per subject and decoder, with Holm correction across nine subjects separately by decoder. Source result SHA-256: `'+hashlib.sha256((OUT/'source_inputs/bci/bci_real_application_v4.json').read_bytes()).hexdigest()+'`.\n\n'
s+='Software versions recorded by the executed analysis: '+ '; '.join(f'{k}: {v}' for k,v in sv.items())+'.\n\n'
s+='The reporting revision does not refit CSP, LDA, or feature selection and does not replace any saved prediction, confidence interval, or permutation result. `evidence/BCI_EXTENDED_TABLES.csv` contains the expanded tabulations; `evidence/BCI_REPORTING_CHECKS.json` records the point-metric reconstruction. The executed-code archive remains the source for the full preprocessing environment and model-fitting workflow.\n'
# FINAL SUBMISSION 4.1 clerical journal-compliance edits (title page, DOI slot, split consent).
m=m.replace("Corresponding author: harrisondfletcher@gmail.com",
 "Correspondence: Harrison D. Fletcher, 2233 Gainsborough Ave, Santa Rosa, CA, USA. Telephone: +1 (972) 567-4006. Email: harrisondfletcher@gmail.com")
m=m.replace("and revision-specific reporting scripts are supplied in the accompanying reproducibility releases. The project repository is https://github.com/harrisondfletcher/accuracy-illusion. The Open Practices Statement identifies the distinction between the project repository and the versioned materials accompanying this revision.",
 "and revision-specific reporting scripts are supplied in the accompanying reproducibility releases. The exact Version 4.1 package is archived at https://doi.org/10.5281/zenodo.22681002. The project repository is https://github.com/harrisondfletcher/accuracy-illusion. The Open Practices Statement identifies the distinction between the project repository and the versioned archived release.")
m=m.replace("The project repository is https://github.com/harrisondfletcher/accuracy-illusion; the versioned accompanying releases, rather than an unversioned project page, identify the numerical sources of this revision.",
 "The exact Version 4.1 package supporting this revision is archived at https://doi.org/10.5281/zenodo.22681002; that versioned archive, rather than the unversioned project page (https://github.com/harrisondfletcher/accuracy-illusion), identifies the numerical sources of this revision.")
m=m.replace("**Consent to participate and consent for publication.** Not applicable to this secondary analysis.",
 "**Consent to participate.** Not applicable to this secondary analysis.\n\n**Consent for publication.** Not applicable to this secondary analysis.")
# Store change records and source outputs.
(OUT/'The_Accuracy_Illusion_v4_1_REVISED.md').write_text(m)
(OUT/'Supplementary_Tables_S0_S8_v4_1_REVISED.md').write_text(s)
(OUT/'evidence/TEXT_CHANGE_LOG.json').write_text(json.dumps({'changes':changes,'abstract_words_whitespace':len(abstract.split())},indent=2))
print('Abstract',len(abstract.split()),'Manuscript',len(m.split()),'Supplement',len(s.split()),'Changes',len(changes))
