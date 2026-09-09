"""Write the pre-E design freeze (handoff §9.2).

Records analysis configuration, code/data/environment identity, and the
combined design fingerprint. The evaluate phase refuses to run unless the
recomputed fingerprint matches. Run this only after the preflight and
train-smoke phases and before any E-session decoding.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bci_local_data import sha256_file  # noqa: E402
from bci_pipeline import (  # noqa: E402
    BCIConfig,
    design_fingerprint,
    utc_now,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mat-dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-bootstrap", type=int, default=10_000)
    parser.add_argument("--n-permutations", type=int, default=5_000)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    cfg = BCIConfig(
        n_bootstrap=args.n_bootstrap,
        n_permutations=args.n_permutations,
        random_seed=args.seed,
    )
    fp = design_fingerprint(cfg, Path(args.mat_dir).resolve())

    amendments = project_root / "audit" / "PROTOCOL_AMENDMENTS.md"
    freeze = {
        "freeze_utc": utc_now(),
        "design_fingerprint": fp["fingerprint"],
        "fingerprint_payload": fp["payload"],
        "amendments_sha256": sha256_file(amendments),
        "registration_note": (
            "Revision-stage analysis of a public dataset with accessible E "
            "labels; frozen before any E-session decoding performance was "
            "computed. Not a newly preregistered unseen study."
        ),
    }
    config_path = project_root / "analysis_config.json"
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(cfg), handle, indent=2, allow_nan=False)
    freeze_path = project_root / "audit" / "DESIGN_FREEZE.json"
    with freeze_path.open("w", encoding="utf-8") as handle:
        json.dump(freeze, handle, indent=2, allow_nan=False)
    print(f"fingerprint: {fp['fingerprint']}")
    print(f"frozen at:   {freeze['freeze_utc']}")
    print(f"wrote {config_path} and {freeze_path}")


if __name__ == "__main__":
    main()
