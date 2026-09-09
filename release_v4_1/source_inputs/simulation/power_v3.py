"""power_v3.py - metric-specific power analysis (Section 5.7, Tables 2a-2e, Figure 5).

One parameter is perturbed per metric while every other channel is held equal.
C2 / R / U use two-sided Fisher exact tests. B_min uses a two-sample,
system-label permutation test on complete (Y, decoded-intent) records. For the
count-matrix simulation, permuted group allocations are drawn exactly from the
multivariate-hypergeometric distribution conditional on the pooled joint table.

Every table includes delta=0 as an empirical-size check. Each cell uses 1,000
Monte Carlo replications and reports a Wilson 95% interval. B_min uses 1,000
permutations per replication with the finite-permutation correction.
"""
from __future__ import annotations
import sys, os, json, math, time, multiprocessing as mp
import numpy as np
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
SEED = 42; REPS = 1000; N_PERM = 1000; K = 12; ALPHA = 0.05; TAU = 0.5; LN2 = math.log(2)


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def mi_mm_batch(cms):
    """Miller-Madow MI on observed support; no non-negativity truncation."""
    cms = np.asarray(cms, float)
    N = cms.sum(axis=(1, 2), keepdims=True)
    J = cms / N
    Py = J.sum(2, keepdims=True); Pz = J.sum(1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(J > 0, J * np.log2(J / (Py * Pz)), 0.0)
    mi = t.sum(axis=(1, 2))
    Kyz = (J > 0).sum(axis=(1, 2)); Ky = (Py[:, :, 0] > 0).sum(1); Kz = (Pz[:, 0, :] > 0).sum(1)
    return mi - (Kyz - Ky - Kz + 1) / (2 * N[:, 0, 0] * LN2)


def mi_mm(cm):
    return float(mi_mm_batch(np.asarray(cm).reshape(1, K, K))[0])


def joint_matrix(p):
    P = np.full((K, K), (1 - p) / (K - 1)); np.fill_diagonal(P, p)
    return P / K


def population_delta_bmin(dp):
    def mi_from_joint(J):
        py = J.sum(1, keepdims=True); pz = J.sum(0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            return float(np.where(J > 0, J * np.log2(J / (py * pz)), 0.0).sum())
    return (mi_from_joint(joint_matrix(0.85 + dp)) - mi_from_joint(joint_matrix(0.85))) / TAU


def _power_bmin_chunk(args):
    seed, n, dp, reps = args
    rng = np.random.default_rng(seed)
    pa = joint_matrix(0.85).ravel(); pb = joint_matrix(0.85 + dp).ravel(); sig = 0
    for _ in range(reps):
        a = rng.multinomial(n, pa).reshape(K, K)
        b = rng.multinomial(n, pb).reshape(K, K)
        observed = (mi_mm(b) - mi_mm(a)) / TAU
        pooled = (a + b).ravel().astype(np.int64)
        perm_a = rng.multivariate_hypergeometric(pooled, n, size=N_PERM).reshape(N_PERM, K, K)
        perm_b = pooled.reshape(1, K, K) - perm_a
        null = (mi_mm_batch(perm_b) - mi_mm_batch(perm_a)) / TAU
        p_value = (np.count_nonzero(np.abs(null) >= abs(observed)) + 1) / (N_PERM + 1)
        sig += p_value < ALPHA
    return sig


def power_bmin(n, dp):
    workers = max(1, min(4, (os.cpu_count() or 2) - 1))
    chunks = [REPS // workers] * workers
    for i in range(REPS % workers): chunks[i] += 1
    args = [(SEED + 90_000 + int(dp * 10_000) + n * 7 + i, n, dp, reps)
            for i, reps in enumerate(chunks)]
    if workers == 1:
        return sum(_power_bmin_chunk(a) for a in args)
    with mp.Pool(workers) as pool:
        return sum(pool.map(_power_bmin_chunk, args))


def power_prop(rng, n0, n1, p0, p1):
    sig = 0
    for _ in range(REPS):
        k0 = rng.binomial(n0, p0); k1 = rng.binomial(n1, p1)
        sig += fisher_exact([[k1, n1 - k1], [k0, n0 - k0]])[1] < ALPHA
    return sig


def cell(k): return dict(rejection_probability=round(k / REPS, 4), power=round(k / REPS, 4), ci=wilson(k, REPS))


def run_c2():
    rng = np.random.default_rng(SEED + 1); out = dict(method="two-sided Fisher exact", replications=REPS, presence={}, resolution={})
    for nU in (4, 8, 15, 38, 75, 150):
        out["presence"][str(nU)] = cell(power_prop(rng, nU, nU, 1 / K, 0.86))
        out["presence"][str(nU)]["N_default_allocation"] = round(nU / 0.075)
    for dC in (0.0, 0.05, 0.10, 0.20, 0.40):
        out["resolution"][str(dC)] = {str(nU): cell(power_prop(rng, nU, nU, 0.50, 0.50 + dC)) for nU in (15, 38, 75, 150, 400, 1600)}
        print("  C2 dC=", dC, {k: v["power"] for k, v in out["resolution"][str(dC)].items()})
    json.dump(out, open(os.path.join(OUT, "power_c2.json"), "w"), indent=1)


def run_r():
    rng = np.random.default_rng(SEED + 2); base = 1 - (1 - 1 / K) ** 2
    out = dict(method="two-sided Fisher exact", replications=REPS, baseline=base, cells={})
    for dR in (0.0, 0.05, 0.10, 0.20, 0.25):
        out["cells"][str(dR)] = {str(nR): cell(power_prop(rng, nR, nR, base, base + dR)) for nR in (20, 40, 100, 200, 400)}
        print("  R dR=", dR, {k: v["power"] for k, v in out["cells"][str(dR)].items()})
    json.dump(out, open(os.path.join(OUT, "power_r.json"), "w"), indent=1)


def run_u():
    """U = P(A|E=1)-P(A|E=0); Fisher on abstention x error table."""
    rng = np.random.default_rng(SEED + 3)
    out = dict(method="two-sided Fisher exact", replications=REPS, baseline_abstention_nonerror=0.10, cells={})
    for pi_e in (0.10, 0.20, 0.35):
        out["cells"][str(pi_e)] = {}
        for dU in (0.0, 0.10, 0.20, 0.30, 0.40):
            out["cells"][str(pi_e)][str(dU)] = {}
            for nA in (100, 200, 500, 1000):
                sig = 0; valid = 0
                for _ in range(REPS):
                    ne = rng.binomial(nA, pi_e); no = nA - ne
                    if ne == 0 or no == 0:
                        continue
                    valid += 1
                    ke = rng.binomial(ne, 0.10 + dU); ko = rng.binomial(no, 0.10)
                    sig += fisher_exact([[ke, ne - ke], [ko, no - ko]])[1] < ALPHA
                c = cell(sig)
                c["valid_replications"] = valid
                out["cells"][str(pi_e)][str(dU)][str(nA)] = c
            print(f"  U pi_e={pi_e} dU={dU}", {k: v["power"] for k, v in out["cells"][str(pi_e)][str(dU)].items()})
    json.dump(out, open(os.path.join(OUT, "power_u.json"), "w"), indent=1)


def run_bmin(dp, only_n=None):
    path = os.path.join(OUT, "power_bmin.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    out.setdefault("method", "two-sided system-label permutation conditional on pooled joint table")
    out.setdefault("replications", REPS); out.setdefault("permutations_per_replication", N_PERM)
    out.setdefault("population_delta_bmin_bpm", {})[str(dp)] = population_delta_bmin(dp)
    out.setdefault("cells", {}).setdefault(str(dp), {})
    n_values = (only_n,) if only_n is not None else (100, 200, 500, 750, 1000, 2000)
    for nS in n_values:
        t = time.time(); c = cell(power_bmin(nS, dp)); out["cells"][str(dp)][str(nS)] = c
        print(f"  B_min dp={dp} n_S={nS}: {c['power']} {c['ci']} ({time.time()-t:.0f}s)", flush=True)
        json.dump(out, open(path, "w"), indent=1)


def write_s7():
    c2 = json.load(open(os.path.join(OUT, "power_c2.json")))
    r = json.load(open(os.path.join(OUT, "power_r.json")))
    u = json.load(open(os.path.join(OUT, "power_u.json")))
    b = json.load(open(os.path.join(OUT, "power_bmin.json")))
    lines = ["# Supplementary Table S7. Metric-specific rejection probabilities with Wilson 95% intervals", "",
             f"All cells use {REPS} Monte Carlo replications. C2, R, and U use two-sided Fisher exact tests. B_min uses {N_PERM} system-label permutations per replication.", ""]
    def emit(title, grid, rows, cols):
        lines.extend([f"## {title}", "", "| effect | " + " | ".join(map(str, cols)) + " |", "|---|" + "---|" * len(cols)])
        for row in rows:
            vals=[]
            for col in cols:
                x=grid[str(row)][str(col)]
                vals.append(f"{x['power']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}]")
            label="0 (size)" if float(row)==0 else str(row)
            lines.append("| " + label + " | " + " | ".join(vals) + " |")
        lines.append("")
    emit("S7a. C2 degree comparison", c2["resolution"], [0.0,0.05,0.10,0.20,0.40], [15,38,75,150,400,1600])
    emit("S7b. Repair efficiency", r["cells"], [0.0,0.05,0.10,0.20,0.25], [20,40,100,200,400])
    emit("S7c. Uncertainty selectivity (error fraction 0.20)", u["cells"]["0.2"], [0.0,0.10,0.20,0.30,0.40], [100,200,500,1000])
    emit("S7d. Effective information rate", b["cells"], [0.0,0.01,0.03,0.05,0.10], [100,200,500,750,1000,2000])
    lines.extend(["## Population effect scale for B_min", "", "| Delta p | Delta B_min (bits/min) |", "|---:|---:|"])
    for dp, value in b["population_delta_bmin_bpm"].items():
        lines.append(f"| {float(dp):.2f} | {value:.3f} |")
    with open(os.path.join(OUT, "table_S7_power.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  -> results/table_S7_power.md")


if __name__ == "__main__":
    args = sys.argv[1:] or ["all"]
    for a in args:
        if a in ("c2", "all"): run_c2()
        if a in ("r", "all"): run_r()
        if a in ("u", "all"): run_u()
        if a.startswith("bmin-cell:"):
            _, dp, n = a.split(":"); run_bmin(float(dp), int(n))
        elif a.startswith("bmin:"):
            run_bmin(float(a.split(":")[1]))
        if a == "all":
            for dp in (0.0, 0.01, 0.03, 0.05, 0.10): run_bmin(dp)
            write_s7()
        if a == "tables":
            write_s7()
