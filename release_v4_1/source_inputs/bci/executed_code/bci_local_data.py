"""Direct local-MAT adapter for BNCI 001-2014 (BCI Competition IV-2a).

Production data path per audit/PROTOCOL_AMENDMENTS.md A1/A2 and handoff §5-§6.

Facts verified against pinned moabb 1.7.1 sources (hashes in audit/RUNLOG.md):
* ``run.trial`` holds MATLAB one-based sample indices of the TRIAL TRIGGER
  (trial onset, t=0 in the organizer timing diagram); the cue is at t=+2 s.
* ``run.X`` is microvolts; the pinned converter scales to volts once.
* 25 recorded channels: 22 EEG (ordered as below) + 3 EOG.
* Organizer artifact flags are per-trial in ``run.artifacts``.

Event anchor contract (amendment A2): events supplied to epoching are
trigger-anchored, so the fixed decision window 0.5-2.5 s post-cue is
2.5-4.5 s post-trigger. At 250 Hz with inclusive endpoints:
cue = s0+500, epoch samples [s0+625, s0+1125], n=501.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.io as sio

SFREQ = 250.0
N_RECORDED_CHANNELS = 25
N_EEG = 22
EEG_CHANNELS = (
    "Fz", "FC3", "FC1", "FCz", "FC2", "FC4", "C5", "C3", "C1", "Cz", "C2",
    "C4", "C6", "CP3", "CP1", "CPz", "CP2", "CP4", "P1", "Pz", "P2", "POz",
)
EOG_CHANNELS = ("EOG1", "EOG2", "EOG3")
CLASSES = ("left_hand", "right_hand", "feet", "tongue")
TRIALS_PER_RUN = 48
TASK_RUNS_PER_SESSION = 6
TRIALS_PER_CLASS_PER_RUN = 12
TRIALS_PER_SESSION = 288
WITHIN_RUN_INTERVALS = (TRIALS_PER_RUN - 1) * TASK_RUNS_PER_SESSION  # 282

# Timing constants (trigger anchor, amendment A2)
CUE_OFFSET_SAMPLES = 500          # +2.0 s
EPOCH_START_OFFSET = 625          # +2.5 s  (0.5 s post-cue)
EPOCH_STOP_OFFSET_INCLUSIVE = 1125  # +4.5 s (2.5 s post-cue), inclusive
EPOCH_N_SAMPLES = EPOCH_STOP_OFFSET_INCLUSIVE - EPOCH_START_OFFSET + 1  # 501


def normalize_class_name(name: object) -> str:
    text = str(name).strip().lower().replace("_", " ")
    text = " ".join(text.split())
    if text == "both feet":
        text = "feet"
    return text.replace(" ", "_")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass
class TaskRun:
    """One source task run, preserving its MAT record identity."""

    source_record_index: int      # index within the MAT ``data`` array
    task_run_index: int           # 0..5 among task runs, in source order
    X_uv: np.ndarray              # samples x 25 recorded channels, microvolts
    trial_samples_matlab: np.ndarray   # one-based trigger sample indices
    labels: np.ndarray            # 1..4, source values
    artifacts: np.ndarray         # per-trial organizer flags (0/1)
    fs: float
    class_names: tuple[str, ...]

    @property
    def trial_samples_zero_based(self) -> np.ndarray:
        return self.trial_samples_matlab - 1


@dataclass
class SessionData:
    subject: int
    session_role: str             # "T" or "E"
    source_file: str
    source_sha256: str
    task_runs: list[TaskRun]
    calibration_records: list[dict] = field(default_factory=list)


class SchemaError(RuntimeError):
    """A MAT file violates the source design contract (handoff §5.3)."""


def _as_1d_int(values, name: str) -> np.ndarray:
    arr = np.asarray(values).reshape(-1)
    if arr.size == 0:
        return arr.astype(np.int64)
    if not np.all(np.isfinite(arr.astype(float))):
        raise SchemaError(f"{name}: non-finite values")
    as_float = arr.astype(float)
    as_int = as_float.astype(np.int64)
    if not np.all(as_float == as_int):
        raise SchemaError(f"{name}: non-integer values")
    return as_int


def load_session(mat_path: Path, subject: int, session_role: str) -> SessionData:
    """Load and schema-validate one MAT session file (handoff §5.3)."""
    mat_path = Path(mat_path)
    payload = sio.loadmat(mat_path, struct_as_record=False, squeeze_me=True)
    if "data" not in payload:
        raise SchemaError(f"{mat_path.name}: no 'data' variable")
    records = np.atleast_1d(payload["data"])

    task_runs: list[TaskRun] = []
    calibration: list[dict] = []
    for record_index, run in enumerate(records):
        trials = _as_1d_int(getattr(run, "trial", []), f"record{record_index}.trial")
        X = np.asarray(run.X, dtype=np.float64)
        if X.ndim != 2 or X.shape[1] != N_RECORDED_CHANNELS:
            raise SchemaError(
                f"{mat_path.name} record{record_index}: X shape {X.shape}, "
                f"expected (*, {N_RECORDED_CHANNELS})"
            )
        fs = float(run.fs)
        if fs != SFREQ:
            raise SchemaError(f"{mat_path.name} record{record_index}: fs={fs}")
        if trials.size == 0:
            calibration.append(
                {"source_record_index": record_index, "n_samples": int(X.shape[0])}
            )
            continue

        labels = _as_1d_int(run.y, f"record{record_index}.y")
        if not hasattr(run, "artifacts"):
            raise SchemaError(
                f"{mat_path.name} record{record_index}: artifacts missing "
                "(must not be interpreted as all-clean)"
            )
        artifacts = _as_1d_int(run.artifacts, f"record{record_index}.artifacts")
        if not (len(trials) == len(labels) == len(artifacts) == TRIALS_PER_RUN):
            raise SchemaError(
                f"{mat_path.name} record{record_index}: trial/y/artifacts lengths "
                f"{len(trials)}/{len(labels)}/{len(artifacts)}, expected {TRIALS_PER_RUN}"
            )
        if not np.all(np.diff(trials) > 0):
            raise SchemaError(f"{mat_path.name} record{record_index}: triggers not strictly increasing")
        if trials[0] < 1 or trials[-1] > X.shape[0]:
            raise SchemaError(f"{mat_path.name} record{record_index}: trigger out of signal bounds")
        last_stop = (trials[-1] - 1) + EPOCH_STOP_OFFSET_INCLUSIVE
        if last_stop >= X.shape[0]:
            raise SchemaError(
                f"{mat_path.name} record{record_index}: final epoch stop {last_stop} "
                f"exceeds signal length {X.shape[0]}"
            )
        if not np.all(np.isin(labels, [1, 2, 3, 4])):
            raise SchemaError(f"{mat_path.name} record{record_index}: labels outside 1..4")
        counts = np.bincount(labels, minlength=5)[1:5]
        if not np.all(counts == TRIALS_PER_CLASS_PER_RUN):
            raise SchemaError(
                f"{mat_path.name} record{record_index}: per-class counts {counts.tolist()}"
            )
        if not np.all(np.isin(artifacts, [0, 1])):
            raise SchemaError(f"{mat_path.name} record{record_index}: artifact flags outside 0/1")
        class_names = tuple(
            normalize_class_name(x) for x in np.atleast_1d(run.classes)
        )
        if class_names != CLASSES:
            raise SchemaError(
                f"{mat_path.name} record{record_index}: classes {class_names} != {CLASSES}"
            )
        if not np.all(np.isfinite(X)):
            raise SchemaError(f"{mat_path.name} record{record_index}: non-finite samples")
        task_runs.append(
            TaskRun(
                source_record_index=record_index,
                task_run_index=len(task_runs),
                X_uv=X,
                trial_samples_matlab=trials,
                labels=labels,
                artifacts=artifacts,
                fs=fs,
                class_names=class_names,
            )
        )

    if len(task_runs) != TASK_RUNS_PER_SESSION:
        raise SchemaError(
            f"{mat_path.name}: {len(task_runs)} task runs, expected {TASK_RUNS_PER_SESSION}"
        )
    return SessionData(
        subject=subject,
        session_role=session_role,
        source_file=mat_path.name,
        source_sha256=sha256_file(mat_path),
        task_runs=task_runs,
        calibration_records=calibration,
    )


def trial_uid(subject: int, session_role: str, record_index: int, trial_index: int) -> str:
    return f"S{subject:02d}:{session_role}:record{record_index:02d}:trial{trial_index + 1:03d}"


def session_ledger_rows(session: SessionData) -> list[dict]:
    """Trial ledger per handoff §5.3, one row per source trial."""
    rows = []
    for run in session.task_runs:
        for j in range(TRIALS_PER_RUN):
            s_matlab = int(run.trial_samples_matlab[j])
            s0 = s_matlab - 1
            rows.append(
                {
                    "trial_uid": trial_uid(
                        session.subject, session.session_role,
                        run.source_record_index, j,
                    ),
                    "subject": f"S{session.subject:02d}",
                    "source_file": session.source_file,
                    "source_file_sha256": session.source_sha256,
                    "session_T_or_E": session.session_role,
                    "source_record_index": run.source_record_index,
                    "task_run_index": run.task_run_index,
                    "within_run_trial_index": j,
                    "trial_sample_matlab": s_matlab,
                    "trial_sample_zero_based": s0,
                    "cue_sample_zero_based": s0 + CUE_OFFSET_SAMPLES,
                    "source_label": int(run.labels[j]),
                    "canonical_class": CLASSES[int(run.labels[j]) - 1],
                    "artifact_flag": int(run.artifacts[j]),
                    "retained": int(run.artifacts[j]) == 0,
                    "exclusion_reason": (
                        "organizer_artifact_flag" if run.artifacts[j] else ""
                    ),
                    "epoch_start_sample": s0 + EPOCH_START_OFFSET,
                    "epoch_stop_sample_inclusive": s0 + EPOCH_STOP_OFFSET_INCLUSIVE,
                }
            )
    return rows


def within_run_intervals(session: SessionData) -> np.ndarray:
    """All within-run inter-trigger intervals in seconds, BEFORE exclusion.

    282 intervals under the six-run design (amendment A11). Anchors are
    homogeneous (all trial triggers); the fixed cue offset cancels.
    """
    intervals: list[float] = []
    for run in session.task_runs:
        intervals.extend(
            (np.diff(run.trial_samples_matlab) / run.fs).tolist()
        )
    out = np.asarray(intervals, dtype=float)
    if len(out) != WITHIN_RUN_INTERVALS:
        raise SchemaError(
            f"{session.source_file}: {len(out)} within-run intervals, "
            f"expected {WITHIN_RUN_INTERVALS}"
        )
    if not np.all(out > 0) or not np.all(np.isfinite(out)):
        raise SchemaError(f"{session.source_file}: non-positive or non-finite interval")
    return out
