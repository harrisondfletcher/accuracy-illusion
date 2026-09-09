"""Handoff §14 test battery for the BCI completion build.

Synthetic fixtures only; nothing here is a BCI result. Each numbered test
maps to the §14 requirement in its docstring.
"""
from __future__ import annotations

import copy
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mne  # noqa: E402

import bci_local_data as bld  # noqa: E402
import bci_pipeline as bp  # noqa: E402
import validate_bci_output as vbo  # noqa: E402

RNG = np.random.default_rng(1234)


# --------------------------------------------------------------------------
# Synthetic MAT fixtures
# --------------------------------------------------------------------------

def make_run_dict(n_samples=40_000, seed=0, classes=None, labels=None,
                  artifacts=None, first_trigger=1000, spacing=800):
    rng = np.random.default_rng(seed)
    trial = first_trigger + spacing * np.arange(48)
    if labels is None:
        labels = np.tile(np.arange(1, 5), 12)
    if artifacts is None:
        artifacts = np.zeros(48, dtype=int)
    if classes is None:
        classes = np.array(["left hand", "right hand", "feet", "tongue"], dtype=object)
    return {
        "X": rng.standard_normal((n_samples, 25)),
        "trial": trial.astype(float),
        "y": np.asarray(labels, dtype=float),
        "fs": 250.0,
        "classes": classes,
        "artifacts": np.asarray(artifacts, dtype=float),
    }


def make_calibration_dict(n_samples=5000, seed=99):
    rng = np.random.default_rng(seed)
    return {
        "X": rng.standard_normal((n_samples, 25)),
        "trial": np.array([], dtype=float),
        "y": np.array([], dtype=float),
        "fs": 250.0,
        "classes": np.array(["left hand", "right hand", "feet", "tongue"], dtype=object),
        "artifacts": np.array([], dtype=float),
    }


def write_mat(tmp_path: Path, records: list[dict], name="A01T.mat") -> Path:
    path = tmp_path / name
    cell = np.empty((len(records),), dtype=object)
    for i, rec in enumerate(records):
        cell[i] = rec
    sio.savemat(path, {"data": cell})
    return path


@pytest.fixture()
def synth_session(tmp_path):
    records = [make_calibration_dict(seed=90 + i) for i in range(3)]
    records += [make_run_dict(seed=i) for i in range(6)]
    path = write_mat(tmp_path, records)
    return bld.load_session(path, 1, "T")


# Test 1 — calibration records skipped, task identities preserved.
def test_calibration_skipped_task_identity_preserved(synth_session):
    session = synth_session
    assert len(session.calibration_records) == 3
    assert [r.source_record_index for r in session.task_runs] == [3, 4, 5, 6, 7, 8]
    assert [r.task_run_index for r in session.task_runs] == [0, 1, 2, 3, 4, 5]


# Test 2 — MATLAB index 1 becomes Python index 0 exactly once.
def test_one_based_conversion_applied_once(synth_session):
    rows = bld.session_ledger_rows(synth_session)
    first = rows[0]
    assert first["trial_sample_matlab"] == 1000
    assert first["trial_sample_zero_based"] == 999
    assert first["cue_sample_zero_based"] == 999 + 500
    assert first["epoch_start_sample"] == 999 + 625
    assert first["epoch_stop_sample_inclusive"] == 999 + 1125


# Test 3 — physical epoch anchor, including missing- and double-offset failures.
def test_epoch_anchor_proof(synth_session):
    session = synth_session
    band = bp.epoch_session_band(session, 8.0, 30.0)
    run = session.task_runs[0]
    raw = np.ascontiguousarray(run.X_uv[:, :22].T) * 1e-6
    reference = mne.filter.filter_data(
        raw, sfreq=250.0, l_freq=8.0, h_freq=30.0, method="fir", phase="zero",
        fir_design="firwin", filter_length="auto",
        l_trans_bandwidth="auto", h_trans_bandwidth="auto", verbose=False,
    )
    s0 = int(run.trial_samples_matlab[0]) - 1
    correct = reference[:, s0 + 625 : s0 + 1126]
    missing_offset = reference[:, s0 + 125 : s0 + 626]     # tmin=0.5 from trigger
    double_offset = reference[:, s0 + 1125 : s0 + 1626]    # +2 s applied twice
    assert band["X"].shape[1:] == (22, 501)
    np.testing.assert_allclose(band["X"][0], correct, rtol=0, atol=1e-24)
    assert not np.allclose(band["X"][0], missing_offset, atol=1e-24)
    assert not np.allclose(band["X"][0], double_offset, atol=1e-24)


# Test 4 — label mapping robust to naming; reordered classes rejected.
def test_label_mapping_and_reorder_rejected(tmp_path):
    ok = make_run_dict(classes=np.array(
        ["Left Hand", "right  hand", "both feet", "tongue"], dtype=object))
    records = [ok] + [make_run_dict(seed=i) for i in range(5)]
    path = write_mat(tmp_path, records, "ok.mat")
    session = bld.load_session(path, 1, "T")
    assert session.task_runs[0].class_names == bld.CLASSES

    bad = make_run_dict(classes=np.array(
        ["feet", "left hand", "right hand", "tongue"], dtype=object))  # sorted order
    path2 = write_mat(tmp_path, [bad] + [make_run_dict(seed=i) for i in range(5)], "bad.mat")
    with pytest.raises(bld.SchemaError):
        bld.load_session(path2, 1, "T")


# Test 5 — microvolt-to-volt scaling applied exactly once.
def test_unit_scaling_once(synth_session):
    band = bp.epoch_session_band(synth_session, 8.0, 30.0)
    # Raw synthetic amplitudes are O(1) microvolts; epochs must be O(1e-6) volts.
    peak = np.abs(band["X"]).max()
    assert 1e-8 < peak < 1e-4


# Test 6 — 22 EEG channels reach features; EOG cannot enter.
def test_eog_never_enters_features(tmp_path):
    records = []
    for i in range(6):
        rec = make_run_dict(seed=i)
        rec["X"][:, 22:] = 1e9  # absurd EOG values
        records.append(rec)
    path = write_mat(tmp_path, records)
    session = bld.load_session(path, 1, "T")
    band = bp.epoch_session_band(session, 8.0, 30.0)
    assert band["X"].shape[1] == 22
    assert np.abs(band["X"]).max() < 1.0  # EOG magnitude never leaked


# Test 7 — artifact masks match exactly at trial-UID level.
def test_artifact_uid_set_equality(tmp_path):
    flags0 = np.zeros(48, dtype=int)
    flags0[[2, 17, 40]] = 1
    records = [make_run_dict(seed=0, artifacts=flags0)]
    records += [make_run_dict(seed=i) for i in range(1, 6)]
    path = write_mat(tmp_path, records)
    session = bld.load_session(path, 1, "T")
    acct = bp.artifact_accounting(session)
    assert acct["n_dropped"] == 3
    flagged = set(acct["per_run"]["record00"]["flagged_uids"])
    expected = {
        bld.trial_uid(1, "T", 0, j) for j in (2, 17, 40)
    }
    assert flagged == expected
    ledger_flagged = {
        row["trial_uid"] for row in bld.session_ledger_rows(session)
        if row["artifact_flag"]
    }
    assert ledger_flagged == expected
    # missing artifacts field is a hard failure, not "all clean"
    rec = make_run_dict(seed=7)
    del rec["artifacts"]
    path2 = write_mat(tmp_path, [rec] + [make_run_dict(seed=i) for i in range(5)], "noart.mat")
    with pytest.raises(bld.SchemaError):
        bld.load_session(path2, 1, "T")


# Test 8 — exactly 282 within-run intervals; flags cannot alter the set.
def test_282_intervals_invariant_to_flags(tmp_path):
    flags = np.zeros(48, dtype=int)
    flags[:10] = 1
    records = [make_run_dict(seed=i, artifacts=(flags if i == 0 else None)) for i in range(6)]
    path = write_mat(tmp_path, records)
    session = bld.load_session(path, 1, "T")
    within = bld.within_run_intervals(session)
    assert len(within) == 282
    np.testing.assert_allclose(within, 800 / 250.0)


# Test 9 — filter bands share one ordered UID list.
def test_band_uid_identity(synth_session):
    a = bp.epoch_session_band(synth_session, 8.0, 30.0)
    b = bp.epoch_session_band(synth_session, 4.0, 8.0)
    assert a["uids"] == b["uids"]
    assert a["uids"][0] == "S01:T:record03:trial001"


# Test 10 — fold isolation: LOGO groups disjoint; missing class rejected.
def test_logo_fold_isolation():
    y = np.tile(np.arange(4), 72)
    groups = np.repeat(np.arange(6), 48)
    from sklearn.model_selection import LeaveOneGroupOut
    for fit_idx, val_idx in LeaveOneGroupOut().split(np.zeros((288, 1)), y, groups):
        assert set(groups[fit_idx]).isdisjoint(set(groups[val_idx]))
        assert len(set(groups[val_idx])) == 1
    bp.check_fold_class_coverage(y, groups)  # must not raise
    y_bad = y.copy()
    y_bad[groups != 0] = np.where(y_bad[groups != 0] == 3, 0, y_bad[groups != 0])
    with pytest.raises(RuntimeError):
        bp.check_fold_class_coverage(y_bad, groups)


# Test 11 — kappa from actual marginals; metrics match a known matrix.
def test_metrics_against_known_confusion_matrix():
    cm = np.array([
        [30, 5, 3, 2],
        [4, 28, 6, 2],
        [2, 3, 20, 5],
        [1, 2, 4, 23],
    ])
    n = cm.sum()
    po = np.trace(cm) / n
    pe = float((cm.sum(axis=1) * cm.sum(axis=0)).sum()) / n**2
    manual_kappa = (po - pe) / (1 - pe)
    assert math.isclose(vbo.cohen_kappa(cm), manual_kappa, rel_tol=1e-12)
    # not the balanced shortcut (accuracy-.25)/.75
    shortcut = (po - 0.25) / 0.75
    assert abs(manual_kappa - shortcut) > 1e-4
    precision, recall, f1 = bp.precision_recall_f1(cm)
    assert math.isclose(precision[0], 30 / 37, rel_tol=1e-12)
    assert math.isclose(recall[0], 30 / 40, rel_tol=1e-12)
    assert math.isclose(
        f1[0], 2 * precision[0] * recall[0] / (precision[0] + recall[0]), rel_tol=1e-12
    )


# Test 12 — observed-support MM correction; negative allowed; zero cells safe.
def test_mm_correction_observed_support():
    cm = np.array([[25, 25, 0, 0], [25, 25, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
    comp = bp.mi_components(cm)
    assert comp["mi_plugin_bits"] == 0.0
    assert comp["K_y"] == 2 and comp["K_z"] == 2 and comp["K_yz"] == 4
    manual = (4 - 2 - 2 + 1) / (2 * 100 * math.log(2))
    assert math.isclose(comp["mi_mm_correction_bits"], manual, rel_tol=1e-12)
    assert comp["mi_corrected_bits"] < 0.0  # not truncated at zero


# Test 13 — stratified bootstrap preserves strata; streams are paired.
def test_bootstrap_strata_and_pairing():
    y = np.tile(np.arange(4), 72)
    groups = np.repeat(np.arange(6), 48)
    keep = np.ones(288, bool)
    keep[[5, 60, 200]] = False  # unbalanced strata
    y_k, g_k = y[keep], groups[keep]
    streams1 = bp.bootstrap_index_streams(y_k, g_k, 25, 42, subject=3)
    streams2 = bp.bootstrap_index_streams(y_k, g_k, 25, 42, subject=3)
    for a, b in zip(streams1, streams2):
        np.testing.assert_array_equal(a, b)  # paired across decoders
    for index in streams1[:5]:
        assert len(index) == len(y_k)
        for g in np.unique(g_k):
            for cls in range(4):
                stratum = np.flatnonzero((g_k == g) & (y_k == cls))
                drawn = np.sum(np.isin(index, stratum) & np.isin(index, stratum))
                resampled = index[np.isin(index, stratum)]
                assert len(resampled) == len(stratum)
    different = bp.bootstrap_index_streams(y_k, g_k, 25, 42, subject=4)
    assert any(
        not np.array_equal(a, b) for a, b in zip(streams1, different)
    )


# Test 14 — Phipson-Smyth p-values and Holm on deterministic toys.
def test_permutation_and_holm_toys():
    y_true = np.tile(np.arange(4), 12)
    groups = np.repeat(np.arange(2), 24)
    perfect = y_true.copy()
    out = bp.within_run_permutation_pvalue(y_true, perfect, groups, 200, 42, 1)
    assert out["p_raw"] >= 1 / 201  # never zero
    assert out["permutation_exceedances"] >= 0
    assert math.isclose(
        out["p_raw"], (out["permutation_exceedances"] + 1) / 201, rel_tol=1e-12
    )
    rng = np.random.default_rng(0)
    noise = rng.integers(0, 4, len(y_true))
    out2 = bp.within_run_permutation_pvalue(y_true, noise, groups, 200, 42, 1)
    assert out2["p_raw"] > 0.05  # independence not rejected on noise
    holm = bp.holm_adjust([0.01, 0.04, 0.03])
    np.testing.assert_allclose(holm, [0.03, 0.06, 0.06])
    assert np.all(bp.holm_adjust([0.9, 0.8, 0.99]) <= 1.0)


# --------------------------------------------------------------------------
# Fake final output builder for validator tests (15, 16)
# --------------------------------------------------------------------------

def build_fake_final(tmp_path: Path, kappa_scale: float = 1.0):
    """Construct an internally consistent fake final JSON + prediction CSVs."""
    predictions_dir = tmp_path / "predictions"
    predictions_dir.mkdir(exist_ok=True)
    tau = 8.0
    subjects = {}
    data_files = []
    for s in range(1, 10):
        for role in ("T", "E"):
            data_files.append(
                {
                    "name": f"A{s:02d}{role}.mat",
                    "source": "official BNCI 001-2014",
                    "bytes": 40_000_000,
                    "sha256": f"{s:02d}{role}{'0' * 60}"[:64].ljust(64, "a"),
                }
            )
    for s in range(1, 10):
        rng = np.random.default_rng(s)
        y_true, y_pred, rows = [], [], []
        for record_index in range(3, 9):
            run_idx = record_index - 3
            for j in range(48):
                truth = j % 4
                if rng.random() < 0.5 * kappa_scale:
                    pred = truth
                else:
                    pred = int(rng.integers(0, 4))
                uid = f"S{s:02d}:E:record{record_index:02d}:trial{j + 1:03d}"
                y_true.append(truth)
                y_pred.append(pred)
                s0 = 1000 + 800 * j
                rows.append(
                    [uid, f"S{s:02d}", "primary", "E", f"A{s:02d}E.mat",
                     data_files[(s - 1) * 2 + 1]["sha256"], record_index, run_idx,
                     j, s0 + 1, s0 + 500, s0 + 625, s0 + 1125, 0,
                     "clean_primary", vbo.CLASSES[truth], vbo.CLASSES[pred]]
                )
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        cm = np.zeros((4, 4), dtype=int)
        for t, p in zip(y_true, y_pred):
            cm[t, p] += 1
        comp = vbo.mi_components(cm)
        precision, recall, f1 = bp.precision_recall_f1(cm)
        support = cm.sum(axis=1)
        veff = {
            str(a): int(np.sum((f1 >= a) & (support >= 30)))
            for a in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        }
        exceed = 4
        decoder_result = {
            "name": "fake",
            "training_only_tuning": {
                "cv_scheme": "leave-one-source-run-out",
                "n_folds": 6,
                "fold_heldout_task_run": list(range(6)),
                "selected": 6,
            },
            **comp,
            "accuracy": float(np.mean(y_true == y_pred)),
            "accuracy_ci": [0.0, 1.0],
            "kappa": float(vbo.cohen_kappa(cm)),
            "kappa_ci": [-1.0, 1.0],
            "mi_ci_bits": [comp["mi_corrected_bits"] - 0.1, comp["mi_corrected_bits"] + 0.1],
            "mi_perm_p_raw": (exceed + 1) / 5001,
            "permutation_count": 5000,
            "permutation_exceedances": exceed,
            "permutation_scheme": "within-run",
            "bootstrap_count": 10_000,
            "bootstrap_scheme": "run x class",
            "inference_seed": {"master": 42},
            "tau_mean_sec": tau,
            "b_min_bpm": comp["mi_corrected_bits"] * 60.0 / tau,
            "b_min_ci_bpm": [
                (comp["mi_corrected_bits"] - 0.1) * 60.0 / tau,
                (comp["mi_corrected_bits"] + 0.1) * 60.0 / tau,
            ],
            "itr_bits_formula": 0.5,
            "itr_bpm": 0.5 * 60.0 / tau,
            "itr_bpm_clipped_at_chance": 0.5 * 60.0 / tau,
            "precision_per_class": precision.tolist(),
            "recall_per_class": recall.tolist(),
            "f1_per_class": f1.tolist(),
            "true_support_per_class": support.astype(int).tolist(),
            "predicted_support_per_class": cm.sum(axis=0).astype(int).tolist(),
            "veff_curve": veff,
            "veff_beta": 30,
            "confusion_matrix": cm.tolist(),
            "prediction_file": f"S{s:02d}_primary_predictions.csv",
            "prediction_sha256": "x",
            "all_scheduled_sensitivity": {
                "N": 288,
                "accuracy": float(np.mean(y_true == y_pred)),
                "kappa": float(vbo.cohen_kappa(cm)),
                "mi_plugin_bits": comp["mi_plugin_bits"],
                "mi_mm_correction_bits": comp["mi_mm_correction_bits"],
                "mi_corrected_bits": comp["mi_corrected_bits"],
                "confusion_matrix": cm.tolist(),
                "prediction_file": f"S{s:02d}_primary_predictions_all_scheduled.csv",
                "prediction_sha256": "x",
            },
        }
        csv_path = predictions_dir / f"S{s:02d}_primary_predictions.csv"
        with csv_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(bp.PREDICTION_COLUMNS)
            writer.writerows(rows)
        all_rows = [list(r) for r in rows]
        for r in all_rows:
            r[14] = "all_scheduled_sensitivity"
        all_path = predictions_dir / f"S{s:02d}_primary_predictions_all_scheduled.csv"
        with all_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(bp.PREDICTION_COLUMNS)
            writer.writerows(all_rows)

        fb = copy.deepcopy(decoder_result)
        fb["prediction_file"] = f"S{s:02d}_fbcsp_predictions.csv"
        fb["all_scheduled_sensitivity"] = copy.deepcopy(
            decoder_result["all_scheduled_sensitivity"]
        )
        fb["all_scheduled_sensitivity"]["prediction_file"] = (
            f"S{s:02d}_fbcsp_predictions_all_scheduled.csv"
        )
        for src, dst in (
            (csv_path, predictions_dir / fb["prediction_file"]),
            (all_path, predictions_dir / fb["all_scheduled_sensitivity"]["prediction_file"]),
        ):
            content = src.read_text().replace(",primary,", ",fbcsp,")
            dst.write_text(content)

        per_run = {
            f"record{r:02d}": {
                "task_run_index": r - 3, "n_trials": 48, "n_flagged": 0,
                "flagged_uids": [],
            }
            for r in range(3, 9)
        }
        by_class = dict.fromkeys(vbo.CLASSES, 72)
        subjects[f"S{s}"] = {
            "subject": f"S{s:02d}",
            "n_eeg_channels": 22,
            "excluded_channels": ["EOG1", "EOG2", "EOG3"],
            "artifact_accounting": {
                session: {
                    "n_all": 288, "n_clean": 288, "n_dropped": 0,
                    "all_by_class": by_class, "clean_by_class": by_class,
                    "dropped_by_class": dict.fromkeys(vbo.CLASSES, 0),
                    "retention": 1.0, "per_run": per_run,
                }
                for session in ("training", "evaluation")
            },
            "evaluation_cycle": {
                "n_within_run_intervals": 282, "tau_mean_sec": tau,
                "tau_sd_sec": 0.0, "tau_min_sec": tau, "tau_max_sec": tau,
            },
            "evaluation_within_run_intervals_sec": [tau] * 282,
            "timing_audit": {
                "evaluation": {
                    "cue_offset_samples": 500,
                    "epoch_start_offset_samples": 625,
                    "epoch_stop_offset_samples_inclusive": 1125,
                    "n_epoch_samples": 501,
                }
            },
            "decoders": {"primary": decoder_result, "fbcsp": fb},
        }
    raw = [subjects[f"S{s}"]["decoders"]["primary"]["mi_perm_p_raw"] for s in range(1, 10)]
    holm = vbo.holm_adjust(raw)
    for s, h in zip(range(1, 10), holm):
        subjects[f"S{s}"]["decoders"]["primary"]["mi_perm_p_holm"] = float(h)
        subjects[f"S{s}"]["decoders"]["fbcsp"]["mi_perm_p_holm"] = float(h)
    payload = {
        "schema_version": "4.1",
        "status": "complete",
        "result_kind": "final",
        "design_fingerprint": "f" * 64,
        "data_files": data_files,
        "subjects": subjects,
    }
    out = tmp_path / "final.json"
    out.write_text(json.dumps(payload, allow_nan=False))
    return out, payload


def run_validator(path: Path, mode="final"):
    return vbo.validate(path, mode, None, None)


# Test 16 first (the fixture sanity + no-performance-gate check).
def test_low_performance_output_is_not_rejected(tmp_path):
    """§14.16: a valid but poor decoder passes; no kappa/MI floor exists."""
    path, payload = build_fake_final(tmp_path, kappa_scale=0.0)  # ~chance level
    kappas = [
        payload["subjects"][f"S{s}"]["decoders"]["primary"]["kappa"]
        for s in range(1, 10)
    ]
    assert all(abs(k) < 0.25 for k in kappas)  # genuinely poor
    run_validator(path)  # must not raise


# Test 15 — tampered outputs must each fail the applicable gate.
@pytest.mark.parametrize(
    "tamper",
    [
        "swap_labels", "alter_cm_cell", "zero_pvalue", "drop_decoder",
        "reduced_inference", "duplicate_trial", "flagged_in_clean",
        "break_holm", "nonfinite_value", "smoke_as_final", "bad_timing_offset",
    ],
)
def test_tampered_outputs_fail(tmp_path, tamper):
    path, payload = build_fake_final(tmp_path)
    predictions_dir = tmp_path / "predictions"
    if tamper == "swap_labels":
        f = predictions_dir / "S03_primary_predictions.csv"
        rows = f.read_text().splitlines()
        rows[1], rows[2] = (
            rows[1].rsplit(",", 1)[0] + ",tongue",
            rows[2].rsplit(",", 1)[0] + ",feet",
        )
        f.write_text("\n".join(rows) + "\n")
    elif tamper == "alter_cm_cell":
        payload["subjects"]["S2"]["decoders"]["primary"]["confusion_matrix"][0][0] += 1
    elif tamper == "zero_pvalue":
        payload["subjects"]["S4"]["decoders"]["primary"]["mi_perm_p_raw"] = 0.0
    elif tamper == "drop_decoder":
        del payload["subjects"]["S5"]["decoders"]["fbcsp"]
    elif tamper == "reduced_inference":
        payload["subjects"]["S6"]["decoders"]["primary"]["bootstrap_count"] = 200
    elif tamper == "duplicate_trial":
        f = predictions_dir / "S07_primary_predictions.csv"
        rows = f.read_text().splitlines()
        rows.append(rows[1])
        f.write_text("\n".join(rows) + "\n")
    elif tamper == "flagged_in_clean":
        f = predictions_dir / "S08_primary_predictions.csv"
        text = f.read_text().splitlines()
        parts = text[1].split(",")
        parts[13] = "1"
        text[1] = ",".join(parts)
        f.write_text("\n".join(text) + "\n")
    elif tamper == "break_holm":
        payload["subjects"]["S9"]["decoders"]["primary"]["mi_perm_p_holm"] = 0.5
    elif tamper == "nonfinite_value":
        raw = json.dumps(payload, allow_nan=False)
        raw = raw.replace('"tau_mean_sec": 8.0', '"tau_mean_sec": NaN', 1)
        path.write_text(raw)
        with pytest.raises(SystemExit):
            run_validator(path)
        return
    elif tamper == "smoke_as_final":
        payload["result_kind"] = "smoke"
    elif tamper == "bad_timing_offset":
        payload["subjects"]["S1"]["timing_audit"]["evaluation"][
            "epoch_start_offset_samples"
        ] = 125  # missing +2 s offset
    path.write_text(json.dumps(payload, allow_nan=False))
    with pytest.raises(SystemExit):
        run_validator(path)


# Test 17 — resume fingerprints: changed config invalidates the freeze.
def test_design_fingerprint_sensitivity(tmp_path, monkeypatch):
    mat_dir = tmp_path / "mats"
    mat_dir.mkdir()
    for s in range(1, 10):
        for role in ("T", "E"):
            (mat_dir / f"A{s:02d}{role}.mat").write_bytes(bytes([s]) + role.encode())
    cfg_a = bp.BCIConfig()
    cfg_b = bp.BCIConfig(n_permutations=4_999)
    fp_a = bp.design_fingerprint(cfg_a, mat_dir)["fingerprint"]
    fp_b = bp.design_fingerprint(cfg_b, mat_dir)["fingerprint"]
    assert fp_a != fp_b
    assert fp_a == bp.design_fingerprint(cfg_a, mat_dir)["fingerprint"]
    freeze = {"design_fingerprint": fp_a, "freeze_utc": "x"}
    assert bp.verify_freeze(freeze, cfg_a, mat_dir) == fp_a
    with pytest.raises(RuntimeError):
        bp.verify_freeze(freeze, cfg_b, mat_dir)
    # data change invalidates too
    (mat_dir / "A01T.mat").write_bytes(b"changed")
    with pytest.raises(RuntimeError):
        bp.verify_freeze(freeze, cfg_a, mat_dir)


# Test 18 — figure error bars preserve actual interval endpoints.
def test_figure_preserves_interval_endpoints():
    import make_figures as mf
    point = np.array([0.5])
    interval = np.array([[0.8, 1.2]])  # point BELOW the interval
    segments = mf.interval_segments(point, interval)
    np.testing.assert_allclose(segments[0], [0.8, 1.2])  # endpoints untouched


# Test 19 — manuscript population is deterministic and marker-checked.
def test_populator_deterministic_and_marker_checked(tmp_path):
    import populate_bci_manuscript as pbm
    template = (
        "intro\n<!-- BCI_PRIMARY_TABLE_START -->old<!-- BCI_PRIMARY_TABLE_END -->\n"
        "<!-- BCI_PRIMARY_VEFF_TABLE_START -->old<!-- BCI_PRIMARY_VEFF_TABLE_END -->\n"
        "No pooled row is permitted as an operating-system claim.\n"
    )
    _, payload = build_fake_final(tmp_path)
    once = pbm.render(template, payload["subjects"])
    twice = pbm.render(template, payload["subjects"])
    assert once == twice  # deterministic
    assert "BCI_PRIMARY_TABLE_START" not in once
    with pytest.raises(SystemExit):
        pbm.render("no markers here", payload["subjects"])


# Test 20 — release manifest detects post-generation modification.
def test_release_manifest_detects_tamper(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    import build_release_manifest as brm
    staged = tmp_path / "staging"
    staged.mkdir()
    (staged / "a.txt").write_text("alpha")
    (staged / "b.txt").write_text("beta")
    manifest = staged / "RELEASE_MANIFEST_FINAL.json"
    brm.build(staged, manifest)
    listed = json.loads(manifest.read_text())
    assert sorted(e["path"] for e in listed["files"]) == ["a.txt", "b.txt"]
    assert brm.verify(staged, manifest) == []
    (staged / "b.txt").write_text("tampered")
    problems = brm.verify(staged, manifest)
    assert problems and "b.txt" in problems[0]
