# Supplementary Protocol S4: Adversarial Evaluation Checklist

## Communicative Throughput Metric Suite — Pre-Study Protocol Checklist

*Complete all items before data collection. This checklist is designed to be included in pre-registration documents.*

---

### A. Ontology and Design Specification

- [ ] Intent space Z defined with explicit list of all elements (including UNKNOWN if applicable)
- [ ] |Z| = _____ (record value)
- [ ] Emission alphabet Σ defined with discriminable token inventory
- [ ] Episode boundaries specified (start condition, end condition, timeout duration)
- [ ] Timeout duration: _____ seconds
- [ ] Ground-truth method specified (controlled condition / sensor verification / blinded judges)
- [ ] If blinded judges: minimum κ ≥ 0.80 for inter-rater reliability
- [ ] Decoder d specified (deterministic mapping / trained classifier / human coder)
- [ ] If trained classifier: decoder calibration protocol specified (known-ground-truth test without agent)

### B. Compositional Design (for C_k measurement)

- [ ] Grammar G defined with k-slot template structure
- [ ] k = _____ slots
- [ ] Training set T and held-out set U partitioned and documented
- [ ] |T| = _____, |U| = _____ (record values)
- [ ] Each individual element appears in both T and U (balance check)
- [ ] Chance baseline computed: 1/|possible responses| = _____
- [ ] Minimum held-out trials for stable estimation: ≥ 100 recommended

### C. Repair Protocol (for R measurement)

- [ ] Induced-error proportion specified: _____ % of trials (recommended: 20%)
- [ ] Error distribution pseudo-random (not predictable by agent)
- [ ] Post-error observation window: n = _____ turns (recommended: 2)
- [ ] Turn timeout: _____ seconds (recommended: 30)
- [ ] Repair classification categories defined (Repeat / Modify / Escalate / Abandon)
- [ ] Blinded coders assigned for repair classification
- [ ] Inter-rater reliability target: κ ≥ 0.75

### D. Uncertainty Protocol (for U measurement)

- [ ] Forced-choice task structure defined with UNKNOWN/abstain option
- [ ] Easy/hard trial proportion: _____ % easy / _____ % hard (recommended: 70/30)
- [ ] Hard trials constitute ≥ 20% of forced-choice tasks (required for adequate power)
- [ ] Follow-up procedure specified for UNKNOWN trials
- [ ] Random baseline b computed: 1/|options| = _____

### E. Blinding and Anti-Cueing

- [ ] Handler is blind to target intent during trials
- [ ] Target set by independent experimenter in separate location
- [ ] No communication between setter and handler during trials
- [ ] Handler behavior video-recorded for cueing review
- [ ] Blinded coder reviews handler video for inadvertent cues
- [ ] If AI decoder: inference logged before any human observation
- [ ] If animal subject: Clever Hans controls documented

### F. Automated Logging

- [ ] All emissions recorded by automated system with timestamps
- [ ] No real-time human interpretation during data collection
- [ ] Button presses logged electronically (if applicable)
- [ ] Vocalizations recorded by calibrated equipment (if applicable)
- [ ] Video recording of all sessions (minimum 2 angles recommended)

### G. Cross-Context Transfer

- [ ] 20% of evaluation trials in novel environment with novel handler
- [ ] Novel context defined and documented
- [ ] Performance comparison (training vs. novel context) planned in analysis

### H. Sample Size and Power

- [ ] Target total trials N = _____ (minimum recommended: 500 for full suite)
- [ ] Trials per intent: ≥ β = _____ (recommended: 30) for V_eff
- [ ] Held-out compositional trials: ≥ 100 for stable C_k
- [ ] Induced-error trials: ≥ 100 for stable R
- [ ] Forced-choice uncertainty trials: ≥ 100 for stable U
- [ ] Power analysis conducted using simulation code (Supplementary Code S1)

### I. Pre-Registration

- [ ] All items A–H registered before data collection begins
- [ ] F1 threshold α for V_eff: _____ (recommended: 0.80; report at 0.60, 0.70, 0.80, 0.90)
- [ ] Minimum trial count β for V_eff: _____ (recommended: 30)
- [ ] Statistical analysis plan documented (bootstrap CIs, permutation tests)
- [ ] Stop conditions specified
- [ ] Exclusion criteria specified (with planned exclusion rate reporting)
- [ ] Deterministic random seed for reproducibility: _____

### J. Reporting Checklist (post-data-collection)

- [ ] B_min reported with 95% bootstrap CI
- [ ] V_eff reported at four α thresholds (0.60, 0.70, 0.80, 0.90)
- [ ] C_k reported with exact binomial CI and chance baseline
- [ ] R reported with 95% CI; full {Repeat, Modify, Escalate, Abandon} distribution reported
- [ ] U reported with 95% CI and random baseline b
- [ ] Any not-measurable metrics explicitly noted with diagnostic explanation
- [ ] Bias-corrected MI used (Miller-Madow or Bayesian estimator)
- [ ] Decoder calibration results reported separately
- [ ] Cross-context comparison reported
- [ ] Handler cueing review results reported
- [ ] Exclusion rate reported with reasons

---

*Citation: [Authors]. An Information-Theoretic Metric Suite for Measuring Communicative Throughput in Behavioral Experiments. Behavior Research Methods.*
