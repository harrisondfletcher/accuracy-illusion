"""Independent validation of BCI pipeline output (handoff §12).

Read-only. Recomputes reported results from prediction CSVs and stored
evidence instead of trusting duplicated JSON values. Modes:

* ``preflight``: source identity, structure, timing, artifact, and duration
  gates (D1, D2, T1, C1); no decoding results expected.
* ``smoke``: engineering-run checks; reduced inference allowed; the output is
  categorically ineligible for manuscript population (result_kind=smoke).
* ``final``: every gate in the handoff §12 table that this validator owns.

No gate anywhere depends on a performance level (A10).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

CLASSES = ("left_hand", "right_hand", "feet", "tongue")
K = 4
LN2 = math.log(2.0)
VEFF_KEYS = {"0.4", "0.5", "0.6", "0.7", "0.8", "0.9"}
TOL = 1e-9


class Gates:
    def __init__(self) -> None:
        self.results: list[dict] = []

    def check(self, gate: str, ok: bool, detail: str) -> None:
        self.results.append({"gate": gate, "pass": bool(ok), "detail": detail})

    @property
    def failures(self) -> list[dict]:
        return [r for r in self.results if not r["pass"]]


def mi_components(cm: np.ndarray) -> dict:
    cm = np.asarray(cm, dtype=float)
    n = float(cm.sum())
    joint = cm / n
    py = joint.sum(axis=1, keepdims=True)
    pz = joint.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        plugin = float(np.where(joint > 0, joint * np.log2(joint / (py * pz)), 0.0).sum())
    k_yz = int((joint > 0).sum())
    k_y = int((py > 0).sum())
    k_z = int((pz > 0).sum())
    correction = (k_yz - k_y - k_z + 1) / (2.0 * n * LN2)
    return {
        "mi_plugin_bits": plugin,
        "mi_mm_correction_bits": correction,
        "mi_corrected_bits": plugin - correction,
        "K_y": k_y, "K_z": k_z, "K_yz": k_yz, "N": int(n),
    }


def cohen_kappa(cm: np.ndarray) -> float:
    cm = np.asarray(cm, dtype=float)
    n = cm.sum()
    po = np.trace(cm) / n
    pe = float((cm.sum(axis=1) * cm.sum(axis=0)).sum()) / (n * n)
    return (po - pe) / (1.0 - pe)


def holm_adjust(p_values: list[float]) -> np.ndarray:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted_ordered = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order])
    adjusted_ordered = np.minimum(adjusted_ordered, 1.0)
    adjusted = np.empty_like(p)
    adjusted[order] = adjusted_ordered
    return adjusted


def read_predictions(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))


def validate_structure(gates: Gates, data: dict, mode: str, expected_subjects: list[str]) -> None:
    subjects = data.get("subjects", {})
    if mode == "final":
        gates.check("R1", data.get("status") == "complete", f"status={data.get('status')!r}")
        gates.check("R1", data.get("result_kind") == "final", f"result_kind={data.get('result_kind')!r}")
        gates.check("R1", bool(data.get("design_fingerprint")), "design fingerprint present")
        gates.check(
            "R1", sorted(subjects) == expected_subjects,
            f"subjects {sorted(subjects)}",
        )
    elif mode == "smoke":
        gates.check(
            "SMOKE", data.get("result_kind") == "smoke",
            "smoke output must be result_kind=smoke (ineligible for manuscript)",
        )
        gates.check("SMOKE", data.get("status") == "complete", f"status={data.get('status')!r}")
    else:
        gates.check("PREFLIGHT", data.get("status") == "complete", f"status={data.get('status')!r}")
        gates.check(
            "PREFLIGHT", data.get("result_kind") == "preflight",
            f"result_kind={data.get('result_kind')!r}",
        )


def validate_sources(gates: Gates, data: dict, manifest: dict | None) -> None:
    files = data.get("data_files", [])
    names = sorted(f["name"] for f in files)
    expected = sorted(
        f"A{s:02d}{r}.mat" for s in range(1, 10) for r in ("T", "E")
    )
    gates.check("D1", names == expected, f"{len(names)} data files listed")
    hashes = [f["sha256"] for f in files]
    gates.check("D1", len(set(hashes)) == len(hashes), "all data hashes distinct (T != E)")
    if manifest is not None:
        manifest_hash = {f["name"]: f["sha256"] for f in manifest.get("files", [])}
        mismatches = [
            f["name"] for f in files
            if manifest_hash.get(f["name"]) != f["sha256"]
        ]
        gates.check("D1", not mismatches, f"manifest hash mismatches: {mismatches}")
        gates.check(
            "D1", manifest.get("n_validated") == 18,
            f"manifest validated count {manifest.get('n_validated')}",
        )


def validate_subject_structure(gates: Gates, name: str, record: dict) -> None:
    gates.check("T2", record.get("n_eeg_channels") == 22, f"{name}: n_eeg_channels")
    gates.check(
        "T2",
        record.get("excluded_channels") == ["EOG1", "EOG2", "EOG3"],
        f"{name}: EOG exclusion list",
    )
    for session in ("training", "evaluation"):
        acct = record.get("artifact_accounting", {}).get(session, {})
        gates.check("D2", acct.get("n_all") == 288, f"{name}/{session}: n_all=288")
        ok_sum = acct.get("n_clean", -1) + acct.get("n_dropped", -1) == 288
        gates.check("A1", ok_sum, f"{name}/{session}: clean+dropped=288")
        per_run = acct.get("per_run", {})
        gates.check("D2", len(per_run) == 6, f"{name}/{session}: six task runs")
        flagged_total = sum(r.get("n_flagged", 0) for r in per_run.values())
        gates.check(
            "A1", flagged_total == acct.get("n_dropped"),
            f"{name}/{session}: flagged=={acct.get('n_dropped')} dropped",
        )
    cycle = record.get("evaluation_cycle", {})
    gates.check("C1", cycle.get("n_within_run_intervals") == 282, f"{name}: 282 intervals")
    intervals = record.get("evaluation_within_run_intervals_sec")
    if intervals is not None:
        arr = np.asarray(intervals, dtype=float)
        gates.check(
            "C1",
            len(arr) == 282 and np.all(arr > 0) and np.all(np.isfinite(arr)),
            f"{name}: interval vector valid",
        )
        gates.check(
            "C1", close(float(arr.mean()), cycle.get("tau_mean_sec", float("nan"))),
            f"{name}: tau_mean recomputed",
        )
    timing = record.get("timing_audit", {}).get("evaluation", {})
    gates.check(
        "T1",
        timing.get("n_epoch_samples") == 501
        and timing.get("epoch_start_offset_samples") == 625
        and timing.get("epoch_stop_offset_samples_inclusive") == 1125
        and timing.get("cue_offset_samples") == 500,
        f"{name}: timing constants (trigger anchor, 0.5-2.5 s post-cue)",
    )


def validate_decoder(
    gates: Gates,
    name: str,
    decoder: str,
    result: dict,
    record: dict,
    predictions_dir: Path,
    mode: str,
    min_bootstrap: int,
    min_permutations: int,
) -> None:
    tag = f"{name}/{decoder}"
    # --- I1 inference counts ---
    gates.check(
        "I1",
        result.get("bootstrap_count", 0) >= min_bootstrap
        and result.get("permutation_count", 0) >= min_permutations,
        f"{tag}: bootstrap={result.get('bootstrap_count')}, "
        f"permutations={result.get('permutation_count')}",
    )
    gates.check(
        "I1",
        bool(result.get("bootstrap_scheme")) and bool(result.get("permutation_scheme"))
        and result.get("inference_seed") is not None
        and result.get("permutation_exceedances") is not None,
        f"{tag}: inference provenance recorded",
    )

    # --- I2 recompute from prediction CSV ---
    csv_path = predictions_dir / result.get("prediction_file", "missing")
    if not csv_path.exists():
        gates.check("I2", False, f"{tag}: prediction CSV missing at {csv_path}")
        return
    rows = read_predictions(csv_path)
    uids = [r["trial_uid"] for r in rows]
    gates.check("I2", len(set(uids)) == len(uids), f"{tag}: no duplicate trial UIDs")
    roles = {r["analysis_role"] for r in rows}
    expected_role = "smoke_T_holdout" if mode == "smoke" else "clean_primary"
    gates.check("I2", roles == {expected_role}, f"{tag}: analysis_role={roles}")
    session_expected = {"T"} if mode == "smoke" else {"E"}
    gates.check(
        "L1", {r["session_T_or_E"] for r in rows} == session_expected,
        f"{tag}: prediction rows from expected session",
    )
    gates.check(
        "A1",
        all(r["artifact_flag"] == "0" for r in rows),
        f"{tag}: no organizer-flagged trial in clean predictions",
    )
    index = {c: i for i, c in enumerate(CLASSES)}
    cm = np.zeros((K, K), dtype=int)
    for r in rows:
        cm[index[r["true_class"]], index[r["predicted_class"]]] += 1
    gates.check(
        "I2", cm.tolist() == result.get("confusion_matrix"),
        f"{tag}: confusion matrix recomputed from CSV",
    )
    comp = mi_components(cm)
    for key in ("mi_plugin_bits", "mi_mm_correction_bits", "mi_corrected_bits"):
        gates.check("I2", close(comp[key], result.get(key, float("nan"))), f"{tag}: {key}")
    for key in ("K_y", "K_z", "K_yz", "N"):
        gates.check("I2", comp[key] == result.get(key), f"{tag}: {key}")
    accuracy = float(np.trace(cm)) / cm.sum()
    gates.check("I2", close(accuracy, result.get("accuracy", float("nan"))), f"{tag}: accuracy")
    gates.check("I2", close(cohen_kappa(cm), result.get("kappa", float("nan"))), f"{tag}: kappa")

    tp = np.diag(cm).astype(float)
    fp = cm.sum(axis=0) - tp
    fn = cm.sum(axis=1) - tp
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        recall = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f1 = np.where(precision + recall > 0, 2 * precision * recall / (precision + recall), 0.0)
    gates.check(
        "I2",
        all(close(a, b) for a, b in zip(f1.tolist(), result.get("f1_per_class", []))),
        f"{tag}: per-class F1",
    )
    support = cm.sum(axis=1)
    veff = {
        str(alpha): int(np.sum((f1 >= alpha) & (support >= result.get("veff_beta", 30))))
        for alpha in (0.40, 0.50, 0.60, 0.70, 0.80, 0.90)
    }
    gates.check("I2", veff == result.get("veff_curve"), f"{tag}: V_eff curve")
    gates.check(
        "I2", set(result.get("veff_curve", {})) == VEFF_KEYS, f"{tag}: V_eff keys"
    )

    tau = result.get("tau_mean_sec", float("nan"))
    gates.check(
        "I2",
        close(result.get("b_min_bpm", float("nan")), comp["mi_corrected_bits"] * 60.0 / tau),
        f"{tag}: b_min consistent with corrected MI and tau",
    )

    # --- I3 permutation arithmetic ---
    p_raw = result.get("mi_perm_p_raw")
    n_perm = result.get("permutation_count", 0)
    exceed = result.get("permutation_exceedances")
    ok_p = (
        p_raw is not None and exceed is not None
        and 0 < p_raw <= 1
        and 0 <= exceed <= n_perm
        and close(p_raw, (exceed + 1) / (n_perm + 1))
    )
    gates.check("I3", ok_p, f"{tag}: p=(exceed+1)/(B+1), strictly positive")

    # --- I4 intervals sane ---
    for field in ("mi_ci_bits", "accuracy_ci", "kappa_ci", "b_min_ci_bpm"):
        ci = result.get(field)
        ok_ci = (
            isinstance(ci, list) and len(ci) == 2
            and all(math.isfinite(float(v)) for v in ci) and ci[0] <= ci[1]
        )
        gates.check("I4", ok_ci, f"{tag}: {field} well-formed")

    # --- L1: no E leakage evidence in tuning; folds disjoint by construction ---
    tuning = result.get("training_only_tuning", {})
    gates.check(
        "L1",
        tuning.get("cv_scheme") == "leave-one-source-run-out"
        and tuning.get("n_folds", 0) >= 5
        and "selected" in tuning,
        f"{tag}: LOGO tuning evidence present (folds={tuning.get('n_folds')})",
    )
    # R2: no performance admission gate — verify low kappa did NOT fail anything.
    kappa_value = result.get("kappa")
    gates.check(
        "R2", isinstance(kappa_value, float),
        f"{tag}: kappa reported without admission gating (value={kappa_value})",
    )
    # ITR conventions (A7)
    gates.check(
        "R2",
        "itr_bits_formula" in result and "itr_bpm_clipped_at_chance" in result,
        f"{tag}: ITR formula and clipped fields both present",
    )

    # all-scheduled sensitivity (A12) — final mode only
    if mode == "final":
        sens = result.get("all_scheduled_sensitivity")
        gates.check("R2", sens is not None, f"{tag}: all_scheduled_sensitivity present")
        if sens:
            gates.check(
                "R2", sens.get("N") == 288,
                f"{tag}: sensitivity covers all scheduled trials (N={sens.get('N')})",
            )
            sens_csv = predictions_dir / sens.get("prediction_file", "missing")
            if sens_csv.exists():
                sens_rows = read_predictions(sens_csv)
                cm_s = np.zeros((K, K), dtype=int)
                for r in sens_rows:
                    cm_s[index[r["true_class"]], index[r["predicted_class"]]] += 1
                gates.check(
                    "I2", cm_s.tolist() == sens.get("confusion_matrix"),
                    f"{tag}: sensitivity CM recomputed from CSV",
                )
            else:
                gates.check("I2", False, f"{tag}: sensitivity CSV missing")


def validate(
    path: Path,
    mode: str,
    manifest_path: Path | None,
    report_path: Path | None,
) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    # Strict JSON: reject non-finite numbers anywhere.
    try:
        json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
        strict_ok = True
    except ValueError:
        strict_ok = False
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path else None
    )
    gates = Gates()
    gates.check("R3", strict_ok, "strict JSON (no NaN/Infinity)")
    expected_subjects = [f"S{i}" for i in range(1, 10)]
    validate_structure(gates, data, mode, expected_subjects)
    validate_sources(gates, data, manifest)

    subjects = data.get("subjects", {})
    predictions_dir = path.parent / "predictions"
    min_boot = 10_000 if mode == "final" else 1
    min_perm = 5_000 if mode == "final" else 1

    for name, record in subjects.items():
        if mode != "smoke":
            validate_subject_structure(gates, name, record)
        if mode == "preflight":
            gates.check(
                "PREFLIGHT", "decoders" not in record,
                f"{name}: preflight contains no decoding results",
            )
            continue
        decoder_map = record.get("decoders", {})
        if mode == "final":
            gates.check(
                "L2", set(decoder_map) == {"primary", "fbcsp"},
                f"{name}: both predeclared decoders present",
            )
        for decoder, result in decoder_map.items():
            validate_decoder(
                gates, name, decoder, result, record, predictions_dir,
                mode, min_boot, min_perm,
            )

    # --- I3: recompute Holm within each decoder family ---
    if mode != "preflight" and subjects:
        for decoder in ("primary", "fbcsp"):
            entries = [
                (name, record["decoders"][decoder])
                for name, record in subjects.items()
                if decoder in record.get("decoders", {})
            ]
            if not entries:
                continue
            raw = [e[1].get("mi_perm_p_raw") for e in entries]
            stored = [e[1].get("mi_perm_p_holm") for e in entries]
            if any(v is None for v in raw + stored):
                gates.check("I3", False, f"{decoder}: missing raw/Holm p-values")
                continue
            recomputed = holm_adjust(raw)
            ok = all(close(a, b) for a, b in zip(recomputed.tolist(), stored))
            gates.check(
                "I3", ok,
                f"{decoder}: Holm family recomputed over {len(raw)} subjects",
            )

    # --- A2: identical retained UID ordering across decoders ---
    if mode == "final":
        for name in subjects:
            files = {
                d: predictions_dir / subjects[name]["decoders"][d]["prediction_file"]
                for d in subjects[name].get("decoders", {})
            }
            if len(files) == 2 and all(f.exists() for f in files.values()):
                uid_lists = {
                    d: [r["trial_uid"] for r in read_predictions(f)]
                    for d, f in files.items()
                }
                gates.check(
                    "A2",
                    uid_lists["primary"] == uid_lists["fbcsp"],
                    f"{name}: identical ordered clean UID lists across decoders",
                )

    report = {
        "mode": mode,
        "input": str(path),
        "n_checks": len(gates.results),
        "n_failures": len(gates.failures),
        "failures": gates.failures,
        "checks": gates.results,
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
    if gates.failures:
        summary = "\n- ".join(
            f"[{f['gate']}] {f['detail']}" for f in gates.failures
        )
        raise SystemExit(f"BCI validation failed ({mode} mode):\n- {summary}")
    print(
        f"BCI validation passed ({mode} mode): {path} "
        f"[{len(gates.results)} checks]"
    )
    return data


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON constant: {value}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--mode", required=True, choices=("preflight", "smoke", "final"))
    parser.add_argument("--source-manifest", default=None)
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    validate(
        Path(args.path),
        args.mode,
        Path(args.source_manifest) if args.source_manifest else None,
        Path(args.report) if args.report else None,
    )


if __name__ == "__main__":
    main()
