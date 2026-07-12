"""Contract completeness sweep — calibration slice.

N1/N2 are noise: strict xfails cite open fixture issues; reviewers must
not re-file them as new findings.
"""

import pytest


@pytest.mark.xfail(strict=True, reason="fixture gap dzackgarza/research-review-calibration#fixture-24")
def test_constructor_implements_all_required_contracts():
    raise AssertionError("Not implemented method: primitive_embedding_morphism")


@pytest.mark.xfail(strict=True, reason="fixture gap dzackgarza/research-review-calibration#fixture-25")
def test_pickling_roundtrip_preserves_equality():
    assert False, "loads(dumps(L)) != L"
