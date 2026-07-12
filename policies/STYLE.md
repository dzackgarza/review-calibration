# Lattice Spike Style Guide (calibration slice)

Subset of the research repo STYLE.md frozen for packet context.

## 9. Every claim is a code assertion, not a print verdict

Self-affirming prints that declare success without printing the witness are noise.
The reader must see mathematical evidence, not the agent's verdict.

## 12. Show existence, not absence

Show EXISTENCE of methods on lattices that use them, not ABSENCE on lattices that do not.
Axiom gating is a development concern.

## 13. Lattice string representation

The repr must surface cheap invariants: signature pair, determinant, evenness, discriminant invariants.

Example: `Synthetic lattice A2: rank 2, sig (2,0), det 3, even, disc (3,)`

Not just `Synthetic lattice A2 of rank 2 over Integer Ring`.
