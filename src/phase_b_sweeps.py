#!/usr/bin/env python3
"""Build 2 Phase B: Noise sweep + Matched-accuracy C2 sweep.
Reuses engine definitions from phase_a.py via import."""
import sys, os, json, time
from dataclasses import asdict
from phase_a import (SimConfig, run_batch, summarize, _sf, JSONDIR,
                      compute_metrics, run_sim, SEED_OFFSETS)

def _save(d, name):
    p = os.path.join(JSONDIR, name)
    with open(p, "w") as f:
        json.dump(d, f, indent=2, default=str)
    sz = os.path.getsize(p)
    print(f"    -> {name} ({sz:,} bytes)")

def main():
    s0 = 42; vb = 30; n_sweep = 250; n_matched = 300
    cfg = SimConfig()
    print("=" * 60)
    print("BUILD 2 PHASE B: Sweeps + Matched C2")
    print("=" * 60)
    t0 = time.time()

    print(f"\n[NOISE SWEEP] {n_sweep} runs x 6 p-values x 2 agents")
    sweep_n = {}
    for p in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
        pcc = min(p + 0.05, 0.99)
        c = SimConfig(**{**asdict(cfg), "p_correct": p, "p_correct_comp": pcc})
        mem = run_batch("memorizer", c, s0, n_sweep, vb)
        comp = run_batch("compositional", c, s0, n_sweep, vb)
        sweep_n[str(p)] = {"memorizer": mem, "compositional": comp,
                           "p_mem": p, "p_comp": pcc}
        print(f"  p={p:.2f}: mem B={mem['b_min_support']['mean']:.3f} "
              f"C2={mem['c2']['mean']!s:8s} | "
              f"comp B={comp['b_min_support']['mean']:.3f} "
              f"C2={comp['c2']['mean']!s:8s}")
    _save(sweep_n, "sweep_noise.json")

    print(f"\n[MATCHED-ACCURACY C2] {n_matched} runs x 6 p-values x 2 agents")
    print("  Design: identical p_correct on single + training. Only held-out differs.")
    matched = {}
    for p in [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]:
        c = SimConfig(**{**asdict(cfg), "p_correct": p, "p_correct_comp": p})
        mem = run_batch("matched_mem", c, s0, n_matched, vb)
        comp = run_batch("matched_comp", c, s0, n_matched, vb)
        acc_m = mem["accuracy"]["mean"]
        acc_c = comp["accuracy"]["mean"]
        acc_diff = abs(acc_m - acc_c) if acc_m and acc_c else 999
        c2_m = mem["c2"]["mean"]
        c2_c = comp["c2"]["mean"]
        c2_gap = (c2_c or 0) - (c2_m or 0)
        matched[str(p)] = {
            "matched_mem": mem, "matched_comp": comp,
            "accuracy_mem": acc_m, "accuracy_comp": acc_c,
            "accuracy_diff": round(acc_diff, 5),
            "accuracy_matched": acc_diff < 0.02,
            "c2_mem": c2_m, "c2_comp": c2_c,
            "c2_gap": round(c2_gap, 4),
            "c2_diverges": c2_gap > 0.20,
        }
        status = "MATCHED" if acc_diff < 0.02 else "WARN"
        print(f"  p={p:.2f}: acc_mem={acc_m:.4f} acc_comp={acc_c:.4f} "
              f"diff={acc_diff:.4f} [{status}] | "
              f"C2_mem={c2_m!s:8s} C2_comp={c2_c!s:8s} gap={c2_gap:.3f}")
    _save(matched, "matched_c2.json")

    elapsed = time.time() - t0
    print(f"\nPHASE B COMPLETE in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    all_files = sorted(os.listdir(JSONDIR))
    print(f"All JSON files: {all_files}")
    for f in all_files:
        fp = os.path.join(JSONDIR, f)
        print(f"  {f}: {os.path.getsize(fp):,} bytes")

if __name__ == "__main__":
    main()
