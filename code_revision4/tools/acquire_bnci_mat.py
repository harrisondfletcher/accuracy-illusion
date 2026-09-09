"""Acquire and authenticate the 18 official BNCI 001-2014 MAT files.

Handoff §5.2 contract: reuse verified local files (labeled
``existing_local_file``); otherwise download with TLS verification to a
``.part`` temporary, validate by MAT parsing + schema audit, and rename
atomically. Parse/schema validation is decisive; byte size is diagnostic only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bci_local_data import SchemaError, load_session, sha256_file  # noqa: E402

BASE_URL = "https://bnci-horizon-2020.eu/database/data-sets/001-2014/"
EXPECTED = [
    (s, role, f"A{s:02d}{role}.mat")
    for s in range(1, 10)
    for role in ("T", "E")
]


def validate_file(path: Path, subject: int, role: str) -> dict:
    """Decisive validation: full MAT parse + schema audit."""
    session = load_session(path, subject, role)
    return {
        "parse_status": "ok",
        "task_runs": len(session.task_runs),
        "calibration_records": len(session.calibration_records),
        "n_trials": sum(len(r.labels) for r in session.task_runs),
        "n_artifact_flagged": int(
            sum(int(r.artifacts.sum()) for r in session.task_runs)
        ),
    }


def download(url: str, dest_part: Path, timeout: float = 60.0) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "bci-acquire/1.0"})
    attempts = 0
    last_error = None
    while attempts < 5:
        attempts += 1
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                final_url = response.geturl()
                with dest_part.open("wb") as handle:
                    shutil.copyfileobj(response, handle)
            return {"final_url": final_url, "attempts": attempts}
        except Exception as error:  # noqa: BLE001 — bounded retry, recorded
            last_error = repr(error)
    raise RuntimeError(f"download failed after {attempts} attempts: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    directory = Path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    entries = []
    failures = []
    for subject, role, name in EXPECTED:
        path = directory / name
        url = BASE_URL + name
        entry: dict = {"name": name, "subject": subject, "session": role,
                       "requested_url": url}
        if path.exists():
            try:
                checks = validate_file(path, subject, role)
                entry.update(
                    source="existing_local_file",
                    bytes=path.stat().st_size,
                    sha256=sha256_file(path),
                    **checks,
                )
                entries.append(entry)
                print(f"ok existing {name} ({entry['bytes']} bytes)")
                continue
            except (SchemaError, OSError, ValueError, KeyError) as error:
                print(f"existing {name} failed validation ({error!r}); re-downloading")
                path.unlink()
        try:
            with tempfile.NamedTemporaryFile(
                dir=directory, prefix=name + ".", suffix=".part", delete=False
            ) as tmp:
                part = Path(tmp.name)
            meta = download(url, part)
            checks = validate_file(part, subject, role)
            part.rename(path)
            entry.update(
                source="downloaded",
                retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                bytes=path.stat().st_size,
                sha256=sha256_file(path),
                **meta,
                **checks,
            )
            entries.append(entry)
            print(f"ok downloaded {name}")
        except Exception as error:  # noqa: BLE001 — recorded as blocker
            part.unlink(missing_ok=True)
            failures.append({"name": name, "url": url, "error": repr(error)})
            print(f"FAILED {name}: {error!r}")

    manifest = {
        "dataset": "BNCI 001-2014 / BCI Competition IV Dataset 2a",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "directory": str(directory.resolve()),
        "n_expected": len(EXPECTED),
        "n_validated": len(entries),
        "files": entries,
        "failures": failures,
    }
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.manifest).open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, allow_nan=False)
    print(f"manifest: {args.manifest} ({len(entries)}/{len(EXPECTED)} validated)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
