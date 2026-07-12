
test:
    @just -f ~/ai-review-ci/justfiles/python.just -d . test

test-ci:
    @just -f ~/ai-review-ci/justfiles/python.just -d . test-ci

# Score a reviewer artifact against GROUND_TRUTH.md (experimenter tool).
score artifact:
    python3 src/score.py "{{artifact}}"

# Normalize CI metadata JSON to full artifact shape, then score.
score-metadata metadata:
    python3 scripts/normalize_metadata.py "{{metadata}}" -o /tmp/cal-normalized.json
    python3 src/score.py /tmp/cal-normalized.json

# Assemble review-packet.tar for advisory review workflows.
# GROUND_TRUTH.md and SCORING.md are NEVER included.
review-packet:
    #!/usr/bin/env bash
    set -euo pipefail
    staging="$(mktemp -d)"
    trap 'rm -rf "$staging"' EXIT

    cat > "$staging/PROMPT.md" <<'PROMPT'
    # Review focus: lattice spike calibration slice

    This repository is a frozen slice of lattice-category spike work. The
    active code surface is `lattice_spike_slice/`. Reviews are advisory:
    they feed a triage ledger. An empty report is preferable to a
    stretched finding.

    Prioritize, in order:

    1. **Mathematical correctness** — consistency with subobject/morphism
       identity (vault decisions), root definition by integral reflection,
       primitive embedding via cokernel not row containment.
    2. **Ratified-decision violations** — `vault/` documents in this packet
       are authoritative for this slice.
    3. **STYLE.md conformance** — assertion discipline, repr richness,
       notebook research workflow (not API-reference gating).

    Do not re-file strict-xfail markers that already cite an open issue.
    Do not raise generic lint/type nitpicks.
    PROMPT

    mkdir -p "$staging/policies" "$staging/spec"
    cp policies/STYLE.md "$staging/policies/STYLE.md"
    echo "# Synthetic lattice model (abbreviated calibration slice)" > "$staging/spec/SYNTHETIC_LATTICE_MODEL.md"

    for section in decisions traps advice; do
        mkdir -p "$staging/vault/$section"
        if compgen -G "lattice_spike_slice/vault/$section/*.md" > /dev/null; then
            cp lattice_spike_slice/vault/"$section"/*.md "$staging/vault/$section/"
        fi
    done

    tar --sort=name --owner=0 --group=0 --numeric-owner \
        --mtime='UTC 2020-01-01' --format=gnu \
        -cf review-packet.tar -C "$staging" .
    echo "review-packet.tar: $(tar -tf review-packet.tar | grep -c -v '/$') files"
