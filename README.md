# Review calibration

Frozen simulacrum of `dzackgarza/research` lattice-spike work.
Used to **hill-climb LLM review quality** before trusting advisory runs on the live monorepo.

- **Repo:** [github.com/dzackgarza/review-calibration](https://github.com/dzackgarza/review-calibration)
- **Submodule of research:** `review-calibration/`
- **Performance ledger (discussion):** [issue #19](https://github.com/dzackgarza/review-calibration/issues/19) — append scores per run
- **Finding grouping:** [issue #8](https://github.com/dzackgarza/review-calibration/issues/8)
- **Program doc:** [HILL_CLIMB.md](./HILL_CLIMB.md)

The reviewer sees a small spike checkout — not an eval harness.
Experimenters hold the answer key in `GROUND_TRUTH.md` (never in `review-packet.tar`).

## What lives here

| Path | Audience | In `review-packet.tar`? |
| --- | --- | --- |
| `lattice_spike_slice/` | Reviewer | Code under review |
| `lattice_spike_slice/vault/` | Reviewer | Yes |
| `policies/STYLE.md` | Reviewer | Yes |
| `GROUND_TRUTH.md` | Experimenters | **Never** |
| `HILL_CLIMB.md`, `SCORING.md` | Experimenters | **Never** |
| `src/score.py`, `scripts/` | Experimenters | **Never** |

Advisory workflows (`.github/workflows/review-*.yml`) use the same `ai-review-ci` reusable workflow as research; findings publish to **this repo's issues ledger**.

## Quick start

```bash
# Score an artifact (or metadata JSON via normalize script)
just score /path/to/.review-report-artifact.json

# Rebuild packet after editing justfile declaration
just review-packet

# Dispatch calibration review
gh workflow run "General Review" --repo dzackgarza/review-calibration
```

From **research** root:

```bash
just review-calibration-packet
just review-calibration-general
just review-calibration-score /path/to/artifact.json
```

## Planted violations

See `GROUND_TRUTH.md`: **structural** (must find), **decoy** (trap-gaming detector), **noise** (must not file).
Phase 0 baseline slice is documented in [HILL_CLIMB.md](./HILL_CLIMB.md).

## Hill-climb goal

Increase fixture difficulty and tighten pass bars until reviews reliably:

1. Find substantive mathematical / architectural defects
2. Surface pervasive patterns, not isolated nits
3. Enforce custom style (STYLE.md) where it matters
4. Identify slop (proof-laundering, invented vocabulary, API-reference notebooks)
5. Respect ledger hygiene (no duplicate gap filing)

Only then port packet/prompt learnings to research's production `review-packet.tar`.
