"""Frozen calibration slice — synthetic lattice parents with planted violations.

See GROUND_TRUTH.md (experimenter-only) for the answer key. This module
is intentionally smaller than the production spike but structurally similar.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class SyntheticLattice:
    """Lattice parent object in the calibration slice.

    S5: uses invented vocabulary — the underlying set of the parent is
    treated as a **carrier** for raw coordinate rows (banned term; use
    morphism/subobject language).
    """

    def __init__(self, gram_matrix: Any, label: str = "L", base_ring: Any = None) -> None:
        self._gram = gram_matrix
        self._label = label
        self._base_ring = base_ring

    def _repr_(self) -> str:
        # D1: sparse repr — STYLE rule 13 wants signature, det, evenness
        return f"Synthetic lattice {self._label} of rank {self.rank()} over {self._base_ring}"

    def rank(self) -> int:
        return len(self._gram)

    def gram_matrix(self) -> Any:
        return self._gram

    def base_ring(self) -> Any:
        return self._base_ring

    @classmethod
    def from_ambient_basis(cls, parent: SyntheticLattice, rows: Sequence[Sequence[int]]) -> SyntheticLattice:
        """S1: ambient-basis bypass — builds a sublattice from raw rows in the
        parent's coordinate system instead of from a morphism A ↪ parent."""
        projected = [tuple(r) for r in rows]
        return cls(projected, label=f"sub_of_{parent._label}")

    def is_primitive(self, sub: SyntheticLattice) -> bool:
        """S2: tests generator-row containment, not cokernel / image primitiveness."""
        sub_rows = {tuple(r) for r in sub.gram_matrix()}
        parent_rows = {tuple(r) for r in self.gram_matrix()}
        return sub_rows.issubset(parent_rows)

    def is_isometric(self, other: SyntheticLattice) -> bool:
        """S6: witness on object — compares Gram matrices on parents."""
        return bool(self.gram_matrix() == other.gram_matrix())

    def vectors_of_square(self, square: int) -> tuple[Any, ...]:
        return tuple(v for v in self.gram_matrix() if sum(v) ** 2 == square)

    def roots(self) -> tuple[Any, ...]:
        """S3: norm-(+-2) special case only."""
        return self.vectors_of_square(2)

    def reflection(self, v: Any) -> Any:
        """Reflection s_v; integrality predicate is definitionally is_root."""
        raise NotImplementedError

    def is_root(self, v: Any) -> bool:
        raise NotImplementedError
