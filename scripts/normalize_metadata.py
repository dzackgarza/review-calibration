#!/usr/bin/env python3
"""Normalize report-metadata JSON (CI log shape) to full artifact shape for score.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


def _require_str(raw: JsonDict, key: str) -> str:
    value = raw[key]
    if not isinstance(value, str):
        msg = f"expected string for {key!r}, got {type(value).__name__}"
        raise TypeError(msg)
    return value


def _require_int(raw: JsonDict, key: str) -> int:
    value = raw[key]
    if not isinstance(value, int):
        msg = f"expected int for {key!r}, got {type(value).__name__}"
        raise TypeError(msg)
    return value


def normalize(meta: JsonDict) -> JsonDict:
    findings: list[JsonDict] = []
    raw_findings = meta["findings"]
    if not isinstance(raw_findings, list):
        msg = "expected list for 'findings'"
        raise TypeError(msg)
    for raw in raw_findings:
        if not isinstance(raw, dict):
            continue
        if "location" in raw:
            findings.append(raw)
            continue
        path = _require_str(raw, "path")
        line = _require_int(raw, "line")
        end = raw["end_line"] if "end_line" in raw else line
        if not isinstance(end, int):
            msg = "expected int for 'end_line'"
            raise TypeError(msg)
        findings.append({**raw, "location": {"path": path, "start_line": line, "end_line": end}})
    report_type = meta["report_type"] if "report_type" in meta else "general"
    if not isinstance(report_type, str):
        msg = "expected string for 'report_type'"
        raise TypeError(msg)
    return {"report_type": report_type, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Metadata or full artifact JSON")
    parser.add_argument("-o", "--output", type=Path, help="Write normalized artifact (default: stdout)")
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    out = normalize(data)
    text = json.dumps(out, indent=2)
    if args.output:
        args.output.write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    main()
