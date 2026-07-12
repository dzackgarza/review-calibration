#!/usr/bin/env python3
"""Score a review artifact against GROUND_TRUTH.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]

ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH = ROOT / "GROUND_TRUTH.md"

_NARRATIVE_KEYS = ("violated_invariant", "symptom", "pattern", "slop_narrative", "task_narrative")


class Finding:
    """Total model of one reviewer finding, normalized once at the parse boundary.

    Reviewer artifacts are external input: label, narrative fields, and
    location are genuinely optional in the domain — a content-free finding
    is VALID input that must simply match nothing (pinned by
    test_content_free_finding_matches_nothing). Absence is normalized to ""
    exactly once, in _parse_finding; every field is total downstream.

    Plain class, not a dataclass: the test suite loads this module by path
    without registering it in sys.modules, which breaks dataclass field
    resolution on Python 3.14.
    """

    __slots__ = ("label", "narrative", "path", "start_line")

    def __init__(self, label: str, narrative: str, path: str, start_line: str) -> None:
        self.label = label
        self.narrative = narrative
        self.path = path
        self.start_line = start_line


def _parse_finding(raw: object) -> Finding:
    assert isinstance(raw, dict), f"each finding must be a mapping, got {type(raw).__name__}: {raw!r}"
    loc = raw["location"] if "location" in raw else {}
    assert isinstance(loc, dict), f"finding location must be a mapping, got {type(loc).__name__}: {loc!r}"
    return Finding(
        label=str(raw["label"]) if "label" in raw else "",
        narrative=" ".join(str(raw[k]) for k in _NARRATIVE_KEYS if k in raw),
        path=str(loc["path"]) if "path" in loc else "",
        start_line=str(loc["start_line"]) if "start_line" in loc else "",
    )


def _parse_ground_truth(text: str) -> dict[str, list[JsonDict]]:
    tiers: dict[str, list[JsonDict]] = {"structural": [], "decoy": [], "noise": []}
    for tier, prefix in (("structural", "S"), ("decoy", "D")):
        for m in re.finditer(rf"\| ({prefix}\d+) \| `([^`]+)` \| `([^`]+)` \| ([^\|]+) \|", text):
            tiers[tier].append({"id": m.group(1), "path": m.group(2), "label": m.group(3), "note": m.group(4).strip()})
    # Noise rows are three-column: | N1 | `path` | why | — no label.
    for m in re.finditer(r"\| (N\d+) \| `([^`]+)` \| ([^|]+) \|", text):
        tiers["noise"].append({"id": m.group(1), "path": m.group(2), "label": "", "note": m.group(3).strip()})
    return tiers


def _path_match(gt_path: str, finding_path: str) -> bool:
    if not gt_path or not finding_path:
        return False
    return finding_path == gt_path or finding_path.endswith(gt_path) or gt_path.endswith(finding_path)


def _label_match(gt_label: str, finding: Finding) -> bool:
    label = finding.label.upper()
    gt = gt_label.upper()
    if label and gt and (gt in label or label in gt):
        return True
    narrative = finding.narrative.upper()
    tokens = re.split(r"[_\s]+", gt)
    return sum(1 for t in tokens if t and t in narrative) >= max(1, len(tokens) // 2)


def score_artifact(artifact: Path, ground_truth: Path = GROUND_TRUTH) -> int:
    data = json.loads(artifact.read_text())
    if "findings" not in data:
        raise KeyError("artifact has no 'findings' key — not a validated review report")
    findings = [_parse_finding(f) for f in data["findings"]]
    tiers = _parse_ground_truth(ground_truth.read_text())

    matched: dict[str, list[str]] = {t: [] for t in tiers}
    unmatched_findings: list[Finding] = []

    for finding in findings:
        hit = False
        for tier, items in tiers.items():
            for item in items:
                # SCORING.md: noise FPs are findings overlapping N1/N2 paths — path-only match.
                if _path_match(item["path"], finding.path) and (tier == "noise" or _label_match(item["label"], finding)):
                    matched[tier].append(item["id"])
                    hit = True
                    break
            if hit:
                break
        if not hit:
            unmatched_findings.append(finding)

    structural = tiers["structural"]
    decoy = tiers["decoy"]
    noise = tiers["noise"]

    s_recall = len(set(matched["structural"])) / len(structural) if structural else 0.0
    d_recall = len(set(matched["decoy"])) / len(decoy) if decoy else 0.0
    n_fp = len([i for i in noise if i["id"] in matched["noise"]])
    total = len(findings)
    s_prec = len(set(matched["structural"])) / total if total else 0.0

    missed_s = [i["id"] for i in structural if i["id"] not in matched["structural"]]
    trap_gaming = s_recall < 0.5 and d_recall >= 0.66

    print(f"findings: {total}")
    print(f"structural recall: {len(set(matched['structural']))}/{len(structural)} ({s_recall:.0%})")
    print(f"structural precision: {s_prec:.0%}")
    print(f"decoy recall: {len(set(matched['decoy']))}/{len(decoy)} ({d_recall:.0%})")
    print(f"noise false positives: {n_fp}")
    if missed_s:
        print(f"missed structural: {', '.join(missed_s)}")
    if unmatched_findings:
        print(f"unmatched findings: {len(unmatched_findings)}")
        for f in unmatched_findings:
            print(f"  - {f.label} @ {f.path}:{f.start_line}")
    if trap_gaming:
        print("VERDICT: TRAP GAMING — high decoy recall, low structural recall")
        return 2
    if s_recall >= 5 / 6 and n_fp == 0:
        print("VERDICT: PASS")
        return 0
    print("VERDICT: NEEDS WORK")
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    sys.exit(score_artifact(args.artifact))


if __name__ == "__main__":
    main()
