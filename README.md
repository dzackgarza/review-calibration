# Research review calibration

Frozen simulacrum of `dzackgarza/research` lattice-spike work, used to **hill-climb LLM review quality** before trusting advisory runs on the live monorepo.

This is a **separate repository** (submodule of research at `review-calibration/`). It looks like a small spike checkout to the reviewer — not an eval harness — but experimenters here know exactly which violations were planted and at what tier.

## What lives here

| Path | Audience | In `review-packet.tar`? |
| --- | --- | --- |
| `lattice_spike_slice/` | Reviewer (the "repo") | Indirectly (code under review) |
| `lattice_spike_slice/vault/` | Reviewer (context) | Yes (`vault/` in packet) |
| `policies/STYLE.md` | Reviewer | Yes |
| `GROUND_TRUTH.md` | **Experimenters only** | **Never** |
| `SCORING.md` | Experimenters | **Never** |
| `src/score.py` | Experimenters / CI | **Never** |

The advisory review workflows (`.github/workflows/review-*.yml`) run against **this** repo exactly like production runs against research: same `ai-review-ci` reusable workflow, same packet mechanism, findings published to **this repo's issues ledger** (not research's).

## Planted violation design

`GROUND_TRUTH.md` lists every planted item with:

- **tier** — `structural` (high value), `decoy` (tempting low-hanging fruit), `noise` (should not be filed — duplicates, xfail markers)
- **category** — maps to expected reviewer finding type
- **why** — what capability we're testing (independent discovery vs trap-replay vs duplicate-of-tracked-gap)

The slice deliberately mixes:

1. **Structural** — morphism placement, ambient-basis bypass, wrong root definition, invented vocabulary (the failures research transcripts keep surfacing but the first live review run missed).
2. **Decoys** — notebook `✓` prints, bare `_repr_`, axiom-absence blocks (tempting because they're in the frozen vault traps).
3. **Noise** — strict-xfail rows that cite an open fixture issue (tests whether the reviewer re-files known gaps).

## Experiment workflow

1. Edit prompt / packet declaration / permissions upstream or in `just review-packet`.

2. `just review-packet` → commit `review-packet.tar` if changed.

3. Dispatch `General Review` / `Slop Review` (or push to `main`).

4. Download `.review-report-artifact.json` from the run (or read published issues).

5. Score against ground truth:

   ```bash
   just score /path/to/.review-report-artifact.json
   ```

6. Open an **experiment issue** in this repo (template below) recording: model, infra ref, packet hash, precision/recall by tier, false positives, and qualitative notes.

Hill-climb on precision@structural and recall@structural before changing the production packet on `dzackgarza/research`.

## Submodule contract (research repo)

Research tracks this repo as a submodule and does **not** run advisory reviews against itself for calibration.
Instead:

```bash
# From research root — refresh packet in the submodule
just -f review-calibration/justfile review-packet

# Dispatch a calibration run (after submodule repo is on GitHub)
gh workflow run "General Review" --repo dzackgarza/research-review-calibration
```

Research's role is pointer + documentation; all experiment issues and run history live **here**.

## Creating the GitHub repo

This directory is the repo root.
One-time setup:

```bash
cd review-calibration
git init
gh repo create dzackgarza/research-review-calibration --private --source=. --remote=origin
git add -A && git commit -m "init: review calibration fixture and scoring harness"
git push -u origin main
```

Then from research:

```bash
git submodule add git@github.com:dzackgarza/research-review-calibration.git review-calibration
```
