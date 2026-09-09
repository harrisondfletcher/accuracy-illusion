"""Populate the execution-gated BCI tables and result prose from validated JSON.

Prose rules (handoff §16.2, amendments):
* "subjects for which the specified independence test rejected after Holm
  adjustment" — never "subjects carrying measurable information".
* No inference of absent information for non-rejected subjects.
* The near-matched accuracy contrast is EXPLORATORY, selected by a disclosed
  rule, and labeled as such (it maximizes the B_min gap among pairs within
  .03 accuracy whose independence tests both rejected).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

from validate_bci_output import validate


def fmt_p(value: float) -> str:
    return "<.001" if value < .001 else f"{value:.3f}"


def holm_rejected(subjects: dict, decoder: str) -> list[str]:
    return [
        subject
        for subject, record in sorted(subjects.items(), key=lambda kv: int(kv[0][1:]))
        if record["decoders"][decoder]["mi_perm_p_holm"] < .05
    ]


def decoder_summary(subjects: dict, decoder: str) -> dict:
    rows = [record["decoders"][decoder] for record in subjects.values()]
    accuracy = np.array([row["accuracy"] for row in rows])
    kappa = np.array([row["kappa"] for row in rows])
    bmin = np.array([row["b_min_bpm"] for row in rows])
    return {
        "mean_accuracy": float(accuracy.mean()),
        "mean_kappa": float(kappa.mean()),
        "accuracy_range": (float(accuracy.min()), float(accuracy.max())),
        "bmin_range": (float(bmin.min()), float(bmin.max())),
        "holm_rejected": holm_rejected(subjects, decoder),
    }


def closest_accuracy_contrast(subjects: dict, decoder: str):
    """Exploratory pair selection; the rule is disclosed wherever it is used."""
    candidates = []
    names = sorted(subjects)
    for i, first in enumerate(names):
        a = subjects[first]["decoders"][decoder]
        for second in names[i + 1:]:
            b = subjects[second]["decoders"][decoder]
            accuracy_gap = abs(a["accuracy"] - b["accuracy"])
            bmin_gap = abs(a["b_min_bpm"] - b["b_min_bpm"])
            if accuracy_gap <= .03 and a["mi_perm_p_holm"] < .05 and b["mi_perm_p_holm"] < .05:
                candidates.append((bmin_gap, -accuracy_gap, first, second, a, b))
    return max(candidates) if candidates else None


def primary_table(subjects: dict) -> str:
    lines = [
        "| Subject | Clean E trials | Accuracy | Kappa | Corrected MI [95% CI] | Holm p | B_min [95% CI], bits/min |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for subject in sorted(subjects, key=lambda x: int(x[1:])):
        primary = subjects[subject]["decoders"]["primary"]
        mi = f"{primary['mi_corrected_bits']:.3f} [{primary['mi_ci_bits'][0]:.3f}, {primary['mi_ci_bits'][1]:.3f}]"
        bmin = f"{primary['b_min_bpm']:.2f} [{primary['b_min_ci_bpm'][0]:.2f}, {primary['b_min_ci_bpm'][1]:.2f}]"
        lines.append(
            f"| {subject} | {primary['N']} | {primary['accuracy']:.3f} | {primary['kappa']:.3f} | {mi} | {fmt_p(primary['mi_perm_p_holm'])} | {bmin} |"
        )
    return "\n".join(lines)


def primary_veff_table(subjects: dict) -> str:
    alphas = ("0.4", "0.5", "0.6", "0.7", "0.8", "0.9")
    values = {
        alpha: [record["decoders"]["primary"]["veff_curve"][alpha] for record in subjects.values()]
        for alpha in alphas
    }
    return "\n".join([
        "| Summary | alpha=.40 | .50 | .60 | .70 | .80 | .90 |",
        "|---|---:|---:|---:|---:|---:|---:|",
        "| Mean V_eff | " + " | ".join(f"{np.mean(values[a]):.2f}" for a in alphas) + " |",
        "| Median V_eff | " + " | ".join(f"{np.median(values[a]):.0f}" for a in alphas) + " |",
        "| Subjects with V_eff >= 1 | " + " | ".join(str(sum(v >= 1 for v in values[a])) for a in alphas) + " |",
    ])


def result_paragraph(subjects: dict) -> str:
    primary = decoder_summary(subjects, "primary")
    robust = decoder_summary(subjects, "fbcsp")
    p_names = ", ".join(primary["holm_rejected"]) or "none"
    r_names = ", ".join(robust["holm_rejected"]) or "none"
    parts = [
        f"The primary fixed-window decoder had mean accuracy {primary['mean_accuracy']:.3f} "
        f"and mean kappa {primary['mean_kappa']:.3f}; the FBCSP-style robustness decoder "
        f"had mean accuracy {robust['mean_accuracy']:.3f} and mean kappa {robust['mean_kappa']:.3f}.",
        f"Subjects for which the specified independence test rejected after Holm "
        f"adjustment were {p_names} for the primary decoder and {r_names} for the "
        f"robustness decoder; non-rejection for the remaining subjects is not "
        f"evidence that no information exists.",
    ]
    contrast = closest_accuracy_contrast(subjects, "primary")
    if contrast:
        _, _, first, second, a, b = contrast
        parts.append(
            f"As an exploratory illustration (pair selected to maximize the B_min "
            f"gap among subject pairs within .03 accuracy whose independence tests "
            f"both rejected; the two per-subject tests do not establish a "
            f"significant between-subject difference), {first} versus {second}: "
            f"accuracy {a['accuracy']:.3f} versus {b['accuracy']:.3f}, but B_min "
            f"{a['b_min_bpm']:.2f} versus {b['b_min_bpm']:.2f} bits/min."
        )
    return " ".join(parts)


def render(text: str, subjects: dict) -> str:
    """Deterministic, idempotent-from-template population (handoff §16, test 19)."""
    if "BCI_PRIMARY_TABLE_START" not in text or "BCI_PRIMARY_VEFF_TABLE_START" not in text:
        raise SystemExit("Template is missing required BCI table markers")
    text = re.sub(
        r"<!-- BCI_PRIMARY_TABLE_START -->.*?<!-- BCI_PRIMARY_TABLE_END -->",
        primary_table(subjects),
        text,
        flags=re.S,
    )
    text = re.sub(
        r"<!-- BCI_PRIMARY_VEFF_TABLE_START -->.*?<!-- BCI_PRIMARY_VEFF_TABLE_END -->",
        primary_veff_table(subjects),
        text,
        flags=re.S,
    )
    paragraph = result_paragraph(subjects)
    insertion = "\n**Validated BCI result summary.** " + paragraph + "\n"
    text = text.replace(
        "No pooled row is permitted as an operating-system claim.",
        insertion + "\nNo pooled row is permitted as an operating-system claim.",
    )
    text = text.replace(
        "The original empirical claims have been withdrawn rather than repaired rhetorically. "
        "The replacement analysis is fully specified, but this draft asserts no BCI result until "
        "the public data are processed by both decoders and every runtime gate passes.",
        paragraph,
    )
    if "BCI_PRIMARY_TABLE_START" in text or "BCI_PRIMARY_VEFF_TABLE_START" in text:
        raise SystemExit("Unpopulated BCI table markers remain")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path")
    parser.add_argument("--template", default="manuscript/The_Accuracy_Illusion_v4.md")
    parser.add_argument("--output", default="manuscript/The_Accuracy_Illusion_v4_BCI_populated.md")
    parser.add_argument("--source-manifest", default=None)
    args = parser.parse_args()
    data = validate(
        Path(args.json_path),
        "final",
        Path(args.source_manifest) if args.source_manifest else None,
        None,
    )
    subjects = data["subjects"]
    text = Path(args.template).read_text(encoding="utf-8")
    Path(args.output).write_text(render(text, subjects), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
