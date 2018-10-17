import attr
import hypothesis.strategies as st
from operator import itemgetter as ig

import pytest
from hypothesis import given
from yasit import infer, scoring, lattice


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
            assert score >= infer.score(p, q + 1e-4)


@attr.s(frozen=True, cmp=False)
class DumbSpec:
    func = attr.ib()
    name = attr.ib()
    _rand_sat = attr.ib()

    def __call__(self, *args) -> bool:
        return self.func(*args)

    def __and__(self, other):
        if any(-n in other.name for n in self.name):
            rand_sat = 0
        else:
            rand_sat = self.rand_sat() * other.rand_sat()
        return attr.evolve(
            self,
            func=lambda x: self.func(x) and other.func(x),
            rand_sat=rand_sat,
            name=self.name | other.name
        )

    def rand_sat(self):
        return self._rand_sat


TRUE = DumbSpec(lambda _: True, {1}, 1)
FALSE = DumbSpec(lambda _: False, {-1}, 0)
PHI0 = DumbSpec(ig(0), {2}, 0.7)
PHI1 = DumbSpec(ig(1), {3}, 0.5)
PHI2 = DumbSpec(ig(2), {4}, 0.8)


CHAIN1 = [FALSE, PHI0 & PHI1 & PHI2, PHI0 & PHI1, PHI0, TRUE]
CHAIN2 = [FALSE, PHI0 & PHI1 & PHI2, PHI0 & PHI2, PHI0, TRUE]
DEMOS = [(True, True, True)] \
    + [(True, False, True)]*10 \
    + [(False, True, False)]*2


def test_percent_sat():
    assert infer.percent_sat(TRUE, DEMOS) == 1
    assert infer.percent_sat(FALSE, DEMOS) == 0
    assert infer.percent_sat(PHI0, DEMOS) == 11/13
    assert infer.percent_sat(PHI1, DEMOS) == 3/13
    assert infer.percent_sat(PHI2, DEMOS) == 11/13
    assert infer.percent_sat(PHI0 & PHI1, DEMOS) == 1/13
    assert infer.percent_sat(PHI0 & PHI1 & PHI2, DEMOS) == 1/13


def test_find_bots():
    bots = list(infer.find_bots(CHAIN1, DEMOS))
    assert len(bots) == 4
    psat2bot = dict(bots)
    assert len(bots) == len(psat2bot)  # Unique spec per partition.
    # TODO: assert binary search equals linear scan.

    assert psat2bot[0].name == {-1}
    assert psat2bot[1].name == {1}
    assert psat2bot[1/13].name == {2, 3, 4}
    assert psat2bot[11/13].name == {2}


def test_chain_inference():
    psat, spec = infer.chain_inference(CHAIN1, DEMOS)
    assert spec.name == {2}

    psat, spec = infer.chain_inference(CHAIN2, DEMOS)
    assert spec.name == {2, 4}


LATTOP = lattice.Lattice(children=[], spec=TRUE)
LAT0 = lattice.Lattice(children=[LATTOP], spec=PHI0)
LAT01 = lattice.Lattice(children=[LAT0], spec=PHI0 & PHI1)
LAT02 = lattice.Lattice(children=[LAT0], spec=PHI0 & PHI2)
LAT012 = lattice.Lattice(children=[LAT01, LAT02], spec=PHI0 & PHI1 & PHI2)
LATBOT = lattice.Lattice(children=[LAT012], spec=FALSE)


def test_gen_chains():
    chains = list(LATBOT.gen_chains())
    assert len(chains) == 2
    assert len(chains[0]) + len(chains[1]) == 6
    assert [n.name for n in chains[0]] == \
        [spec.name for spec in CHAIN2]


def test_lattice_inference():
    psat, spec = LATBOT.infer(DEMOS)
    assert spec.name == {2, 4}
