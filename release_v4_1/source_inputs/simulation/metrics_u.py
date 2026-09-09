"""metrics_u.py - Uncertainty Selectivity U (Eq. 6) with inference.

U = P(A = 1 | E = 1) - P(A = 1 | E = 0)
A: 1 if the agent signalled UNKNOWN on the trial.
E: 1 if the forced commitment elicited after the trial (before outcome feedback)
   was incorrect. E is observed on every uncertainty trial; it is not a counterfactual.

U is Youden's J for abstention as a detector of error and equals 2*AUROC - 1 for a
binary abstention decision. U = 0 when abstention is independent of error, including
an agent that never abstains, PROVIDED both strata (E = 1 and E = 0) are observed.
If either stratum is empty, U is not estimable and every function returns nan.

Confidence convention for risk_coverage(): higher `confidence` = MORE confident =
committed earlier when sweeping coverage. Pass 1 - confidence if your score is an
uncertainty score.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm, fisher_exact


def _strata(abstain, err):
    a = np.asarray(abstain, bool); e = np.asarray(err, bool)
    return a, e, int(e.sum()), int((~e).sum())


def u_selectivity(abstain, err):
    a, e, ne, no = _strata(abstain, err)
    if ne == 0 or no == 0:
        return float("nan")
    return float(a[e].mean() - a[~e].mean())


def auroc_abstention(abstain, err):
    u = u_selectivity(abstain, err)
    return float("nan") if np.isnan(u) else 0.5 * (1.0 + u)


def u_newcombe_ci(abstain, err, alpha=0.05):
    """Newcombe (1998) hybrid score interval for the difference of two proportions."""
    a, e, ne, no = _strata(abstain, err)
    if ne == 0 or no == 0:
        return float("nan"), float("nan")
    z = norm.ppf(1 - alpha / 2)
    def wilson(k, n):
        p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    k1, k0 = int(a[e].sum()), int(a[~e].sum())
    p1, p0 = k1 / ne, k0 / no
    l1, u1 = wilson(k1, ne); l0, u0 = wilson(k0, no)
    return float(p1 - p0 - np.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)), float(p1 - p0 + np.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2))


def u_stratified_bootstrap_ci(abstain, err, n_boot=10000, seed=0, alpha=0.05):
    a, e, ne, no = _strata(abstain, err)
    if ne == 0 or no == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    ae, ao = a[e].astype(float), a[~e].astype(float)
    vals = rng.choice(ae, (n_boot, ne)).mean(1) - rng.choice(ao, (n_boot, no)).mean(1)
    return float(np.percentile(vals, 100 * alpha / 2)), float(np.percentile(vals, 100 * (1 - alpha / 2)))


def u_fisher_p(abstain, err):
    a, e, ne, no = _strata(abstain, err)
    if ne == 0 or no == 0:
        return float("nan")
    k1, k0 = int(a[e].sum()), int(a[~e].sum())
    return float(fisher_exact([[k1, ne - k1], [k0, no - k0]])[1])


def risk_coverage(confidence, err):
    """Selective risk vs coverage; higher confidence commits first. Returns (coverage, risk, AURC)."""
    c = np.asarray(confidence, float); e = np.asarray(err, float)
    order = np.argsort(-c); es = e[order]; n = len(es)
    coverage = np.arange(1, n + 1) / n; risk = np.cumsum(es) / np.arange(1, n + 1)
    trap = getattr(np, "trapezoid", None) or np.trapz
    return coverage, risk, float(trap(risk, coverage))


if __name__ == "__main__":
    rng = np.random.default_rng(42); n = 200000
    def sim(ah, ae, eh, ee, hard=0.30):
        h = rng.random(n) < hard
        return rng.random(n) < np.where(h, ah, ae), rng.random(n) < np.where(h, eh, ee)
    for name, prm in {"calibrated-selective": (0.60, 0.10, 0.25, 0.05), "random_abstain": (0.25, 0.25, 0.25, 0.05),
                      "anti_selective": (0.10, 0.60, 0.25, 0.05), "never_abstain": (0.0, 0.0, 0.45, 0.10)}.items():
        a, e = sim(*prm); print(f"{name:20s} U={u_selectivity(a,e):+.3f} AUROC={auroc_abstention(a,e):.3f} CI={tuple(round(x,3) for x in u_newcombe_ci(a,e))}")
    print("empty stratum ->", u_selectivity([0, 1, 0], [1, 1, 1]))
