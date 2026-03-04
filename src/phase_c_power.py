#!/usr/bin/env python3
"""Build 2 Phase C: Power analysis for C2, R, and B_min metrics."""
import sys, os, json, time
import numpy as np
from dataclasses import asdict
from phase_a import SimConfig, compute_metrics, run_sim, JSONDIR

def run_power(metric, s0=42, vb=30, NE=20, NB=50):
    NVS = [100, 200, 500, 1000, 2000]
    DPS = [0.01, 0.03, 0.05, 0.10]
    cfg = SimConfig()
    t0 = time.time()
    R = {}
    print(f"PHASE C: Power for {metric}")
    for dp in DPS:
        R[str(dp)] = {}
        for N in NVS:
            tc = time.time()
            pm = 0.85; pc = min(pm + dp, 0.99)
            c = SimConfig(**{**asdict(cfg), "n_episodes": N, "p_correct": pm, "p_correct_comp": pc})
            sig = 0; defi = 0; dts = []
            for ei in range(NE):
                em = run_sim("memorizer", c, s0 + 2000000 + ei * 2)
                ec = run_sim("compositional", c, s0 + 2000000 + ei * 2 + 1)
                mm = compute_metrics(em, cfg.n_intents, vb)
                mc = compute_metrics(ec, cfg.n_intents, vb)
                vm = getattr(mm, metric); vc = getattr(mc, metric)
                if vm is None or vc is None: continue
                dh = float(vc) - float(vm); defi += 1; dts.append(dh)
                br = np.random.default_rng(s0 + 5000000 + ei)
                nm = len(em); nc = len(ec); bd = []
                for _ in range(NB):
                    im = br.integers(0, nm, size=nm); ic = br.integers(0, nc, size=nc)
                    bm = compute_metrics([em[j] for j in im], cfg.n_intents, vb)
                    bc = compute_metrics([ec[j] for j in ic], cfg.n_intents, vb)
                    bvm = getattr(bm, metric); bvc = getattr(bc, metric)
                    if bvm is not None and bvc is not None: bd.append(float(bvc) - float(bvm))
                if len(bd) < 15: continue
                lo = float(np.percentile(bd, 2.5)); hi = float(np.percentile(bd, 97.5))
                if lo > 0 or hi < 0: sig += 1
            pw = sig / defi if defi > 0 else None
            dm = float(np.mean(dts)) if dts else None
            R[str(dp)][str(N)] = {
                "power": round(pw, 4) if pw is not None else None,
                "n_def": defi, "n_sig": sig,
                "delta": round(dm, 6) if dm is not None else None,
            }
            ps = str(round(pw, 2)) if pw is not None else "NA"
            ds = str(round(dm, 4)) if dm is not None else "NA"
            print(f"  dp={dp} N={N} pw={ps} ({sig}/{defi}) d={ds} [{round(time.time() - tc, 1)}s]")
    print(f"  {metric} done in {round(time.time() - t0)}s")
    return R

def main():
    results = {}
    for metric in ["c2", "r", "b_min_support"]:
        results[metric] = run_power(metric)
    p = os.path.join(JSONDIR, "power_analysis.json")
    with open(p, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n-> power_analysis.json ({os.path.getsize(p):,} bytes)")

if __name__ == "__main__":
    main()
