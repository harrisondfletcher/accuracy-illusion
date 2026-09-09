"""run_simulations.py - regenerates every simulation result in the manuscript from engine_v2.

Outputs (results/):
    table1.json           five core agents, 400 runs, default configuration
    null_models.json      class-biased and overproduction under Zipf s in {0,.5,1,1.5}; strategic random
    counterexamples.json  CE1-CE3, 400 runs, with verification flags
    sweep_noise.json      memorizer vs compositional at equal p_single in {.5,...,.95}; 300 runs
    grid.json             |Z| x p x zipf x N, 100 paired runs per cell, memorizer vs compositional
    nonredundancy.json    1,000 continuously parameterized synthetic agents; Spearman, Pearson, PCA
    tables_S3.md          supplementary tables generated from the JSON files
    table_S0_spec.md      agent specification table
"""
from __future__ import annotations
import json, os, sys, time, math, multiprocessing as mp
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_v2 import (AGENT_SPEC, SimConfig, run_batch, run_sim, make_spec, spec_table_markdown,
                       mi_plugin_and_mm, veff, f1_per_class, u_selectivity, zipf, repair_chance)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
SEED = 42
CORE = ["random", "class_biased", "overproduction", "memorizer", "compositional"]


def save(obj, name):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1, default=lambda o: None if isinstance(o, float) and math.isnan(o) else str(o))
    print(f"  -> results/{name}")


def cohens_d(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[~np.isnan(a)]; b = b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2: return float("nan")
    sp = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((b.mean() - a.mean()) / sp) if sp > 0 else float("inf")


def table1():
    print("[Table 1] 400 runs x 5 agents; Memorizer/Compositional paired on the base channel")
    cfg = SimConfig()
    out = {a: run_batch(a, cfg, 400, SEED) for a in ("random", "class_biased", "overproduction")}
    paired_offset = 3_000_000
    out["memorizer"] = run_batch("memorizer", cfg, 400, SEED, seed_offset=paired_offset)
    out["compositional"] = run_batch("compositional", cfg, 400, SEED, seed_offset=paired_offset)
    out["config"] = cfg.__dict__
    out["paired_base_seed_offset"] = paired_offset
    save(out, "table1.json")


def null_models():
    print("[Null models] Zipf sweep, 400 runs")
    out = {"class_biased": {}, "overproduction": {}}
    for s in (0.0, 0.5, 1.0, 1.5):
        cfg = SimConfig(zipf_s=s)
        for a in ("class_biased", "overproduction"):
            out[a][str(s)] = run_batch(a, cfg, 400, SEED)
            b = out[a][str(s)]
            print(f"  {a:15s} s={s}: acc={b['accuracy_base']['mean']:.3f} MI={b['mi']['mean']:.3f} B={b['b_min']['mean']:.3f} V60={b['veff_60']['mean']:.2f} V80={b['veff_80']['mean']:.2f}")
    out["strategic_random"] = run_batch("strategic_random", SimConfig(), 400, SEED)
    K = 12; P = zipf(K, 1.0); top = np.sort(P)[::-1][:3].sum()
    out["class_biased_expected_accuracy_s1"] = float(top * 0.90 + (1 - top) / K)
    save(out, "null_models.json")


def counterexamples():
    print("[Counterexamples] 400 runs")
    cfg = SimConfig(); out = {c: run_batch(c, cfg, 400, SEED) for c in ("ce1", "ce2", "ce3")}
    ch = 1.0 / cfg.K; rch = repair_chance(cfg.K, 2)
    out["verification"] = {
        "ce1_high_mi_chance_c2": out["ce1"]["mi"]["mean"] > 2.0 and abs(out["ce1"]["c2"]["mean"] - ch) < 0.05,
        "ce2_high_c2_chance_r": out["ce2"]["c2"]["mean"] > 0.7 and abs(out["ce2"]["r"]["mean"] - rch) < 0.05,
        "ce3_high_r_zero_u": out["ce3"]["r"]["mean"] > 0.3 and abs(out["ce3"]["u"]["mean"]) < 1e-9,
    }
    print("  ", out["verification"]); save(out, "counterexamples.json")


def sweep_noise():
    print("[Noise / matched sweep] 300 runs x 6 p x 2 agents (equal p_single)")
    out = {}
    for i, p in enumerate((0.50, 0.60, 0.70, 0.80, 0.90, 0.95)):
        cfg = SimConfig()
        paired_offset = 3_500_000 + i * 1000
        mem = run_batch(make_spec("memorizer", p_single=p, p_train=p), cfg, 300, SEED, seed_offset=paired_offset)
        comp = run_batch(make_spec("compositional", p_single=p, p_train=p, p_heldout=p), cfg, 300, SEED, seed_offset=paired_offset)
        out[str(p)] = dict(memorizer=mem, compositional=comp,
                           acc_gap=comp["accuracy_pooled"]["mean"] - mem["accuracy_pooled"]["mean"],
                           c2_gap=comp["c2"]["mean"] - mem["c2"]["mean"],
                           bmin_gap=comp["b_min"]["mean"] - mem["b_min"]["mean"])
        print(f"  p={p}: accB mem={mem['accuracy_base']['mean']:.3f} comp={comp['accuracy_base']['mean']:.3f} | pooled gap={out[str(p)]['acc_gap']:.3f} | C2 gap={out[str(p)]['c2_gap']:.3f} | B gap={out[str(p)]['bmin_gap']:.3f}")
    save(out, "sweep_noise.json")


def _grid_cell(args):
    idx, K, p, s, N = args
    cfg = SimConfig(K=K, zipf_s=s, N=N, heldout_eval_frac=0.50)
    mem = make_spec("memorizer", p_single=p, p_train=p)
    comp = make_spec("compositional", p_single=p, p_train=p, p_heldout=p)
    rm, rc = [], []
    for i in range(100):
        paired_seed = SEED + 5_000_000 + idx * 1000 + i
        rm.append(run_sim(mem, cfg, paired_seed))
        rc.append(run_sim(comp, cfg, paired_seed))
    g = lambda rs, k: np.array([getattr(r, k) for r in rs], float)
    return dict(
        K=K, p=p, zipf=s, N=N,
        heldout_eval_frac=cfg.heldout_eval_frac,
        c2_mem=float(np.nanmean(g(rm, "c2"))), c2_comp=float(np.nanmean(g(rc, "c2"))),
        c2_d=cohens_d(g(rm, "c2"), g(rc, "c2")),
        r_mem=float(np.nanmean(g(rm, "r"))), r_comp=float(np.nanmean(g(rc, "r"))),
        r_d=cohens_d(g(rm, "r"), g(rc, "r")),
        bmin_mem=float(np.nanmean(g(rm, "b_min"))), bmin_comp=float(np.nanmean(g(rc, "b_min"))),
        base_bmin_max_abs_pair_diff=float(np.max(np.abs(g(rm, "b_min") - g(rc, "b_min")))),
        veff80_mem=float(np.mean([r.veff[0.80] for r in rm])),
        veff60_mem=float(np.mean([r.veff[0.60] for r in rm])),
        n_heldout=int(round(np.mean(g(rm, "c2_n")))))


def grid():
    print("[Grid] |Z| x p x zipf x N, 100 paired runs, Memorizer vs Compositional")
    t0 = time.time()
    params=[]; idx=0
    for K in (6, 12, 24, 48):
        for p in (0.50, 0.60, 0.70, 0.80, 0.90, 0.95):
            for s in (0.0, 0.5, 1.0, 1.5):
                for N in (100, 200, 500, 1000, 2000):
                    params.append((idx,K,p,s,N)); idx += 1
    workers=max(1, min(4, (os.cpu_count() or 2)-1))
    with mp.Pool(workers) as pool:
        cells=pool.map(_grid_cell, params, chunksize=4)
    c2d = np.array([c["c2_d"] for c in cells]); rd = np.array([c["r_d"] for c in cells])
    mono_noise = {}
    for K in (6, 12, 24, 48):
        for s in (0.0, 0.5, 1.0, 1.5):
            for N in (100, 200, 500, 1000, 2000):
                seq = [np.mean([c["bmin_mem"] for c in cells if c["K"] == K and c["zipf"] == s and c["N"] == N and c["p"] == p]) for p in (0.50, 0.60, 0.70, 0.80, 0.90, 0.95)]
                mono_noise[f"K{K}_s{s}_N{N}"] = bool(np.all(np.diff(seq) >= -1e-9))
    summary = dict(
        n_cells=len(cells), runs_per_cell=100, workers=workers,
        grammar_partition_protocol="80/20 assumed; combination identities not represented", heldout_eval_frac=0.50,
        c2_d_min=float(np.nanmin(c2d)), c2_d_median=float(np.nanmedian(c2d)),
        c2_d_min_by_N={str(N): float(np.nanmin([c["c2_d"] for c in cells if c["N"] == N])) for N in (100, 200, 500, 1000, 2000)},
        r_d_min=float(np.nanmin(rd)), r_d_median=float(np.nanmedian(rd)),
        r_d_min_by_N={str(N): float(np.nanmin([c["r_d"] for c in cells if c["N"] == N])) for N in (100, 200, 500, 1000, 2000)},
        max_paired_base_bmin_difference=float(max(c["base_bmin_max_abs_pair_diff"] for c in cells)),
        bmin_monotone_in_p_all=bool(all(mono_noise.values())),
        bmin_monotone_fraction=float(np.mean(list(mono_noise.values()))),
        veff_monotone_in_alpha_all=bool(all(c["veff80_mem"] <= c["veff60_mem"] + 1e-9 for c in cells)),
        seconds=time.time() - t0)
    print("  ", {k: v for k, v in summary.items() if k != "seconds"})
    save(dict(summary=summary, cells=cells), "grid.json")


def nonredundancy():
    print("[Synthetic covariance] 1,000 continuously parameterized agents, base channel 500 trials")
    rng = np.random.default_rng(SEED + 7_000_000); rows = []; params = []
    cfg = SimConfig()
    for i in range(1000):
        p = rng.uniform(0.30, 0.98); g = rng.uniform(0, 1); m = rng.uniform(0, 0.8); s = rng.uniform(-0.3, 1.0)
        base_a = 0.25; ah = float(np.clip(base_a + 0.5 * s, 0, 1)); ae = float(np.clip(base_a - 0.2 * s, 0, 1))
        spec = make_spec("compositional", p_single=p, p_train=p, p_heldout=1 / cfg.K + g * (p - 1 / cfg.K),
                         repair_policy=(1 - m, m, 0.0, 0.0), abstain_hard=ah, abstain_easy=ae)
        r = run_sim(spec, cfg, SEED + 7_000_000 + i)
        rows.append([r.b_min, r.veff[0.80], r.c2, r.r, r.u]); params.append([p, g, m, s])
    X = np.array(rows, float); names = ["B_min", "V_eff", "C2", "R", "U"]
    rho, _ = spearmanr(X, nan_policy="omit"); C = np.corrcoef(X[~np.isnan(X).any(1)].T)
    ev = np.sort(np.linalg.eigvalsh(C))[::-1]
    out = dict(n_agents=len(X), base_trials=cfg.allocation()[0], names=names,
               generator=dict(p_single="U(0.30,0.98)", heldout="1/K + g(p-1/K), g~U(0,1)",
                              repair="repeat 1-m / modify m, m~U(0,0.8); recovery modify 0.55, repeat chance",
                              abstention="hard 0.25+0.5s, easy 0.25-0.2s, s~U(-0.3,1); forced-commit error 0.25 hard / 0.05 easy"),
               spearman=rho.tolist(), pearson=C.tolist(), eigenvalues=ev.tolist(),
               cumulative_variance=(np.cumsum(ev) / ev.sum()).tolist(), n_u_nan=int(np.isnan(X[:, 4]).sum()))
    print("  Spearman:\n", np.round(rho, 2)); print("  eigen:", np.round(ev, 3), " cum:", np.round(np.cumsum(ev) / ev.sum(), 3))
    save(out, "nonredundancy.json")


def equal_mi_matrices():
    print("[Equal-MI matrices]")
    from scipy.optimize import brentq
    def h2(x): return -x * math.log2(x) - (1 - x) * math.log2(1 - x)
    A = np.full((4, 4), 0.05); np.fill_diagonal(A, 0.85)
    def mi_u(P):
        J = P / 4; Py = J.sum(1, keepdims=True); Pz = J.sum(0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            return float(np.where(J > 0, J * np.log2(J / (Py * Pz)), 0).sum())
    miA = mi_u(A); d = 0.81
    q = brentq(lambda x: 0.5 * (h2(d) + h2(x)) - (2 - miA), 0.5001, 0.9999, xtol=1e-14)
    B = np.array([[d, 1 - d, 0, 0], [1 - d, d, 0, 0], [0, 0, q, 1 - q], [0, 0, 1 - q, q]])
    D95 = np.full((4, 4), 0.05 / 3); np.fill_diagonal(D95, 0.95)
    out = dict(alpha=A.tolist(), beta=B.tolist(), q=q, mi_alpha=miA, mi_beta=mi_u(B), abs_diff=abs(miA - mi_u(B)),
               f1_alpha=f1_per_class(A).tolist(), f1_beta=f1_per_class(B).tolist(),
               veff80_alpha=int((f1_per_class(A) >= 0.8).sum()), veff80_beta=int((f1_per_class(B) >= 0.8).sum()),
               same_veff_diff_mi=dict(diag_085_mi=miA, diag_095_mi=mi_u(D95), veff80_both=4))
    print(f"  q={q:.12f} MI_alpha={miA:.10f} MI_beta={mi_u(B):.10f} diff={out['abs_diff']:.2e} | V80 {out['veff80_alpha']} vs {out['veff80_beta']} | diag .95 MI={mi_u(D95):.4f}")
    save(out, "equal_mi_matrices.json")


def write_tables():
    print("[Tables]")
    with open(os.path.join(OUT, "table_S0_spec.md"), "w") as f:
        f.write("# Table S0. Agent specification (single source of truth: engine_v2.AGENT_SPEC)\n\n" + spec_table_markdown() + "\n")
    t1 = json.load(open(os.path.join(OUT, "table1.json")))
    nm = json.load(open(os.path.join(OUT, "null_models.json")))
    ce = json.load(open(os.path.join(OUT, "counterexamples.json")))
    sw = json.load(open(os.path.join(OUT, "sweep_noise.json")))
    gr = json.load(open(os.path.join(OUT, "grid.json")))["summary"]
    nr = json.load(open(os.path.join(OUT, "nonredundancy.json")))
    L = ["# Supplementary Tables S3 (generated by run_simulations.py, seed 42)\n"]
    L.append("## Table S1. Core agent profiles (400 runs, |Z| = 12, N = 1000; base channel 500 trials). Mean (SD).\n")
    L.append("| Agent | Acc (base) | MI (bits) | B_min (bpm) | V_eff(.60) | V_eff(.80) | C2 | R | U |\n|---|---|---|---|---|---|---|---|---|")
    for a in CORE:
        b = t1[a]; f = lambda k, d=3: f"{b[k]['mean']:.{d}f} ({b[k]['sd']:.{d}f})"
        L.append(f"| {a} | {f('accuracy_base')} | {f('mi')} | {f('b_min')} | {f('veff_60',2)} | {f('veff_80',2)} | {f('c2')} | {f('r')} | {f('u')} |")
    L.append("\nReference values: C2 = 1/12 = 0.083 under uniform response; R = 1 - (11/12)^2 = 0.160 under the simulation's independent-uniform receiver null; U = 0 under abstention-error independence.\n")
    L.append("## Table S2. Counterexamples (400 runs)\n\n| CE | Acc (base) | MI | C2 | R | U |\n|---|---|---|---|---|---|")
    for c in ("ce1", "ce2", "ce3"):
        b = ce[c]; L.append(f"| {c.upper()} | {b['accuracy_base']['mean']:.3f} | {b['mi']['mean']:.3f} | {b['c2']['mean']:.3f} | {b['r']['mean']:.3f} | {b['u']['mean']:.3f} |")
    L.append(f"\nVerification: {ce['verification']}\n")
    L.append("## Table S3. Null models under Zipf imbalance (400 runs)\n")
    for a in ("class_biased", "overproduction"):
        L.append(f"**{a}**\n\n| Zipf s | Acc (base) | MI | B_min | V_eff(.60) | V_eff(.80) |\n|---|---|---|---|---|---|")
        for s in ("0.0", "0.5", "1.0", "1.5"):
            b = nm[a][s]; L.append(f"| {s} | {b['accuracy_base']['mean']:.3f} | {b['mi']['mean']:.3f} | {b['b_min']['mean']:.3f} | {b['veff_60']['mean']:.2f} | {b['veff_80']['mean']:.2f} |")
        L.append("")
    L.append(f"Expected class-biased accuracy at s = 1 under the response rule: {nm['class_biased_expected_accuracy_s1']:.3f}.\n")
    b = nm["strategic_random"]; L.append(f"**strategic_random**: Acc {b['accuracy_base']['mean']:.3f}, MI {b['mi']['mean']:.3f}, B_min {b['b_min']['mean']:.3f}, V_eff(.60) {b['veff_60']['mean']:.2f}, V_eff(.80) {b['veff_80']['mean']:.2f}, C2 {b['c2']['mean']:.3f}, R {b['r']['mean']:.3f}.\n")
    L.append("## Table S4. Equal-p sweep: memorizer vs compositional (300 runs)\n\n| p | Acc base (mem/comp) | Aggregate acc gap | B_min (mem/comp) | C2 (mem/comp) | C2 gap |\n|---|---|---|---|---|---|")
    for p, v in sw.items():
        L.append(f"| {p} | {v['memorizer']['accuracy_base']['mean']:.3f} / {v['compositional']['accuracy_base']['mean']:.3f} | {v['acc_gap']:.3f} | {v['memorizer']['b_min']['mean']:.3f} / {v['compositional']['b_min']['mean']:.3f} | {v['memorizer']['c2']['mean']:.3f} / {v['compositional']['c2']['mean']:.3f} | {v['c2_gap']:.3f} |")
    L.append("\n## Table S5. Parameter grid summary\n")
    L.append(f"Cells: {gr['n_cells']} (|Z| in {{6,12,24,48}} x p in {{.5,...,.95}} x Zipf s in {{0,.5,1,1.5}} x N in {{100,...,2000}}), {gr['runs_per_cell']} paired runs each. The manuscript protocol assumes an 80/20 grammar partition, but this Bernoulli engine does not represent combination identities or a split parameter; held-out-labelled trials receive 50% of compositional evaluation allocations.\n")
    L.append(f"- C2 separation (Cohen's d, compositional - memorizer): min {gr['c2_d_min']:.2f}, median {gr['c2_d_median']:.2f}; min by N: {gr['c2_d_min_by_N']}")
    L.append(f"- R separation (Cohen's d): min {gr['r_d_min']:.2f}, median {gr['r_d_median']:.2f}; min by N: {gr['r_d_min_by_N']}")
    L.append(f"- B_min non-decreasing in p in {gr['bmin_monotone_fraction']*100:.1f}% of (|Z|, s, N) series (Proposition 1)")
    L.append(f"- V_eff(.80) <= V_eff(.60) in every cell: {gr['veff_monotone_in_alpha_all']} (Proposition 2)\n")
    L.append("## Table S6. Covariation in a continuously parameterized synthetic population (1,000 agents): Spearman rho\n\n| | " + " | ".join(nr["names"]) + " |\n|---|" + "---|" * 5)
    for i, n in enumerate(nr["names"]):
        L.append(f"| {n} | " + " | ".join(f"{nr['spearman'][i][j]:.2f}" for j in range(5)) + " |")
    L.append(f"\nEigenvalues: {[round(e,3) for e in nr['eigenvalues']]}; cumulative variance: {[round(c,3) for c in nr['cumulative_variance']]}.\n")
    with open(os.path.join(OUT, "tables_S3.md"), "w") as f: f.write("\n".join(L))
    print("  -> results/tables_S3.md, results/table_S0_spec.md")


if __name__ == "__main__":
    steps = sys.argv[1:] or ["table1", "null_models", "counterexamples", "sweep_noise", "equal_mi", "nonredundancy", "grid", "tables"]
    fn = dict(table1=table1, null_models=null_models, counterexamples=counterexamples, sweep_noise=sweep_noise,
              equal_mi=equal_mi_matrices, nonredundancy=nonredundancy, grid=grid, tables=write_tables)
    for s in steps:
        fn[s]()
