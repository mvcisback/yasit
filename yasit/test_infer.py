import attr
import hypothesis.strategies as st
from itertools import product
from operator import itemgetter as ig

import pytest
from hypothesis import given
from yasit import chain, scoring, lattice, equiv_classes


@given(st.floats(min_value=0, max_value=1),
       st.floats(min_value=0, max_value=1))
def test_score(p, q):
    if q == 0 and p > 0:
        with pytest.raises(AssertionError):  # Impossible to satisfy spec.
            scoring.score(p, q)
    else:
        score = scoring.score(p, q)
        assert score >= 0
        if p < q:
            assert score == 0

        if q + 1e-4 <= 1:
            assert score >= chain.score(p, q + 1e-4)


def _func_to_set(f):
    BOOL = {True, False}
    if isinstance(f, frozenset):
        return f
    return frozenset({x for x in product(BOOL, BOOL, BOOL) if f(x)})


@attr.s(frozen=True)
class DumbSpec:
    data = attr.ib(converter=_func_to_set)
    _rand_sat = attr.ib()

    def __call__(self, arg) -> bool:
        return arg in self.data

    def __and__(self, other):
        data = self.data & other.data
        rand_sat = self.rand_sat() * other.rand_sat() if data else 0
        return attr.evolve(self, data=data, rand_sat=rand_sat)

    def __leq__(self, other):
        return self.data <= other.data

    def rand_sat(self):
        return self._rand_sat


TRUE = DumbSpec(lambda _: True, 1)
FALSE = DumbSpec(lambda _: False, 0)
PHI0 = DumbSpec(ig(0), 0.7)
PHI1 = DumbSpec(ig(1), 0.5)
PHI2 = DumbSpec(ig(2), 0.8)


CHAIN1 = [FALSE, PHI0 & PHI1 & PHI2, PHI0 & PHI1, PHI0, TRUE]
CHAIN2 = [FALSE, PHI0 & PHI1 & PHI2, PHI0 & PHI2, PHI0, TRUE]
DEMOS = [(True, True, True)] \
    + [(True, False, True)]*10 \
    + [(False, True, False)]*2
DEMOS = tuple(DEMOS)


def test_percent_sat():
    assert chain.percent_sat(TRUE, DEMOS) == 1
    assert chain.percent_sat(FALSE, DEMOS) == 0
    assert chain.percent_sat(PHI0, DEMOS) == 11/13
    assert chain.percent_sat(PHI1, DEMOS) == 3/13
    assert chain.percent_sat(PHI2, DEMOS) == 11/13
    assert chain.percent_sat(PHI0 & PHI1, DEMOS) == 1/13
    assert chain.percent_sat(PHI0 & PHI1 & PHI2, DEMOS) == 1/13


def test_find_bots():
    bots = list(chain.find_bots(CHAIN1, DEMOS))
    assert len(bots) == 4
    psat2bot = dict(bots)
    assert len(bots) == len(psat2bot)  # Unique spec per partition.
    # TODO: assert binary search equals linear scan.

    assert psat2bot[0] == FALSE
    assert psat2bot[1] == TRUE
    assert psat2bot[1/13] == PHI0 & PHI1 & PHI2
    assert psat2bot[11/13] == PHI0


def test_chain_chainence():
    psat, spec = chain.chain_inference(CHAIN1, DEMOS)
    assert spec == PHI0

    psat, spec = chain.chain_inference(CHAIN2, DEMOS)
    assert spec == PHI0 & PHI2


CC1 = [TRUE, FALSE, PHI0, PHI0 & PHI1, PHI0 & PHI2, PHI0 & PHI1 & PHI2]


class Smallest(DumbSpec):  # Semantically the same as FALSE.
    def __leq__(self, _):
        return True


def test_find_equiv_cls():
    eqs = equiv_classes.find_equiv_cls(CC1)
    assert len(eqs) == 6

    eqs = equiv_classes.find_equiv_cls(CC1 + [Smallest(lambda _: False, 0)])
    assert len(eqs) == 6


def test_create_lattice():
    lat = lattice.create_lattice(CC1)

    assert len(lat.edges) == 6
    assert sum(1 for _, d in lat.out_degree() if d == 0) == 1
    assert sum(1 for _, d in lat.in_degree() if d == 0) == 1


def test_lattice_inference():
    spec = lattice.infer(CC1, DEMOS).data
    assert lattice.infer(CC1, DEMOS, brute_force=True).data == spec
    assert spec == (PHI0 & PHI2).data
