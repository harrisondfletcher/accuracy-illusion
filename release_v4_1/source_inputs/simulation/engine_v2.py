"""engine_v2.py - four-channel simulation engine for The Accuracy Illusion (revision).

Measurement architecture (Section 2.7 of the manuscript):
    base single-intent trials      -> B_min, V_eff   (confusion matrix)
    held-out compositional trials  -> C_k
    induced-error trials           -> R
    uncertainty trials             -> U (abstention selectivity, Eq. 6)

Every agent is fully described by a row of AGENT_SPEC. Manuscript Table S0 is
generated from that dict, so text, code, and tables share one specification.

Conventions:
    Single-intent response rule: correct with probability p, otherwise a
    uniform draw over the K-1 incorrect intents, so P(correct) = p exactly.
    Mutual information is Miller-Madow corrected on observed support,
        I_MM = I_plugin - (K_YZ - K_Y - K_Z + 1) / (2 N ln 2),
    and is NOT truncated at zero.
    Repair chance baseline for two independent guesses: 1 - (1 - 1/K)^2.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field, asdict
from typing import Optional
import numpy as np
from scipy.stats import beta as beta_dist

LN2 = math.log(2.0)


def repair_chance(K: int, n_turns: int = 2) -> float:
    return 1.0 - (1.0 - 1.0 / K) ** n_turns


AGENT_SPEC = {
    "random": dict(
        p_single=None, p_train=None, p_heldout=None,
        repair_policy=(0.25, 0.25, 0.25, 0.25), repair_recovery=None,
        abstain_hard=0.30, abstain_easy=0.30, err_hard=0.50, err_easy=0.50,
        favored="none", dominant=False,
        description="Uniform response on every channel; abstains at a fixed 0.30 independent of error risk."),
    "class_biased": dict(
        p_single=0.90, p_train=None, p_heldout=None,
        repair_policy=(0.30, 0.20, 0.10, 0.40), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="top3", dominant=False,
        description="Correct with p=0.90 on the three most frequent intents under P(Y); uniform otherwise. Never abstains."),
    "overproduction": dict(
        p_single=0.85, p_train=None, p_heldout=None,
        repair_policy=(0.30, 0.20, 0.10, 0.40), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="none", dominant=True,
        description="Emits the most frequent intent on 70% of trials; otherwise correct with p=0.85. Never abstains."),
    "memorizer": dict(
        p_single=0.85, p_train=0.85, p_heldout=None,
        repair_policy=(1.0, 0.0, 0.0, 0.0), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="none", dominant=False,
        description="p=0.85 on single-intent and training combinations; chance on held-out; repeats without modification after induced error; never abstains."),
    "compositional": dict(
        p_single=0.85, p_train=0.85, p_heldout=0.85,
        repair_policy=(0.20, 0.45, 0.20, 0.15),
        repair_recovery=dict(repeat=None, modify=0.55, escalate=0.35, abandon=0.0),
        abstain_hard=0.60, abstain_easy=0.10, err_hard=0.25, err_easy=0.05,
        favored="none", dominant=False,
        description="p=0.85 on single-intent, training, and held-out combinations; modifies signal after induced error; abstains selectively (0.60 on hard, 0.10 on easy trials)."),
    "ce1": dict(
        p_single=0.90, p_train=0.90, p_heldout=None,
        repair_policy=(1.0, 0.0, 0.0, 0.0), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="none", dominant=False,
        description="Counterexample 1: high MI, chance C2."),
    "ce2": dict(
        p_single=0.90, p_train=0.90, p_heldout=0.85,
        repair_policy=(1.0, 0.0, 0.0, 0.0), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="none", dominant=False,
        description="Counterexample 2: high MI, high C2, R at the simulation null."),
    "strategic_random": dict(
        p_single=0.70, p_train=0.70, p_heldout=None,
        repair_policy=(0.30, 0.20, 0.10, 0.40), repair_recovery=None,
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="neighbor", dominant=False,
        description="Correct with p=0.70; every error is a cyclic-neighbor intent (index +/-1), so errors are structured rather than uniform."),
    "ce3": dict(
        p_single=0.90, p_train=0.90, p_heldout=0.85,
        repair_policy=(0.20, 0.45, 0.20, 0.15),
        repair_recovery=dict(repeat=None, modify=0.55, escalate=0.35, abandon=0.0),
        abstain_hard=0.0, abstain_easy=0.0, err_hard=0.45, err_easy=0.10,
        favored="none", dominant=False,
        description="Counterexample 3: high MI, high C2, high R, U = 0 (never abstains)."),
}

REPAIR_OUTCOMES = ("repeat", "modify", "escalate", "abandon")


@dataclass
class SimConfig:
    K: int = 12
    N: int = 1000
    zipf_s: float = 0.0
    heldout_eval_frac: float = 0.50
    frac_single: float = 0.50
    frac_comp: float = 0.15
    frac_repair: float = 0.20
    frac_unc: float = 0.15
    hard_fraction: float = 0.30
    overproduction_rate: float = 0.70
    veff_beta: int = 30
    n_base_override: Optional[int] = None

    def allocation(self):
        n_s = self.n_base_override if self.n_base_override is not None else int(round(self.N * self.frac_single))
        n_c = int(round(self.N * self.frac_comp))
        n_r = int(round(self.N * self.frac_repair))
        n_a = self.N - n_s - n_c - n_r
        if min(n_s, n_c, n_r, n_a) < 0:
            raise ValueError(f"Invalid channel allocation: N={self.N}, counts={(n_s, n_c, n_r, n_a)}")
        if not 0.0 <= self.heldout_eval_frac <= 1.0:
            raise ValueError("heldout_eval_frac must lie in [0, 1]")
        return n_s, n_c, n_r, n_a


def zipf(K: int, s: float) -> np.ndarray:
    if s <= 0:
        return np.ones(K) / K
    w = 1.0 / np.arange(1, K + 1, dtype=float) ** s
    return w / w.sum()


def mi_plugin_and_mm(cm: np.ndarray):
    """Return (plug-in MI, Miller-Madow corrected MI on observed support, N)."""
    cm = np.asarray(cm, float)
    N = cm.sum()
    if N <= 0:
        return 0.0, 0.0, 0
    J = cm / N
    Py = J.sum(1, keepdims=True)
    Pz = J.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(J > 0, J * np.log2(J / (Py * Pz)), 0.0)
    mi = float(t.sum())
    Kyz = int((J > 0).sum()); Ky = int((Py > 0).sum()); Kz = int((Pz > 0).sum())
    corr = (Kyz - Ky - Kz + 1) / (2.0 * N * LN2)
    return mi, mi - corr, int(N)


def f1_per_class(cm: np.ndarray) -> np.ndarray:
    cm = np.asarray(cm, float)
    tp = np.diag(cm); fp = cm.sum(0) - tp; fn = cm.sum(1) - tp
    with np.errstate(divide="ignore", invalid="ignore"):
        pr = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        rc = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f1 = np.where(pr + rc > 0, 2 * pr * rc / (pr + rc), 0.0)
    return f1


def veff(cm: np.ndarray, alpha: float, beta: int) -> int:
    f1 = f1_per_class(cm); n = np.asarray(cm).sum(1)
    return int(np.sum((f1 >= alpha) & (n >= beta)))


def clopper_pearson(k: int, n: int, a: float = 0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    lo = beta_dist.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta_dist.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return float(lo), float(hi)


def u_selectivity(abstain: np.ndarray, err: np.ndarray):
    """Eq. 6. Returns (U, tpr, fpr, n_err, n_ok); U is nan when a stratum is empty."""
    a = np.asarray(abstain, bool); e = np.asarray(err, bool)
    n_err = int(e.sum()); n_ok = int((~e).sum())
    if n_err == 0 or n_ok == 0:
        return float("nan"), float("nan"), float("nan"), n_err, n_ok
    tpr = float(a[e].mean()); fpr = float(a[~e].mean())
    return tpr - fpr, tpr, fpr, n_err, n_ok


@dataclass
class Result:
    accuracy_base: float
    accuracy_pooled: float
    mi_plugin: float
    mi: float
    tau_min: float
    b_min: float
    veff: dict
    c2: float
    c2_ci: tuple
    c2_n: int
    c2_chance: float
    r: float
    r_n: int
    r_chance: float
    repair_dist: dict
    u: float
    u_tpr: float
    u_fpr: float
    u_n_err: int
    u_n_ok: int
    abstain_rate: float
    n_alloc: tuple


def _single_responses(rng, gt, K, spec, P_Y, cfg):
    n = len(gt)
    fav = spec["favored"]; p = spec["p_single"]
    if p is None:
        return rng.integers(0, K, n)
    if fav == "top3":
        favored = np.argsort(-P_Y)[:3]
        is_fav = np.isin(gt, favored)
        correct = (rng.random(n) < p) & is_fav
        wrong_uniform_all = rng.integers(0, K, n)
        wrong_other = (gt + rng.integers(1, K, n)) % K
        out = np.where(is_fav, np.where(correct, gt, wrong_other), wrong_uniform_all)
        return out
    correct = rng.random(n) < p
    if fav == "neighbor":
        step = np.where(rng.random(n) < 0.5, 1, K - 1)
        wrong_other = (gt + step) % K
    else:
        wrong_other = (gt + rng.integers(1, K, n)) % K
    out = np.where(correct, gt, wrong_other)
    if spec["dominant"]:
        dom = int(np.argmax(P_Y))
        use_dom = rng.random(n) < cfg.overproduction_rate
        out = np.where(use_dom, dom, out)
    return out


def make_spec(base: str, **overrides) -> dict:
    spec = dict(AGENT_SPEC[base]); spec.update(overrides); return spec


def run_sim(agent, cfg: SimConfig, seed: int) -> Result:
    rng = np.random.default_rng(seed)
    spec = AGENT_SPEC[agent] if isinstance(agent, str) else agent
    K = cfg.K
    P_Y = zipf(K, cfg.zipf_s)
    n_s, n_c, n_r, n_a = cfg.allocation()

    gt = rng.choice(K, size=n_s, p=P_Y)
    dec = _single_responses(rng, gt, K, spec, P_Y, cfg)
    cm = np.zeros((K, K), int)
    np.add.at(cm, (gt, dec), 1)
    durations = np.clip(rng.lognormal(np.log(0.5), 0.4, n_s), 0.05, 3.0)
    tau = float(durations.mean())
    mi_plug, mi_mm, _ = mi_plugin_and_mm(cm)
    acc_base = float(np.trace(cm) / n_s)
    ve = {a: veff(cm, a, cfg.veff_beta) for a in (0.60, 0.70, 0.80, 0.90)}

    # The engine labels compositional evaluation trials as training or held-out.
    # It does not represent individual combination identities or a grammar-split
    # parameter. heldout_eval_frac controls only the evaluation allocation.
    is_heldout = rng.random(n_c) < cfg.heldout_eval_frac
    chance = 1.0 / K
    p_tr = spec["p_train"] if spec["p_train"] is not None else chance
    p_ho = spec["p_heldout"] if spec["p_heldout"] is not None else chance
    comp_correct = rng.random(n_c) < np.where(is_heldout, p_ho, p_tr)
    c2_n = int(is_heldout.sum()); c2_k = int(comp_correct[is_heldout].sum())
    c2 = c2_k / c2_n if c2_n else float("nan")

    pol = np.array(spec["repair_policy"], float); pol = pol / pol.sum()
    outcomes = rng.choice(4, size=n_r, p=pol)
    base_rec = repair_chance(K, 2)
    rec_map = spec["repair_recovery"]
    if rec_map is None:
        rec_p = np.full(n_r, base_rec)
    else:
        table = np.array([base_rec if rec_map.get(o) is None else rec_map[o] for o in REPAIR_OUTCOMES])
        rec_p = table[outcomes]
    recovered = rng.random(n_r) < rec_p
    r_val = float(recovered.mean()) if n_r else float("nan")
    rdist = {o: float((outcomes == i).mean()) if n_r else float("nan") for i, o in enumerate(REPAIR_OUTCOMES)}

    hard = rng.random(n_a) < cfg.hard_fraction
    abstain = rng.random(n_a) < np.where(hard, spec["abstain_hard"], spec["abstain_easy"])
    err = rng.random(n_a) < np.where(hard, spec["err_hard"], spec["err_easy"])
    u, tpr, fpr, n_err, n_ok = u_selectivity(abstain, err) if n_a else (float("nan"),) * 3 + (0, 0)

    acc_pooled = float((np.trace(cm) + comp_correct.sum()) / (n_s + n_c))

    return Result(acc_base, acc_pooled, mi_plug, mi_mm, tau, mi_mm / tau, ve,
                  c2, clopper_pearson(c2_k, c2_n), c2_n, chance,
                  r_val, n_r, base_rec, rdist,
                  u, tpr, fpr, n_err, n_ok, float(abstain.mean()) if n_a else float("nan"),
                  (n_s, n_c, n_r, n_a))


SEED_OFFSET = {a: i * 100000 for i, a in enumerate(AGENT_SPEC)}


def run_batch(agent, cfg: SimConfig, n_runs: int, seed0: int = 42, seed_offset: Optional[int] = None) -> dict:
    keys = ["accuracy_base", "accuracy_pooled", "mi_plugin", "mi", "b_min", "c2", "r", "u", "abstain_rate"]
    data = {k: [] for k in keys}
    for a in (0.60, 0.70, 0.80, 0.90):
        data[f"veff_{int(a*100)}"] = []
    for o in REPAIR_OUTCOMES:
        data[f"repair_{o}"] = []
    for i in range(n_runs):
        off = seed_offset if seed_offset is not None else (SEED_OFFSET[agent] if isinstance(agent, str) else 0)
        res = run_sim(agent, cfg, seed0 + off + i)
        for k in keys:
            data[k].append(getattr(res, k))
        for a in (0.60, 0.70, 0.80, 0.90):
            data[f"veff_{int(a*100)}"].append(res.veff[a])
        for o in REPAIR_OUTCOMES:
            data[f"repair_{o}"].append(res.repair_dist[o])
    out = {}
    for k, v in data.items():
        arr = np.array(v, float)
        ok = arr[~np.isnan(arr)]
        out[k] = dict(mean=float(ok.mean()) if len(ok) else None,
                      sd=float(ok.std(ddof=1)) if len(ok) > 1 else None,
                      ci_lo=float(np.percentile(ok, 2.5)) if len(ok) else None,
                      ci_hi=float(np.percentile(ok, 97.5)) if len(ok) else None,
                      n=int(len(ok)), n_nan=int(len(arr) - len(ok)))
    out["config"] = asdict(cfg)
    out["n_runs"] = n_runs
    return out


def spec_table_markdown() -> str:
    rows = ["| Agent | p_single | p_train | p_heldout | Repair policy (repeat/modify/escalate/abandon) | Recovery | Abstain (hard/easy) | Forced-commit error (hard/easy) | Notes |",
            "|---|---|---|---|---|---|---|---|---|"]
    for a, s in AGENT_SPEC.items():
        rec = "simulation null 1-(1-1/K)^2" if s["repair_recovery"] is None else \
            "modify 0.55, escalate 0.35, repeat chance, abandon 0"
        rows.append(f"| {a} | {s['p_single'] if s['p_single'] is not None else 'uniform'} | "
                    f"{s['p_train'] if s['p_train'] is not None else '1/K'} | "
                    f"{s['p_heldout'] if s['p_heldout'] is not None else '1/K'} | "
                    f"{'/'.join(f'{x:.2f}' for x in s['repair_policy'])} | {rec} | "
                    f"{s['abstain_hard']:.2f}/{s['abstain_easy']:.2f} | {s['err_hard']:.2f}/{s['err_easy']:.2f} | {s['description']} |")
    return "\n".join(rows)
