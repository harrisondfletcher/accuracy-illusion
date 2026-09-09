# Supplementary Protocol S4: Adversarial Evaluation and Trial-Budget Checklist

Complete Sections A–J before data collection. Record deviations rather than silently changing the protocol.

## A. Ontology and base channel

- [ ] Finite intent ontology `Z` listed and preregistered; `|Z| = ____`.
- [ ] Emission alphabet `Σ` listed with discriminability criteria.
- [ ] Abstention is recorded separately from `Z`.
- [ ] Base-channel episode ground truth is independently verifiable.
- [ ] Decoder and decision rule are frozen before evaluation.
- [ ] Episode duration definition is fixed:
  - [ ] externally paced: onset to next onset;
  - [ ] self-paced: onset to verified resolution or preregistered timeout.
- [ ] Decoder analysis-window duration is not substituted for the full episode cycle.
- [ ] Base class-allocation rule is specified.
- [ ] `β = ____` observations per intent; under controlled allocation, `n_S ≥ β|Z|`.
- [ ] Reference F1 threshold `α = ____` is application-specific and preregistered.
- [ ] Full `V_eff(α,β)` curve will be reported at `α = .60, .70, .80, .90` plus the application threshold.

## B. Compositional channel (`C_k`)

- [ ] `k = ____`-slot grammar `G` is explicit.
- [ ] Training set `T` and held-out set `U = G \ T` are fixed before evaluation.
- [ ] Every constituent element appears in both `T` and `U`.
- [ ] Held-out combination identities, not only held-out trial counts, are recorded.
- [ ] Response space and chance model are specified.
- [ ] Scoring is blinded to condition and training status.
- [ ] Grammar structure, item difficulty, response space, and hold-out construction are reported so `C_k` can be compared across studies.
- [ ] Held-out evaluation trials per system: `n_U = ____`.

Power reference, two independent systems, baseline `C_k=.50`:

| Target difference `δ_C` | Approximate held-out trials per system for 80% power |
|---:|---:|
| .40 | 38 |
| .20 | 150 |
| .10 | 400 |
| .05 | 1,600 |

The extreme chance-versus-.86 presence contrast reaches about 90% power at eight held-out trials per system. It is not a general sample-size recommendation.

## C. Repair channel (`R`)

- [ ] Induced misunderstanding proportion: `____%`.
- [ ] Induced errors are pseudorandom and unpredictable by the agent.
- [ ] Observation window: `n = ____` turns; timeout `____` seconds/turn.
- [ ] Outcomes are coded as Repeat / Modify / Escalate / Abandon.
- [ ] Correct recovery is defined independently of the outcome category.
- [ ] Blinded repair coders assigned; target reliability `κ ≥ .75`.
- [ ] The repair null is derived from the actual receiver/decoder and repair policy.
- [ ] If the independent-uniform null is used, state that assumption explicitly: `1-(1-1/|Z|)^n`.
- [ ] Induced-error trials per system: `n_R = ____`.

Power reference at independent-uniform baseline `.160`, two systems:

| Target difference `δ_R` | Approximate induced-error trials per system |
|---:|---:|
| .25 | 100 gives about .97 power |
| .20 | 100 gives about .88 power |
| .10 | 400 gives about .91 power |
| .05 | More than 400 required |

## D. Uncertainty channel (`U`)

- [ ] UNKNOWN/abstain is available before forced commitment.
- [ ] The same stimulus remains in view or otherwise unchanged.
- [ ] No additional task-relevant information is supplied between abstention and forced commitment.
- [ ] Forced commitment follows after a fixed short delay of `____` seconds.
- [ ] Outcome feedback occurs only after forced commitment.
- [ ] `a_i` records abstention and `e_i` records forced-commitment error on every uncertainty trial.
- [ ] Both `e=1` and `e=0` strata are expected to be populated.
- [ ] Report `U`, its interval, abstention rate/coverage, `n_{e=1}`, and `n_{e=0}`.
- [ ] For graded confidence, report risk–coverage and AURC; assess calibration separately with a proper score.
- [ ] Uncertainty trials: `n_A = ____`; anticipated error fraction `π_e = ____`.

Power reference for non-error abstention `.10` and error fraction `.20`:

| Target selectivity `δ_U` | Approximate uncertainty trials |
|---:|---:|
| .40 | 100 gives about .96 power |
| .30 | 100 gives about .86 power |
| .20 | 200 gives about .81 power |
| .10 | 1,000 gives about .95 power |

Power changes materially with the error fraction. Use the complete Table S7 rather than a fixed minimum.

## E. Blinding and anti-cueing

- [ ] Handler is blind to target intent.
- [ ] Target is set by an independent experimenter or automated system.
- [ ] No setter–handler communication occurs during trials.
- [ ] Handler behavior is video recorded.
- [ ] A blinded coder reviews cue leakage.
- [ ] Decoder output is logged before human observation.
- [ ] Clever Hans controls are described for interactive animal paradigms.

## F. Automated logging and data schema

- [ ] All emissions, decoder outputs, targets, abstentions, forced commitments, repair turns, and timestamps are logged automatically.
- [ ] Raw and processed data retain stable episode identifiers.
- [ ] Exclusions preserve an audit trail and reason code.
- [ ] The released schema contains at least:
  `episode_id, channel, ground_truth, decoded_intent, onset, resolution_or_next_onset, duration_min, is_training, combination_id, correct, repair_outcome, recovered, abstained, forced_commit_error`.

## G. Ground truth and measurement error

- [ ] Ground truth is not inferred from the decoder or handler narrative.
- [ ] Spontaneous-intent coding uses at least two blinded judges and target `κ ≥ .80`.
- [ ] Indeterminate episodes are flagged before analysis; exclusion rate reported.
- [ ] A sensitivity analysis is specified when estimated label error exceeds .10.
- [ ] For `U`, distinguish nondifferential forced-commitment outcome error, which generally attenuates selectivity, from differential error, which can bias either direction.

## H. Statistical analysis

- [ ] Miller–Madow correction uses observed support:
  `(K_yz - K_y - K_z + 1)/(2N ln 2)`.
- [ ] Corrected MI is not truncated at zero for inference.
- [ ] `B_min` descriptive interval uses bias correction inside every bootstrap sample.
- [ ] Confirmatory one-system MI test permutes decoded outputs relative to ground truth.
- [ ] Confirmatory two-system `B_min` test permutes system labels on complete episode records; paired systems use within-episode swaps.
- [ ] Permutation p-values use `(b+1)/(B+1)` with at least 1,000 permutations.
- [ ] `C_k` reports exact binomial interval and `n_U`.
- [ ] `R` reports interval, null model, `n_R`, and full outcome distribution.
- [ ] `U` reports a Newcombe or stratified-bootstrap interval and error-stratum counts.
- [ ] Multiplicity procedure is specified when making subject-level or class-level claims.

## I. Cross-context transfer

- [ ] Novel context and/or handler is defined in advance.
- [ ] Transfer-trial proportion: `____%`.
- [ ] Training-context and transfer-context results are reported separately.
- [ ] A decrement qualifies the capacity estimate rather than being silently pooled away.

## J. Reproducibility and reporting

- [ ] Random seeds and software versions are frozen.
- [ ] A clean environment can execute `python reproduce_all.py`.
- [ ] Every table and figure is generated from machine-readable results.
- [ ] Base, compositional, repair, and uncertainty channels remain separate in code.
- [ ] No pooled confusion matrix across heterogeneous subject-specific systems is interpreted as an operating system.
- [ ] Accuracy, MI, `B_min`, per-class precision/recall/F1, and the `V_eff` curve are reported together.
- [ ] Metrics not computable from the design are explicitly marked not measurable.
- [ ] Claims about internal representation, conceptual understanding, or consciousness are excluded unless independently tested.
