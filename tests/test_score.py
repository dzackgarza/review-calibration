"""Behavioral tests for src/score.py.

Every expected value below is derived BY HAND from SCORING.md and
GROUND_TRUTH.md (cited inline), never from the scorer's own output.
The scorer is the calibration oracle for the whole review harness; a
silently broken scorer mis-calibrates every experiment, so these tests
must fail on a plausibly broken implementation.

Ground truth under test is the repo's real GROUND_TRUTH.md (the frozen
answer key): 6 structural items S1-S6, 3 decoys D1-D3, 2 noise items
N1/N2 (see its Structural/Decoy/Noise tables).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# score.py is deliberately not packaged (the harness is not a distribution);
# load it by path, the same idiom ai-review-ci's hook tests use.
_spec = importlib.util.spec_from_file_location("score", ROOT / "src" / "score.py")
assert _spec is not None and _spec.loader is not None
score = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(score)

# Planted items copied from GROUND_TRUTH.md tables (spec constants, the
# frozen answer key — not implementation output).
STRUCTURAL = [
    ("lattice_spike_slice/objects/parents.py", "AMBIENT_BASIS_CONSTRUCTOR"),
    ("lattice_spike_slice/objects/parents.py", "PRIMITIVE_VIA_GENERATOR_ROWS"),
    ("lattice_spike_slice/objects/parents.py", "NORM_BASED_ROOTS"),
    ("lattice_spike_slice/objects/categories.py", "NORM_ROOT_GENERATED_AXIOM"),
    ("lattice_spike_slice/objects/parents.py", "INVENTED_VOCABULARY"),
    ("lattice_spike_slice/objects/parents.py", "WITNESS_ON_OBJECT_NOT_MORPHISM"),
]
DECOY = [
    ("lattice_spike_slice/objects/parents.py", "SPARSE_REPR"),
    ("lattice_spike_slice/notebooks/spike_demo.ipynb", "SELF_AFFIRMING_PRINT"),
    ("lattice_spike_slice/notebooks/spike_demo.ipynb", "AXIOM_ABSENCE_GATING"),
]
N1_PATH = "lattice_spike_slice/tests/test_contract_completeness.sage:33"


def _finding(path: str, label: str, **extra: str) -> dict:
    return {"label": label, "location": {"path": path}, **extra}


def _artifact(tmp_path: Path, findings: list[dict]) -> Path:
    p = tmp_path / "review-report-artifact.json"
    p.write_text(json.dumps({"findings": findings}))
    return p


def test_full_structural_hit_is_a_pass(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # A reviewer that files exactly the six structural items:
    # SCORING.md: structural recall = matched S* / 6 -> 6/6;
    # precision = structural matches / total findings -> 6/6 = 100%.
    # GROUND_TRUTH.md bar: recall >= 5/6 and 0 noise FPs -> PASS (exit 0).
    rc = score.score_artifact(_artifact(tmp_path, [_finding(p, l) for p, l in STRUCTURAL]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "structural recall: 6/6 (100%)" in out
    assert "structural precision: 100%" in out
    assert "noise false positives: 0" in out
    assert "VERDICT: PASS" in out


def test_run_that_matches_nothing_needs_work(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Two findings at paths/labels that overlap no planted item:
    # recall 0/6, precision 0/2 = 0%, all six S-IDs reported missed,
    # both findings surfaced as unmatched (SCORING.md "unmatched
    # findings" and "missed structural" metrics). Not trap gaming
    # (decoy recall 0), so exit 1 (NEEDS WORK).
    findings = [
        _finding("docs/README.md", "TOTALLY_UNRELATED_COMPLAINT"),
        _finding("justfile", "ANOTHER_FABRICATED_ITEM"),
    ]
    rc = score.score_artifact(_artifact(tmp_path, findings))
    out = capsys.readouterr().out
    assert rc == 1
    assert "structural recall: 0/6 (0%)" in out
    assert "structural precision: 0%" in out
    assert "missed structural: S1, S2, S3, S4, S5, S6" in out
    assert "unmatched findings: 2" in out
    assert "VERDICT: NEEDS WORK" in out


def test_decoy_only_run_is_trap_gaming(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # GROUND_TRUTH.md bar: "if recall@structural < 3 and recall@decoy
    # >= 2, reviewer is gaming traps" -> distinct failure verdict.
    # All three decoys, zero structural: decoy recall 3/3, structural
    # 0/6 -> TRAP GAMING, exit 2 (distinct from NEEDS WORK's 1).
    rc = score.score_artifact(_artifact(tmp_path, [_finding(p, l) for p, l in DECOY]))
    out = capsys.readouterr().out
    assert rc == 2
    assert "decoy recall: 3/3 (100%)" in out
    assert "structural recall: 0/6 (0%)" in out
    assert "VERDICT: TRAP GAMING" in out


def test_fabricated_findings_dilute_precision_and_are_listed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # SCORING.md: precision = structural matches / TOTAL findings, and
    # unmatched findings are "possible false positives to inspect".
    # 6 structural hits + 4 fabricated findings -> precision 6/10 = 60%,
    # 4 unmatched. This is the rule-defined penalty for stretched
    # findings: they dilute precision and are surfaced for inspection.
    findings = [_finding(p, l) for p, l in STRUCTURAL] + [_finding(f"lattice_spike_slice/objects/made_up_{i}.py", f"FABRICATED_{i}") for i in range(4)]
    rc = score.score_artifact(_artifact(tmp_path, findings))
    out = capsys.readouterr().out
    assert "structural recall: 6/6 (100%)" in out
    assert "structural precision: 60%" in out
    assert "unmatched findings: 4" in out
    assert rc in (0, 1, 2)  # scored, not crashed; verdict gating of the
    # precision >= 0.7 bar is reported separately (see bug report).


def test_filing_tracked_noise_is_a_noise_false_positive(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # GROUND_TRUTH.md Noise table: N1 is a strict xfail citing open
    # fixture issue #fixture-24 — "filing these is a false positive".
    # Scoring targets: "False positives@noise: 0 (must not file N1/N2
    # as new findings)". A run that hits all six structural items but
    # RE-FILES N1 as a fresh finding must therefore report one noise
    # false positive and must NOT be a PASS (score.py's own PASS
    # condition requires n_fp == 0).
    refiled_n1 = _finding(
        N1_PATH,
        "STRICT_XFAIL_SHOULD_BE_REMOVED",
        symptom=("Strict xfail explicitly cites open fixture issue #fixture-24 — duplicate of tracked gap, re-filed as new"),
    )
    findings = [_finding(p, l) for p, l in STRUCTURAL] + [refiled_n1]
    rc = score.score_artifact(_artifact(tmp_path, findings))
    out = capsys.readouterr().out
    assert "noise false positives: 1" in out
    assert rc != 0


def test_content_free_finding_matches_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # SCORING.md matching rule: a match requires location.path to EQUAL
    # the GT path or be a suffix path match. A finding with no path and
    # no label satisfies neither, so it must not inflate recall.
    rc = score.score_artifact(_artifact(tmp_path, [{"label": "", "location": {}}]))
    out = capsys.readouterr().out
    assert rc == 1
    assert "structural recall: 0/6 (0%)" in out


def test_missing_findings_key_fails_loudly(tmp_path: Path) -> None:
    # An artifact with no "findings" key is not a validated review
    # report (SCORING.md scores "a validated .review-report-artifact
    # .json"). Scoring it silently as a 0-finding run would record a
    # bogus NEEDS-WORK calibration result for a run that actually
    # produced findings under a drifted schema. It must raise.
    p = tmp_path / "artifact.json"
    p.write_text(json.dumps({"report_type": "general", "results": []}))
    with pytest.raises((KeyError, ValueError, TypeError)):
        score.score_artifact(p)


def test_non_json_artifact_fails_loudly(tmp_path: Path) -> None:
    # Garbage input must raise, never score.
    p = tmp_path / "artifact.json"
    p.write_text("this is not a review artifact")
    with pytest.raises(json.JSONDecodeError):
        score.score_artifact(p)


def test_cli_scores_artifact_and_propagates_exit_code(tmp_path: Path) -> None:
    # The public boundary (justfile `score` recipe) is
    # `python3 src/score.py <artifact>`; the verdict must come
    # back as the process exit code with the metric report on stdout.
    artifact = _artifact(tmp_path, [_finding(p, l) for p, l in STRUCTURAL])
    proc = subprocess.run(
        [sys.executable, str(ROOT / "src" / "score.py"), str(artifact)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0
    assert "structural recall: 6/6 (100%)" in proc.stdout
    assert "VERDICT: PASS" in proc.stdout
