# Supplementary Tables S0-S8 — Revision 4

All simulation tables are machine-generated from seed 42. Table S8 is an execution-gated BCI shell and must be replaced only from a validated `bci_real_application_v4.json`.


## Table S0. Programmed-agent specification

**Table S0a. Base, compositional, and uncertainty-channel parameters.**

| Agent | p_single | p_train | p_heldout | Abstain hard/easy | Forced-commit error hard/easy |
|---|---:|---:|---:|---:|---:|
| Random | uniform | 1/K | 1/K | .30/.30 | .50/.50 |
| Class-Biased | .90 on top 3; uniform otherwise | 1/K | 1/K | 0/0 | .45/.10 |
| Overproduction | .85 when not dominant-output | 1/K | 1/K | 0/0 | .45/.10 |
| Memorizer | .85 | .85 | 1/K | 0/0 | .45/.10 |
| Compositional | .85 | .85 | .85 | .60/.10 | .25/.05 |
| CE1 | .90 | .90 | 1/K | 0/0 | .45/.10 |
| CE2 | .90 | .90 | .85 | 0/0 | .45/.10 |
| Strategic Random | .70; cyclic-neighbor errors | .70 | 1/K | 0/0 | .45/.10 |
| CE3 | .90 | .90 | .85 | 0/0 | .45/.10 |

**Table S0b. Repair policies and programmed role.** Policies are ordered Repeat/Modify/Escalate/Abandon. The recovery reference is the independent-uniform two-attempt simulation null, not a universal empirical chance rate.

| Agent | Repair policy | Recovery model | Programmed role |
|---|---|---|---|
| Random | .25/.25/.25/.25 | Simulation null for every outcome | Uniform response; abstention independent of error risk. |
| Class-Biased | .30/.20/.10/.40 | Simulation null | Accurate only on the three most frequent intents. |
| Overproduction | .30/.20/.10/.40 | Simulation null | Emits the most frequent intent on 70% of trials. |
| Memorizer | 1/0/0/0 | Repeat at simulation null | Trained-combination success; held-out performance at chance; never abstains. |
| Compositional | .20/.45/.20/.15 | Repeat: null; Modify: .55; Escalate: .35; Abandon: 0 | Generalizes on held-out trials, repairs, and abstains selectively. |
| CE1 | 1/0/0/0 | Repeat at simulation null | High MI with chance C2. |
| CE2 | 1/0/0/0 | Repeat at simulation null | High MI and C2 with R at the simulation null. |
| Strategic Random | .30/.20/.10/.40 | Simulation null | Structured cyclic-neighbor errors rather than uniform errors. |
| CE3 | .20/.45/.20/.15 | Repeat: null; Modify: .55; Escalate: .35; Abandon: 0 | High MI, C2, and R; U=0 because it never abstains. |

## Table S1. Core agent profiles (400 runs, |Z| = 12, N = 1000; base channel 500 trials). Mean (SD).

| Agent | Acc (base) | MI (bits) | B_min (bpm) | V_eff(.60) | V_eff(.80) | C2 | R | U |
|---|---|---|---|---|---|---|---|---|
| random | 0.083 (0.012) | 0.027 (0.027) | 0.050 (0.049) | 0.00 (0.00) | 0.00 (0.00) | 0.083 (0.031) | 0.161 (0.026) | 0.002 (0.075) |
| class_biased | 0.287 (0.020) | 0.638 (0.062) | 1.178 (0.116) | 2.71 (0.50) | 0.01 (0.11) | 0.082 (0.032) | 0.160 (0.026) | 0.000 (0.000) |
| overproduction | 0.314 (0.021) | 0.768 (0.071) | 1.418 (0.134) | 0.04 (0.20) | 0.00 (0.00) | 0.084 (0.032) | 0.160 (0.026) | 0.000 (0.000) |
| memorizer | 0.850 (0.016) | 2.572 (0.096) | 4.748 (0.199) | 11.79 (0.47) | 10.44 (1.27) | 0.082 (0.030) | 0.161 (0.026) | 0.000 (0.000) |
| compositional | 0.850 (0.016) | 2.572 (0.096) | 4.748 (0.199) | 11.79 (0.47) | 10.44 (1.27) | 0.856 (0.042) | 0.350 (0.034) | 0.217 (0.132) |

Reference values: C2 = 1/12 = 0.083 under uniform response; R = 1 - (11/12)^2 = 0.160 under the simulation's independent-uniform receiver null; U = 0 under abstention-error independence.

## Table S2. Counterexamples (400 runs)

| CE | Acc (base) | MI | C2 | R | U |
|---|---|---|---|---|---|
| CE1 | 0.902 | 2.896 | 0.081 | 0.160 | 0.000 |
| CE2 | 0.899 | 2.881 | 0.849 | 0.160 | 0.000 |
| CE3 | 0.900 | 2.882 | 0.851 | 0.351 | 0.000 |

Verification: {'ce1_high_mi_chance_c2': True, 'ce2_high_c2_chance_r': True, 'ce3_high_r_zero_u': True}

## Table S3. Null models under Zipf imbalance (400 runs)

**class_biased**

| Zipf s | Acc (base) | MI | B_min | V_eff(.60) | V_eff(.80) |
|---|---|---|---|---|---|
| 0.0 | 0.287 | 0.638 | 1.178 | 2.71 | 0.01 |
| 0.5 | 0.414 | 0.926 | 1.709 | 3.00 | 1.12 |
| 1.0 | 0.565 | 1.147 | 2.117 | 3.00 | 2.36 |
| 1.5 | 0.700 | 1.191 | 2.197 | 3.00 | 2.71 |

**overproduction**

| Zipf s | Acc (base) | MI | B_min | V_eff(.60) | V_eff(.80) |
|---|---|---|---|---|---|
| 0.0 | 0.314 | 0.768 | 1.418 | 0.04 | 0.00 |
| 0.5 | 0.380 | 0.709 | 1.310 | 0.04 | 0.00 |
| 1.0 | 0.480 | 0.599 | 1.106 | 0.03 | 0.00 |
| 1.5 | 0.596 | 0.465 | 0.858 | 1.01 | 0.00 |

Expected class-biased accuracy at s = 1 under the response rule: 0.566.

**strategic_random**: Acc 0.699, MI 2.402, B_min 4.439, V_eff(.60) 11.12, V_eff(.80) 0.34, C2 0.083, R 0.160.

## Table S4. Equal-p sweep: memorizer vs compositional (300 runs)

| p | Acc base (mem/comp) | Aggregate acc gap | B_min (mem/comp) | C2 (mem/comp) | C2 gap |
|---|---|---|---|---|---|
| 0.5 | 0.500 / 0.500 | 0.047 | 1.684 / 1.684 | 0.081 / 0.497 | 0.416 |
| 0.6 | 0.599 / 0.599 | 0.060 | 2.400 / 2.400 | 0.081 / 0.600 | 0.519 |
| 0.7 | 0.701 / 0.701 | 0.071 | 3.263 / 3.263 | 0.079 / 0.697 | 0.618 |
| 0.8 | 0.801 / 0.801 | 0.083 | 4.213 / 4.213 | 0.083 / 0.800 | 0.717 |
| 0.9 | 0.899 / 0.899 | 0.095 | 5.312 / 5.312 | 0.084 / 0.900 | 0.816 |
| 0.95 | 0.950 / 0.950 | 0.099 | 5.950 / 5.950 | 0.086 / 0.951 | 0.864 |

## Table S5. Parameter grid summary

Cells: 480 (|Z| in {6,12,24,48} x p in {.5,...,.95} x Zipf s in {0,.5,1,1.5} x N in {100,...,2000}), 100 paired runs each. The manuscript protocol assumes an 80/20 grammar partition, but this Bernoulli engine does not represent combination identities or a split parameter; held-out-labelled trials receive 50% of compositional evaluation allocations.

- C2 separation (Cohen's d, compositional - memorizer): min 1.80, median 11.48; min by N: {'100': 1.7990665645732073, '200': 2.7242138168288235, '500': 4.220398527339975, '1000': 6.333734862636938, '2000': 9.048569524065496}
- R separation (Cohen's d): min 0.53, median 4.36; min by N: {'100': 0.5277612371335976, '200': 0.8737678708074401, '500': 1.3214000868061868, '1000': 1.8231103604460055, '2000': 2.6774108619382155}
- B_min non-decreasing in p in 98.8% of (|Z|, s, N) series (Proposition 1)
- V_eff(.80) <= V_eff(.60) in every cell: True (Proposition 2)

## Table S6. Covariation in a continuously parameterized synthetic population (1,000 agents): Spearman rho

| | B_min | V_eff | C2 | R | U |
|---|---|---|---|---|---|
| B_min | 1.00 | 0.87 | 0.47 | -0.01 | -0.00 |
| V_eff | 0.87 | 1.00 | 0.40 | -0.00 | -0.04 |
| C2 | 0.47 | 0.40 | 1.00 | 0.00 | 0.02 |
| R | -0.01 | -0.00 | 0.00 | 1.00 | 0.02 |
| U | -0.00 | -0.04 | 0.02 | 0.02 | 1.00 |

Eigenvalues: [2.262, 1.033, 0.973, 0.626, 0.106]; cumulative variance: [0.452, 0.659, 0.854, 0.979, 1.0].


All cells use 1000 Monte Carlo replications. C2, R, and U use two-sided Fisher exact tests. B_min uses 1000 system-label permutations per replication.

## S7a. C2 degree comparison

| effect | 15 | 38 | 75 | 150 | 400 | 1600 |
|---|---|---|---|---|---|---|
| 0 (size) | 0.015 [0.009, 0.025] | 0.034 [0.024, 0.047] | 0.042 [0.031, 0.056] | 0.047 [0.035, 0.062] | 0.047 [0.035, 0.062] | 0.048 [0.036, 0.063] |
| 0.05 | 0.029 [0.020, 0.041] | 0.050 [0.038, 0.065] | 0.082 [0.067, 0.101] | 0.132 [0.112, 0.154] | 0.253 [0.227, 0.281] | 0.786 [0.759, 0.810] |
| 0.1 | 0.032 [0.023, 0.045] | 0.099 [0.082, 0.119] | 0.204 [0.180, 0.230] | 0.356 [0.327, 0.386] | 0.795 [0.769, 0.819] | 1.000 [0.996, 1.000] |
| 0.2 | 0.103 [0.086, 0.123] | 0.331 [0.302, 0.361] | 0.657 [0.627, 0.686] | 0.930 [0.912, 0.944] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |
| 0.4 | 0.550 [0.519, 0.581] | 0.972 [0.960, 0.981] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |

## S7b. Repair efficiency

| effect | 20 | 40 | 100 | 200 | 400 |
|---|---|---|---|---|---|
| 0 (size) | 0.021 [0.014, 0.032] | 0.028 [0.019, 0.040] | 0.038 [0.028, 0.052] | 0.047 [0.035, 0.062] | 0.035 [0.025, 0.048] |
| 0.05 | 0.034 [0.024, 0.047] | 0.050 [0.038, 0.065] | 0.090 [0.074, 0.109] | 0.200 [0.176, 0.226] | 0.409 [0.379, 0.440] |
| 0.1 | 0.061 [0.048, 0.078] | 0.142 [0.122, 0.165] | 0.352 [0.323, 0.382] | 0.631 [0.601, 0.660] | 0.910 [0.891, 0.926] |
| 0.2 | 0.217 [0.193, 0.244] | 0.444 [0.413, 0.475] | 0.875 [0.853, 0.894] | 0.996 [0.990, 0.998] | 1.000 [0.996, 1.000] |
| 0.25 | 0.296 [0.269, 0.325] | 0.617 [0.587, 0.647] | 0.974 [0.962, 0.982] | 0.999 [0.994, 1.000] | 1.000 [0.996, 1.000] |

## S7c. Uncertainty selectivity (error fraction 0.20)

| effect | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|
| 0 (size) | 0.017 [0.011, 0.027] | 0.038 [0.028, 0.052] | 0.043 [0.032, 0.057] | 0.031 [0.022, 0.044] |
| 0.1 | 0.210 [0.186, 0.236] | 0.364 [0.335, 0.394] | 0.726 [0.698, 0.753] | 0.950 [0.935, 0.962] |
| 0.2 | 0.569 [0.538, 0.599] | 0.805 [0.779, 0.828] | 0.994 [0.987, 0.997] | 1.000 [0.996, 1.000] |
| 0.3 | 0.861 [0.838, 0.881] | 0.985 [0.975, 0.991] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |
| 0.4 | 0.960 [0.946, 0.971] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |

## S7d. Effective information rate

| effect | 100 | 200 | 500 | 750 | 1000 | 2000 |
|---|---|---|---|---|---|---|
| 0 (size) | 0.050 [0.038, 0.065] | 0.039 [0.029, 0.053] | 0.044 [0.033, 0.059] | 0.057 [0.044, 0.073] | 0.052 [0.040, 0.068] | 0.047 [0.035, 0.062] |
| 0.01 | 0.047 [0.035, 0.062] | 0.060 [0.047, 0.076] | 0.071 [0.057, 0.089] | 0.081 [0.066, 0.100] | 0.086 [0.070, 0.105] | 0.130 [0.111, 0.152] |
| 0.03 | 0.107 [0.089, 0.128] | 0.126 [0.107, 0.148] | 0.289 [0.262, 0.318] | 0.365 [0.336, 0.395] | 0.488 [0.457, 0.519] | 0.798 [0.772, 0.822] |
| 0.05 | 0.155 [0.134, 0.179] | 0.310 [0.282, 0.339] | 0.665 [0.635, 0.694] | 0.823 [0.798, 0.845] | 0.929 [0.911, 0.943] | 1.000 [0.996, 1.000] |
| 0.1 | 0.655 [0.625, 0.684] | 0.905 [0.885, 0.922] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |

## Population effect scale for B_min

| Delta p | Delta B_min (bits/min) |
|---:|---:|
| 0.00 | 0.000 |
| 0.01 | 0.120 |
| 0.03 | 0.369 |
| 0.05 | 0.628 |
| 0.10 | 1.339 |

## Table S8. BCI execution-gated supplementary report

This table is not populated in the pre-execution revision. After `validate_bci_output.py` passes, report for each subject and both decoders: all/clean/excluded trials by class, software versions, filter specification, selected hyperparameters, accuracy and kappa with intervals, plug-in MI, correction amount, corrected MI with interval, raw and Holm-adjusted permutation p-values, full-cycle `B_min`, conventional ITR, class precision/recall/F1, `V_eff(.40-.90,30)`, and the complete confusion matrix. A micro-average may be included only as a reference aggregation and must not be interpreted as an operating subject-specific system.
