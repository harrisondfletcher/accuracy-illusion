import math
import numpy as np

from engine_v2 import SimConfig, run_sim, mi_plugin_and_mm, u_selectivity, run_batch


def test_paired_base_channel_is_exact():
    cfg = SimConfig()
    mem = run_sim("memorizer", cfg, 12345)
    comp = run_sim("compositional", cfg, 12345)
    assert mem.accuracy_base == comp.accuracy_base
    assert mem.mi == comp.mi
    assert mem.b_min == comp.b_min
    assert mem.veff == comp.veff


def test_grammar_partition_not_an_inert_grid_factor():
    fields = SimConfig.__dataclass_fields__
    assert "comp_split" not in fields
    assert "grammar_train_frac" not in fields
    assert "heldout_eval_frac" in fields
    low = run_sim("memorizer", SimConfig(N=2000, heldout_eval_frac=0.2), 42)
    high = run_sim("memorizer", SimConfig(N=2000, heldout_eval_frac=0.8), 42)
    assert high.c2_n > low.c2_n


def test_allocation_respects_base_override():
    cfg = SimConfig(N=1000, n_base_override=600)
    assert cfg.allocation() == (600, 150, 200, 50)


def test_miller_madow_is_not_truncated():
    cm = np.array([[25, 25], [25, 25]])
    plugin, corrected, n = mi_plugin_and_mm(cm)
    assert plugin == 0.0
    assert corrected < 0.0
    assert n == 100


def test_uncertainty_empty_stratum_is_nan():
    u, *_ = u_selectivity(np.array([0, 1, 0]), np.array([1, 1, 1]))
    assert math.isnan(u)


def test_class_biased_matches_analytic_s1():
    cfg = SimConfig(N=5000, zipf_s=1.0)
    result = run_batch("class_biased", cfg, 100, seed0=9)
    K = 12
    weights = 1 / np.arange(1, K + 1)
    weights /= weights.sum()
    top3 = np.sort(weights)[::-1][:3].sum()
    expected = top3 * 0.90 + (1 - top3) / K
    assert abs(result["accuracy_base"]["mean"] - expected) < 0.015


def test_equal_mi_construction_avoids_threshold_equality():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "results" / "equal_mi_matrices.json"
    data = json.loads(path.read_text())
    assert data["beta"][0][0] == 0.81
    assert data["f1_beta"][0] > 0.80
    assert data["f1_beta"][2] < 0.80
    assert data["veff80_alpha"] == 4
    assert data["veff80_beta"] == 2
    assert abs(data["mi_alpha"] - data["mi_beta"]) < 1e-12


def test_grid_has_no_nominal_split_factor():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "results" / "grid.json"
    data = json.loads(path.read_text())
    assert data["summary"]["n_cells"] == 480
    assert "grammar_train_frac" not in data["summary"]
    assert all("grammar_train_frac" not in cell for cell in data["cells"])


def test_bci_pipeline_is_explicit_local_mat_contract():
    """Amended per audit/PROTOCOL_AMENDMENTS.md A1/A2: the production path is
    the local-MAT adapter with an explicit organizer artifact mask; MOABB
    annotation-based rejection (which silently rejected nothing in "ignore"
    mode) is retired."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    pipeline = (root / "bci_pipeline.py").read_text()
    adapter = (root / "bci_local_data.py").read_text()
    assert "from bci_local_data import" in pipeline
    assert "artifact_flags" in pipeline
    assert "artifact_handling" not in pipeline  # annotation path retired
    assert "reject_by_annotation" not in pipeline
    assert "EPOCH_START_OFFSET = 625" in adapter
    assert "EPOCH_STOP_OFFSET_INCLUSIVE = 1125" in adapter
    assert "WITHIN_RUN_INTERVALS = (TRIALS_PER_RUN - 1) * TASK_RUNS_PER_SESSION" in adapter
    assert "artifacts missing" in adapter  # missing flags are a hard failure
