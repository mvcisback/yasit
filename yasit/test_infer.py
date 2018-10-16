import attr
import hypothesis.strategies as st
from operator import itemgetter as ig
from itertools import product

import pytest
from hypothesis import given
from yasit import infer


@given(st.floats(min_value=0, max_value=1),
       st.floats(min_value=0, max_value=1))
def test_score(p, q):
    if q == 0 and p > 0:
        with pytest.raises(AssertionError):  # Impossible to satisfy spec.
            infer.score(p, q)
    else:
        score = infer.score(p, q)
        assert score >= 0
        if p < q:
            assert score == 0

        if q + 1e-4 <= 1:
            assert score >= infer.score(p, q + 1e-4)


@attr.s(frozen=True, cmp=False)
class IndependentSpec:
    func = attr.ib()
    _rand_sat = attr.ib()

    def __call__(self, *args) -> bool:
        return self.func(*args)

    def __and__(self, other):
        return attr.evolve(
            self,
            func=lambda x: self.func(x) and other.func(x),
            rand_sat=self.rand_sat() * other.rand_sat()
        )

    def rand_sat(self):
        return self._rand_sat


BASIS = [
    IndependentSpec(ig(2), 0.8),
    IndependentSpec(lambda x: not x[2], 0.2),
    IndependentSpec(ig(1), 0.5),
    IndependentSpec(lambda x: not x[1], 0.5),
    IndependentSpec(ig(0), 0.7),
    IndependentSpec(lambda x: not x[0], 0.3),
]


TRCS = [(True, False, True)]*10 + [(False, True, False)]*2


def test_contain_trc():
    for trc in TRCS:
        specs = infer.contain_trc(BASIS, trc)
        assert all(spec(trc) for spec in specs)


def test_smallest():
    smallest = infer.smallest(BASIS)
    for spec, trc in product(BASIS, TRCS):
        assert smallest.rand_sat() <= spec.rand_sat()
        assert not smallest(trc) or spec(trc)


def test_infer():
    states = list(infer._infer(TRCS, BASIS, pruning=False))
    assert len(states) == 2**len(TRCS) - 1
    assert states[-1].best_score > 0
    assert states[-1].best_spec((True, False, True))

    states2 = list(infer._infer(TRCS, BASIS, pruning=True))
    assert states[-1].best_score == states2[-1].best_score
