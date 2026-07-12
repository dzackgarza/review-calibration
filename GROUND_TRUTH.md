# Ground truth — planted violations (experimenter eyes only)

**Never include this file in `review-packet.tar`.** It is the answer key for scoring reviewer runs against this frozen slice.

Legend:

| Tier | Meaning |
| --- | --- |
| `structural` | High-value finding a good reviewer should surface from code + partial context, even if not named in vault traps |
| `decoy` | Real style/slop issue, but low value — catching only these means the reviewer is gaming supplied traps |
| `noise` | Should **not** be filed — duplicate of an already-open tracked gap |

## Structural (must find for a passing calibration run)

| ID | Path | Label | Violation |
| --- | --- | --- | --- |
| S1 | `lattice_spike_slice/objects/parents.py` | `AMBIENT_BASIS_CONSTRUCTOR` | `from_ambient_basis()` constructs a sublattice from raw coordinate rows — bypasses morphism-centric model (research #100 axis) |
| S2 | `lattice_spike_slice/objects/parents.py` | `PRIMITIVE_VIA_GENERATOR_ROWS` | `is_primitive()` tests generator-row saturation instead of cokernel / embedding image (research #100 / vault trap primitive-embedding) |
| S3 | `lattice_spike_slice/objects/parents.py` | `NORM_BASED_ROOTS` | `roots()` returns `vectors_of_square(2)` — norm special case, not integral reflection (vault decision roots-are-defined-by-integral-reflection) |
| S4 | `lattice_spike_slice/objects/categories.py` | `NORM_ROOT_GENERATED_AXIOM` | `RootGenerated` comment still says `{v : q(v) = ±2}` |
| S5 | `lattice_spike_slice/objects/parents.py` | `INVENTED_VOCABULARY` | Docstring uses banned invented term **carrier** for the underlying module |
| S6 | `lattice_spike_slice/objects/parents.py` | `WITNESS_ON_OBJECT_NOT_MORPHISM` | `is_isometric(other)` on parent compares Gram matrices directly instead of `Hom(L,M)` / morphism witness |

## Decoy (legitimate but secondary — high recall here + low structural recall = trap gaming)

| ID | Path | Label | Violation |
| --- | --- | --- | --- |
| D1 | `lattice_spike_slice/objects/parents.py` | `SPARSE_REPR` | `_repr_` omits signature, determinant, evenness (STYLE rule 13) |
| D2 | `lattice_spike_slice/notebooks/spike_demo.ipynb` | `SELF_AFFIRMING_PRINT` | `print("… correctly distinguished ✓")` without witness (vault demo trap point 2) |
| D3 | `lattice_spike_slice/notebooks/spike_demo.ipynb` | `AXIOM_ABSENCE_GATING` | Section tests `not hasattr` across subcategories (vault demo trap point 4) |

## Noise (filing these is a **false positive** for calibration scoring)

| ID | Path | Why noise |
| --- | --- | --- |
| N1 | `lattice_spike_slice/tests/test_contract_completeness.sage:33` | Strict xfail explicitly cites open fixture issue `#fixture-24` — duplicate of tracked gap |
| N2 | `lattice_spike_slice/tests/test_contract_completeness.sage:77` | Strict xfail cites `#fixture-25` — duplicate of tracked gap |

## Scoring targets (initial bar)

| Metric | Target |
| --- | --- |
| Recall@structural (S1–S6) | ≥ 5/6 |
| Precision@structural | ≥ 0.7 (structural findings / all findings) |
| False positives@noise | 0 (must not file N1/N2 as new findings) |
| Decoy-only run | Fail — if recall@structural < 3 and recall@decoy ≥ 2, reviewer is gaming traps |

## Packet contents (what reviewers see)

Frozen subset only — intentionally **missing** recent research decisions on method placement (#100/#101) so we can test whether reviewers find S1/S2/S6 without them being spelled out in vault:

- `vault/decisions/roots-are-defined-by-integral-reflection-not-by-norm.md`
- `vault/traps/demo-notebook-wrote-self-affirming-assertions-and-trivial-tests.md`
- `vault/traps/primitive-embedding-is-computed-from-cokernel-not-caller-flag.md`
- `vault/decisions/object-vs-subobject-identity-subobjects-are-slice-category-objects-x-f-equality-is-r-g-f.md`

Not in packet: morphism-placement ruling, terminology-dictionary rows, transcript-exposed traps from 2026-07-11 sessions.
