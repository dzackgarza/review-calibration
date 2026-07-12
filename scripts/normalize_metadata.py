#!/usr/bin/env python3
"""Normalize report-metadata JSON (CI log shape) to full artifact shape for score.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


def normalize(meta: JsonDict) -> JsonDict:
    findings: list[JsonDict] = []
    for raw in meta.get("findings", []):
        if not isinstance(raw, dict):
            continue
        if "location" in raw:
            findings.append(raw)
            continue
        path = raw.get("path", "")
        line = raw.get("line", 1)
        end = raw.get("end_line", line)
        findings.append({**raw, "location": {"path": path, "start_line": line, "end_line": end}})
    return {"report_type": meta.get("report_type", "general"), "findings": findings}


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
