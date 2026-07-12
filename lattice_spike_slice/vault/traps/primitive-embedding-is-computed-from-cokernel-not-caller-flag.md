---
type: trap
title: Primitive embedding is computed from cokernel, not caller flag
---

# Primitive embedding is computed from cokernel, not caller flag

Primitiveness of an embedding is computed from the embedding image, equivalently from torsion-freeness of the module cokernel.
Do not add `embedding(..., primitive=True)` flags.
Construct the morphism, compute its image, check codomain primitive-submodule predicate or `is_primitive_embedding()` on the morphism.

Verification: no `primitive=True` on public embedding signatures; tests use cokernel torsion or `codomain.is_primitive(image)` as evidence.
