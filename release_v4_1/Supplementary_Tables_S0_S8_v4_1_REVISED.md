# Supplementary Tables S0-S8 — Revision 4.1

Simulation values are retained from the archived seed-42 analyses. Tables S1b–S1c add deterministic reconstructions of the same 400 core runs per agent; the reconstructed original summary fields match the archive within numerical tolerance. Table S8 reports the completed BCI analysis. New BCI displays are exported from the archived result JSON without refitting either decoder.


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

## Table S1. Core agent profiles

### Table S1a. Existing metric profiles

400 runs per agent; |Z|=12, total N=1,000, 500 base trials per run. Cells are mean (sample SD) across runs. These are the original numerical profiles, reorganized for readability.

| Measure | Random | Class-Biased | Overproduction | Memorizer | Compositional |
|---|---:|---:|---:|---:|---:|
| Base accuracy | 0.083 (0.012) | 0.287 (0.020) | 0.314 (0.021) | 0.850 (0.016) | 0.850 (0.016) |
| MI, bits | 0.027 (0.027) | 0.638 (0.062) | 0.768 (0.071) | 2.572 (0.096) | 2.572 (0.096) |
| B_min, bits/min | 0.050 (0.049) | 1.178 (0.116) | 1.418 (0.134) | 4.748 (0.199) | 4.748 (0.199) |
| V_eff(.60) | 0.00 (0.00) | 2.71 (0.50) | 0.04 (0.20) | 11.79 (0.47) | 11.79 (0.47) |
| V_eff(.80) | 0.00 (0.00) | 0.01 (0.11) | 0.00 (0.00) | 10.44 (1.27) | 10.44 (1.27) |
| C2 | 0.083 (0.031) | 0.082 (0.032) | 0.084 (0.032) | 0.082 (0.030) | 0.856 (0.042) |
| R | 0.161 (0.026) | 0.160 (0.026) | 0.160 (0.026) | 0.161 (0.026) | 0.350 (0.034) |
| U | 0.002 (0.075) | 0.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) | 0.217 (0.132) |

Reference values: C2=1/12 under uniform response; R=1−(11/12)² under the simulation's independent-uniform two-attempt receiver null; U=0 under abstention-error independence.

### Table S1b. Uncertainty selectivity and operating behavior

Each original core run contains 150 uncertainty trials. Conditional rates are computed within each run, then summarized; they are not ratios of pooled counts. Commitment coverage equals one minus the abstention rate. Cells are mean (sample SD) across the same 400 runs.

| Agent | U | Abstention rate | Commitment coverage | P(A=1 given E=1) | P(A=1 given E=0) |
|---|---:|---:|---:|---:|---:|
| Random | 0.002 (0.075) | 0.300 (0.038) | 0.700 (0.038) | 0.302 (0.053) | 0.300 (0.054) |
| Class-Biased | 0.000 (0.000) | 0.000 (0.000) | 1.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) |
| Overproduction | 0.000 (0.000) | 0.000 (0.000) | 1.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) |
| Memorizer | 0.000 (0.000) | 0.000 (0.000) | 1.000 (0.000) | 0.000 (0.000) | 0.000 (0.000) |
| Compositional | 0.217 (0.132) | 0.251 (0.033) | 0.749 (0.033) | 0.444 (0.123) | 0.226 (0.036) |

### Table S1c. Forced-commitment denominators

| Agent | Error count, mean (SD) | Error count range | Correct count, mean (SD) | Correct count range | Non-estimable U runs |
|---|---:|---:|---:|---:|---:|
| Random | 74.78 (5.62) | 58–95 | 75.22 (5.62) | 55–92 | 0/400 |
| Class-Biased | 30.82 (4.92) | 19–46 | 119.19 (4.92) | 104–131 | 0/400 |
| Overproduction | 30.25 (4.89) | 16–45 | 119.75 (4.89) | 105–134 | 0/400 |
| Memorizer | 30.99 (4.78) | 17–45 | 119.01 (4.78) | 105–133 | 0/400 |
| Compositional | 16.70 (3.84) | 5–27 | 133.30 (3.84) | 123–145 | 0/400 |

The complete per-run denominators and conditional rates are in `evidence/core_uncertainty_runs.csv`; source hashes, summary comparisons, and aggregation definitions are in `evidence/CORE_UNCERTAINTY_REPORT.json`. These records reconstruct the original seeded core runs using the unchanged archived engine. Data S2 is a different illustrative dataset.

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

Cells: 480 (|Z| in {6,12,24,48} x p in {.5,.6,.7,.8,.9,.95} x Zipf s in {0,.5,1,1.5} x N in {100,200,500,1000,2000}), 100 paired runs each. The manuscript protocol assumes an 80/20 grammar partition, but this Bernoulli engine does not represent combination identities or a split parameter; held-out-labelled trials receive 50% of compositional evaluation allocations.

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

Pearson-correlation eigenvalues: [2.262, 1.033, 0.973, 0.626, 0.106]; cumulative variance: [0.452, 0.659, 0.854, 0.979, 1.0]. The displayed matrix above contains Spearman correlations. This distinction is preserved from the analysis.


## Table S7. Metric-specific power

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

## S7e. Uncertainty selectivity at error fraction 0.1

Each cell reports rejection probability [95% Wilson Monte Carlo interval], with 1,000 replications. Trial count is the total uncertainty-channel count. These are archived results newly displayed here, not rerun experiments.

| effect | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|
| 0 (size) | 0.021 [0.014, 0.032] | 0.025 [0.017, 0.037] | 0.037 [0.027, 0.051] | 0.035 [0.025, 0.048] |
| 0.1 | 0.154 [0.133, 0.178] | 0.234 [0.209, 0.261] | 0.469 [0.438, 0.500] | 0.793 [0.767, 0.817] |
| 0.2 | 0.378 [0.348, 0.408] | 0.606 [0.575, 0.636] | 0.939 [0.922, 0.952] | 1.000 [0.996, 1.000] |
| 0.3 | 0.595 [0.564, 0.625] | 0.868 [0.846, 0.888] | 0.997 [0.991, 0.999] | 1.000 [0.996, 1.000] |
| 0.4 | 0.786 [0.759, 0.810] | 0.961 [0.947, 0.971] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |

## S7f. Uncertainty selectivity at error fraction 0.35

Each cell reports rejection probability [95% Wilson Monte Carlo interval], with 1,000 replications. Trial count is the total uncertainty-channel count. These are archived results newly displayed here, not rerun experiments.

| effect | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|
| 0 (size) | 0.037 [0.027, 0.051] | 0.041 [0.030, 0.055] | 0.045 [0.034, 0.060] | 0.041 [0.030, 0.055] |
| 0.1 | 0.244 [0.218, 0.272] | 0.455 [0.424, 0.486] | 0.844 [0.820, 0.865] | 0.988 [0.979, 0.993] |
| 0.2 | 0.653 [0.623, 0.682] | 0.918 [0.899, 0.933] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |
| 0.3 | 0.906 [0.886, 0.923] | 0.996 [0.990, 0.998] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |
| 0.4 | 0.989 [0.980, 0.994] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] | 1.000 [0.996, 1.000] |

## S7g. Presence contrast for compositional generalization

Chance (1/12) versus .86, two-sided Fisher test. Each system receives the listed held-out trial count; intervals quantify Monte Carlo uncertainty across 1,000 replications.

| Held-out trials per system | Implied default total N | Power | 95% Monte Carlo interval |
|---|---|---|---|
| 4 | 53 | 0.384 | [0.354, 0.414] |
| 8 | 107 | 0.897 | [0.877, 0.914] |
| 15 | 200 | 0.994 | [0.987, 0.997] |
| 38 | 507 | 1.000 | [0.996, 1.000] |
| 75 | 1000 | 1.000 | [0.996, 1.000] |
| 150 | 2000 | 1.000 | [0.996, 1.000] |

## Table S8. Executed subject-specific BCI results

### Table S8a. FBCSP-style robustness decoder

Generated from the validated final result JSON (sha256 5b8075d274a57153...). Micro-averages are descriptive aggregations of heterogeneous subject-specific systems, not an operating-system claim.

| Subject | Clean E trials | Accuracy | Kappa | Corrected MI [95% CI] | Holm p | B_min [95% CI], bits/min | Selected features |
|---|---:|---:|---:|---|---:|---|---:|
| S1 | 281 | 0.854 | 0.805 | 1.391 [1.288, 1.528] | 0.002 | 10.38 [9.61, 11.40] | 64 |
| S2 | 283 | 0.403 | 0.208 | 0.172 [0.131, 0.260] | 0.002 | 1.28 [0.98, 1.94] | 96 |
| S3 | 273 | 0.813 | 0.751 | 1.174 [1.058, 1.348] | 0.002 | 8.76 [7.89, 10.06] | 64 |
| S4 | 228 | 0.680 | 0.573 | 0.783 [0.672, 0.976] | 0.002 | 5.84 [5.01, 7.28] | 96 |
| S5 | 276 | 0.609 | 0.480 | 0.554 [0.455, 0.701] | 0.002 | 4.14 [3.40, 5.23] | 32 |
| S6 | 215 | 0.498 | 0.331 | 0.257 [0.189, 0.382] | 0.002 | 1.92 [1.41, 2.85] | 16 |
| S7 | 277 | 0.866 | 0.822 | 1.376 [1.261, 1.521] | 0.002 | 10.27 [9.40, 11.35] | 96 |
| S8 | 271 | 0.812 | 0.749 | 1.064 [0.940, 1.245] | 0.002 | 7.94 [7.01, 9.29] | 96 |
| S9 | 264 | 0.697 | 0.595 | 0.808 [0.703, 0.968] | 0.002 | 6.03 [5.24, 7.22] | 96 |

### Table S8b. Paired decoder contrasts (FBCSP minus primary)

Intervals use identical bootstrap resamples of the shared evaluation trials. They are descriptive, not multiplicity-adjusted confirmatory between-decoder tests.

| Subject | dAccuracy [95% CI] | dKappa [95% CI] | dCorrected MI, bits [95% CI] |
|---|---|---|---|
| S1 | +0.075 [+0.028, +0.125] | +0.100 [+0.038, +0.166] | +0.196 [+0.038, +0.341] |
| S2 | -0.042 [-0.092, +0.011] | -0.054 [-0.120, +0.017] | -0.027 [-0.120, +0.064] |
| S3 | +0.073 [+0.029, +0.121] | +0.098 [+0.039, +0.161] | +0.239 [+0.098, +0.398] |
| S4 | +0.092 [+0.026, +0.158] | +0.122 [+0.035, +0.209] | +0.192 [+0.038, +0.366] |
| S5 | +0.210 [+0.149, +0.272] | +0.280 [+0.198, +0.361] | +0.467 [+0.343, +0.597] |
| S6 | +0.084 [+0.023, +0.149] | +0.114 [+0.032, +0.201] | +0.159 [+0.045, +0.263] |
| S7 | +0.159 [+0.101, +0.217] | +0.211 [+0.134, +0.287] | +0.482 [+0.301, +0.655] |
| S8 | +0.037 [-0.011, +0.085] | +0.049 [-0.015, +0.113] | +0.068 [-0.098, +0.230] |
| S9 | -0.034 [-0.087, +0.019] | -0.046 [-0.116, +0.025] | -0.197 [-0.344, -0.048] |

### Table S8c. Artifact exclusions by subject and session (organizer flags)

| Subject | T clean/288 | E clean/288 | E dropped by class (LH/RH/Ft/Tg) |
|---|---:|---:|---|
| S1 | 273 | 281 | 1/2/3/1 |
| S2 | 270 | 283 | 1/1/3/0 |
| S3 | 270 | 273 | 5/2/4/4 |
| S4 | 262 | 228 | 13/15/13/19 |
| S5 | 262 | 276 | 2/7/0/3 |
| S6 | 219 | 215 | 19/17/18/19 |
| S7 | 271 | 277 | 1/3/1/6 |
| S8 | 264 | 271 | 6/4/3/4 |
| S9 | 237 | 264 | 7/7/3/7 |

### Table S8d. Information-rate comparison

Both rates use the same measured full cycle of 8.043148936 s. B_min uses the subject's observed joint distribution and first-order MI correction. Conventional Wolpaw ITR uses accuracy, four equiprobable classes, and symmetric errors; it is a reference calculation, not a second measurement of the same error geometry. Every observed accuracy exceeds .25, so the stored formula and below-chance-clipped ITR agree here.

| Subject | Decoder | n | Corrected MI, bits | B_min, bits/min | Wolpaw ITR, bits/min |
|---|---|---|---|---|---|
| S1 | Primary | 281 | 1.195 | 8.92 | 6.63 |
| S1 | FBCSP-style | 281 | 1.391 | 10.38 | 8.72 |
| S2 | Primary | 283 | 0.198 | 1.48 | 0.97 |
| S2 | FBCSP-style | 283 | 0.172 | 1.28 | 0.60 |
| S3 | Primary | 273 | 0.935 | 6.97 | 5.68 |
| S3 | FBCSP-style | 273 | 1.174 | 8.76 | 7.53 |
| S4 | Primary | 228 | 0.591 | 4.41 | 2.75 |
| S4 | FBCSP-style | 228 | 0.783 | 5.84 | 4.39 |
| S5 | Primary | 276 | 0.087 | 0.65 | 0.57 |
| S5 | FBCSP-style | 276 | 0.554 | 4.14 | 3.09 |
| S6 | Primary | 215 | 0.099 | 0.74 | 0.69 |
| S6 | FBCSP-style | 215 | 0.257 | 1.92 | 1.52 |
| S7 | Primary | 277 | 0.894 | 6.67 | 4.96 |
| S7 | FBCSP-style | 277 | 1.376 | 10.27 | 9.11 |
| S8 | Primary | 271 | 0.996 | 7.43 | 6.52 |
| S8 | FBCSP-style | 271 | 1.064 | 7.94 | 7.49 |
| S9 | Primary | 264 | 1.005 | 7.49 | 5.47 |
| S9 | FBCSP-style | 264 | 0.808 | 6.03 | 4.74 |

### Table S8e. Full V_eff threshold curves

**Primary decoder.** Counts use alpha values shown and beta=30; all evaluation classes satisfy the support requirement.

| Subject | .40 | .50 | .60 | .70 | .80 | .90 |
|---|---:|---:|---:|---:|---:|---:|
| S1 | 4 | 4 | 4 | 3 | 2 | 0 |
| S2 | 3 | 1 | 1 | 0 | 0 | 0 |
| S3 | 4 | 4 | 3 | 3 | 1 | 0 |
| S4 | 4 | 3 | 2 | 0 | 0 | 0 |
| S5 | 2 | 0 | 0 | 0 | 0 | 0 |
| S6 | 2 | 1 | 0 | 0 | 0 | 0 |
| S7 | 4 | 4 | 4 | 2 | 0 | 0 |
| S8 | 4 | 4 | 4 | 3 | 1 | 0 |
| S9 | 4 | 3 | 3 | 2 | 2 | 0 |

**FBCSP-style decoder.** The same thresholds and support rule apply.

| Subject | .40 | .50 | .60 | .70 | .80 | .90 |
|---|---|---|---|---|---|---|
| S1 | 4 | 4 | 4 | 4 | 3 | 2 |
| S2 | 1 | 1 | 0 | 0 | 0 | 0 |
| S3 | 4 | 4 | 4 | 3 | 2 | 1 |
| S4 | 4 | 4 | 3 | 2 | 0 | 0 |
| S5 | 3 | 3 | 2 | 2 | 0 | 0 |
| S6 | 3 | 3 | 0 | 0 | 0 | 0 |
| S7 | 4 | 4 | 4 | 4 | 4 | 1 |
| S8 | 4 | 4 | 4 | 4 | 2 | 0 |
| S9 | 4 | 4 | 3 | 3 | 1 | 0 |

### Table S8f. All-scheduled sensitivity (frozen decoders, flagged epochs included)

| Subject | Primary clean MI | Primary all-scheduled MI | FBCSP clean MI | FBCSP all-scheduled MI |
|---|---:|---:|---:|---:|
| S1 | 1.195 | 1.177 | 1.391 | 1.363 |
| S2 | 0.198 | 0.205 | 0.172 | 0.174 |
| S3 | 0.935 | 0.915 | 1.174 | 1.176 |
| S4 | 0.591 | 0.547 | 0.783 | 0.752 |
| S5 | 0.087 | 0.098 | 0.554 | 0.563 |
| S6 | 0.099 | 0.087 | 0.257 | 0.233 |
| S7 | 0.894 | 0.896 | 1.376 | 1.372 |
| S8 | 0.996 | 0.970 | 1.064 | 1.063 |
| S9 | 1.005 | 0.962 | 0.808 | 0.826 |

### Table S8g. Methods note: epoch sample-index arithmetic and timing evidence

MAT `trial` values are one-based sample indices of the trial trigger and are converted to zero-based indexing exactly once. For a trigger at zero-based sample s0 (250 Hz): cue = s0+500; the 0.5-2.5 s post-cue decision window spans samples [s0+625, s0+1125] inclusive, 501 samples. Both a missing and a doubled 2-s cue offset are rejected by an impulse-fixture test in the released test suite. Per-trial coordinates for all 5,184 trials are in the released trial ledger. Within-run inter-trigger interval vectors (282 per evaluation session) are stored per subject in the result JSON; a per-file audit of all 18 source files (both sessions, all subjects), documenting that they share one fixed pseudorandom trigger schedule, is provided as `evidence/TRIGGER_SCHEDULE_AUDIT.json`. This reporting-stage audit recomputes the schedule comparison from the archived trial ledger; it does not claim to have reread the MAT binaries. It carries the ledger and result hashes, all six trigger vectors per file, all within-run interval vectors, and comparisons for all 18 file identities.

### Table S8h. Observed-support MI correction components

| Subject | Decoder | Plug-in MI | Subtraction term | Corrected MI | Ky / Kz / Kyz |
|---|---|---|---|---|---|
| S1 | Primary | 1.208029 | 0.012835 | 1.195193 | 4/4/12 |
| S1 | FBCSP | 1.398542 | 0.007701 | 1.390841 | 4/4/10 |
| S2 | Primary | 0.218878 | 0.020391 | 0.198486 | 4/4/15 |
| S2 | FBCSP | 0.189545 | 0.017843 | 0.171703 | 4/4/14 |
| S3 | Primary | 0.950570 | 0.015854 | 0.934716 | 4/4/13 |
| S3 | FBCSP | 1.192303 | 0.018496 | 1.173807 | 4/4/14 |
| S4 | Primary | 0.616238 | 0.025310 | 0.590927 | 4/4/15 |
| S4 | FBCSP | 0.811344 | 0.028474 | 0.782870 | 4/4/16 |
| S5 | Primary | 0.110726 | 0.023522 | 0.087204 | 4/4/16 |
| S5 | FBCSP | 0.572692 | 0.018295 | 0.554397 | 4/4/14 |
| S6 | Primary | 0.125527 | 0.026841 | 0.098686 | 4/4/15 |
| S6 | FBCSP | 0.280871 | 0.023486 | 0.257385 | 4/4/14 |
| S7 | Primary | 0.906934 | 0.013021 | 0.893914 | 4/4/12 |
| S7 | FBCSP | 1.384014 | 0.007812 | 1.376202 | 4/4/10 |
| S8 | Primary | 1.014987 | 0.018633 | 0.996355 | 4/4/14 |
| S8 | FBCSP | 1.082882 | 0.018633 | 1.064249 | 4/4/14 |
| S9 | Primary | 1.021058 | 0.016394 | 1.004663 | 4/4/13 |
| S9 | FBCSP | 0.827134 | 0.019127 | 0.808007 | 4/4/14 |

All MI quantities are in bits. Corrections are subject- and decoder-specific; rounded displays may differ in their last digit. Full precision remains in the source JSON.

### Table S8i. Execution and reporting provenance

The executed BCI configuration uses 10,000 run-by-class stratified bootstrap resamples and 5,000 within-run label permutations per subject and decoder, with Holm correction across nine subjects separately by decoder. Source result SHA-256: `5b8075d274a57153421ba078212df9554bc48e8609d42d6684c1c08b6915da38`.

Software versions recorded by the executed analysis: moabb: 1.7.1; mne: 1.12.1; scikit-learn: 1.8.0; numpy: 2.3.5; scipy: 1.17.0; matplotlib: 3.10.8.

The reporting revision does not refit CSP, LDA, or feature selection and does not replace any saved prediction, confidence interval, or permutation result. `evidence/BCI_EXTENDED_TABLES.csv` contains the expanded tabulations; `evidence/BCI_REPORTING_CHECKS.json` records the point-metric reconstruction. The executed-code archive remains the source for the full preprocessing environment and model-fitting workflow.
