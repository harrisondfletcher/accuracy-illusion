"""Regenerate manuscript figures from results/*.json.

Figures 1, 3, and 5 are simulation based. Figures 2 and 4 are generated only
when results/bci_real_application_v4.json exists.
"""
from __future__ import annotations
import os, json, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 11})


def _save(fig, stem):
    fig.savefig(os.path.join(FIG, stem + ".png"), dpi=220, bbox_inches="tight")
    fig.savefig(os.path.join(FIG, stem + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def interval_segments(points, intervals):
    """Return descriptive interval endpoints exactly as saved (handoff 16.3).

    No clamping: if a point lies outside its interval, the segment still spans
    the true saved endpoints and the point is drawn separately.
    """
    import numpy as _np
    intervals = _np.asarray(intervals, dtype=float)
    if intervals.ndim != 2 or intervals.shape[1] != 2:
        raise ValueError("intervals must be (n, 2)")
    return intervals.copy()


def fig1_radar():
    t1 = json.load(open(os.path.join(RES, "table1.json")))
    agents = ["random", "class_biased", "overproduction", "memorizer", "compositional"]
    labels = ["$B_{min}$", "$V_{eff}(0.80)$", "$C_2$", "$R$", "$U$"]
    keys = ["b_min", "veff_80", "c2", "r", "u"]
    maxes = {"b_min": max(t1[a]["b_min"]["mean"] for a in agents), "veff_80": 12, "c2": 1, "r": 1, "u": 1}
    ang = np.linspace(0, 2 * math.pi, 5, endpoint=False).tolist(); ang += ang[:1]
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    styles = {"random": ("0.6", "--", 1.2), "class_biased": ("0.5", ":", 1.2), "overproduction": ("0.4", "-.", 1.2),
              "memorizer": ("#d94a5f", "-", 2.5), "compositional": ("#2bb5a0", "-", 2.5)}
    for a in agents:
        vals = [max(0, t1[a][k]["mean"]) / maxes[k] for k in keys]; vals += vals[:1]
        c, ls, lw = styles[a]
        ax.plot(ang, vals, color=c, ls=ls, lw=lw, label=a.replace("_", "-").title())
        if a in ("memorizer", "compositional"):
            ax.fill(ang, vals, color=c, alpha=0.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels); ax.set_ylim(0, 1.05); ax.set_yticklabels([])
    ax.set_title("The Measurement Blind Spot", pad=20, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), frameon=False)
    fig.text(0.5, 0.02, "Memorizer and Compositional are exactly matched on the realized base channel;\nthey separate on $C_2$, $R$, and $U$.", ha="center", fontsize=9, style="italic")
    _save(fig, "fig1_radar")


def fig3_knife():
    sw = json.load(open(os.path.join(RES, "sweep_noise.json")))
    ps = sorted(sw.keys(), key=float); x = np.arange(len(ps)); w = 0.38
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
    am = [sw[p]["memorizer"]["accuracy_pooled"]["mean"] for p in ps]
    ac = [sw[p]["compositional"]["accuracy_pooled"]["mean"] for p in ps]
    cm = [sw[p]["memorizer"]["c2"]["mean"] for p in ps]
    cc = [sw[p]["compositional"]["c2"]["mean"] for p in ps]
    a1.bar(x - w / 2, am, w, color="#d94a5f", label="Memorizer")
    a1.bar(x + w / 2, ac, w, color="#2bb5a0", label="Compositional")
    for i in range(len(ps)):
        a1.text(x[i], max(am[i], ac[i]) + 0.02, f"$\\Delta$={100*(ac[i]-am[i]):.1f} pts", ha="center", fontsize=8)
    a1.set_xticks(x); a1.set_xticklabels(ps)
    a1.set_xlabel("$p$ (exactly matched base-channel accuracy)")
    a1.set_ylabel("Aggregate accuracy (base + compositional trials)")
    a1.set_title("Aggregate accuracy compresses the held-out difference")
    a1.set_ylim(0.3, 1.05); a1.legend(frameon=False)
    a2.bar(x - w / 2, cm, w, color="#d94a5f", label="Memorizer")
    a2.bar(x + w / 2, cc, w, color="#2bb5a0", label="Compositional")
    a2.axhline(1 / 12, color="0.6", ls="--", lw=1)
    a2.text(len(ps) - 0.5, 1 / 12 + 0.02, "chance", color="0.5", fontsize=8, ha="right")
    for i in range(len(ps)):
        a2.text(x[i], cc[i] + 0.02, f"$\\Delta$={100*(cc[i]-cm[i]):.0f} pts", ha="center", fontsize=8)
    a2.set_xticks(x); a2.set_xticklabels(ps); a2.set_xlabel("$p$")
    a2.set_ylabel("$C_2$"); a2.set_title("$C_2$ exposes the structural difference")
    a2.set_ylim(0, 1.1); a2.legend(frameon=False)
    fig.suptitle("The Matched-Base Knife", fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig3_knife")


def fig5_power():
    c2 = json.load(open(os.path.join(RES, "power_c2.json")))
    r = json.load(open(os.path.join(RES, "power_r.json")))
    u = json.load(open(os.path.join(RES, "power_u.json")))
    b = json.load(open(os.path.join(RES, "power_bmin.json")))
    fig, axes = plt.subplots(1, 4, figsize=(20, 5.1))

    def heat(ax, grid, rows, cols, title, xl, yl):
        M = np.array([[grid[str(rw)][str(c)]["power"] for c in cols] for rw in rows], float)
        im = ax.imshow(M, vmin=0, vmax=1, cmap="cividis", aspect="auto")
        for i in range(len(rows)):
            for j in range(len(cols)):
                value = M[i, j]
                color = "white" if value < 0.48 else "black"
                ax.text(j, i, f"{value*100:.0f}%", ha="center", va="center", fontsize=8,
                        color=color, fontweight="bold" if value >= 0.80 else None)
                if value >= 0.80:
                    ax.add_patch(Rectangle((j - 0.49, i - 0.49), 0.98, 0.98, fill=False, edgecolor="white", linewidth=1.2))
        ax.axhline(0.5, color="white", linewidth=1.4)
        ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols)
        ax.set_yticks(range(len(rows))); ax.set_yticklabels(["0 (size)" if float(x) == 0 else x for x in rows])
        ax.set_title(title); ax.set_xlabel(xl); ax.set_ylabel(yl)
        return im

    heat(axes[0], c2["resolution"], [0.0, 0.05, 0.1, 0.2, 0.4], [15, 38, 75, 150, 400, 1600],
         "$C_2$ (baseline 0.50)", "held-out trials per agent $n_U$", "$\\delta_C$")
    heat(axes[1], r["cells"], [0.0, 0.05, 0.1, 0.2, 0.25], [20, 40, 100, 200, 400],
         "$R$ (independent-uniform null = 0.16)", "induced-error trials per agent $n_R$", "")
    heat(axes[2], u["cells"]["0.2"], [0.0, 0.1, 0.2, 0.3, 0.4], [100, 200, 500, 1000],
         "$U$ ($\\pi_e$ = 0.20, $a_0$ = 0.10)", "uncertainty trials $n_A$", "")
    im = heat(axes[3], b["cells"], [0.0, 0.01, 0.03, 0.05, 0.1], [100, 200, 500, 750, 1000, 2000],
              "$B_{min}$ (system-label permutation)", "base trials per agent $n_S$", "")
    fig.suptitle("Rejection Landscape: one perturbed parameter per metric; first row is empirical size at $\\delta=0$", fontweight="bold", y=1.02)
    fig.colorbar(im, ax=axes, fraction=0.015, pad=0.012, label="Rejection probability across 1,000 replications")
    _save(fig, "fig5_power")


def _decoder_subject_view(subject_data, decoder):
    return {subject: record["decoders"][decoder] for subject, record in subject_data.items()}


def _confusion_grid(subject_data, decoder, stem, title):
    decoded = _decoder_subject_view(subject_data, decoder)
    subjects = sorted(decoded)
    fig, axes = plt.subplots(3, 3, figsize=(10.8, 9.6))
    axes = np.asarray(axes).ravel()
    image = None
    for ax, subject in zip(axes, subjects):
        result = decoded[subject]
        cm = np.asarray(result["confusion_matrix"], float)
        normalized = np.divide(
            cm,
            cm.sum(axis=1, keepdims=True),
            out=np.zeros_like(cm),
            where=cm.sum(axis=1, keepdims=True) > 0,
        )
        image = ax.imshow(normalized, cmap="cividis", vmin=0, vmax=1)
        for i in range(4):
            for j in range(4):
                value = normalized[i, j]
                ax.text(
                    j, i, f"{100*value:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if value < 0.25 or value > 0.72 else "black",
                )
        ax.set_title(
            f"{subject}: acc {result['accuracy']:.2f}, $\\kappa$ {result['kappa']:.2f}",
            fontsize=9,
        )
        ax.set_xticks(range(4)); ax.set_xticklabels(["LH", "RH", "Feet", "Tongue"], fontsize=8)
        ax.set_yticks(range(4)); ax.set_yticklabels(["LH", "RH", "Feet", "Tongue"], fontsize=8)
    for ax in axes[len(subjects):]:
        ax.axis("off")
    fig.suptitle(title, fontweight="bold")
    if image is not None:
        fig.colorbar(image, ax=axes.tolist(), fraction=0.025, pad=0.015,
                     label="Row-normalized classification rate")
    _save(fig, stem)


def bci_figures(results_path=None):
    path = results_path or os.environ.get(
        "BCI_RESULTS_JSON", os.path.join(RES, "bci_real_application_v4.json")
    )
    if not os.path.exists(path):
        print("  Validated BCI results not found; skipping BCI figures.")
        return
    data = json.load(open(path))
    if data.get("status") != "complete":
        raise RuntimeError("BCI result exists but status is not complete")
    subject_data = data["subjects"]
    primary = _decoder_subject_view(subject_data, "primary")
    subjects = sorted(primary, key=lambda subject: primary[subject]["accuracy"])
    accuracy = np.array([primary[subject]["accuracy"] for subject in subjects])
    bmin = np.array([primary[subject]["b_min_bpm"] for subject in subjects])
    intervals = np.array([primary[subject]["b_min_ci_bpm"] for subject in subjects])

    fig, (left, right) = plt.subplots(1, 2, figsize=(12.4, 5.3))
    segments = interval_segments(bmin, intervals)
    left.vlines(accuracy, segments[:, 0], segments[:, 1], color="C0", lw=1.4)
    left.plot(accuracy, bmin, "o", color="C0")
    for x, y, subject in zip(accuracy, bmin, subjects):
        left.annotate(subject, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    left.axhline(0, color="0.7", linewidth=1)
    left.set_xlabel("Accuracy")
    left.set_ylabel("$B_{min}$ (bits/min; full trial cycle)")
    left.set_title("Primary fixed-window decoder")

    alphas = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    mean_veff = [np.mean([primary[s]["veff_curve"][str(a)] for s in subjects]) for a in alphas]
    median_veff = [np.median([primary[s]["veff_curve"][str(a)] for s in subjects]) for a in alphas]
    qualifying = [sum(primary[s]["veff_curve"][str(a)] >= 1 for s in subjects) for a in alphas]
    right.plot(alphas, mean_veff, marker="o", label="Mean $V_{eff}$")
    right.plot(alphas, median_veff, marker="s", label="Median $V_{eff}$")
    count_axis = right.twinx()
    count_axis.plot(alphas, qualifying, marker="^", linestyle="--", label="Subjects with ≥1")
    right.set_xlabel("Pre-specified F1 threshold $\\alpha$")
    right.set_ylabel("Effective vocabulary count")
    count_axis.set_ylabel("Subjects with at least one qualifying intent")
    count_axis.set_ylim(0, len(subjects) + 0.5)
    right.set_title("Threshold sensitivity")
    handles, labels = right.get_legend_handles_labels()
    handles2, labels2 = count_axis.get_legend_handles_labels()
    right.legend(handles + handles2, labels + labels2, frameon=False, loc="upper right")
    fig.suptitle("BCI subject-level information and threshold sensitivity", fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig2_bci_subjects")

    _confusion_grid(
        subject_data,
        "primary",
        "fig4_confusion",
        "Primary fixed-window decoder: per-subject confusion structure (%)",
    )
    _confusion_grid(
        subject_data,
        "fbcsp",
        "figS8_fbcsp_confusion",
        "FBCSP-style robustness decoder: per-subject confusion structure (%)",
    )


if __name__ == "__main__":
    requested = set(sys.argv[1:] or ["all"])
    if "all" in requested or "fig1" in requested:
        fig1_radar(); print("  -> figures/fig1_radar")
    if "all" in requested or "fig3" in requested:
        fig3_knife(); print("  -> figures/fig3_knife")
    if "all" in requested or "fig5" in requested:
        fig5_power(); print("  -> figures/fig5_power")
    if "all" in requested or "bci" in requested:
        bci_figures()
