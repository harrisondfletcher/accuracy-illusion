"""One-command reproduction for the simulation package.

    python reproduce_all.py           full simulation, power, tables, figures, tests
    python reproduce_all.py --quick   clean-state core smoke run (no grid/power cache required)

The public-data BCI application is intentionally separate:
    python bci_pipeline.py
    python make_figures.py bci
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
PY = sys.executable


def run(*args):
    subprocess.check_call([PY, *args])


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(mode):
    files = []
    for root in (HERE / "results", HERE / "figures", HERE / "data", HERE / "protocol"):
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            files.append({"path": str(path.relative_to(HERE)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {"mode": mode, "python": sys.version, "files": files}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "reproduction_manifest.json").write_text(json.dumps(manifest, indent=1))


def main():
    quick = "--quick" in sys.argv
    core = ["table1", "null_models", "counterexamples", "sweep_noise", "equal_mi", "nonredundancy"]
    run("generate_worked_example.py")
    if quick:
        run("run_simulations.py", *core)
        run("make_figures.py", "fig1", "fig3")
        run("-m", "pytest", "-q", "tests/test_core.py")
        write_manifest("quick")
        print("quick reproduction complete")
        return

    run("run_simulations.py", *(core + ["grid", "tables"]))
    run("power_v3.py", "all")
    run("make_figures.py", "all")
    run("-m", "pytest", "-q", "tests/test_core.py")
    write_manifest("full")
    print("full simulation reproduction complete")


if __name__ == "__main__":
    main()
