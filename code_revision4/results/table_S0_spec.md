# Table S0. Agent specification (single source of truth: engine_v2.AGENT_SPEC)

| Agent | p_single | p_train | p_heldout | Repair policy (repeat/modify/escalate/abandon) | Recovery | Abstain (hard/easy) | Forced-commit error (hard/easy) | Notes |
|---|---|---|---|---|---|---|---|---|
| random | uniform | 1/K | 1/K | 0.25/0.25/0.25/0.25 | simulation null 1-(1-1/K)^2 | 0.30/0.30 | 0.50/0.50 | Uniform response on every channel; abstains at a fixed 0.30 independent of error risk. |
| class_biased | 0.9 | 1/K | 1/K | 0.30/0.20/0.10/0.40 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | Correct with p=0.90 on the three most frequent intents under P(Y); uniform otherwise. Never abstains. |
| overproduction | 0.85 | 1/K | 1/K | 0.30/0.20/0.10/0.40 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | Emits the most frequent intent on 70% of trials; otherwise correct with p=0.85. Never abstains. |
| memorizer | 0.85 | 0.85 | 1/K | 1.00/0.00/0.00/0.00 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | p=0.85 on single-intent and training combinations; chance on held-out; repeats without modification after induced error; never abstains. |
| compositional | 0.85 | 0.85 | 0.85 | 0.20/0.45/0.20/0.15 | modify 0.55, escalate 0.35, repeat chance, abandon 0 | 0.60/0.10 | 0.25/0.05 | p=0.85 on single-intent, training, and held-out combinations; modifies signal after induced error; abstains selectively (0.60 on hard, 0.10 on easy trials). |
| ce1 | 0.9 | 0.9 | 1/K | 1.00/0.00/0.00/0.00 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | Counterexample 1: high MI, chance C2. |
| ce2 | 0.9 | 0.9 | 0.85 | 1.00/0.00/0.00/0.00 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | Counterexample 2: high MI, high C2, R at the simulation null. |
| strategic_random | 0.7 | 0.7 | 1/K | 0.30/0.20/0.10/0.40 | simulation null 1-(1-1/K)^2 | 0.00/0.00 | 0.45/0.10 | Correct with p=0.70; every error is a cyclic-neighbor intent (index +/-1), so errors are structured rather than uniform. |
| ce3 | 0.9 | 0.9 | 0.85 | 0.20/0.45/0.20/0.15 | modify 0.55, escalate 0.35, repeat chance, abandon 0 | 0.00/0.00 | 0.45/0.10 | Counterexample 3: high MI, high C2, high R, U = 0 (never abstains). |
