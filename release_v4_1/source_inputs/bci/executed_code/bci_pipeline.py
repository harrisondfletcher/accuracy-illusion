"""Supplementary Code S1b: rigorous BCI Competition IV-2a re-analysis.

Revision-4 completion build. Production data path is the direct local-MAT
adapter (``bci_local_data``); the MOABB loader is retained only as an audit
reference. All methodological changes from the previously shipped version are
recorded in ``audit/PROTOCOL_AMENDMENTS.md`` (A1-A14) and were adopted before
any E-session performance was computed.

Contract highlights
-------------------
* Event anchor: MAT trial trigger; epoch = trigger+2.5..4.5 s inclusive
  (= 0.5..2.5 s post-cue), 501 samples at 250 Hz. (A2)
* Artifact policy: explicit organizer ``run.artifacts`` mask; set-equality of
  flagged and excluded trial UIDs. (A1)
* Training CV: six-fold leave-one-source-run-out on T. (A3)
* Permutation test: plug-in MI statistic, within-run label permutation,
  Phipson-Smyth correction. (A4)
* Bootstrap: (run x class)-stratified, index streams shared across decoders
  for paired contrasts. (A5)
* Phases: preflight | train-smoke | evaluate; evaluate requires a frozen
  design fingerprint; --resume accepts only matching checkpoints. (A8)
* No performance-based admission gate anywhere. (A10)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.metadata as metadata
import json
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import mne
import numpy as np
from mne.decoding import CSP
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import cohen_kappa_score, confusion_matrix, make_scorer
from sklearn.model_selection import GridSearchCV, LeaveOneGroupOut
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from bci_local_data import (
    CLASSES,
    CUE_OFFSET_SAMPLES,
    EEG_CHANNELS,
    EPOCH_N_SAMPLES,
    EPOCH_START_OFFSET,
    EPOCH_STOP_OFFSET_INCLUSIVE,
    SFREQ,
    SessionData,
    load_session,
    session_ledger_rows,
    sha256_file,
    trial_uid,
    within_run_intervals,
)

SCHEMA_VERSION = "4.1"
SEED_DEFAULT = 42
K = len(CLASSES)
LN2 = math.log(2.0)
FILTERBANK_BANDS = tuple((float(lo), float(lo + 4)) for lo in range(4, 40, 4))
VEFF_ALPHAS = (0.40, 0.50, 0.60, 0.70, 0.80, 0.90)

# SeedSequence operation codes (A6)
OP_BOOTSTRAP = 1
OP_PERMUTATION = 2

MICROVOLT_TO_VOLT = 1e-6


@dataclass(frozen=True)
class BCIConfig:
    epoch_tmin_postcue: float = 0.5
    epoch_tmax_postcue: float = 2.5
    event_anchor: str = "mat_trial_trigger"
    epoch_tmin_post_trigger: float = 2.5
    epoch_tmax_post_trigger: float = 4.5
    primary_fmin: float = 8.0
    primary_fmax: float = 30.0
    primary_component_grid: tuple[int, ...] = (4, 6, 8)
    fbcsp_components_per_class_band: int = 4
    fbcsp_feature_grid: tuple[int, ...] = (16, 32, 64, 96)
    cv_scheme: str = "leave-one-source-run-out"
    tie_rule: str = "first-best-in-ascending-grid (simpler candidate wins ties)"
    csp_regularization: str = "ledoit_wolf"
    veff_beta: int = 30
    n_bootstrap: int = 10_000
    n_permutations: int = 5_000
    bootstrap_scheme: str = "stratified by (E source run x true class), paired across decoders"
    permutation_scheme: str = (
        "true labels permuted within each source E run against frozen "
        "predictions; statistic = plug-in MI; Phipson-Smyth (1+exceed)/(B+1)"
    )
    artifact_policy: str = "organizer run.artifacts mask, explicit exclusion"
    random_seed: int = SEED_DEFAULT


# --------------------------------------------------------------------------
# Environment / provenance helpers
# --------------------------------------------------------------------------

def software_versions() -> dict[str, str | None]:
    names = ("moabb", "mne", "scikit-learn", "numpy", "scipy", "matplotlib")
    out: dict[str, str | None] = {}
    for name in names:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def code_hashes() -> dict[str, str]:
    here = Path(__file__).resolve().parent
    return {
        name: sha256_file(here / name)
        for name in ("bci_pipeline.py", "bci_local_data.py")
    }


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json_atomic(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, allow_nan=False)
    tmp.replace(path)


# --------------------------------------------------------------------------
# Data assembly (local MAT adapter)
# --------------------------------------------------------------------------

def filter_specification(l_freq: float, h_freq: float, n_times: int = 20_000) -> dict:
    kernel = mne.filter.create_filter(
        np.zeros((1, n_times), dtype=float),
        sfreq=SFREQ,
        l_freq=l_freq,
        h_freq=h_freq,
        method="fir",
        phase="zero",
        fir_design="firwin",
        filter_length="auto",
        l_trans_bandwidth="auto",
        h_trans_bandwidth="auto",
        verbose=False,
    )
    return {
        "l_freq_hz": l_freq,
        "h_freq_hz": h_freq,
        "method": "fir",
        "phase": "zero",
        "fir_design": "firwin",
        "filter_length": "auto",
        "l_trans_bandwidth": "auto",
        "h_trans_bandwidth": "auto",
        "resolved_n_taps": int(kernel.shape[-1]),
        "kernel_sha256": sha256_text(kernel.tobytes().hex()),
        "sampling_rate_hz": SFREQ,
    }


def epoch_session_band(
    session: SessionData, l_freq: float, h_freq: float
) -> dict:
    """Filter each source run independently, then slice fixed epochs.

    Returns ALL scheduled trials in source order with UIDs, labels (0..3),
    organizer artifact flags, and LOGO group indices. No exclusion here;
    retention masks are applied by callers so clean/sensitivity subsets share
    one extraction path.
    """
    epochs = []
    labels = []
    flags = []
    groups = []
    uids = []
    for run in session.task_runs:
        eeg_uv = run.X_uv[:, : len(EEG_CHANNELS)]  # first 22 channels are EEG
        data = np.ascontiguousarray(eeg_uv.T) * MICROVOLT_TO_VOLT
        filtered = mne.filter.filter_data(
            data,
            sfreq=run.fs,
            l_freq=l_freq,
            h_freq=h_freq,
            method="fir",
            phase="zero",
            fir_design="firwin",
            filter_length="auto",
            l_trans_bandwidth="auto",
            h_trans_bandwidth="auto",
            verbose=False,
        )
        for j, s_matlab in enumerate(run.trial_samples_matlab):
            s0 = int(s_matlab) - 1
            start = s0 + EPOCH_START_OFFSET
            stop_inclusive = s0 + EPOCH_STOP_OFFSET_INCLUSIVE
            window = filtered[:, start : stop_inclusive + 1]
            if window.shape[1] != EPOCH_N_SAMPLES:
                raise RuntimeError(
                    f"{session.source_file} record{run.source_record_index} "
                    f"trial{j + 1}: epoch has {window.shape[1]} samples"
                )
            if not np.all(np.isfinite(window)):
                raise RuntimeError(
                    f"{session.source_file} record{run.source_record_index} "
                    f"trial{j + 1}: non-finite epoch samples"
                )
            epochs.append(window.astype(np.float64))
            labels.append(int(run.labels[j]) - 1)
            flags.append(int(run.artifacts[j]))
            groups.append(run.task_run_index)
            uids.append(
                trial_uid(
                    session.subject,
                    session.session_role,
                    run.source_record_index,
                    j,
                )
            )
    return {
        "X": np.stack(epochs, axis=0),
        "y": np.asarray(labels, dtype=int),
        "artifact_flags": np.asarray(flags, dtype=int),
        "groups": np.asarray(groups, dtype=int),
        "uids": uids,
        "filter": filter_specification(l_freq, h_freq),
    }


def artifact_accounting(session: SessionData) -> dict:
    per_run = {}
    all_by = dict.fromkeys(CLASSES, 0)
    clean_by = dict.fromkeys(CLASSES, 0)
    for run in session.task_runs:
        flagged_uids = [
            trial_uid(session.subject, session.session_role, run.source_record_index, j)
            for j in np.flatnonzero(run.artifacts).tolist()
        ]
        per_run[f"record{run.source_record_index:02d}"] = {
            "task_run_index": run.task_run_index,
            "n_trials": int(len(run.labels)),
            "n_flagged": int(run.artifacts.sum()),
            "flagged_uids": flagged_uids,
        }
        for j, label in enumerate(run.labels):
            name = CLASSES[int(label) - 1]
            all_by[name] += 1
            if run.artifacts[j] == 0:
                clean_by[name] += 1
    n_all = sum(all_by.values())
    n_clean = sum(clean_by.values())
    return {
        "n_all": n_all,
        "n_clean": n_clean,
        "n_dropped": n_all - n_clean,
        "all_by_class": all_by,
        "clean_by_class": clean_by,
        "dropped_by_class": {name: all_by[name] - clean_by[name] for name in CLASSES},
        "retention": n_clean / n_all,
        "per_run": per_run,
        "policy": "organizer run.artifacts mask, explicit exclusion",
    }


def cycle_summary(session: SessionData) -> dict:
    within = within_run_intervals(session)
    return {
        "n_within_run_intervals": int(len(within)),
        "tau_mean_sec": float(np.mean(within)),
        "tau_sd_sec": float(np.std(within, ddof=1)),
        "tau_min_sec": float(np.min(within)),
        "tau_max_sec": float(np.max(within)),
        "scope": (
            "all six task runs, all scheduled trials, before artifact "
            "exclusion; within-run inter-trigger differences (fixed cue "
            "offset cancels); inter-run gaps excluded by run identity"
        ),
    }


def timing_audit(session: SessionData) -> dict:
    first = session.task_runs[0]
    s0 = int(first.trial_samples_matlab[0]) - 1
    return {
        "event_anchor": "mat_trial_trigger",
        "convention": (
            "trigger at zero-based s0; cue = s0+500; epoch samples "
            "[s0+625, s0+1125] inclusive; 501 samples; 250 Hz"
        ),
        "cue_offset_samples": CUE_OFFSET_SAMPLES,
        "epoch_start_offset_samples": EPOCH_START_OFFSET,
        "epoch_stop_offset_samples_inclusive": EPOCH_STOP_OFFSET_INCLUSIVE,
        "n_epoch_samples": EPOCH_N_SAMPLES,
        "first_trial_example": {
            "trial_sample_matlab": int(first.trial_samples_matlab[0]),
            "trial_sample_zero_based": s0,
            "cue_sample_zero_based": s0 + CUE_OFFSET_SAMPLES,
            "first_epoch_sample": s0 + EPOCH_START_OFFSET,
            "last_epoch_sample_inclusive": s0 + EPOCH_STOP_OFFSET_INCLUSIVE,
        },
    }


# --------------------------------------------------------------------------
# Decoders
# --------------------------------------------------------------------------

def primary_estimator(n_components: int):
    return OneVsRestClassifier(
        Pipeline(
            [
                (
                    "csp",
                    CSP(
                        n_components=n_components,
                        reg="ledoit_wolf",
                        log=True,
                        norm_trace=False,
                        cov_est="concat",
                    ),
                ),
                ("lda", LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
            ]
        ),
        n_jobs=1,
    )


def check_fold_class_coverage(y: np.ndarray, groups: np.ndarray) -> None:
    for held_out in np.unique(groups):
        y_fit = y[groups != held_out]
        if len(np.unique(y_fit)) != K:
            raise RuntimeError(
                f"training fold holding out group {held_out} lacks a class"
            )


def cv_evidence(search: GridSearchCV, param_name: str, groups: np.ndarray) -> dict:
    results = search.cv_results_
    n_folds = sum(1 for key in results if key.startswith("split") and key.endswith("_test_score"))
    return {
        "cv_scheme": "leave-one-source-run-out",
        "n_folds": n_folds,
        "fold_heldout_task_run": [int(g) for g in np.unique(groups)],
        "candidates": [
            {
                "value": int(params[param_name]),
                "mean_kappa": float(results["mean_test_score"][i]),
                "sd_kappa": float(results["std_test_score"][i]),
                "fold_kappas": [
                    float(results[f"split{f}_test_score"][i]) for f in range(n_folds)
                ],
            }
            for i, params in enumerate(results["params"])
        ],
        "tie_rule": "first best value in ascending grid order (simpler wins ties)",
        "selected": int(search.best_params_[param_name]),
        "selected_mean_kappa": float(search.best_score_),
    }


def fit_primary(X_train, y_train, groups, cfg: BCIConfig):
    check_fold_class_coverage(y_train, groups)
    search = GridSearchCV(
        primary_estimator(cfg.primary_component_grid[0]),
        {"estimator__csp__n_components": list(cfg.primary_component_grid)},
        scoring=make_scorer(cohen_kappa_score),
        cv=LeaveOneGroupOut(),
        refit=True,
        n_jobs=1,
        return_train_score=False,
    )
    search.fit(X_train, y_train, groups=groups)
    tuning = cv_evidence(search, "estimator__csp__n_components", groups)
    tuning["candidate_components"] = list(cfg.primary_component_grid)
    return search.best_estimator_, tuning


class OVRFilterBankCSP(BaseEstimator, TransformerMixin):
    """Binary one-vs-rest CSP for every filter band and target class."""

    def __init__(self, n_components: int = 4, reg: str = "ledoit_wolf"):
        self.n_components = n_components
        self.reg = reg

    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)
        if X.ndim != 4:
            raise ValueError("Expected X with shape epochs x bands x channels x time")
        self.classes_ = np.unique(y)
        self.models_ = []
        for band in range(X.shape[1]):
            row = []
            for target in self.classes_:
                model = CSP(
                    n_components=self.n_components,
                    reg=self.reg,
                    log=True,
                    norm_trace=False,
                    cov_est="concat",
                )
                model.fit(X[:, band], (y == target).astype(int))
                row.append(model)
            self.models_.append(row)
        return self

    def transform(self, X):
        X = np.asarray(X)
        return np.concatenate(
            [
                model.transform(X[:, band])
                for band, row in enumerate(self.models_)
                for model in row
            ],
            axis=1,
        )


def deterministic_mutual_information(X, y):
    return mutual_info_classif(X, y, random_state=SEED_DEFAULT)


def fit_fbcsp(X_train, y_train, groups, cfg: BCIConfig):
    check_fold_class_coverage(y_train, groups)
    total_features = len(FILTERBANK_BANDS) * K * cfg.fbcsp_components_per_class_band
    candidate_k = [k for k in cfg.fbcsp_feature_grid if k <= total_features]
    if not candidate_k:
        raise ValueError("No admissible FBCSP feature-count candidate")
    estimator = Pipeline(
        [
            (
                "fbcsp",
                OVRFilterBankCSP(
                    n_components=cfg.fbcsp_components_per_class_band,
                    reg=cfg.csp_regularization,
                ),
            ),
            ("select", SelectKBest(deterministic_mutual_information, k=candidate_k[0])),
            ("lda", LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
        ]
    )
    search = GridSearchCV(
        estimator,
        {"select__k": candidate_k},
        scoring=make_scorer(cohen_kappa_score),
        cv=LeaveOneGroupOut(),
        refit=True,
        n_jobs=1,
        return_train_score=False,
    )
    search.fit(X_train, y_train, groups=groups)
    tuning = cv_evidence(search, "select__k", groups)
    tuning.update(
        bands_hz=[list(x) for x in FILTERBANK_BANDS],
        csp_components_per_class_band=cfg.fbcsp_components_per_class_band,
        total_preselection_features=total_features,
        candidate_feature_counts=candidate_k,
    )
    selector = search.best_estimator_.named_steps["select"]
    support = np.flatnonzero(selector.get_support()).tolist()
    n_comp = cfg.fbcsp_components_per_class_band
    tuning["selected_feature_indices"] = support
    tuning["selected_feature_map"] = [
        {
            "index": int(idx),
            "band_hz": list(FILTERBANK_BANDS[idx // (K * n_comp)]),
            "ovr_class": CLASSES[(idx % (K * n_comp)) // n_comp],
            "csp_component": int(idx % n_comp),
        }
        for idx in support
    ]
    return search.best_estimator_, tuning


# --------------------------------------------------------------------------
# Metrics and inference
# --------------------------------------------------------------------------

def mi_components(cm: np.ndarray) -> dict:
    cm = np.asarray(cm, dtype=float)
    n = float(cm.sum())
    if n <= 0:
        raise ValueError("Empty confusion matrix")
    joint = cm / n
    py = joint.sum(axis=1, keepdims=True)
    pz = joint.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        plugin = float(
            np.where(joint > 0, joint * np.log2(joint / (py * pz)), 0.0).sum()
        )
    k_yz = int((joint > 0).sum())
    k_y = int((py > 0).sum())
    k_z = int((pz > 0).sum())
    correction = (k_yz - k_y - k_z + 1) / (2.0 * n * LN2)
    return {
        "mi_plugin_bits": plugin,
        "mi_mm_correction_bits": float(correction),
        "mi_corrected_bits": float(plugin - correction),
        "K_y": k_y,
        "K_z": k_z,
        "K_yz": k_yz,
        "N": int(n),
    }


def plugin_mi(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(K))
    return mi_components(cm)["mi_plugin_bits"]


def precision_recall_f1(cm: np.ndarray):
    cm = np.asarray(cm, dtype=float)
    tp = np.diag(cm)
    fp = cm.sum(axis=0) - tp
    fn = cm.sum(axis=1) - tp
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        recall = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f1 = np.where(
            precision + recall > 0,
            2 * precision * recall / (precision + recall),
            0.0,
        )
    return precision, recall, f1


def veff_curve(cm: np.ndarray, beta: int) -> dict[str, int]:
    _, _, f1 = precision_recall_f1(cm)
    support = np.asarray(cm).sum(axis=1)
    return {
        str(alpha): int(np.sum((f1 >= alpha) & (support >= beta)))
        for alpha in VEFF_ALPHAS
    }


def itr_bits_formula(accuracy: float, n_classes: int = K) -> float:
    """Wolpaw symmetric-channel formula with 0log0=0 endpoint conventions.

    No below-chance clipping here (A7); the clipped presentation value is a
    separately named field.
    """
    if accuracy <= 0.0:
        return math.log2(n_classes) + math.log2(1.0 / (n_classes - 1))
    if accuracy >= 1.0:
        return math.log2(n_classes)
    return (
        math.log2(n_classes)
        + accuracy * math.log2(accuracy)
        + (1 - accuracy) * math.log2((1 - accuracy) / (n_classes - 1))
    )


def stratified_bootstrap_indices(
    y: np.ndarray, groups: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Resample within each (source run x true class) stratum (A5)."""
    parts = []
    for g in np.unique(groups):
        for cls in np.unique(y):
            idx = np.flatnonzero((groups == g) & (y == cls))
            if len(idx):
                parts.append(rng.choice(idx, size=len(idx), replace=True))
    return np.concatenate(parts)


def bootstrap_index_streams(
    y: np.ndarray, groups: np.ndarray, n_bootstrap: int, master_seed: int, subject: int
) -> list[np.ndarray]:
    """Deterministic per-subject bootstrap indices, shared by both decoders."""
    rng = np.random.default_rng(
        np.random.SeedSequence([master_seed, subject, OP_BOOTSTRAP])
    )
    return [stratified_bootstrap_indices(y, groups, rng) for _ in range(n_bootstrap)]


def within_run_permutation_pvalue(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    n_permutations: int,
    master_seed: int,
    subject: int,
) -> dict:
    """Plug-in-MI permutation test, labels permuted within each run (A4)."""
    rng = np.random.default_rng(
        np.random.SeedSequence([master_seed, subject, OP_PERMUTATION])
    )
    observed = plugin_mi(y_true, y_pred)
    run_indices = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    exceed = 0
    permuted = y_true.copy()
    for _ in range(n_permutations):
        for idx in run_indices:
            permuted[idx] = y_true[idx][rng.permutation(len(idx))]
        if plugin_mi(permuted, y_pred) >= observed - 1e-12:
            exceed += 1
    return {
        "statistic": "plug-in MI (bits)",
        "observed_plugin_mi_bits": observed,
        "permutation_count": int(n_permutations),
        "permutation_exceedances": int(exceed),
        "p_raw": (exceed + 1) / (n_permutations + 1),
        "tie_tolerance": 1e-12,
    }


def evaluate_decoder(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    tau_mean_sec: float,
    cfg: BCIConfig,
    boot_indices: list[np.ndarray],
    subject: int,
) -> dict:
    labels = np.arange(K)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    observed = mi_components(cm)
    boot = np.empty((len(boot_indices), 3), dtype=float)
    for b, index in enumerate(boot_indices):
        cm_b = confusion_matrix(y_true[index], y_pred[index], labels=labels)
        boot[b, 0] = mi_components(cm_b)["mi_corrected_bits"]
        boot[b, 1] = float(np.mean(y_true[index] == y_pred[index]))
        boot[b, 2] = float(cohen_kappa_score(y_true[index], y_pred[index], labels=labels))

    perm = within_run_permutation_pvalue(
        y_true, y_pred, groups, cfg.n_permutations, cfg.random_seed, subject
    )
    accuracy = float(np.mean(y_true == y_pred))
    kappa = float(cohen_kappa_score(y_true, y_pred, labels=labels))
    precision, recall, f1 = precision_recall_f1(cm)
    tau_min = tau_mean_sec / 60.0
    mi_lo, mi_hi = np.quantile(boot[:, 0], [0.025, 0.975])
    itr_formula = itr_bits_formula(accuracy)
    chance = 1.0 / K
    return {
        **observed,
        "accuracy": accuracy,
        "accuracy_ci": np.quantile(boot[:, 1], [0.025, 0.975]).tolist(),
        "kappa": kappa,
        "kappa_ci": np.quantile(boot[:, 2], [0.025, 0.975]).tolist(),
        "mi_ci_bits": [float(mi_lo), float(mi_hi)],
        "mi_perm_p_raw": float(perm["p_raw"]),
        "permutation_count": perm["permutation_count"],
        "permutation_exceedances": perm["permutation_exceedances"],
        "permutation_scheme": cfg.permutation_scheme,
        "permutation_statistic_plugin_mi_bits": perm["observed_plugin_mi_bits"],
        "bootstrap_count": int(len(boot_indices)),
        "bootstrap_scheme": cfg.bootstrap_scheme,
        "inference_seed": {
            "master": cfg.random_seed,
            "derivation": "numpy SeedSequence [master, subject, op]",
            "op_bootstrap": OP_BOOTSTRAP,
            "op_permutation": OP_PERMUTATION,
        },
        "tau_mean_sec": float(tau_mean_sec),
        "b_min_bpm": float(observed["mi_corrected_bits"] / tau_min),
        "b_min_ci_bpm": [float(mi_lo / tau_min), float(mi_hi / tau_min)],
        "itr_bits_formula": float(itr_formula),
        "itr_bpm": float(itr_formula / tau_min),
        "itr_bpm_clipped_at_chance": float(
            (itr_formula if accuracy > chance else 0.0) / tau_min
        ),
        "itr_interpretation": (
            "accuracy-based symmetric-channel reference assuming uniform "
            "classes; not a substitute for confusion-matrix MI; clipped field "
            "sets the value to 0 when accuracy <= 1/K"
        ),
        "precision_per_class": precision.tolist(),
        "recall_per_class": recall.tolist(),
        "f1_per_class": f1.tolist(),
        "true_support_per_class": np.asarray(cm).sum(axis=1).astype(int).tolist(),
        "predicted_support_per_class": np.asarray(cm).sum(axis=0).astype(int).tolist(),
        "veff_curve": veff_curve(cm, cfg.veff_beta),
        "veff_beta": cfg.veff_beta,
        "confusion_matrix": cm.tolist(),
    }


def holm_adjust(p_values: list[float]) -> np.ndarray:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted_ordered = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order])
    adjusted_ordered = np.minimum(adjusted_ordered, 1.0)
    adjusted = np.empty_like(p)
    adjusted[order] = adjusted_ordered
    return adjusted


# --------------------------------------------------------------------------
# Prediction records
# --------------------------------------------------------------------------

PREDICTION_COLUMNS = (
    "trial_uid", "subject", "decoder", "session_T_or_E", "source_file",
    "source_file_sha256", "source_record_index", "task_run_index",
    "within_run_trial_index", "trial_sample_matlab", "cue_sample_zero_based",
    "epoch_start_sample", "epoch_stop_sample_inclusive", "artifact_flag",
    "analysis_role", "true_class", "predicted_class",
)


def write_predictions_csv(
    path: Path,
    subject: int,
    decoder: str,
    ledger_by_uid: dict[str, dict],
    uids: list[str],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    role: str,
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(PREDICTION_COLUMNS)
        for uid, truth, predicted in zip(uids, y_true, y_pred):
            row = ledger_by_uid[uid]
            if CLASSES[int(truth)] != row["canonical_class"]:
                raise RuntimeError(f"{uid}: truth/ledger mismatch")
            writer.writerow(
                [
                    uid, f"S{subject:02d}", decoder, row["session_T_or_E"],
                    row["source_file"], row["source_file_sha256"],
                    row["source_record_index"], row["task_run_index"],
                    row["within_run_trial_index"], row["trial_sample_matlab"],
                    row["cue_sample_zero_based"], row["epoch_start_sample"],
                    row["epoch_stop_sample_inclusive"], row["artifact_flag"],
                    role, CLASSES[int(truth)], CLASSES[int(predicted)],
                ]
            )
    return sha256_file(path)


# --------------------------------------------------------------------------
# Subject execution
# --------------------------------------------------------------------------

def load_subject(mat_dir: Path, subject: int) -> tuple[SessionData, SessionData]:
    t_path = mat_dir / f"A{subject:02d}T.mat"
    e_path = mat_dir / f"A{subject:02d}E.mat"
    train = load_session(t_path, subject, "T")
    test = load_session(e_path, subject, "E")
    if train.source_sha256 == test.source_sha256:
        raise RuntimeError(f"S{subject}: T and E resolve to identical files")
    return train, test


def subject_preflight_record(train: SessionData, test: SessionData) -> dict:
    return {
        "subject": f"S{train.subject:02d}",
        "sessions": {
            "training": {"source_file": train.source_file, "sha256": train.source_sha256},
            "evaluation": {"source_file": test.source_file, "sha256": test.source_sha256},
        },
        "calibration_records": {
            "training": train.calibration_records,
            "evaluation": test.calibration_records,
        },
        "task_run_records": {
            "training": [r.source_record_index for r in train.task_runs],
            "evaluation": [r.source_record_index for r in test.task_runs],
        },
        "n_eeg_channels": len(EEG_CHANNELS),
        "eeg_channel_names": list(EEG_CHANNELS),
        "excluded_channels": ["EOG1", "EOG2", "EOG3"],
        "artifact_accounting": {
            "training": artifact_accounting(train),
            "evaluation": artifact_accounting(test),
        },
        "evaluation_cycle": cycle_summary(test),
        "evaluation_within_run_intervals_sec": within_run_intervals(test).tolist(),
        "timing_audit": {
            "training": timing_audit(train),
            "evaluation": timing_audit(test),
        },
    }


def run_subject_evaluate(
    train: SessionData,
    test: SessionData,
    decoders: tuple[str, ...],
    cfg: BCIConfig,
    predictions_dir: Path,
) -> dict:
    subject = train.subject
    ledger_rows = session_ledger_rows(train) + session_ledger_rows(test)
    ledger_by_uid = {row["trial_uid"]: row for row in ledger_rows}
    test_cycle = cycle_summary(test)

    result = subject_preflight_record(train, test)
    result["decoders"] = {}

    # --- extract primary band ---
    train_primary = epoch_session_band(train, cfg.primary_fmin, cfg.primary_fmax)
    test_primary = epoch_session_band(test, cfg.primary_fmin, cfg.primary_fmax)
    result["primary_filter"] = train_primary["filter"]

    train_clean = train_primary["artifact_flags"] == 0
    test_clean = test_primary["artifact_flags"] == 0

    # A1 gate evidence: flagged set == excluded set, by UID.
    for band_data, session in ((train_primary, train), (test_primary, test)):
        flagged = {
            uid
            for uid, flag in zip(band_data["uids"], band_data["artifact_flags"])
            if flag
        }
        ledger_flagged = {
            row["trial_uid"]
            for row in session_ledger_rows(session)
            if row["artifact_flag"]
        }
        if flagged != ledger_flagged:
            raise RuntimeError(f"S{subject}: artifact UID set mismatch")

    y_train = train_primary["y"][train_clean]
    g_train = train_primary["groups"][train_clean]
    y_test = test_primary["y"][test_clean]
    g_test = test_primary["groups"][test_clean]
    clean_test_uids = [u for u, keep in zip(test_primary["uids"], test_clean) if keep]

    boot_indices = bootstrap_index_streams(
        y_test, g_test, cfg.n_bootstrap, cfg.random_seed, subject
    )

    def finish_decoder(name: str, estimator, tuning: dict, X_test_clean, X_test_all):
        y_pred = estimator.predict(X_test_clean)
        metrics = evaluate_decoder(
            y_test, y_pred, g_test, test_cycle["tau_mean_sec"], cfg,
            boot_indices, subject,
        )
        clean_csv = predictions_dir / f"S{subject:02d}_{name}_predictions.csv"
        clean_sha = write_predictions_csv(
            clean_csv, subject, name, ledger_by_uid, clean_test_uids,
            y_test, y_pred, "clean_primary",
        )
        # A12 prespecified sensitivity: frozen model, all scheduled epochs.
        y_pred_all = estimator.predict(X_test_all)
        cm_all = confusion_matrix(
            test_primary["y"], y_pred_all, labels=np.arange(K)
        )
        all_csv = predictions_dir / f"S{subject:02d}_{name}_predictions_all_scheduled.csv"
        all_sha = write_predictions_csv(
            all_csv, subject, name, ledger_by_uid, test_primary["uids"],
            test_primary["y"], y_pred_all, "all_scheduled_sensitivity",
        )
        sens = mi_components(cm_all)
        return {
            "training_only_tuning": tuning,
            **metrics,
            "prediction_file": str(clean_csv.name),
            "prediction_sha256": clean_sha,
            "all_scheduled_sensitivity": {
                "note": (
                    "frozen decoder applied to every scheduled E epoch, "
                    "organizer-flagged included; no refit or selection"
                ),
                "N": sens["N"],
                "accuracy": float(np.mean(test_primary["y"] == y_pred_all)),
                "kappa": float(
                    cohen_kappa_score(
                        test_primary["y"], y_pred_all, labels=np.arange(K)
                    )
                ),
                "mi_plugin_bits": sens["mi_plugin_bits"],
                "mi_mm_correction_bits": sens["mi_mm_correction_bits"],
                "mi_corrected_bits": sens["mi_corrected_bits"],
                "confusion_matrix": cm_all.tolist(),
                "prediction_file": str(all_csv.name),
                "prediction_sha256": all_sha,
            },
        }

    if "primary" in decoders:
        estimator, tuning = fit_primary(
            train_primary["X"][train_clean], y_train, g_train, cfg
        )
        result["decoders"]["primary"] = {
            "name": "fixed-window OVR-CSP + shrinkage LDA",
            **finish_decoder(
                "primary", estimator, tuning,
                test_primary["X"][test_clean], test_primary["X"],
            ),
        }

    if "fbcsp" in decoders:
        train_bands, test_bands, band_specs = [], [], []
        for l_freq, h_freq in FILTERBANK_BANDS:
            tr = epoch_session_band(train, l_freq, h_freq)
            te = epoch_session_band(test, l_freq, h_freq)
            if tr["uids"] != train_primary["uids"] or te["uids"] != test_primary["uids"]:
                raise RuntimeError(
                    f"S{subject}: epoch UID ordering differs in band {l_freq:g}-{h_freq:g}"
                )
            train_bands.append(tr["X"].astype(np.float32))
            test_bands.append(te["X"].astype(np.float32))
            band_specs.append(tr["filter"])
        X_train_fb = np.stack(train_bands, axis=1)
        X_test_fb = np.stack(test_bands, axis=1)
        del train_bands, test_bands
        estimator, tuning = fit_fbcsp(
            X_train_fb[train_clean], y_train, g_train, cfg
        )
        result["decoders"]["fbcsp"] = {
            "name": "nine-band FBCSP-style robustness decoder",
            "scope_note": "not an exact reproduction of Ang et al. (2012)",
            "filter_specs": band_specs,
            **finish_decoder(
                "fbcsp", estimator, tuning,
                X_test_fb[test_clean], X_test_fb,
            ),
        }
    return result


def run_subject_smoke(
    train: SessionData,
    decoders: tuple[str, ...],
    cfg: BCIConfig,
    predictions_dir: Path,
) -> dict:
    """Engineering smoke test on T only; the last T run is a temporary holdout.

    No E file is opened in this phase. Metrics here are engineering output,
    result_kind=smoke, ineligible for manuscript population.
    """
    subject = train.subject
    ledger_by_uid = {row["trial_uid"]: row for row in session_ledger_rows(train)}
    band = epoch_session_band(train, cfg.primary_fmin, cfg.primary_fmax)
    holdout_group = int(band["groups"].max())
    is_holdout = band["groups"] == holdout_group
    clean = band["artifact_flags"] == 0

    fit_mask = clean & ~is_holdout
    eval_mask = clean & is_holdout
    y_fit = band["y"][fit_mask]
    g_fit = band["groups"][fit_mask]
    y_eval = band["y"][eval_mask]
    g_eval = band["groups"][eval_mask]
    eval_uids = [u for u, keep in zip(band["uids"], eval_mask) if keep]

    # duration surrogate: within-run intervals of the training session
    within = within_run_intervals(train)
    tau = float(np.mean(within))
    boot_indices = bootstrap_index_streams(
        y_eval, g_eval, cfg.n_bootstrap, cfg.random_seed, subject
    )

    record = {
        "subject": f"S{subject:02d}",
        "smoke_holdout_task_run_index": holdout_group,
        "n_fit_trials": int(fit_mask.sum()),
        "n_holdout_trials": int(eval_mask.sum()),
        "decoders": {},
    }
    if "primary" in decoders:
        estimator, tuning = fit_primary(band["X"][fit_mask], y_fit, g_fit, cfg)
        y_pred = estimator.predict(band["X"][eval_mask])
        metrics = evaluate_decoder(
            y_eval, y_pred, g_eval, tau, cfg, boot_indices, subject
        )
        csv_path = predictions_dir / f"S{subject:02d}_primary_smoke_predictions.csv"
        sha = write_predictions_csv(
            csv_path, subject, "primary", ledger_by_uid, eval_uids,
            y_eval, y_pred, "smoke_T_holdout",
        )
        record["decoders"]["primary"] = {
            "training_only_tuning": tuning, **metrics,
            "prediction_file": str(csv_path.name), "prediction_sha256": sha,
        }
    if "fbcsp" in decoders:
        bands = [
            epoch_session_band(train, lo, hi)["X"].astype(np.float32)
            for lo, hi in FILTERBANK_BANDS
        ]
        X_fb = np.stack(bands, axis=1)
        del bands
        estimator, tuning = fit_fbcsp(X_fb[fit_mask], y_fit, g_fit, cfg)
        y_pred = estimator.predict(X_fb[eval_mask])
        metrics = evaluate_decoder(
            y_eval, y_pred, g_eval, tau, cfg, boot_indices, subject
        )
        csv_path = predictions_dir / f"S{subject:02d}_fbcsp_smoke_predictions.csv"
        sha = write_predictions_csv(
            csv_path, subject, "fbcsp", ledger_by_uid, eval_uids,
            y_eval, y_pred, "smoke_T_holdout",
        )
        record["decoders"]["fbcsp"] = {
            "training_only_tuning": tuning, **metrics,
            "prediction_file": str(csv_path.name), "prediction_sha256": sha,
        }
    return record


# --------------------------------------------------------------------------
# Freeze / fingerprint / checkpoints
# --------------------------------------------------------------------------

def data_file_inventory(mat_dir: Path) -> list[dict]:
    files = []
    for s in range(1, 10):
        for role in ("T", "E"):
            path = mat_dir / f"A{s:02d}{role}.mat"
            files.append(
                {
                    "name": path.name,
                    "source": "official BNCI 001-2014",
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return files


def design_fingerprint(cfg: BCIConfig, mat_dir: Path) -> dict:
    inventory = data_file_inventory(mat_dir)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "config": asdict(cfg),
        "code_sha256": code_hashes(),
        "software_versions": software_versions(),
        "data_files": inventory,
    }
    return {
        "fingerprint": sha256_text(canonical_json(payload)),
        "payload": payload,
    }


def load_freeze(project_root: Path) -> dict:
    path = project_root / "audit" / "DESIGN_FREEZE.json"
    if not path.exists():
        raise RuntimeError(
            "evaluate phase requires audit/DESIGN_FREEZE.json; run "
            "tools/freeze_design.py after the smoke phase"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def verify_freeze(freeze: dict, cfg: BCIConfig, mat_dir: Path) -> str:
    current = design_fingerprint(cfg, mat_dir)
    if current["fingerprint"] != freeze["design_fingerprint"]:
        raise RuntimeError(
            "design fingerprint mismatch: configuration, code, environment, "
            "or data changed after freeze; re-freeze deliberately or restore"
        )
    return freeze["design_fingerprint"]


def checkpoint_path(run_dir: Path, subject: int) -> Path:
    return run_dir / "checkpoints" / f"S{subject:02d}.json"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_subjects(value: str) -> list[int]:
    if value == "1-9":
        return list(range(1, 10))
    subjects = [int(item) for item in value.split(",") if item.strip()]
    if not subjects or any(subject < 1 or subject > 9 for subject in subjects):
        raise argparse.ArgumentTypeError("subjects must be 1-9 or a comma list within 1..9")
    return subjects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mat-dir", required=True)
    parser.add_argument("--subjects", default="1-9")
    parser.add_argument(
        "--decoders", nargs="+", choices=("primary", "fbcsp"),
        default=("primary", "fbcsp"),
    )
    parser.add_argument(
        "--phase", required=True, choices=("preflight", "train-smoke", "evaluate")
    )
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    parser.add_argument("--n-bootstrap", type=int, default=10_000)
    parser.add_argument("--n-permutations", type=int, default=5_000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--mne-log-level", default="ERROR")
    args = parser.parse_args()

    mne.set_log_level(args.mne_log_level)
    mat_dir = Path(args.mat_dir).resolve()
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subjects = parse_subjects(args.subjects)
    decoders = tuple(args.decoders)
    project_root = Path(__file__).resolve().parent
    cfg = BCIConfig(
        n_bootstrap=args.n_bootstrap,
        n_permutations=args.n_permutations,
        random_seed=args.seed,
    )

    result_kind = {"preflight": "preflight", "train-smoke": "smoke", "evaluate": "final"}[args.phase]
    results: dict = {
        "schema_version": SCHEMA_VERSION,
        "status": "running",
        "result_kind": result_kind,
        "phase": args.phase,
        "dataset": {
            "name": "BNCI2014_001 / BCI Competition IV Dataset 2a",
            "subjects": subjects,
            "class_order": list(CLASSES),
            "scope": "subject-specific session-T training and session-E evaluation",
            "data_path_mode": "local MAT adapter (bci_local_data)",
        },
        "class_order": list(CLASSES),
        "config": asdict(cfg),
        "software_versions": software_versions(),
        "source_code_sha256": code_hashes(),
        "data_files": data_file_inventory(mat_dir),
        "published_benchmark_context": {
            "Ang_2012_OVR_CSP_mean_evaluation_kappa": 0.503,
            "Ang_2012_OVR_FBCSP_mean_evaluation_kappa": 0.569,
            "comparability_note": (
                "Ang et al. used a causal, time-resolved competition "
                "evaluation scored by maximum kappa; these values are "
                "context, not fixed-window acceptance targets."
            ),
        },
        "run_started_utc": utc_now(),
        "run_completed_utc": None,
        "analysis_freeze_utc": None,
        "design_fingerprint": None,
        "subjects": {},
        "validation_report": None,
    }

    fingerprint = None
    if args.phase == "evaluate":
        freeze = load_freeze(project_root)
        fingerprint = verify_freeze(freeze, cfg, mat_dir)
        results["design_fingerprint"] = fingerprint
        results["analysis_freeze_utc"] = freeze["freeze_utc"]

    predictions_dir = run_dir / "predictions"
    predictions_dir.mkdir(parents=True, exist_ok=True)

    try:
        for subject in subjects:
            started = time.time()
            print(f"[{args.phase}] S{subject}: {', '.join(decoders)}", flush=True)

            if args.phase == "evaluate":
                cp = checkpoint_path(run_dir, subject)
                if args.resume and cp.exists():
                    saved = json.loads(cp.read_text(encoding="utf-8"))
                    if saved.get("design_fingerprint") == fingerprint and set(
                        saved.get("record", {}).get("decoders", {})
                    ) >= set(decoders):
                        print(f"  resume: checkpoint accepted for S{subject}")
                        results["subjects"][f"S{subject}"] = saved["record"]
                        continue
                    print(f"  resume: checkpoint for S{subject} incompatible; recomputing")
                train, test = load_subject(mat_dir, subject)
                record = run_subject_evaluate(train, test, decoders, cfg, predictions_dir)
                record["runtime_sec"] = float(time.time() - started)
                write_json_atomic(
                    cp,
                    {"design_fingerprint": fingerprint, "record": record},
                )
                results["subjects"][f"S{subject}"] = record
            elif args.phase == "train-smoke":
                train = load_session(mat_dir / f"A{subject:02d}T.mat", subject, "T")
                record = run_subject_smoke(train, decoders, cfg, predictions_dir)
                record["runtime_sec"] = float(time.time() - started)
                results["subjects"][f"S{subject}"] = record
            else:  # preflight
                train, test = load_subject(mat_dir, subject)
                record = subject_preflight_record(train, test)
                record["runtime_sec"] = float(time.time() - started)
                results["subjects"][f"S{subject}"] = record

            write_json_atomic(output_path, results)

        if args.phase != "preflight":
            for decoder in decoders:
                raw_p = [
                    results["subjects"][f"S{subject}"]["decoders"][decoder]["mi_perm_p_raw"]
                    for subject in subjects
                ]
                adjusted = holm_adjust(raw_p)
                for subject, p_adjusted in zip(subjects, adjusted):
                    results["subjects"][f"S{subject}"]["decoders"][decoder][
                        "mi_perm_p_holm"
                    ] = float(p_adjusted)
            results["holm_family_note"] = (
                f"Holm applied within decoder across the {len(subjects)} "
                "subject tests of this run; primary and fbcsp are separate "
                "prespecified families"
            )

        if args.phase == "preflight":
            ledger_path = run_dir / "trial_ledger.csv"
            all_rows: list[dict] = []
            for subject in subjects:
                train, test = load_subject(mat_dir, subject)
                all_rows.extend(session_ledger_rows(train))
                all_rows.extend(session_ledger_rows(test))
            with ledger_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(all_rows[0].keys()))
                writer.writeheader()
                writer.writerows(all_rows)
            results["trial_ledger"] = {
                "path": str(ledger_path.name),
                "sha256": sha256_file(ledger_path),
                "n_rows": len(all_rows),
            }

        results["status"] = "complete"
        results["completed_subjects"] = len(subjects)
        results["run_completed_utc"] = utc_now()
        write_json_atomic(output_path, results)
        print(f"Wrote {output_path}")
    except Exception as error:
        results["status"] = "failed"
        results["error"] = repr(error)
        results["run_completed_utc"] = utc_now()
        write_json_atomic(output_path, results)
        raise


if __name__ == "__main__":
    main()
