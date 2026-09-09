"""Build and verify the final release manifest (handoff §18).

The manifest is generated LAST, hashes every payload file, and excludes
itself, archives, virtual environments, raw EEG, caches, and temp files.
It is an integrity inventory, not a digital signature.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

EXCLUDE_NAMES = {"RELEASE_MANIFEST_FINAL.json"}
EXCLUDE_SUFFIXES = {".zip", ".tar", ".gz", ".part", ".tmp", ".pyc"}
EXCLUDE_DIRS = {".venv-bci", ".git", "__pycache__", ".pytest_cache", "raw_data", "mne_data"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def payload_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
            continue
        if path.name.endswith(".mat"):
            continue  # raw EEG never redistributed in the archive
        files.append(path)
    return files


def build(root: Path, manifest_path: Path) -> dict:
    root = Path(root)
    entries = [
        {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in payload_files(root)
    ]
    manifest = {
        "kind": "integrity manifest (SHA-256 inventory; not a digital signature)",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "root": str(root),
        "n_files": len(entries),
        "files": entries,
    }
    with Path(manifest_path).open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, allow_nan=False)
    return manifest


def verify(root: Path, manifest_path: Path) -> list[str]:
    root = Path(root)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    problems = []
    listed = {entry["path"]: entry for entry in manifest["files"]}
    for rel, entry in listed.items():
        path = root / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        if path.stat().st_size != entry["bytes"]:
            problems.append(f"{rel}: size changed")
        elif sha256_file(path) != entry["sha256"]:
            problems.append(f"{rel}: sha256 changed")
    current = {str(p.relative_to(root)) for p in payload_files(root)}
    for extra in sorted(current - set(listed)):
        problems.append(f"{extra}: present but not in manifest")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = Path(args.manifest) if args.manifest else root / "RELEASE_MANIFEST_FINAL.json"
    if args.verify:
        problems = verify(root, manifest_path)
        if problems:
            raise SystemExit("Manifest verification failed:\n- " + "\n- ".join(problems))
        print(f"Manifest verified: {manifest_path}")
    else:
        manifest = build(root, manifest_path)
        print(f"Wrote {manifest_path} ({manifest['n_files']} files)")


if __name__ == "__main__":
    main()
