---
type: decision
title: Roots are defined by integral reflection, not by norm
description: v is a root iff s_v lands in O(L); norm-(+-2) is a special case
---

# Roots are defined by integral reflection, not by norm

User ruling: a root of a lattice L is NOT a vector of a prescribed square.
The definition is: v is a root iff the reflection s_v is integral (s_v ∈ O(L)).

Consequences in the spike:

- `roots()` implementations spelled `vectors_of_square(+-2)` compute only the norm-(+-2) special case.
- The `RootGenerated` axiom docstring must use the reflective definition, not `{v : q(v) = +-2}`.
