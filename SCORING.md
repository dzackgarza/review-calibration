# Scoring reviewer runs

Compare a validated report against `GROUND_TRUTH.md`:

```bash
just score path/to/.review-report-artifact.json
```

CI often emits **metadata JSON** (top-level `path`/`line` per finding). Normalize first:

```bash
python3 scripts/normalize_metadata.py run-metadata.json -o artifact.json
just score artifact.json
```

## Matching rule

A ground-truth item is **matched** when the report contains a finding whose
`location.path` matches the GT path (suffix ok for notebooks) **and** whose
`label` or narrative names the same violation class.

## Metrics

| Metric | Meaning |
|--------|---------|
| structural recall | matched S* / 6 |
| structural precision | structural / all findings |
| decoy recall | matched D* / 3 |
| noise false positives | findings on N* paths (target: 0) |
| trap-gaming | decoy recall ≥ 66% while structural recall < 50% → fail |

## Recording results

**Do not open a new issue per run.** Comment on the
[Performance ledger #19](https://github.com/dzackgarza/review-calibration/issues/19)
with:

```markdown
### Run <YYYY-MM-DD> — <general|slop> — phase <N>

- Workflow: <URL>
- Commit: `<SHA>`
- Packet sha256: `<hash>`
- ai-review-ci: `<ref>`

**Scores**
```
(paste `just score` output)
```

**Qualitative**
- Waste turns (git, infra, submit-candidate reads)?
- Trap gaming vs independent structural discovery?
- Next change to try:
```

Optional one-off deep dives can use label `calibration` + `needs-analysis`;
the ledger issue is the canonical time series.
