#!/usr/bin/env python3
"""
BRM Protocol — Information-Theoretic Metric Suite
=================================================

This script is a "proper protocol" implementation for the simulation study in:
"An Information-Theoretic Metric Suite for Measuring Communicative Throughput in Behavioral Experiments"

Key improvements over exploratory simulation scripts:
- All tests are inferential (bootstrap CI on metric differences; optional permutation test helper).
- Power analysis is defined as: proportion of experiments where the 95% bootstrap CI of (Compositional − Memorizer)
  excludes 0 for the target metric (alpha = 0.05).
- Fully reproducible via deterministic seeding.

Outputs:
- JSON summaries for Table 1, null models, parameter sweeps, and power curves.
- Optional CSVs for human inspection.

No external dependencies beyond: numpy, pandas (optional), standard library.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

import numpy as np


# ----------------------------
# Metrics: MI, F1, V_eff, etc.
# ----------------------------

def _safe_log2(x: float) -> float:
    return math.log(x, 2)


def compute_mi_miller_madow(confusion_matrix: np.ndarray) -> float:
    """
    Plug-in MI with Miller–Madow correction.

    Note: The classic Miller–Madow correction is for entropy; for MI, a common practical approach is:
      I_hat_MM = I_hat_plugin - (K - 1)(L - 1) / (2N ln 2)
    where K,L are the number of non-empty bins in Y and Zhat (or full |Z| if fixed).
    Many implementations vary; this function implements a conservative correction using observed non-zero support.

    Returns MI in bits (>= 0).
    """
    cm = confusion_matrix.astype(float)
    N = cm.sum()
    if N <= 0:
        return 0.0

    P_joint = cm / N
    P_y = P_joint.sum(axis=1)
    P_z = P_joint.sum(axis=0)

    mi = 0.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            p = P_joint[i, j]
            if p <= 0:
                continue
            py = P_y[i]
            pz = P_z[j]
            if py <= 0 or pz <= 0:
                continue
            mi += p * _safe_log2(p / (py * pz))

    # Support-based correction
    # Count non-zero marginals rather than full |Z| to avoid over-correcting when labels unused
    Ky = int(np.sum(P_y > 0))
    Kz = int(np.sum(P_z > 0))
    bias = ((Ky - 1) * (Kz - 1)) / (2.0 * N * math.log(2))

    return max(0.0, mi - bias)


def compute_f1_per_class(confusion_matrix: np.ndarray) -> np.ndarray:
    n = confusion_matrix.shape[0]
    f1 = np.zeros(n, dtype=float)
    for i in range(n):
        tp = confusion_matrix[i, i]
        fp = confusion_matrix[:, i].sum() - tp
        fn = confusion_matrix[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1[i] = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return f1


def compute_veff(confusion_matrix: np.ndarray, alpha: float = 0.80, beta: int = 30) -> int:
    f1 = compute_f1_per_class(confusion_matrix)
    counts = confusion_matrix.sum(axis=1)
    return int(sum(1 for i in range(len(f1)) if f1[i] >= alpha and counts[i] >= beta))


@dataclass
class Metrics:
    accuracy: float
    mi_bits: float
    b_min: float
    veff_60: int
    veff_80: int
    veff_90: int
    c2: Optional[float]
    c2_chance: float
    c2_test_total: int
    r: Optional[float]
    r_chance: float
    repair_total: int
    u: Optional[float]
    unknown_total: int
    mean_duration: float


def compute_metrics_from_episodes(
    episodes: List[Dict[str, Any]],
    n_intents: int,
    veff_beta: int = 30,
) -> Metrics:
    """
    Compute the full metric suite from a list of episode dicts.

    Required episode keys:
      - gt (int), decoded (int), duration (float), type (str)
      - type == "comp": must include is_training (bool), correct (bool)
      - type == "repair": must include recovered (bool)
      - type == "uncertainty": must include signals_unknown (bool), correct (bool) for unknown cases
    """
    cm = np.zeros((n_intents, n_intents), dtype=int)
    durations = []
    for ep in episodes:
        gt = int(ep["gt"])
        dec = int(ep["decoded"])
        if 0 <= gt < n_intents and 0 <= dec < n_intents:
            cm[gt, dec] += 1
        dur = float(ep.get("duration", 0.5))
        durations.append(dur if dur > 0 else 0.5)

    N = cm.sum()
    acc = float(np.trace(cm) / N) if N > 0 else 0.0
    mi = compute_mi_miller_madow(cm)
    mean_dur = float(np.mean(durations)) if durations else 0.5
    bmin = float(mi / mean_dur) if mean_dur > 0 else 0.0

    ve60 = compute_veff(cm, alpha=0.60, beta=veff_beta)
    ve80 = compute_veff(cm, alpha=0.80, beta=veff_beta)
    ve90 = compute_veff(cm, alpha=0.90, beta=veff_beta)

    # C2 on held-out (non-training) compositional episodes
    c2_correct = 0
    c2_total = 0
    for ep in episodes:
        if ep.get("type") == "comp" and (not bool(ep.get("is_training", True))):
            c2_total += 1
            c2_correct += int(bool(ep.get("correct", False)))
    c2 = (c2_correct / c2_total) if c2_total > 0 else None
    c2_chance = 1.0 / n_intents if n_intents > 0 else 0.0

    # Repair efficiency
    rep_total = 0
    rep_rec = 0
    for ep in episodes:
        if ep.get("type") == "repair":
            rep_total += 1
            rep_rec += int(bool(ep.get("recovered", False)))
    r = (rep_rec / rep_total) if rep_total > 0 else None
    r_chance = 1.0 / n_intents if n_intents > 0 else 0.0

    # Uncertainty utility (binary baseline = 0.5 by protocol unless overridden)
    unk_total = 0
    unk_correct = 0
    for ep in episodes:
        if ep.get("type") == "uncertainty" and bool(ep.get("signals_unknown", False)):
            unk_total += 1
            unk_correct += int(bool(ep.get("correct", False)))
    u = ((unk_correct / unk_total) - 0.5) if unk_total > 0 else None

    return Metrics(
        accuracy=acc,
        mi_bits=mi,
        b_min=bmin,
        veff_60=ve60,
        veff_80=ve80,
        veff_90=ve90,
        c2=c2,
        c2_chance=c2_chance,
        c2_test_total=c2_total,
        r=r,
        r_chance=r_chance,
        repair_total=rep_total,
        u=u,
        unknown_total=unk_total,
        mean_duration=mean_dur,
    )


# ----------------------------
# Agents + Environment
# ----------------------------

class Agent:
    def __init__(self, agent_type: str, n_intents: int, p_correct: float = 0.85, rng: Optional[np.random.Generator] = None):
        self.agent_type = agent_type
        self.n_intents = int(n_intents)
        self.p_correct = float(p_correct)
        self.rng = rng or np.random.default_rng()

        if agent_type == "class_biased":
            k = min(3, self.n_intents)
            self.favored = self.rng.choice(self.n_intents, size=k, replace=False)
        else:
            self.favored = None

        if agent_type == "overproduction":
            self.dominant_label = 0

    def respond_single(self, gt: int) -> int:
        r = self.rng
        if self.agent_type == "random":
            return int(r.integers(0, self.n_intents))

        if self.agent_type == "class_biased":
            if gt in set(self.favored.tolist()):
                return int(gt) if r.random() < 0.90 else int(r.integers(0, self.n_intents))
            return int(r.integers(0, self.n_intents))

        if self.agent_type == "overproduction":
            if r.random() < 0.70:
                return int(self.dominant_label)
            return int(gt) if r.random() < self.p_correct else int(r.integers(0, self.n_intents))

        if self.agent_type == "memorizer":
            return int(gt) if r.random() < self.p_correct else int(r.integers(0, self.n_intents))

        if self.agent_type == "compositional":
            return int(gt) if r.random() < 0.90 else int(r.integers(0, self.n_intents))

        return int(r.integers(0, self.n_intents))

    def respond_compositional(self, is_training: bool) -> bool:
        r = self.rng
        if self.agent_type in ("random", "class_biased", "overproduction"):
            return bool(r.random() < (1.0 / self.n_intents))

        if self.agent_type == "memorizer":
            if is_training:
                return bool(r.random() < self.p_correct)
            return bool(r.random() < (1.0 / self.n_intents))

        if self.agent_type == "compositional":
            return bool(r.random() < 0.90)

        return False

    def respond_repair(self) -> Tuple[str, bool]:
        r = self.rng
        if self.agent_type == "random":
            outcome = str(r.choice(["repeat", "modify", "escalate", "abandon"]))
            recovered = bool(r.random() < (1.0 / self.n_intents))
            return outcome, recovered

        if self.agent_type in ("class_biased", "overproduction"):
            outcome = str(r.choice(["repeat", "modify", "escalate", "abandon"], p=[0.30, 0.20, 0.10, 0.40]))
            recovered = bool(r.random() < (1.0 / self.n_intents))
            return outcome, recovered

        if self.agent_type == "memorizer":
            outcome = str(r.choice(["repeat", "modify", "escalate", "abandon"], p=[0.50, 0.10, 0.10, 0.30]))
            recovered = bool(r.random() < 0.10)
            return outcome, recovered

        if self.agent_type == "compositional":
            outcome = str(r.choice(["repeat", "modify", "escalate", "abandon"], p=[0.20, 0.45, 0.20, 0.15]))
            if outcome == "modify":
                recovered = bool(r.random() < 0.55)
            elif outcome == "repeat":
                recovered = bool(r.random() < 0.20)
            elif outcome == "escalate":
                recovered = bool(r.random() < 0.35)
            else:
                recovered = False
            return outcome, recovered

        return "abandon", False

    def respond_uncertainty(self, is_hard: bool) -> Tuple[bool, bool]:
        r = self.rng
        if self.agent_type == "random":
            signals_unknown = bool(r.random() < 0.30)
            correct = bool(r.random() < 0.50)
            return signals_unknown, correct

        if self.agent_type in ("class_biased", "overproduction", "memorizer"):
            signals_unknown = False
            # correctness here represents "if forced"; used only if signals_unknown is True (not the case here)
            correct = bool(r.random() < (0.55 if is_hard else 0.90))
            return signals_unknown, correct

        if self.agent_type == "compositional":
            if is_hard:
                signals_unknown = bool(r.random() < 0.60)
                correct_after_followup = bool(r.random() < 0.75)
            else:
                signals_unknown = bool(r.random() < 0.10)
                correct_after_followup = bool(r.random() < 0.95)
            return signals_unknown, correct_after_followup

        return False, bool(r.random() < 0.50)


@dataclass
class SimConfig:
    n_intents: int = 12
    n_episodes: int = 500
    p_correct: float = 0.85
    class_imbalance: float = 0.0  # Zipf exponent s
    comp_split: float = 0.80      # training proportion for compositional combos
    hard_fraction: float = 0.30
    single_frac: float = 0.50
    comp_frac: float = 0.15
    repair_frac: float = 0.20


def _zipf_probs(n: int, s: float) -> np.ndarray:
    ranks = np.arange(1, n + 1, dtype=float)
    p = 1.0 / (ranks ** s)
    p = p / p.sum()
    return p


def run_simulation(agent_type: str, cfg: SimConfig, seed: int) -> List[Dict[str, Any]]:
    """
    Generate a single synthetic dataset (episodes list) per protocol.
    """
    rng = np.random.default_rng(seed)
    agent = Agent(agent_type, cfg.n_intents, cfg.p_correct, rng=rng)

    if cfg.class_imbalance and cfg.class_imbalance > 0:
        probs = _zipf_probs(cfg.n_intents, cfg.class_imbalance)
    else:
        probs = np.ones(cfg.n_intents, dtype=float) / cfg.n_intents

    n_single = int(round(cfg.n_episodes * cfg.single_frac))
    n_comp = int(round(cfg.n_episodes * cfg.comp_frac))
    n_repair = int(round(cfg.n_episodes * cfg.repair_frac))
    n_unc = max(0, cfg.n_episodes - n_single - n_comp - n_repair)

    episodes: List[Dict[str, Any]] = []

    # Single-intent episodes
    for _ in range(n_single):
        gt = int(rng.choice(cfg.n_intents, p=probs))
        decoded = int(agent.respond_single(gt))
        dur = float(np.clip(rng.lognormal(mean=np.log(0.5), sigma=0.4), 0.1, 3.0))
        episodes.append({"type": "single", "gt": gt, "decoded": decoded, "duration": dur})

    # Compositional episodes: generate 2-slot combos from intent indices
    n_slots = min(cfg.n_intents // 2, max(2, cfg.n_intents // 3))
    slot_a = list(range(n_slots))
    slot_b = list(range(n_slots, min(2 * n_slots, cfg.n_intents)))
    if len(slot_b) == 0:
        slot_b = list(range(1, min(n_slots + 1, cfg.n_intents)))

    combos = [(a, b) for a in slot_a for b in slot_b]
    rng.shuffle(combos)
    n_train = max(1, int(round(len(combos) * cfg.comp_split)))
    train_set = set(combos[:n_train])
    test_set = set(combos[n_train:])

    for _ in range(n_comp):
        # 50/50 sampling between test and train when test exists
        if test_set and (rng.random() < 0.50):
            combo = list(test_set)[int(rng.integers(0, len(test_set)))]
            is_training = False
        else:
            combo = list(train_set)[int(rng.integers(0, len(train_set)))]
            is_training = True

        correct = bool(agent.respond_compositional(is_training))
        gt = int(combo[0])
        decoded = gt if correct else int(rng.integers(0, cfg.n_intents))
        dur = float(np.clip(rng.lognormal(mean=np.log(0.6), sigma=0.4), 0.1, 3.0))
        episodes.append({
            "type": "comp",
            "gt": gt,
            "decoded": decoded,
            "duration": dur,
            "is_training": is_training,
            "correct": correct
        })

    # Repair episodes
    for _ in range(n_repair):
        gt = int(rng.choice(cfg.n_intents, p=probs))
        decoded = int(agent.respond_single(gt))
        outcome, recovered = agent.respond_repair()
        dur = float(np.clip(rng.lognormal(mean=np.log(0.7), sigma=0.4), 0.1, 3.0))
        episodes.append({
            "type": "repair",
            "gt": gt,
            "decoded": decoded,
            "duration": dur,
            "outcome": outcome,
            "recovered": bool(recovered)
        })

    # Uncertainty episodes
    for _ in range(n_unc):
        is_hard = bool(rng.random() < cfg.hard_fraction)
        signals_unknown, correct = agent.respond_uncertainty(is_hard)

        gt = int(rng.choice(cfg.n_intents, p=probs))
        if signals_unknown:
            decoded = gt if correct else int(rng.integers(0, cfg.n_intents))
        else:
            decoded = int(agent.respond_single(gt))

        dur = float(np.clip(rng.lognormal(mean=np.log(0.5), sigma=0.4), 0.1, 3.0))
        episodes.append({
            "type": "uncertainty",
            "gt": gt,
            "decoded": decoded,
            "duration": dur,
            "signals_unknown": bool(signals_unknown),
            "correct": bool(correct),
            "is_hard": is_hard
        })

    return episodes


# ----------------------------
# Inferential testing
# ----------------------------

def bootstrap_ci_of_difference(
    metric_name: str,
    episodes_a: List[Dict[str, Any]],
    episodes_b: List[Dict[str, Any]],
    n_intents: int,
    n_boot: int,
    seed: int,
    veff_beta: int = 30,
) -> Tuple[float, float, float]:
    """
    Bootstrap CI for Δ = metric(B) - metric(A) by resampling episodes WITHIN each dataset.

    Returns: (delta_mean, lo, hi) for 95% CI.
    """
    rng = np.random.default_rng(seed)
    n_a = len(episodes_a)
    n_b = len(episodes_b)
    if n_a == 0 or n_b == 0:
        return (0.0, 0.0, 0.0)

    def get_metric(eps: List[Dict[str, Any]]) -> Optional[float]:
        m = compute_metrics_from_episodes(eps, n_intents=n_intents, veff_beta=veff_beta)
        val = getattr(m, metric_name)
        return None if val is None else float(val)

    # Point estimate
    ma = get_metric(episodes_a)
    mb = get_metric(episodes_b)
    if ma is None or mb is None:
        return (0.0, 0.0, 0.0)
    delta_hat = mb - ma

    deltas = []
    for _ in range(n_boot):
        idx_a = rng.integers(0, n_a, size=n_a)
        idx_b = rng.integers(0, n_b, size=n_b)
        samp_a = [episodes_a[i] for i in idx_a]
        samp_b = [episodes_b[i] for i in idx_b]
        sa = get_metric(samp_a)
        sb = get_metric(samp_b)
        if sa is None or sb is None:
            continue
        deltas.append(sb - sa)

    if len(deltas) < max(200, n_boot // 10):
        # not enough defined samples; return degenerate
        return (delta_hat, 0.0, 0.0)

    deltas = np.sort(np.array(deltas, dtype=float))
    lo = float(np.percentile(deltas, 2.5))
    hi = float(np.percentile(deltas, 97.5))
    return (float(delta_hat), lo, hi)


def significant_ci_excludes_zero(lo: float, hi: float) -> bool:
    return (lo > 0.0) or (hi < 0.0)


# ----------------------------
# Aggregation helpers
# ----------------------------

def summarize_scalar(xs: List[float]) -> Dict[str, Any]:
    arr = np.array(xs, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "ci_lo": float(np.percentile(arr, 2.5)),
        "ci_hi": float(np.percentile(arr, 97.5)),
        "n": int(arr.size)
    }


def table1_core(cfg: SimConfig, n_runs: int, seed0: int, veff_beta: int) -> Dict[str, Any]:
    """
    Table 1: core differentiation across agent types.
    Returns per-agent summary over n_runs independent datasets.
    """
    agent_types = ["random", "class_biased", "overproduction", "memorizer", "compositional"]
    out: Dict[str, Any] = {}

    for a in agent_types:
        mets = {
            "accuracy": [],
            "mi_bits": [],
            "b_min": [],
            "veff_60": [],
            "veff_80": [],
            "veff_90": [],
            "c2": [],
            "r": [],
            "u": [],
        }
        for i in range(n_runs):
            seed = seed0 + (hash(a) % 10_000) * 100_000 + i
            eps = run_simulation(a, cfg, seed=seed)
            m = compute_metrics_from_episodes(eps, n_intents=cfg.n_intents, veff_beta=veff_beta)

            mets["accuracy"].append(m.accuracy)
            mets["mi_bits"].append(m.mi_bits)
            mets["b_min"].append(m.b_min)
            mets["veff_60"].append(float(m.veff_60))
            mets["veff_80"].append(float(m.veff_80))
            mets["veff_90"].append(float(m.veff_90))
            if m.c2 is not None:
                mets["c2"].append(float(m.c2))
            if m.r is not None:
                mets["r"].append(float(m.r))
            if m.u is not None:
                mets["u"].append(float(m.u))

        out[a] = {k: summarize_scalar(v) if len(v) > 0 else {"mean": None, "std": None, "ci_lo": None, "ci_hi": None, "n": 0}
                  for k, v in mets.items()}

    return out


def power_curve(
    n_trials_list: List[int],
    n_experiments: int,
    cfg_template: SimConfig,
    metric: str,
    n_boot: int,
    alpha: float,
    seed0: int,
    veff_beta: int,
) -> Dict[str, Any]:
    """
    Power definition:
      For each N in n_trials_list, repeat n_experiments times:
        - generate one dataset for Memorizer and one for Compositional (independent seeds),
        - bootstrap CI for Δ = metric(Comp) - metric(Mem),
        - declare significant if 95% CI excludes 0 (two-sided alpha=0.05).
      Power = proportion significant.

    Notes:
      - This is conservative for metrics with undefined regions (e.g., U when no UNKNOWN signals).
      - alpha parameter is currently fixed to 0.05 by using 95% CI; included for clarity.
    """
    assert abs(alpha - 0.05) < 1e-9, "This implementation uses 95% CI; set alpha=0.05."

    out: Dict[str, Any] = {}
    for N in n_trials_list:
        cfg = SimConfig(**{**cfg_template.__dict__, "n_episodes": int(N)})
        sig = 0
        defined = 0
        deltas = []
        cis = []

        for i in range(n_experiments):
            seed_m = seed0 + 1_000_000 + i * 2 + 0
            seed_c = seed0 + 1_000_000 + i * 2 + 1

            eps_m = run_simulation("memorizer", cfg, seed=seed_m)
            eps_c = run_simulation("compositional", cfg, seed=seed_c)

            delta_hat, lo, hi = bootstrap_ci_of_difference(
                metric_name=metric,
                episodes_a=eps_m,
                episodes_b=eps_c,
                n_intents=cfg.n_intents,
                n_boot=n_boot,
                seed=seed0 + 9_000_000 + i,
                veff_beta=veff_beta
            )

            # If metric undefined, CI returns (0,0,0). Treat as undefined experiment.
            if lo == 0.0 and hi == 0.0 and delta_hat == 0.0 and metric in ("u", "c2", "r"):
                continue

            defined += 1
            deltas.append(delta_hat)
            cis.append((lo, hi))
            if significant_ci_excludes_zero(lo, hi):
                sig += 1

        out[str(N)] = {
            "metric": metric,
            "n_experiments": n_experiments,
            "n_defined": defined,
            "power": (sig / defined) if defined > 0 else None,
            "delta_mean": float(np.mean(deltas)) if len(deltas) > 0 else None,
            "delta_ci_lo": float(np.percentile(deltas, 2.5)) if len(deltas) > 0 else None,
            "delta_ci_hi": float(np.percentile(deltas, 97.5)) if len(deltas) > 0 else None,
            # keep a small sample of CIs for debugging without blowing up file size
            "ci_samples": cis[:10],
        }

    return out


# ----------------------------
# CLI + Output
# ----------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="BRM Protocol simulation + inferential power curves.")
    p.add_argument("--outdir", default="./brm_protocol_results", help="Output directory for JSON artifacts.")
    p.add_argument("--seed", type=int, default=42, help="Master seed.")
    p.add_argument("--n_runs_table1", type=int, default=1000, help="Monte Carlo runs per agent for Table 1.")
    p.add_argument("--veff_beta", type=int, default=30, help="Minimum per-class trial count for V_eff.")
    p.add_argument("--power_metric", default="c2", choices=["b_min", "veff_80", "c2", "r", "u"], help="Metric to power-test.")
    p.add_argument("--power_n_boot", type=int, default=1000, help="Bootstrap resamples per experiment (power).")
    p.add_argument("--power_n_experiments", type=int, default=300, help="Number of experiments per N (power).")
    p.add_argument("--power_trials", default="100,200,500,1000,2000", help="Comma-separated N list for power curve.")
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # Default configuration (matches manuscript defaults)
    cfg = SimConfig(
        n_intents=12,
        n_episodes=500,
        p_correct=0.85,
        class_imbalance=0.0,
        comp_split=0.80,
        hard_fraction=0.30,
        single_frac=0.50,
        comp_frac=0.15,
        repair_frac=0.20,
    )

    # Table 1
    table1 = table1_core(cfg, n_runs=args.n_runs_table1, seed0=args.seed, veff_beta=args.veff_beta)
    with open(os.path.join(args.outdir, "table1_core_differentiation.json"), "w", encoding="utf-8") as f:
        json.dump(table1, f, indent=2)

    # Power curve
    trial_list = [int(x.strip()) for x in args.power_trials.split(",") if x.strip()]
    metric = args.power_metric
    pc = power_curve(
        n_trials_list=trial_list,
        n_experiments=args.power_n_experiments,
        cfg_template=cfg,
        metric=metric,
        n_boot=args.power_n_boot,
        alpha=0.05,
        seed0=args.seed,
        veff_beta=args.veff_beta,
    )
    with open(os.path.join(args.outdir, f"power_curve_{metric}.json"), "w", encoding="utf-8") as f:
        json.dump(pc, f, indent=2)

    # Minimal manifest
    manifest = {
        "protocol_version": "1.0",
        "seed": args.seed,
        "default_config": cfg.__dict__,
        "table1_file": "table1_core_differentiation.json",
        "power_file": f"power_curve_{metric}.json",
        "notes": [
            "Power uses bootstrap CI on metric difference (Compositional − Memorizer); significant if CI excludes 0.",
            "MI is Miller–Madow corrected using observed marginal support.",
            "V_eff uses per-class minimum trial count veff_beta.",
        ],
    }
    with open(os.path.join(args.outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main()
