"""Per-file trigger-schedule audit for BNCI 001-2014 (read-only).

Documents, for each of the 18 source MAT files, the 282 within-run
inter-trigger intervals: vector SHA-256, mean/SD/min/max, and unique-value
count. Supports the manuscript claim that all files share one fixed
pseudorandom trigger schedule. Deliberately independent of the pipeline so
the frozen design fingerprint is untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import scipy.io as sio


def intervals(path: Path) -> np.ndarray:
    payload = sio.loadmat(path, struct_as_record=False, squeeze_me=True)
    out: list[int] = []
    for run in np.atleast_1d(payload["data"]):
        trials = np.atleast_1d(run.trial)
        if trials.size and trials.dtype != object:
            out.extend(np.diff(trials.astype(np.int64)).tolist())
    return np.asarray(out, dtype=np.int64)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mat-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    mat_dir = Path(args.mat_dir)
    entries = []
    vector_hashes = set()
    for s in range(1, 10):
        for role in ("T", "E"):
            name = f"A{s:02d}{role}.mat"
            vec = intervals(mat_dir / name)
            sec = vec / 250.0
            digest = hashlib.sha256(vec.tobytes()).hexdigest()
            vector_hashes.add(digest)
            entries.append(
                {
                    "file": name,
                    "n_within_run_intervals": int(len(vec)),
                    "interval_vector_sha256": digest,
                    "mean_sec": float(sec.mean()),
                    "sd_sec": float(sec.std(ddof=1)),
                    "min_sec": float(sec.min()),
                    "max_sec": float(sec.max()),
                    "n_unique_values": int(len(np.unique(vec))),
                }
            )
    report = {
        "dataset": "BNCI 001-2014 / BCI Competition IV Dataset 2a",
        "sampling_rate_hz": 250.0,
        "n_files": len(entries),
        "n_distinct_interval_vectors": len(vector_hashes),
        "conclusion": (
            "all files share one identical trigger-interval sequence"
            if len(vector_hashes) == 1
            else "files DO NOT share a single trigger schedule"
        ),
        "files": entries,
    }
    with Path(args.output).open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
    print(
        f"{len(entries)} files, {len(vector_hashes)} distinct interval "
        f"vector(s); wrote {args.output}"
    )
    sys.exit(0 if len(vector_hashes) == 1 else 1)


if __name__ == "__main__":
    main()
