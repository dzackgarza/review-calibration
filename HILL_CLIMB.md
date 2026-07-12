# Hill-climb program — LLM review calibration

This repository exists to **measure and improve** advisory LLM reviews before
they drive the production ledger on `dzackgarza/research`. The reviewer must
look like it is auditing a real spike checkout; experimenters hold the answer
key (`GROUND_TRUTH.md`) and score every run.

**Living discussion:** file scores and qualitative notes on the
[Performance ledger](https://github.com/dzackgarza/review-calibration/issues/19)
issue (one thread, append via comments for each run). Grouping issue
[#8](https://github.com/dzackgarza/review-calibration/issues/8) collects
finding sub-issues from advisory workflows.

## North-star capabilities

Reviews must eventually do all of the following **reliably** on frozen
fixtures before we trust them on the live monorepo:

| Capability | What “good” looks like |
|------------|------------------------|
| **Substantive defects** | Finds ratified-decision violations and deep structural slop (morphism placement, subobject identity, wrong mathematics) without the exact ruling being inlined in the packet |
| **Pervasive patterns** | Names recurring failure modes across files, not one-off nits; ties findings to vault traps/decisions when relevant |
| **Custom style enforcement** | Catches STYLE.md violations (repr shape, assertion discipline, notebook research workflow) when they matter — without treating style as a substitute for structure |
| **Slop identification** | Distinguishes proof-laundering, API-reference notebooks, invented vocabulary, and completion-shaped code from legitimate unusual-but-correct patterns |
| **Ledger hygiene** | Does not re-file strict-xfail / open-issue duplicates; honest empty reports when nothing new is found |

## Fixture tiers (difficulty ramp)

Each phase adds plantings and/or **withholds** packet context to test
independent discovery vs trap replay.

| Phase | Fixture | Packet | Pass bar |
|-------|---------|--------|----------|
| **0 — baseline** (current) | `lattice_spike_slice/` v1 | Partial vault (roots, primitive-embedding, demo traps, subobject identity); **no** morphism-placement #100/#101 rulings | structural recall ≥ 5/6, noise FP = 0, not trap-gaming |
| **1 — decoys** | Same code | Same packet | Above + decoy recall ≥ 2/3 without structural recall drop |
| **2 — context starvation** | Same code | Smaller vault (STYLE + spec only) | structural recall ≥ 4/6 |
| **3 — slop emphasis** | Notebook + vocabulary expanded | Slop-focused packet | slop run finds D2+D3 + ≥1 structural |
| **4 — research simulacrum** | Larger slice, more files | Research-shaped packet (terminology dictionary rows) | Combined general+slop pass bars |
| **5 — adversarial** | Subtle “looks wrong but correct per decision” shims | Full packet | precision ≥ 0.8, zero false positives on shims |

Advance a phase only when the **last three consecutive** scored runs meet the
phase bar. Regress → fix packet, permissions, or model before touching
research production `review-packet.tar`.

## Metrics (every run)

```bash
just score path/to/.review-report-artifact.json
```

| Metric | Meaning |
|--------|---------|
| structural recall | Fraction of S* plantings found |
| structural precision | Structural matches / all findings |
| decoy recall | Fraction of D* found |
| noise false positives | Findings on N* paths (should be 0) |
| trap-gaming verdict | High decoy + low structural → FAIL regardless |

Metadata JSON from CI logs (`finding_count` line) must be normalized to full
artifact shape before scoring — see `scripts/normalize_metadata.py`.

## Operational workflow

1. Change packet, prompt, permissions, or fixture → commit → `just review-packet` if packet changed.
2. `gh workflow run "General Review" --repo dzackgarza/review-calibration` (and Slop when phase requires it).
3. Score artifact; **comment on issue #19** with run URL, scores, and qualitative notes.
4. When a phase bar is met consistently, bump `GROUND_TRUTH.md` / fixture for the next phase.

## Research repo contract

- Submodule path: `review-calibration/` in `dzackgarza/research`
- Research recipes: `just review-calibration-packet`, `review-calibration-score`, `review-calibration-general`
- Production advisory reviews on research stay separate until calibration phases pass

## Files

| File | Role |
|------|------|
| `GROUND_TRUTH.md` | Answer key (never in packet) |
| `SCORING.md` | Matching rules + comment template |
| `src/score.py` | Scorer |
| `scripts/normalize_metadata.py` | Log JSON → artifact shape |
| `review-packet.tar` | Reviewer context (tracked, deterministic) |
