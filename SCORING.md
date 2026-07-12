# Scoring reviewer runs

Compare a validated `.review-report-artifact.json` against `GROUND_TRUTH.md` using:

```bash
just score path/to/.review-report-artifact.json
```

## Matching rule

A ground-truth item is **matched** when the report contains a finding whose `location.path` equals the GT path (or is a suffix path match for notebook line drift) **and** whose `label` or narrative clearly names the same violation class.
Fuzzy label match is intentional — we care whether the reviewer saw the defect, not whether it invented the same slug.

## Reported metrics

- **structural recall** — matched S* / 6
- **structural precision** — structural matches / total findings
- **decoy recall** — matched D* / 3
- **noise false positives** — findings overlapping N1/N2 paths without acknowledging they're already tracked
- **unmatched findings** — possible false positives to inspect
- **missed structural** — S* IDs with no match (hill-climb targets)

## Experiment issue template

After each run, open an issue titled:

`[calibration] <report_type> <YYYY-MM-DD> <infra-ref> <model-if-known>`

Body:

```markdown
## Run
- Workflow run: <URL>
- Artifact commit: <SHA>
- review-packet.tar sha256: <hash>
- ai-review-ci ref: <ref>

## Scores
(paste `just score` output)

## Qualitative
- Did the reviewer waste turns on git / infra / submit-candidate reads?
- Did it replay vault traps without finding structural items?
- Packet changes to try next:
```

Use labels: `calibration`, `ai-review/<type>`, `needs-analysis`.
