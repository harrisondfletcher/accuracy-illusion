# The Accuracy Illusion: Measuring What Accuracy Cannot in Communicative Behavior

**Harrison D. Fletcher**

Independent Researcher, Santa Rosa, California

Correspondence: Harrison D. Fletcher, 2233 Gainsborough Ave, Santa Rosa, CA, USA. Telephone: +1 (972) 567-4006. Email: harrisondfletcher@gmail.com

Revised manuscript for *Behavior Research Methods*. Version 4.1, September 2026.

**Data and code availability.** Simulation code, the executed BCI code and prediction records, and revision-specific reporting scripts are supplied in the accompanying reproducibility releases. The exact Version 4.1 package is archived at https://doi.org/10.5281/zenodo.22681002. The project repository is https://github.com/harrisondfletcher/accuracy-illusion. The Open Practices Statement identifies the distinction between the project repository and the versioned archived release.

## Abstract

Aggregate accuracy does not identify all properties of communicative behavior. We introduce five measures organized into four experimental channels: information rate from mutual information and full episode duration, thresholded effective vocabulary, held-out compositional generalization, recovery after induced misunderstanding, and uncertainty selectivity from abstention and observed forced-commitment errors. Reference-design constructions establish that no population measure is recoverable from the other four under the stated conditions. In simulations, Memorizer and Compositional agents have identical realized base channels by construction, yet differ by 42–86 percentage points on held-out generalization while aggregate accuracy differs by 5–10 points. A 480-cell grid varies ontology size, base accuracy, class imbalance, and trial count. Metric-specific power analyses use 1,000 replications and empirical-size checks; a .10 compositional difference requires approximately 400 held-out trials per system, while a .05 base-accuracy difference reaches .82 power at 750 base trials under the specified system-label permutation test. Uncertainty results include abstention coverage and error-stratum summaries. In a completed nine-subject BCI Competition IV-2a application, primary-decoder information rates span 0.65–8.92 bits/min and mean kappa is .493; an FBCSP-style decoder yields mean kappa .591. All nine subject-specific independence tests reject after Holm adjustment under each decoder. At F1 ≥ .90, no subject retains a qualifying class under the primary decoder, whereas three retain at least one under FBCSP-style decoding. The dataset cannot measure the three specialized channels. Code, data, and design requirements are provided.

**Keywords:** mutual information; communicative throughput; compositionality; measurement framework; adversarial evaluation; metric validation; behavioral methods; information theory


## 1. Introduction

In any domain where one agent must communicate intent to another through a constrained signal channel, researchers face a common measurement problem. The communicating agent — a non-human animal pressing buttons on a soundboard, a locked-in patient using a brain–computer interface, a prelinguistic infant producing gestures, a human speaker using an augmentative communication device — generates signals that must be decoded into intended meanings. The question "how effectively does this agent communicate?" requires a metric. In practice, the dominant metric is accuracy on paradigm-specific forced-choice tasks. This is insufficient for three reasons, a limitation recognized in signal detection theory (Green & Swets, 1966) and in systematic analyses of classification metrics (Sokolova & Lapalme, 2009).

First, accuracy conflates vocabulary size with communicative structure. An agent that correctly retrieves 10 of 12 named objects (accuracy 83%) and an agent that correctly executes 10 of 12 novel two-element command sequences (accuracy 83%) receive identical scores. The second provides evidence about held-out compositional behavior that the first task does not elicit. Equal aggregate scores alone do not distinguish these experimental conditions.

Second, accuracy provides no information about communicative robustness. An agent that performs well on standard trials but abandons communication after any error, and an agent that modifies its signal and recovers, both receive accuracy scores computed only from initial responses. The second demonstrates communicative repair — a capacity that is diagnostically and practically important — that accuracy does not capture.

Third, accuracy is sensitive to class imbalance. In paradigms where some intents are tested more frequently than others, or where agents overuse a dominant response, accuracy can be inflated. Mutual information addresses this. But mutual information alone does not capture compositionality, repair, or selective uncertainty signaling.

We propose a metric suite comprising five measures grounded in information theory and adversarial experimental design. We define each formally, establish its stated properties and reference-design nonrecoverability, state the design element each requires, validate the framework through simulation of programmed and continuously parameterized agents, report metric-specific power with empirical size checks, and provide a complete adversarial protocol with open-source evaluation code. The framework is domain-general in its definitions; Section 2.7 makes explicit what each measure requires of an experimental design.

To be explicit about scope: the metrics detect statistical structure in the mapping between agent emissions and ground-truth intents. They measure behavioral throughput. They do not measure, infer, or claim to detect internal semantic representations, conceptual understanding, or subjective experience. The framework asks: given that this agent produces signals and those signals are decoded, how much information is transferred, how compositionally structured is the transfer, how robust is it to disruption, and how selective is the agent's own uncertainty signaling? These are behavioral questions with information-theoretic answers.


## 2. Formal Definitions

### 2.1 Primitives

We define a communication system as a tuple (Σ, Z, E, d, Y).

**Σ (emission alphabet).** The finite set of discriminable tokens the agent can produce within the paradigm. |Σ| is fixed per study and declared in advance.

**Z (intent space).** The finite set of communicative intents defined by the experimental ontology. |Z| is fixed per study and pre-registered. Abstention is represented as a decoder outcome ∅ (Section 2.6), not as an element of Z.

**E (episode).** A bounded interaction window with measured duration τ(e) in minutes. In an externally paced design, τ(e) is onset to the next onset. In a self-paced design, it is onset to verified resolution or a pre-registered timeout. The decoder's feature-extraction window is never substituted for the full operational cycle.

**d (decoder).** A function mapping observed emissions to intent estimates. In deterministic paradigms, d is a fixed mapping. In probabilistic paradigms, d produces p(z | x) over Z plus an abstain outcome ∅, with a decision rule d(x) ∈ Z ∪ {∅} specified in advance.

**Y (ground truth).** The true intent for each episode, established by controlled experimental condition, independent sensor verification, or blinded human judges with pre-registered coding criteria and reported inter-rater reliability (κ ≥ 0.80). Ground truth is never determined by the decoder, by the handler, or by post-hoc narrative interpretation.

### 2.2 Metric 1: Effective Information Rate (B_min)

For N base-channel episodes with ground-truth labels Y = {y₁, …, y_N} and decoded intents Ẑ = {ẑ₁, …, ẑ_N}, compute the empirical joint distribution P(Y, Ẑ) from the confusion matrix, the marginals P(Y) and P(Ẑ), and mutual information:

$$I(Y;\widehat Z)=\sum_{y,\widehat z}P(y,\widehat z)\log_2\frac{P(y,\widehat z)}{P_Y(y)P_{\widehat Z}(\widehat z)}.\qquad(1)$$

Here I denotes population mutual information; substitution of the empirical joint distribution gives the plug-in estimator. Reported sample estimates use the first-order correction in Eq. 7 (Section 7) and are not truncated at zero. Population constructions in Sections 3–4 do not include a finite-sample correction. The effective information rate normalizes by mean episode duration:

$$B_{\min}=\frac{I(Y;\widehat Z)}{\mathbb{E}[\tau(e)]}.\qquad(2)$$

Mutual information measures statistical dependence between ground truth and decoded intent — how much knowledge of the decoded signal reduces uncertainty about the ground truth, in bits. It does not measure semantic richness, conceptual depth, or open-ended linguistic competence. Report B_min with a descriptive bootstrap 95% interval (10,000 resamples, with bias correction recomputed within each resample). Resampling must respect the design, including relevant strata, pairing, and clustering. Confirmatory inference uses a permutation scheme with justified exchangeability for the specified null (Section 7).

### 2.3 Metric 2: Effective Vocabulary Size V_eff(α, β)

For each intent z ∈ Z, compute the F1 score from precision and recall in the base-channel confusion matrix. Define a pre-registered minimum trial count β (β = 30 is used as a reference in the simulations) and an application-specific F1 threshold α (α = 0.80 is a reference threshold, not a universal usability standard).

$$V_{\mathrm{eff}}(\alpha,\beta)=\left|\{z\in Z:F1(z)\geq\alpha,\ n(z)\geq\beta\}\right|.\qquad(3)$$

The reliability required of a command is application-specific. Report V_eff at α ∈ {0.60, 0.70, 0.80, 0.90}, together with the pre-registered application threshold, as a discrimination curve rather than as a single cutoff. Describe intents as meeting the pre-specified F1 criterion rather than as usable. Under controlled equal allocation, β|Z| is a hard lower bound on base trials; under random or imbalanced sampling, additional trials are required to ensure that every intent reaches β.

### 2.4 Metric 3: Compositional Depth C_k

Define a compositional grammar G as a set of k-slot templates. Partition the valid combinations into a pre-registered training set T and a held-out set $\mathcal{U}=G\smallsetminus T$, balanced so that each individual element appears in both.

$$C_k=P(\text{correct response}\mid\text{combination}\in\mathcal{U}).\qquad(4)$$

"Correct response" means the agent executes the appropriate behavior for the novel combination, judged by a blinded evaluator against pre-registered criteria. Under an independent uniform-response null with one correct answer per item, the baseline is 1/|responses|; other response or scoring designs require an explicit null. Report with an exact binomial (Clopper–Pearson) interval and the number of held-out trials n_U.

C_k measures behavioral generalization to combinations withheld under a pre-registered grammar. Above-chance performance is consistent with productive compositional generalization but does not identify the internal mechanism producing it. The logic follows the systematicity requirement of Fodor and Pylyshyn (1988) as operationalized in SCAN (Lake & Baroni, 2018), COGS (Kim & Linzen, 2020), and the PCFG suite of Keysers et al. (2020); in the taxonomy of Hupkes et al. (2020), C_k is the productivity dimension. Values are comparable across studies only when grammar structure, hold-out construction, response space, and item difficulty are commensurate.

### 2.5 Metric 4: Repair Efficiency R

On a pre-registered proportion of trials (recommended 20%), the system induces misunderstanding by deliberately providing an incorrect response. The agent's behavior in the subsequent window (n turns, recommended n = 2) is classified as Repeat, Modify, Escalate, or Abandon.

$$R=P(\text{correct intent within }n\text{ turns}\mid\text{misunderstanding induced}).\qquad(5)$$

Under the independent-uniform repair null used in the simulations, recovery within n attempts is 1 − (1 − 1/|Z|)ⁿ (0.160 for |Z| = 12, n = 2). This is not a universal chance baseline: empirical studies must derive their null from the pre-registered receiver/decoder error process and repair policy. Report the outcome distribution as secondary data with inter-rater reliability κ ≥ 0.75.

### 2.6 Metric 5: Uncertainty Selectivity U

In forced-choice tasks, include an UNKNOWN/abstain option. For each uncertainty trial i, define the abstention indicator a_i ∈ {0, 1}. Whether or not the agent abstains, the protocol then elicits a forced commitment before revealing the outcome, and the error indicator e_i ∈ {0, 1} records whether that forced commitment was incorrect. Both a_i and e_i are observed on every uncertainty trial. Define

$$U=P(a=1\mid e=1)-P(a=1\mid e=0).\qquad(6)$$

U is Youden's J for abstention as a detector of forced-commitment error and, for a binary abstention decision, equals 2·AUROC − 1 (Chow, 1970; El-Yaniv & Wiener, 2010). U ∈ [−1, 1]. U = 0 when abstention is independent of error, including the case of an agent that never abstains, provided both strata e = 1 and e = 0 are observed; if either stratum is empty, U is not estimable and is reported as such. U > 0 indicates selective abstention; U < 0 indicates anti-selective abstention.

U measures discrimination, not probabilistic calibration: an agent can rank its uncertainty well while reporting poorly calibrated probabilities. The forced commitment must concern the same unchanged stimulus, follow after a fixed short delay, and occur without added task-relevant information. Report U with a Newcombe hybrid-score interval or a design-respecting stratified bootstrap, together with abstention rate, commitment coverage, both conditional abstention rates, n_{e=1}, and n_{e=0}. If a graded confidence score is available, report the risk–coverage curve and its area (AURC) as the primary measure, with U at the operating point as the summary; proper scoring rules (DeGroot & Fienberg, 1983; Guo et al., 2017) then measure calibration separately (Supplementary Code `metrics_u.py`).

### 2.7 Measurement channels and design requirements

The five measures are computed from four disjoint sets of trials, which we call protocol channels:

- base single-intent trials → B_min and V_eff (one confusion matrix)
- held-out compositional trials → C_k
- induced-error trials → R
- uncertainty trials → U

Compositional, repair, and uncertainty trials never enter the base confusion matrix. Table 0 lists the design element each channel requires. A paradigm lacking an element cannot compute the corresponding measure, and the framework's first output on any dataset is which rows are satisfied. Trial budgets for a target power are given in Section 5.7; they are metric- and effect-size-specific and are not repeated here.

**Table 0.** Design requirements by measure.

| Measure | Ground truth required | Trial structure | Additional design element |
|---|---|---|---|
| B_min | Per-episode intent label | Bounded episodes with timestamped full cycle | None |
| V_eff | Per-episode intent label | ≥ β trials per intent in the base channel | None |
| C_k | Correctness of the response to each combination | Pre-registered k-slot grammar with training / held-out partition | Held-out combinations withheld from training; blinded scoring |
| R | Correct intent known on each induced-error trial | Interactive, multi-turn | Pseudo-random induced misunderstanding; blinded repair coding (κ ≥ 0.75) |
| U | Forced-commitment error e_i on every uncertainty trial | Forced choice with abstain option, followed by forced commitment before feedback | Enough error trials to populate both strata |


## 3. Why Accuracy and Mutual Information Alone Are Insufficient

A reviewer may ask: mutual information already exists; what does this suite add? We answer in three steps. Sections 3.1–3.3 exhibit agent profiles that separate the measures pairwise. Section 3.4 states precisely what we mean by "irreducible" and proves it. Section 3.5 reports what the measures look like across a continuously parameterized population, which is a different question.

### 3.1 Counterexample 1: High MI, Zero Compositionality

An agent with |Z| = 12 responds correctly on single-intent trials with probability 0.90 and otherwise emits a uniformly chosen incorrect intent. On the base channel, accuracy is 0.90 and bias-corrected I(Y; Ẑ) ≈ 2.9 bits (upper bound log₂ 12 = 3.58). V_eff(0.80) is near |Z|. On a 2-slot grammar the agent has memorized the training combinations and responds at chance (1/12) on held-out combinations. MI is high, accuracy is high, V_eff is high; C₂ is at chance. The programmed behavior implements lookup-table success on trained combinations without productive held-out generalization. Simulated values: Table S2.

### 3.2 Counterexample 2: High MI and High C₂, Zero Repair

Extend the agent to generalize on held-out combinations (C₂ = 0.85). After an induced misunderstanding it always repeats the original signal identically. Under the simulation's independent-uniform receiver-error null, recovery within two attempts is 1 − (11/12)² = 0.16. MI is high, C₂ is high, and R is at its specified null.

### 3.3 Counterexample 3: High MI, High C₂, High R, Zero Uncertainty Selectivity

Extend the agent to modify its signal after induced error and recover (R ≈ 0.35). On uncertainty trials it never abstains. Because P(a = 1 | e) = 0 for both strata, U = 0 by Eq. 6: the agent exhibits no selective abstention, and U records this as zero rather than as undefined.

### 3.4 What "irreducible" means

We use *irreducible* to mean nonrecoverability of one population measure from the remaining four over a specified class of behavioral channels. Proposition 4 establishes this result for the reference design below; it is not a claim for every ontology, threshold, sample allocation, or restricted agent architecture. In particular, a thresholded count can become constant under a degenerate design. Functional nonrecoverability is distinct from statistical independence and from a requirement that every empirical application measure all five quantities.

For the population constructions, F1 is computed from the joint probabilities and support eligibility is fixed by the planned allocation. Write $F1_P(z)=2P(z,z)/[P_Y(z)+P_{\widehat Z}(z)]$ and $V_{\mathrm{eff}}^{\mathrm{pop}}(\alpha,\beta)=\sum_z\mathbf{1}\{F1_P(z)\geq\alpha,\ n_z^{\mathrm{plan}}\geq\beta\}$. This is the population counterpart of the observed count in Eq. 3, not a finite-sample estimator. Let the common episode-duration distribution have a finite positive mean $\mu_\tau$, so that population $B_{\min}=I/\mu_\tau$.

**Proposition 3 (base MI does not determine held-out generalization).** Fix a base-channel joint distribution $P(Y,\widehat Z)$, its episode-duration distribution, and a nonempty held-out trial set. Suppose each held-out trial permits a correct and an incorrect response, and the admissible behavioral-channel class allows separate response laws on base and held-out trials. For every $c\in[0,1]$, a channel in this class has base distribution P and $C_k=c$.

*Proof.* Retain P and the duration law on base trials. On each held-out trial, emit a correct response with probability c and an incorrect response with probability $1-c$. The base law, MI, and information rate remain fixed, while the held-out correctness probability is c. This constructs a behavioral channel; it does not establish how a particular learning mechanism acquires it. *End of proof.*

**Proposition 4 (functional nonrecoverability in the reference design).** Fix four equiprobable base intents, $\alpha=.80$, a planned allocation $n_z^{\mathrm{plan}}\geq\beta$ for every intent, and a common positive finite mean episode duration. Allow unrestricted stochastic response laws on the four protocol channels, with correct and incorrect responses available on held-out and repair trials and both uncertainty error strata having positive probability. For each population quantity $M\in\{B_{\min},V_{\mathrm{eff}}^{\mathrm{pop}},C_k,R,U\}$, two admissible channels agree on the other four quantities and differ on M. Therefore none of these five population quantities is a function of the other four over this channel class.

*Proof.* To vary $C_k$ or R, fix the base joint law and all other channel laws, and change only the corresponding correctness or recovery probability. To vary U, fix the other channel laws and the uncertainty error probability at one half. An abstention signal independent of error has $U=0$; a signal equal to the error indicator has $U=1$. Both uncertainty strata remain nonempty at population level, and no other reported population quantity changes. These constructions use the explicitly allowed independent specification of channel laws, not disjoint sampling alone.

For $V_{\mathrm{eff}}^{\mathrm{pop}}$, use the two four-class matrices in Section 4.3. Their population MI values are equal, their duration means are equal, and their thresholded counts are four and two. Hold the specialized channel laws fixed. For $B_{\min}$, use symmetric four-class matrices with diagonal probabilities .85 and .95 and uniform off-diagonal errors. Both have $V_{\mathrm{eff}}^{\mathrm{pop}}(.80,\beta)=4$, but their MI values are approximately 1.152 and 1.634 bits. Hold the duration and specialized-channel laws fixed. Each construction gives two channels with the same remaining four quantities and a different target quantity. *End of proof.*

Finite-sample estimates need not satisfy the equalities in the population constructions. In particular, the Section 4.3 matrices have different joint supports and hence can receive different first-order finite-sample corrections. Estimation and uncertainty are treated in Section 7. The matched-base simulation establishes a separate, exact sample-level equality by reusing the same realized base records.

### 3.5 Covariation in a continuously parameterized synthetic population

Proposition 4 concerns functions, not correlations, and the programmed agents of Section 5.3 were designed to dissociate the measures. To describe covariation under a continuously parameterized generator rather than only the programmed archetypes, we simulated 1,000 agents with continuously sampled parameters: base accuracy p ~ U(0.30, 0.98); held-out generalization fraction g ~ U(0, 1) with p_heldout = 1/|Z| + g(p − 1/|Z|); signal-modification probability after induced error m ~ U(0, 0.8); abstention selectivity s ~ U(−0.3, 1) (abstention 0.25 + 0.5s on hard trials and 0.25 − 0.2s on easy trials; forced-commitment error 0.25 hard, 0.05 easy). Each agent was evaluated at |Z| = 12 with 500 base trials, 150 compositional trials (half held-out), 200 induced-error trials, and 150 uncertainty trials. U was estimable for every agent.

**Table 1a.** Spearman correlations across the synthetic population (n = 1,000).

| | B_min | V_eff(.80) | C₂ | R | U |
|---|---|---|---|---|---|
| B_min | 1.00 | 0.87 | 0.47 | −0.01 | −0.00 |
| V_eff(.80) | | 1.00 | 0.40 | −0.00 | −0.04 |
| C₂ | | | 1.00 | 0.00 | 0.02 |
| R | | | | 1.00 | 0.02 |
| U | | | | | 1.00 |

Eigenvalues of the Pearson correlation matrix: 2.26, 1.03, 0.97, 0.63, 0.11; the first four components account for 97.9% of correlation-matrix variance.

Under this population, B_min and V_eff were strongly associated (they are complementary summaries of the same base confusion matrix); C₂ was moderately associated with both, a consequence of the generative rule that bounds held-out accuracy by base accuracy; R and U were approximately uncorrelated with every other measure, which follows from the generator sampling m and s independently. These are properties of the synthetic population, not of communicative behavior in general. The covariance pattern is consistent with the four-channel protocol architecture under this generator; V_eff supplies an interpretable thresholded summary of the base confusion matrix rather than evidence for a fifth general statistical dimension. Incremental validity against an external criterion cannot be assessed in simulation and is proposed for the prospective design of Section 15.


## 4. Formal Properties

### 4.1 Bounds

Proofs follow from standard information theory (Shannon, 1948; Cover & Thomas, 2006) and the definitions. The measurement-theoretic framing of behavioral metrics as indicators has a long tradition in psychometrics (Cronbach, 1951; Embretson & Reise, 2000).

**B_min.** I(Y; Ẑ) ≥ 0 with equality iff Y and Ẑ are independent. I(Y; Ẑ) ≤ min(H(Y), H(Ẑ)) ≤ log₂|Z|. Perfect decoding gives I = H(Y), which equals log₂|Z| only when Y is uniform. Hence B_min ∈ [0, H(Y)/Ē[τ]] ⊆ [0, log₂|Z|/Ē[τ]]. The bias-corrected estimator may be slightly negative under independence and is not truncated.

**V_eff.** V_eff ∈ {0, 1, …, |Z|}; V_eff = 0 iff no intent has F1 ≥ α with n ≥ β; V_eff = |Z| iff every intent does.

**C_k.** C_k ∈ [0, 1]. The independent uniform-response reference is 1/|responses| under the conditions in Section 2.4. A sample estimate below that reference requires uncertainty assessment before interpreting systematic misapplication.

**R.** R ∈ [0, 1]. Under the independent-uniform repair null, recovery within n attempts is 1 − (1 − 1/|Z|)ⁿ; other receiver/repair processes require their own null.

**U.** U ∈ [−1, 1]; U = 0 under independence of abstention and error (including never-abstain), U = 1 iff the agent abstains on every erroneous forced commitment and no correct one; U is not estimable if either error stratum is empty.

### 4.2 Monotonicity

**Proposition 1 (MI monotonicity under output noise).** Let ε ∈ [0, 1] and let the decoded intent be replaced, independently of Y, by a uniform draw from Z with probability ε. Then I(Y; Ẑ(ε)) is non-increasing in ε with I = 0 at ε = 1.

*Proof.* The joint law is $P_\epsilon(y,\widehat z)=(1-\epsilon)P_0(y,\widehat z)+\epsilon P_Y(y)/|Z|$. For $0\leq\epsilon_1<\epsilon_2\leq1$, apply to the $\epsilon_1$ output another independent uniform-replacement channel with probability

$$\delta=\frac{\epsilon_2-\epsilon_1}{1-\epsilon_1}.$$

Its retained-original weight is $(1-\delta)(1-\epsilon_1)=1-\epsilon_2$, so the resulting channel is exactly the $\epsilon_2$ channel. Thus $Y\to\widehat Z_{\epsilon_1}\to\widehat Z_{\epsilon_2}$ is a Markov chain and data processing gives $I(Y;\widehat Z_{\epsilon_2})\leq I(Y;\widehat Z_{\epsilon_1})$. At $\epsilon=1$ the output is independent of Y, so MI is zero. *End of proof.*

Empirically, B_min was non-decreasing in base accuracy p in 79 of 80 (|Z|, s, N) Monte Carlo series of the parameter grid (Section 5.8).

**Proposition 2 (V_eff monotonicity in α).** V_eff(α, β) is non-increasing in α for fixed β and data, since {z : F1(z) ≥ α′} ⊆ {z : F1(z) ≥ α} for α′ > α. Confirmed in every grid cell.

### 4.3 Two confusion matrices, same MI, different geometry and different V_eff

Mutual information is a scalar, non-injective functional of the joint distribution: distinct confusion geometries can therefore have the same value. Let the intent prior be uniform over four classes. Agent alpha has diagonal probability .85 and off-diagonal probability .05 in every row. Agent beta has zero cross-group confusion:

| | A | B | C | D |
|---|---:|---:|---:|---:|
| A | 0.81 | 0.19 | 0 | 0 |
| B | 0.19 | 0.81 | 0 | 0 |
| C | 0 | 0 | q | 1 - q |
| D | 0 | 0 | 1 - q | q |

Set q = 0.5467007423005. Under a uniform prior, I(Y; Ẑ) equals 2 minus mean row entropy. Agent alpha has I = 1.1524153202 bits. Solving ½[h(.81) + h(q)] = 2 − 1.1524153202 gives the q above, and Agent beta has the same MI at the ten decimal places reported. Exact equality refers to the unique root q in (.5,.81) of the entropy equation, rather than to an arbitrary rounding of that root. Their error structures and accuracy differ: accuracy is .850 for alpha and .678 for beta. Per-class F1 is (.85, .85, .85, .85) for alpha and (.81, .81, .547, .547) for beta, giving V_eff(.80) = 4 versus 2 at identical MI. Conversely, symmetric four-class matrices with diagonals .85 and .95 both give V_eff(.80) = 4 but MI values 1.152 and 1.634 bits. Thus neither population MI nor the support-eligible population vocabulary count determines the other in this reference design. Nothing in beta's single-intent error geometry determines its compositional behavior; Proposition 3 treats that channel separately.


## 5. Simulation Study

### 5.1 Purpose and design

The simulation verifies that the measures behave as their formal properties predict under controlled conditions, that the null models expose the failure modes accuracy conceals, and that the matched-agent contrast at the center of the paper holds numerically. Every agent is defined by one row of a specification table (Table S0, generated from the code) so that text, code, and tables share a single source. All results are regenerated by `reproduce_all.py` (seed 42).

### 5.2 Environment

A closed ontology of |Z| intents (default 12). Ground truth on base trials is sampled uniformly or from a Zipf prior with exponent s. The single-intent response rule is: correct with probability p, otherwise a uniform draw over the |Z| − 1 incorrect intents, so that the population base correctness probability is p; realized sample accuracy fluctuates around it. Episode durations are log-normal (median 0.5 min, σ = 0.4). Trials are allocated to channels as 50% base, 15% compositional (half held-out), 20% induced-error, 15% uncertainty; the default N = 1,000 gives 500 base trials, exceeding the aggregate lower bound β·|Z| = 360; actual per-class eligibility is still checked. The real-study protocol assumes a 2-slot grammar with an 80/20 training/held-out partition. The Bernoulli engine does not instantiate combination identities or a partition parameter; it represents only training-labelled versus held-out-labelled trial types. Half of compositional evaluation trials are assigned the held-out label to stabilize the estimate. Uncertainty trials are 30% hard.

### 5.3 Agent types

- **Random.** Uniform response on every channel; abstains with fixed probability 0.30 regardless of error risk.
- **Class-Biased (Null 1).** Correct with probability 0.90 when the ground truth is one of the three most frequent intents under P(Y); uniform otherwise. Never abstains.
- **Overproduction (Null 2).** Emits the most frequent intent on 70% of trials; otherwise correct with p = 0.85. Never abstains.
- **Memorizer.** p = 0.85 on base trials and on training combinations; chance on held-out combinations; repeats the original signal without modification after induced error; never abstains.
- **Compositional.** p = 0.85 on base, training, and held-out trials; after induced error modifies (0.45), escalates (0.20), repeats (0.20), or abandons (0.15) with recovery 0.55, 0.35, chance, 0; abstains on 60% of hard and 10% of easy uncertainty trials, with forced-commitment error 0.25 hard and 0.05 easy.

The Memorizer and Compositional agents use identical base-channel parameters and common random numbers, so every matched run has exactly the same realized base ground truths, responses, durations, B_min, and V_eff. This makes the measurement blind spot exact rather than approximate.

### 5.4 Runs

Table 1: 400 runs per agent. Null models and counterexamples: 400. Equal-p sweep: 300 per configuration. Parameter grid: 100 per cell. Synthetic-population covariance analysis: 1,000 agents. Power: 1,000 replications per cell.

### 5.5 Results: core agent differentiation

**Table 1.** Metric profiles at default parameters (|Z| = 12, N = 1,000, 400 runs). Mean (SD). Reference values are C₂=.083 under uniform response, R=.160 under the independent-uniform two-attempt simulation null, and U=0 under abstention-error independence. Every run contains 150 uncertainty trials. U was estimable in all 400 runs for every agent. Supplementary Tables S1b–S1c report abstention, commitment coverage, conditional abstention rates, and error-stratum counts for these same core runs. Data S2 is a separate worked example, not the source of the core-run denominators.

| | Random | Class-Biased | Overprod. | Memorizer | Compos. |
|---|---|---|---|---|---|
| Base accuracy | 0.083 (0.012) | 0.287 (0.020) | 0.314 (0.021) | 0.850 (0.016) | 0.850 (0.016) |
| MI (bits) | 0.027 (0.027) | 0.638 (0.062) | 0.768 (0.071) | 2.572 (0.096) | 2.572 (0.096) |
| B_min (bpm) | 0.050 (0.049) | 1.178 (0.116) | 1.418 (0.134) | 4.748 (0.199) | 4.748 (0.199) |
| V_eff(0.60) | 0.00 (0.00) | 2.71 (0.50) | 0.04 (0.20) | 11.79 (0.47) | 11.79 (0.47) |
| V_eff(0.80) | 0.00 (0.00) | 0.01 (0.11) | 0.00 (0.00) | 10.44 (1.27) | 10.44 (1.27) |
| C₂ | 0.083 (0.031) | 0.082 (0.032) | 0.084 (0.032) | 0.082 (0.030) | 0.856 (0.042) |
| R | 0.161 (0.026) | 0.160 (0.026) | 0.160 (0.026) | 0.161 (0.026) | 0.350 (0.034) |
| U | 0.002 (0.075) | 0.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) | 0.217 (0.132) |
| Abstention rate | 0.300 (0.038) | 0.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) | 0.251 (0.033) |

The Memorizer and Compositional agents are exactly equal on every realized base-channel quantity by construction and are separated by 0.77 on C₂, 0.19 on R, and 0.22 on U (Figure 1). The three counterexamples reproduce with the same architecture (Table S2): CE1 has MI 2.90 bits and C₂ 0.081; CE2 has C₂ 0.849 and R 0.160; CE3 has R 0.351 and U 0.000.

### 5.6 Results: null-model validation

**Class-Biased under imbalance.** As the Zipf exponent rises from 0 to 1.5, base accuracy rises from 0.287 to 0.700 (0.565 at s = 1, matching the analytic value 0.566 under the response rule) while MI rises only from 0.64 to 1.19 bits and V_eff(0.60) approaches 3 — the three favored intents — as imbalance increases (Table S3). Accuracy rewards the strategy; MI and V_eff identify it as three-intent communication.

**Overproduction under imbalance.** Accuracy rises from 0.314 to 0.596 as s rises to 1.5 while MI falls from 0.77 to 0.47 bits and V_eff(0.80) stays at 0. The metrics move in opposite directions from accuracy.

**Strategic randomization.** An agent correct with p = 0.70 whose every error is a cyclic-neighbor intent has base accuracy 0.699, MI 2.40 bits, V_eff(0.60) = 11.1 but V_eff(0.80) = 0.34, and C₂ and R at chance. Structured errors preserve MI while collapsing the high-threshold vocabulary count.

### 5.7 Statistical power

The original submission varied a single accuracy parameter while comparing programmed agent types; because those agents differ structurally, the quantity detected was agent identity rather than the nominal effect size. We now report power separately for each measure against an effect defined on that measure's own scale, perturbing one parameter with all other channels held equal, indexed by the number of trials that feed the measure. Each cell uses 1,000 replications; every table includes the null row δ = 0 as an empirical size check; Wilson 95% intervals for every cell are in Supplementary Table S7. C₂, R, and U are tested with Fisher's exact test (H₀: δ = 0, α = 0.05). B_min is tested by a two-sided system-label permutation test: complete base episodes are pooled, system labels are permuted, and the corrected B_min difference is recomputed. The count-matrix simulation draws each permuted allocation from the exact multivariate-hypergeometric distribution conditional on the pooled joint table; each replication uses 1,000 permutations and p = (b + 1)/(B + 1).

**Table 2a.** Detecting the presence of compositional generalization: memorizer at chance (1/12) versus an agent at 0.86 on held-out combinations, by held-out trials per system n_U.

| n_U | 4 | 8 | 15 | 38 | 75 | 150 |
|---|---|---|---|---|---|---|
| Implied total N | 53 | 107 | 200 | 507 | 1,000 | 2,000 |
| Power | 0.38 | 0.90 | 0.99 | 1.00 | 1.00 | 1.00 |

**Table 2b.** Resolving degrees of compositional depth: baseline C₂ = 0.50 versus 0.50 + δ_C.

| δ_C / n_U | 15 | 38 | 75 | 150 | 400 | 1,600 |
|---|---|---|---|---|---|---|
| 0 (size) | 0.015 | 0.034 | 0.042 | 0.047 | 0.047 | 0.048 |
| 0.05 | 0.03 | 0.05 | 0.08 | 0.13 | 0.25 | 0.79 |
| 0.10 | 0.03 | 0.10 | 0.20 | 0.36 | 0.80 | 1.00 |
| 0.20 | 0.10 | 0.33 | 0.66 | 0.93 | 1.00 | 1.00 |
| 0.40 | 0.55 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 |

**Table 2c.** Repair efficiency: baseline 0.160 versus 0.160 + δ_R, by induced-error trials per system n_R.

| δ_R / n_R | 20 | 40 | 100 | 200 | 400 |
|---|---|---|---|---|---|
| 0 (size) | 0.021 | 0.028 | 0.038 | 0.047 | 0.035 |
| 0.05 | 0.03 | 0.05 | 0.09 | 0.20 | 0.41 |
| 0.10 | 0.06 | 0.14 | 0.35 | 0.63 | 0.91 |
| 0.20 | 0.22 | 0.44 | 0.88 | 1.00 | 1.00 |
| 0.25 | 0.30 | 0.62 | 0.97 | 1.00 | 1.00 |

**Table 2d.** Uncertainty selectivity: abstention 0.10 on non-error trials versus 0.10 + δ_U on error trials, error fraction π_e = 0.20, by uncertainty trial count n_A. (π_e = 0.10 and 0.35 in Table S7.)

| δ_U / n_A | 100 | 200 | 500 | 1,000 |
|---|---|---|---|---|
| 0 (size) | 0.017 | 0.038 | 0.043 | 0.031 |
| 0.10 | 0.21 | 0.36 | 0.73 | 0.95 |
| 0.20 | 0.57 | 0.81 | 0.99 | 1.00 |
| 0.30 | 0.86 | 0.99 | 1.00 | 1.00 |
| 0.40 | 0.96 | 1.00 | 1.00 | 1.00 |

**Table 2e.** Information rate: base accuracy 0.85 versus 0.85 + Δp, |Z| = 12, by base trials per system n_S. Population ΔB_min is shown in bits/min for mean cycle 0.5 min.

| Δp / n_S | ΔB_min | 100 | 200 | 500 | 750 | 1,000 | 2,000 |
|---|---:|---|---|---|---|---|---|
| 0 (size) | 0.000 | 0.050 | 0.039 | 0.044 | 0.057 | 0.052 | 0.047 |
| 0.01 | 0.120 | 0.047 | 0.060 | 0.071 | 0.081 | 0.086 | 0.130 |
| 0.03 | 0.369 | 0.107 | 0.126 | 0.289 | 0.365 | 0.488 | 0.798 |
| 0.05 | 0.628 | 0.155 | 0.310 | 0.665 | 0.823 | 0.929 | 1.000 |
| 0.10 | 1.339 | 0.655 | 0.905 | 1.000 | 1.000 | 1.000 | 1.000 |

Three conclusions. First, two regimes must be distinguished for C₂. Detecting the *presence* of compositional generalization — chance versus 0.86 — is achieved at about eight held-out trials (power 0.90), which under the default allocation is N ≈ 107. This is the only sense in which C₂ is "powered at small N." *Resolving* degrees of compositional depth is expensive: at baseline 0.50, δ_C = 0.10 requires n_U ≈ 400 for 80% power and δ_C = 0.05 requires n_U ≈ 1,600, consistent with the two-proportion approximation n_U ≈ 3.92/δ_C². Studies whose question concerns degree rather than presence should allocate at least 25% of trials to held-out combinations and design grammars accordingly. Second, R and U behave the same way: δ_R = 0.20 is detectable at n_R = 100 (0.88), δ_R = 0.10 has power .63 at n_R=200 and .91 at n_R=400; δ_U = 0.20 requires n_A ≈ 200 at π_e = 0.20, and U power depends on the number of error trials, so designs should ensure enough errors to populate that stratum. Third, B_min requires approximately 750 base trials per system for Δp = 0.05 (power 0.82; 0.67 at 500) and approximately 2,000 for Δp = 0.03 (0.80); a one-point difference in base accuracy is not reliably detectable at any tested n_S. The corresponding population rate differences are 0.628, 0.369, and 0.120 bits/min for Δp = .05, .03, and .01 at the simulated 0.5-min cycle.

Empirical size is at or below nominal for the Fisher tests and ranges from 0.039 to 0.057 for the B_min system-label permutation test. Bootstrap intervals for B_min remain descriptive uncertainty summaries; confirmatory comparisons use the permutation procedure.

### 5.8 Metric behavior across the parameter grid

Across 480 cells (|Z| ∈ {6, 12, 24, 48} × p ∈ {.50, .60, .70, .80, .90, .95} × Zipf s ∈ {0, 0.5, 1, 1.5} × N ∈ {100, 200, 500, 1,000, 2,000}; 100 paired runs per cell; an 80/20 grammar partition assumed by the real-study protocol but not represented as a grid factor, and 50% held-out evaluation allocation): (a) B_min is non-decreasing in p in 79 of 80 (|Z|, s, N) Monte Carlo series, with the single reversal consistent with Monte Carlo fluctuation; (b) V_eff(0.80) ≤ V_eff(0.60) in every cell; (c) C₂ separation has median Cohen's d 11.48, minimum 1.80 at N = 100, and minimum 2.72 for N ≥ 200; (d) R separation has median d 4.36, minimum 0.53 at N = 100, and minimum 1.32 for N ≥ 500. Paired base-channel B_min differences are exactly zero in every cell. The memorization–composition distinction is robust to noise, imbalance, and ontology size once the held-out channel contains more than a handful of trials (Table S5).

### 5.9 Matched-base analysis

A potential objection to C₂ is that it merely reflects overall accuracy on a subset of trials. We address this directly. Across p ∈ {.50, .60, .70, .80, .90, .95} (300 runs per configuration) the Memorizer and Compositional agents have exactly identical realized base accuracy, B_min, and V_eff within every matched run. Aggregate accuracy over all scored trials (base plus compositional, as an accuracy-reporting study would compute it) differs by 4.7–9.9 points, the gap arising entirely from held-out trials, which are 11.5% of scored trials. C₂ differs by 42–86 points (Figure 3). At p = .80, aggregate accuracy differs by 8.3 points while C₂ differs by 72.


## 6. Empirical Application: BCI Competition IV-2a

We report a subject-specific replacement analysis of BCI Competition IV Dataset 2a. Both predeclared decoders were executed for all nine subjects. The analysis specification was frozen before evaluation-session decoding in this replacement run; its timestamp, design fingerprint, pre-evaluation amendments, and validation records are provided in the supplementary release. The response letter documents why the original analysis was withdrawn.

### 6.1 Data, preprocessing, and decoders

BCI Competition IV Dataset 2a contains nine subjects performing four-class motor imagery (left hand, right hand, feet, tongue), with a training session T and evaluation session E of 288 trials each, 22 EEG channels, three EOG channels, and 250-Hz sampling (Brunner et al., 2008; Tangermann et al., 2012). Cue onset is at trial time 2 s and imagery extends through 6 s. The analysis is subject-specific: T is used for all fitting and tuning, and E is evaluated once.

The pipeline reads the 18 official BNCI MAT files directly, preserving the six source task runs per session. The decision window is 0.5–2.5 s after cue onset, equivalent to 2.5–4.5 s after the source trial trigger. Exact sample coordinates and timing checks are documented in Supplementary S8. Organizer artifact flags are applied identically to both decoders. They exclude 224 of 2,592 scheduled evaluation trials, ranging from 5 to 73 exclusions per subject (1.7%–25.3%). Evaluation samples therefore contain 215–283 trials, with 53–72 observations per class; every class meets β=30. Subject- and class-specific training and evaluation counts are reported in S8. Exactly 22 EEG channels enter the decoders; the three EOG channels are excluded.

The primary decoder uses the fixed post-cue window and an 8–30 Hz zero-phase MNE FIR filter with `firwin` design, applied independently to each continuous source run before epoching. Both decoders use class-wise concatenated training epochs for CSP covariance estimation with Ledoit–Wolf shrinkage and no trace normalization (`reg="ledoit_wolf"`, `cov_est="concat"`, `norm_trace=False`); LDA uses automatic covariance shrinkage. The primary one-vs-rest classifier selects 4, 6, or 8 CSP components by six-fold leave-one-source-run-out cross-validation within T. All fitting occurs inside the training folds, score ties select the smaller component count, and the selected model is refit on clean T before E is evaluated. Resolved filters, software versions, channel order, and tuning details are archived in the result JSON.

A separate FBCSP-style robustness decoder uses nine 4 Hz bands from 4–40 Hz, binary one-vs-rest CSP for every class and band, training-only selection among 16, 32, 64, or 96 retained features, and shrinkage LDA. CSP fitting and feature selection occur inside each training fold. This decoder is not described as an exact reproduction of Ang et al. (2012). Their reported mean evaluation kappa values of .503 for OVR-CSP and .569 for OVR-FBCSP provide context rather than exact acceptance targets because their competition analysis used time-resolved predictions and maximum-over-time evaluation.

Episode duration is the full operating cycle. For each subject, tau-bar is the mean of all 282 within-source-run inter-trigger intervals in E, computed before artifact exclusion from source sample coordinates (the fixed cue offset cancels in within-run differences), not the 2-s feature epoch or the original submission's 3-s analysis window. A source-data audit found that all 18 files share one fixed pseudorandom trigger schedule, so tau-bar is identical for every subject and session: 8.043 s (SD 0.271, range 7.58-8.48 s). Supplementary Table S8d compares conventional Wolpaw ITR and B_min using the same full-cycle denominator. ITR assumes uniform class priors and symmetric errors; the source JSON also retains the unclipped formula and its below-chance-zero presentation.

### 6.2 Inference and results

For each subject and decoder, the complete confusion matrix; accuracy; Cohen's kappa from observed marginals; per-class precision, recall, and F1; V_eff(.40-.90, beta = 30); plug-in MI; the observed-support Miller-Madow correction and corrected MI; B_min using full-cycle tau-bar; conventional ITR; a run-and-class-stratified 10,000-resample descriptive interval (strata are E source run by true class, refining the previously described class-only bootstrap); and a 5,000-permutation independence p-value with (b+1)/(B+1), using plug-in MI as the statistic and permuting labels within each source run, are reported, with Holm adjustment across nine subjects separately by decoder. Corrected MI is not truncated at zero. A subject is described only as one for which the specified independence test rejected after Holm adjustment; non-rejection is not evidence of absent information, and low-information subjects are not compared by point estimates alone. Because organizer-clean estimates are conditional on retained trials, a prespecified sensitivity applies each frozen decoder to every scheduled E epoch, including flagged trials. Across subjects, this sensitivity changes corrected MI by less than 0.05 bits for either decoder; individual V_eff counts differ by at most one class in the few affected subject-threshold cells, leaving the overall threshold pattern unchanged.

**Table 3a. Primary fixed-window OVR-CSP results.** Populated from the validated `bci_real_application_v4.json`.

| Subject | Clean E trials | Accuracy | Kappa | Corrected MI [95% CI] | Holm p | B_min [95% CI], bits/min |
|---|---:|---:|---:|---|---:|---|
| S1 | 281 | 0.779 | 0.706 | 1.195 [1.102, 1.334] | 0.002 | 8.92 [8.22, 9.95] |
| S2 | 283 | 0.445 | 0.261 | 0.198 [0.144, 0.305] | 0.002 | 1.48 [1.08, 2.28] |
| S3 | 273 | 0.740 | 0.653 | 0.935 [0.834, 1.085] | 0.002 | 6.97 [6.22, 8.09] |
| S4 | 228 | 0.588 | 0.452 | 0.591 [0.497, 0.755] | 0.002 | 4.41 [3.70, 5.63] |
| S5 | 276 | 0.399 | 0.200 | 0.087 [0.050, 0.178] | 0.002 | 0.65 [0.38, 1.33] |
| S6 | 215 | 0.414 | 0.217 | 0.099 [0.059, 0.210] | 0.002 | 0.74 [0.44, 1.56] |
| S7 | 277 | 0.708 | 0.612 | 0.894 [0.785, 1.041] | 0.002 | 6.67 [5.86, 7.77] |
| S8 | 271 | 0.775 | 0.700 | 0.996 [0.877, 1.175] | 0.002 | 7.43 [6.54, 8.77] |
| S9 | 264 | 0.731 | 0.641 | 1.005 [0.909, 1.151] | 0.002 | 7.49 [6.78, 8.59] |


**BCI result summary.** Mean accuracy and kappa are .620 and .493 for the primary decoder and .692 and .591 for the FBCSP-style decoder. The specified within-run independence null is rejected after Holm adjustment for all nine subjects under both decoder families (raw p=1/5001; adjusted p=9/5001=.00180). These are within-subject tests, not tests of differences between subjects. As an exploratory illustration, S1 and S8 have accuracies .779 and .775 and information rates 8.92 and 7.43 bits/min. This pair was selected to maximize the B_min gap among pairs within .03 accuracy whose independence tests rejected; the selection and the two subject-specific tests do not establish a significant between-subject difference.

No pooled confusion matrix is interpreted as an operating subject-specific BCI. All reported operating-system estimates are subject-specific.

**Table 3b. V_eff threshold sensitivity for the primary decoder.** Complete per-subject V_eff curves for both decoders appear in Supplementary Table S8e.

| Summary | alpha=.40 | .50 | .60 | .70 | .80 | .90 |
|---|---:|---:|---:|---:|---:|---:|
| Mean V_eff | 3.44 | 2.67 | 2.33 | 1.44 | 0.67 | 0.00 |
| Median V_eff | 4 | 3 | 3 | 2 | 0 | 0 |
| Subjects with V_eff >= 1 | 9 | 8 | 7 | 5 | 4 | 0 |

The FBCSP-style results and paired descriptive contrasts are reported in Supplementary S8. Accuracy is higher under FBCSP-style decoding for seven of nine subjects; S2 and S9 are the exceptions. Threshold dependence changes with the decoder: at F1 ≥ .90, the primary decoder has no qualifying class in any subject, whereas FBCSP-style decoding retains at least one class in S1, S3, and S7. The complete subject-level curves, rather than one threshold, characterize this decoder dependence. The paired intervals are descriptive and are not multiplicity-adjusted between-decoder hypothesis tests.

### 6.3 Confusion structure

Figure 4 presents all nine row-normalized primary-decoder confusion matrices; the supplement presents the FBCSP-style matrices. The structure is heterogeneous and class-specific rather than uniformly diagonal. Feet-tongue confusion is prominent in several higher-performing subjects: S1 misreads 28% of feet trials as tongue and 30% of tongue trials as feet, S3 misreads 38% of feet as tongue, S4 41%, and S7 38%, while S8 shows the reverse asymmetry (tongue-to-feet 26% against feet-to-tongue 1%). Hand-class asymmetries are equally subject-specific: S1 classifies left hand almost perfectly (97%) while sending 23% of right-hand trials to left hand; S4 sends 53% of left-hand trials to right hand; S9 sends 46% of right-hand trials to feet while recognizing tongue at 94%. The weakest subjects are not weak in the same way: S5's rows are diffuse (no diagonal cell above 51%), whereas S6's errors concentrate on the right-hand column (44% of feet and 43% of tongue trials predicted right hand). No single failure mechanism describes all nine subjects; scalar accuracy is not substituted for this analysis.

### 6.4 Diagnostic gaps

IV-2a can supply only the base-channel measures B_min and V_eff. It cannot supply C₂ because no compositional grammar and held-out combinations were tested; R because no misunderstanding was induced and no repair turn was observed; or U because no abstention action and forced-commitment outcome were elicited. These are design diagnoses, not zero scores.

### 6.5 Published benchmark reporting

Ang et al. (2012) report subject-level kappa values but not the complete per-subject confusion matrices needed to reconstruct corrected MI, B_min, class-level F1, or V_eff. The proposed suite therefore cannot be retrofitted to that report from accuracy or kappa alone. The within-package FBCSP-style reanalysis is included to separate the measurement framework's conclusions from the primary decoder implementation while preserving complete confusion-matrix reporting.


## 7. Asymptotic Behavior and Bias

As N → ∞ the empirical MI converges to the true MI. The plug-in estimator has positive finite-sample bias (Treves & Panzeri, 1995; Paninski, 2003). With K_Y and K_Ẑ occupied marginal cells and K_YẐ occupied joint cells, the first-order Miller–Madow correction to Î = Ĥ_Y + Ĥ_Ẑ − Ĥ_YẐ is

$$\widehat I_{\mathrm{MM}}=\widehat I_{\mathrm{plugin}}-\frac{K_{Y\widehat Z}-K_Y-K_{\widehat Z}+1}{2N\ln2}.\qquad(7)$$

(Miller, 1955; Panzeri & Treves, 1996), which reduces to (K_Y − 1)(K_Ẑ − 1)/(2N ln 2) when every joint cell is occupied. For |Z| = 12 and N = 500 with full support the term is 121/(1,000 ln 2) ≈ 0.175 bits; for four classes and N = 288, 0.0225 bits. All reported sample MI estimates use Eq. 7 on observed support and are not truncated at zero. The population examples in Sections 3–4 use the MI functional without a sample-size correction.

The correction is first-order. Empirically, an independent agent at |Z| = 12 with 500 base trials retains a mean corrected MI of 0.027 bits (SD 0.027; Table 1), and with 250 base trials about 0.13 bits, because many joint cells have expected counts below one. For a one-system test of independence, shuffle decoded outputs relative to Y, recompute plug-in MI, and report p = (b + 1)/(B + 1) with B ≥ 1,000 (Phipson & Smyth, 2010). For two independent systems with exchangeable complete episode records under the null, pool the records and permute system labels. For paired systems under a within-pair exchangeability null, swap the paired records while preserving their pairing and relevant design strata. Such tests are exact under their exchangeability nulls, not under equality of the scalar B_min alone. The zero-effect simulation in Section 5.7 satisfies the stronger common-distribution null. The permutation reference captures the statistic's finite-sample behavior under that null. For stronger correction, Bayesian or jackknife estimators (Nemenman et al., 2004; Archer et al., 2014) apply; Quiroga and Panzeri (2009) review the options.

The bootstrap interval for B_min is retained as a descriptive uncertainty summary. Confirmatory inference uses the permutation procedures above. C_k, R, and U are proportions or differences of proportions with exact or score-based intervals.


## 8. Extension to Growing Ontology

The framework requires a finite, pre-specified ontology at the time of measurement. Mutual information as a mathematical object does not; the operational evaluation design does, because the estimators of Section 7 and the ground-truth comparison require a known support. Studies that claim open-ended communication without a defined ontology are making unmeasurable claims within this framework.

To compare across ontology sizes we define a normalized information fraction

$$D=\frac{I(Y;\widehat Z)}{\log_2|Z|}.\qquad(8)$$

D ∈ [0, 1] is the fraction of the maximum-entropy ceiling that is realized. It is not a fraction of Shannon channel capacity, which is max over P(Y) of I(Y; Ẑ) and depends on the channel rather than the prior. For longitudinal studies with an expanding ontology Z(t), report both raw B_min and D at each time point, so that throughput gains can be separated from ontology inflation. A full treatment of dynamic ontology expansion is future work.


## 9. Measurement Error

Ground-truth labeling is not error-free. Let $Y_{\mathrm{true}}$ denote the latent true label and $\widetilde Y$ the recorded label. Under a nondifferential labeling channel satisfying $\widetilde Y\perp\widehat Z\mid Y_{\mathrm{true}}$, the Markov relation $\widehat Z\to Y_{\mathrm{true}}\to\widetilde Y$ gives $I(\widetilde Y;\widehat Z)\leq I(Y_{\mathrm{true}};\widehat Z)$ by data processing. This population result does not imply that every finite-sample estimate decreases, and it does not hold for arbitrary differential labeling mechanisms.

There is no universal multiplicative correction: attenuation depends on the labeling channel. Where labeling error is material, report sensitivity analyses under explicit alternative labeling mechanisms or model the error process as a nuisance component (Archer et al., 2014). Accuracy-based C_k and R can be biased in either direction by erroneous outcome labels; their direction cannot be inferred from the MI inequality. For U, error-outcome misclassification independent of abstention conditional on the true outcome attenuates selectivity when the recorded outcome retains positive discrimination; differential or label-inverting error can behave differently. Inter-rater agreement documents reliability but does not by itself identify a true labeling-error rate.

## 10. Separating Conditioning from Representation

Do these measures measure "language"? No. They detect statistical structure in the mapping between emissions and externally defined ground truth. High B_min means the signals reliably predict the experimental conditions. High C₂ means behavior generalizes to novel combinations withheld under the grammar. High R means the agent adjusts its signaling to recover from failure. High U means abstention discriminates trials on which commitment fails.

These are behavioral measurements consistent with multiple mechanisms. An agent with high C₂ could have an internal compositional grammar or a similarity-based generalization strategy that happens to succeed. An agent with high R could model its partner's state or follow a heuristic. The measures do not distinguish mechanisms; they measure whether the behavior occurs. The information-theoretic framing treats communication as a channel property (Shannon, 1948; Bialek et al., 2001), with statistical complexity (Crutchfield & Feldman, 2003) as the broader context. We caution against interpreting high scores on any measure as evidence for internal symbolic language, conceptual understanding, or conscious intention.


## 11. Adversarial Experimental Protocol

**11.1 Blinding.** The person with the agent must not know the target intent, which is set by an independent experimenter elsewhere. Handler behavior is video-recorded and reviewed by a blinded coder for cueing. Any AI decoder's inference is logged before any human observes it.

**11.2 Automated logging.** All emissions are recorded with timestamps by automated systems; no real-time human interpretation.

**11.3 Ground truth.** Forced-choice tasks: determined by design. Spontaneous communication: verified by independent sensors or ≥ 2 blinded judges (κ ≥ 0.80). Indeterminate episodes are excluded and the exclusion rate reported.

**11.4 Induced-error protocol.** 20% of trials receive deliberately incorrect responses, pseudo-randomly distributed. Post-error behavior is recorded for two turns (30 s timeout each) and classified by blinded coders (κ ≥ 0.75).

**11.5 Uncertainty protocol.** Forced-choice trials include an UNKNOWN option. After every trial — whether or not the agent abstained — a forced commitment on the same unchanged stimulus is elicited after a fixed short delay, without added task-relevant information and before outcome feedback; e_i is recorded from that commitment. Difficulty manipulation is recommended to ensure that the error stratum is populated, but difficulty is not part of the definition of U.

**11.6 Cross-context transfer.** 20% of evaluation trials occur in a novel environment with a novel handler; the decrement is reported.

**11.7 Pre-registration.** Ontology Z, alphabet Σ, episode boundaries and the definition of τ, ground-truth method, decoder, α and β, grammar G with its partition, induced-error proportion and repair window, uncertainty structure and forced-commitment procedure, analysis plan including effect sizes and trial budgets per channel (Section 5.7), stop conditions, exclusion criteria.


## 12. Comparison to Existing Approaches

**Table 4.** Information supplied by an aggregate base-channel score versus the protocol-separated suite. Task-specific accuracy can measure held-out performance or recovery when those trials are actually collected; the contrast concerns what can be inferred from the base score alone.

| Capability | Accuracy | MI alone | Proposed suite |
|---|---|---|---|
| Preserves intended-label correctness as a separate criterion | Yes | No: invertible label permutations preserve MI | Yes, through base accuracy and class-level F1 |
| Accounts for observed class marginals and penalizes constant-output strategies | No | Yes | Yes |
| Detects compositional generalization | No | No | Yes (C_k) |
| Detects communicative repair | No | No | Yes (R) |
| Detects selective uncertainty signaling | No | No | Yes (U) |
| Vocabulary discrimination curve | No | No | Yes (V_eff) |
| Domain-general definitions | Yes | Yes | Yes |
| Design requirements stated per measure | No | No | Yes (Table 0) |
| Adversarial protocol specified | No | No | Yes |


## 13. Worked Example

Synthetic dataset S2. An agent with |Z| = 12 is evaluated over 600 base trials (50 per intent), with heterogeneous per-intent accuracy generated from a fixed seed. A 2-slot grammar yields 20 valid combinations (16 training, 4 held-out); the agent is correct on 14 of 16 training and 3 of 4 held-out combinations. On 120 induced-error trials it recovers on 42. On 200 uncertainty trials the forced commitment fails on 40; the agent abstained on 18 of those 40 and on 7 of the remaining 160.

- **B_min.** Corrected I(Y; Ẑ) = 2.358 bits; mean cycle 0.451 min; B_min = 5.23 bits/min.
- **V_eff(α, 30).** The curve is 12, 11, 7, 0 at α = .60, .70, .80, .90.
- **C₂.** 3/4 = 0.75, Clopper–Pearson [0.19, 0.99]. Four held-out trials give a very wide interval; the presence/degree distinction is planned from Tables 2a–2b.
- **R.** 42/120 = 0.35 against the simulation's independent-uniform null .160; distribution Repeat 45%, Modify 30%, Escalate 10%, Abandon 15%.
- **U.** P(a | e = 1) = 18/40 = .450; P(a | e = 0) = 7/160 = .044; U = 0.406, Newcombe 95% interval [0.26, 0.56]; Fisher p < .001. Abstention rate is 0.125, with 40 error and 160 non-error forced commitments.


## 14. Limitations

**Closed ontology.** The evaluation design requires a finite pre-specified intent space; Section 8 provides a normalization, not a theory of ontology growth.

**Discrete episodes.** Continuous communication requires segmentation; report sensitivity to segmentation granularity.

**No inference of representation.** Section 10.

**Independent ground truth required.** Claims of communication without verifiable ground truth are unfalsifiable within the framework.

**Finite-sample MI bias.** Eq. 7 is first-order; residual bias at small n_S is empirically non-negligible (Section 7). Use permutation tests for null rejection.

**Descriptive bootstrap.** Bootstrap intervals summarize uncertainty but are not the confirmatory test for B_min; use the system-label or within-episode permutation procedure appropriate to the design.

**Decoder dependence.** Where the decoder is a trained classifier, measured throughput is the joint capacity of agent and decoder. Report decoder performance against known ground truth and benchmark it; a decoder far below relevant published context requires debugging or qualification before the empirical application can support substantive claims.

**Synthetic population.** Section 3.5 describes one generative population; the covariance of the measures in real behavior is an empirical question.


## 15. Discussion

### 15.1 The irreducibility argument

The central methodological contribution is not any single measure, but the reference-design construction showing that none of the five population quantities is recoverable from the other four over the stated behavioral-channel class (Proposition 4), together with the design requirements for each measure (Table 0). Studies reporting only accuracy, or only MI, leave communicative structure unmeasured that the held-out, induced-error, and abstention channels would reveal. The matched-base analysis (Section 5.9) is the sharpest form of the argument: two agents with identical base-channel behavior differ by up to 86 points on compositional depth while aggregate accuracy differs by single digits.

### 15.2 The adversarial standard

Cue leakage is structural in any paradigm where an evaluator interacts with a responsive agent; the Clever Hans effect (Pfungst, 1911; Sebeok & Rosenthal, 1981) is not historical. Section 11 provides an adoptable, citable standard.

### 15.3 Domain generality and its limits

The definitions reference no application domain, but their computability depends on experimental design. The completed BCI application illustrates both points: base-channel measures are computed from subject-specific confusion matrices, whereas the three specialized measures remain unmeasured because IV-2a lacks the required manipulations. This application does not establish cross-domain criterion validity for the complete suite.

### 15.4 Empirical application

The replacement empirical analysis was executed under the frozen design described in Section 6. The completed application reports subject-specific systems only: full-cycle information rates span 0.65 to 8.92 bits/min across the nine subjects under the primary decoder — a range produced by confusion structure, not by accuracy differences alone — and the specified independence test rejects after Holm adjustment for all nine subjects under both decoders. Threshold sensitivity is substantial: at alpha = .60 the median effective vocabulary is 3 of four intents, and under the primary decoder no subject retains a qualifying intent at alpha = .90 (three of nine do under the FBCSP-style decoder). No pooled operating-system claim is made, and no fold ratio is reported. The dataset supplies only the base-channel measures; compositional depth, repair efficiency, and uncertainty selectivity remain unmeasured here by design. Prospective studies designed around the complete suite—compositional imagery tasks, induced decoder errors with re-imagery, and an abstention channel followed by forced commitment—are required to test the three specialized measures and incremental validity against downstream task completion.

### 15.5 Power and design

Presence of compositional generalization and of repair is detectable from small specialized channels; resolving degrees of either requires trial counts on the order of 4/δ². B_min comparisons at small Δp require base channels in the high hundreds to thousands; at the simulated 0.5-min cycle, Δp = .05 corresponds to ΔB_min = .628 bits/min and reaches .82 power at 750 trials per system. Trial budgets should be planned per channel from Tables 2a–2e, not from a single global minimum.

### 15.6 Conclusion

All simulation code, synthetic data, analysis scripts, and simulation figure generation are supplied and regenerate every simulation-based number from seed 42. The framework measures what accuracy and mutual information alone cannot: whether an agent's communication is compositional, robust, and selective.


## Declarations

**Funding.** None.

**Competing interests.** None declared.

**Ethics approval.** Not applicable to the reported simulations and secondary analysis of the public benchmark; no new participants were recruited.

**Consent to participate.** Not applicable to this secondary analysis.

**Consent for publication.** Not applicable to this secondary analysis.

**Availability of data and materials.** Synthetic data, trial-level BCI prediction records, and supplementary results accompany the reproducibility releases. Raw EEG recordings are available from the official BNCI 001-2014 dataset source.

**Code availability.** The accompanying releases contain the simulation and executed BCI code. This reporting revision adds scripts and source hashes for the uncertainty summaries, expanded BCI tables, and timing audit.

**Author contributions.** H.D.F. conceived the framework and is responsible for the analyses and manuscript.

## Open Practices Statement

The materials supporting this revision are supplied in the accompanying simulation and BCI reproducibility releases, together with the Version 4.1 reporting supplement. They include synthetic worked-example data, simulation outputs and code, executed BCI configuration and environment records, prediction CSVs, the trial ledger, and reporting scripts. The exact Version 4.1 package supporting this revision is archived at https://doi.org/10.5281/zenodo.22681002; that versioned archive, rather than the unversioned project page (https://github.com/harrisondfletcher/accuracy-illusion), identifies the numerical sources of this revision. Raw BCI data are available from the official BNCI 001-2014 source (https://bnci-horizon-2020.eu/database/data-sets/001-2014/).

No public preregistration is claimed for these analyses. The replacement BCI analysis specification was frozen on September 9, 2026, before evaluation-session decoding in that replacement run; its design fingerprint and pre-evaluation amendments are archived. This local analysis freeze is not presented as a public preregistration. The subject-pair illustration in Section 6.2 is explicitly exploratory. The Version 4.1 additions are post-execution reporting corrections and deterministic reconstruction of already specified simulation runs, not new confirmatory studies.

## References

Ang, K. K., Chin, Z. Y., Wang, C., Guan, C., & Zhang, H. (2012). Filter bank common spatial pattern algorithm on BCI Competition IV Datasets 2a and 2b. *Frontiers in Neuroscience, 6*, 39.

Archer, E., Park, I. M., & Pillow, J. W. (2014). Bayesian and quasi-Bayesian estimators for mutual information from discrete data. *Entropy, 16*(3), 1586–1617.

Bialek, W., Nemenman, I., & Tishby, N. (2001). Predictability, complexity, and learning. *Neural Computation, 13*(11), 2409–2463.

Brunner, C., Leeb, R., Müller-Putz, G., Schlögl, A., & Pfurtscheller, G. (2008). *BCI Competition 2008 – Graz data set A.* Institute for Knowledge Discovery, Graz University of Technology.

Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory, 16*(1), 41–46.

Cover, T. M., & Thomas, J. A. (2006). *Elements of information theory* (2nd ed.). Wiley-Interscience.

Cronbach, L. J. (1951). Coefficient alpha and the internal structure of tests. *Psychometrika, 16*(3), 297–334.

Crutchfield, J. P., & Feldman, D. P. (2003). Regularities unseen, randomness observed: Levels of entropy convergence. *Chaos, 13*(1), 25–54.

DeGroot, M. H., & Fienberg, S. E. (1983). The comparison and evaluation of forecasters. *The Statistician, 32*(1–2), 12–22.

El-Yaniv, R., & Wiener, Y. (2010). On the foundations of noise-free selective classification. *Journal of Machine Learning Research, 11*, 1605–1641.

Embretson, S. E., & Reise, S. P. (2000). *Item response theory for psychologists.* Lawrence Erlbaum.

Fodor, J. A., & Pylyshyn, Z. W. (1988). Connectionism and cognitive architecture: A critical analysis. *Cognition, 28*(1–2), 3–71.

Green, D. M., & Swets, J. A. (1966). *Signal detection theory and psychophysics.* Wiley.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *Proceedings of ICML 2017*, 1321–1330.

Hupkes, D., Dankers, V., Mul, M., & Bruni, E. (2020). Compositionality decomposed: How do neural networks generalise? *Journal of Artificial Intelligence Research, 67*, 757–795.

Keysers, D., Schärli, N., Scales, N., Buber, H., Furber, D., Kasber, J., … Eisenschlos, J. (2020). Measuring compositional generalization: A comprehensive method on realistic data. *Proceedings of ICLR 2020.*

Kim, N., & Linzen, T. (2020). COGS: A compositional generalization challenge based on semantic interpretation. *Proceedings of EMNLP 2020.*

Lake, B. M., & Baroni, M. (2018). Generalization without systematicity: On the compositional skills of sequence-to-sequence recurrent networks. *Proceedings of ICML 2018.*

Miller, G. A. (1955). Note on the bias of information estimates. In H. Quastler (Ed.), *Information theory in psychology* (pp. 95–100). Free Press.

Nemenman, I., Bialek, W., & de Ruyter van Steveninck, R. (2004). Entropy and information in neural spike trains: Progress on the sampling problem. *Physical Review E, 69*(5), 056111.

Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions: Comparison of eleven methods. *Statistics in Medicine, 17*(8), 873–890.

Nykopp, T. (2001). *Statistical modelling issues for the adaptive brain interface* (Master's thesis). Helsinki University of Technology.

Paninski, L. (2003). Estimation of entropy and mutual information. *Neural Computation, 15*(6), 1191–1253.

Panzeri, S., & Treves, A. (1996). Analytical estimates of limited sampling biases in different information measures. *Network: Computation in Neural Systems, 7*(1), 87–107.

Panzeri, S., Senatore, R., Montemurro, M. A., & Petersen, R. S. (2007). Correcting for the sampling bias problem in spike train information measures. *Journal of Neurophysiology, 98*(3), 1064–1072.

Pfungst, O. (1911). *Clever Hans (the horse of Mr. von Osten).* Henry Holt.

Phipson, B., & Smyth, G. K. (2010). Permutation p-values should never be zero. *Statistical Applications in Genetics and Molecular Biology, 9*(1), Article 39.

Quiroga, R. Q., & Panzeri, S. (2009). Extracting information from neuronal populations: Information theory and decoding approaches. *Nature Reviews Neuroscience, 10*(3), 173–185.

Schlögl, A., Lee, F., Bischof, H., & Pfurtscheller, G. (2005). Characterization of four-class motor imagery EEG data for the BCI-competition 2005. *Journal of Neural Engineering, 2*(4), L14–L22.

Sebeok, T. A., & Rosenthal, R. (Eds.). (1981). *The Clever Hans phenomenon.* Annals of the New York Academy of Sciences, 364.

Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal, 27*(3), 379–423.

Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. *Information Processing and Management, 45*(4), 427–437.

Tangermann, M., Müller, K. R., Aertsen, A., Birbaumer, N., Braun, C., Brunner, C., … Blankertz, B. (2012). Review of the BCI Competition IV. *Frontiers in Neuroscience, 6*, 55.

Thompson, D. E., Blain-Moraes, S., & Bhardwaj, P. (2014). Performance assessment in brain–computer interface-based augmentative and alternative communication. *BioMedical Engineering OnLine, 13*, 43.

Treves, A., & Panzeri, S. (1995). The upward bias in measures of information derived from limited data samples. *Neural Computation, 7*(2), 399–407.

Wolpaw, J. R., Birbaumer, N., McFarland, D. J., Pfurtscheller, G., & Vaughan, T. M. (2002). Brain–computer interfaces for communication and control. *Clinical Neurophysiology, 113*(6), 767–791.

Wolpaw, J. R., Ramoser, H., McFarland, D. J., & Pfurtscheller, G. (2000). EEG-based communication: Improved accuracy by response verification. *IEEE Transactions on Rehabilitation Engineering, 8*(2), 164–173.

Yuan, P., Gao, X., Allison, B., Wang, Y., Bin, G., & Gao, S. (2013). A study of the existing problems of estimating the information transfer rate in online brain–computer interfaces. *Journal of Neural Engineering, 10*(2), 026014.


## Supplementary Material

**Code S1.** `engine_v2.py` (four-channel engine and agent specification), `run_simulations.py` (Tables 1 and S1-S6; 480-cell grid), `power_v3.py` (Tables 2a-2e and S7), `metrics_u.py` (Eq. 6, coverage, and intervals), `make_figures.py`, `reproduce_all.py`, `bci_pipeline.py` (S1b), `validate_bci_output.py`, `requirements-simulation.txt`, and `requirements-bci.txt`.

**Data S2.** Synthetic worked-example dataset with columns {episode_id, channel, ground_truth, decoded_intent, duration_min, is_training, correct, repair_outcome, recovered, abstained, forced_commit_error}.

**Tables S0-S8.** S0 agent specification; S1 core profiles and uncertainty companions; S2 counterexamples; S3 null models; S4 matched-base sweep; S5 parameter grid; S6 synthetic-population covariance; S7 power cells with Wilson intervals; S8 executed primary and FBCSP-style results, ITR comparisons, artifact counts, both threshold curves, and timing evidence.

**Protocol S4.** Blinding checklist, pre-registration template, forced-commitment procedure for U, per-channel trial-budget planner keyed to Tables 2a–2e.

**Figures.** Fig. 1 measurement blind spot; Fig. 2 subject-level accuracy, full-cycle B_min, and V_eff threshold sensitivity; Fig. 3 matched-base knife; Fig. 4 per-subject BCI confusion matrices; Fig. 5 rejection landscape with empirical-size rows.
