import operator as op
from functools import reduce
from itertools import combinations
from math import log

import attr
import funcy as fn


oo = float('inf')


def _info_gain(p, q):
    return p*(log(p) - log(q))


def info_gain(p, q):
    if p == q:
        return 0
    elif p == 0:
        return _info_gain(1, 1 - q)
    elif p == 1:
        return _info_gain(1, q)
    else:
        return _info_gain(p, q) + _info_gain(1 - p, 1 - q)


def score(data, rand):
    assert data == 0 or rand > 0  # Cannot satisfy spec if rand == 0.
    worse_than_random = data < rand
    return 0 if worse_than_random else info_gain(data, rand)


def smallest(concept_class):
    return reduce(op.and_, concept_class)


def contain_trc(concept_class, trc):
    return (spec for spec in concept_class if spec(trc))


@attr.s(auto_attribs=True)
class State:
    ndemos: int
    best_spec: "Spec" = None
    best_score: float = -oo
    lower_bound: float = oo
    next_lower_bound: float = oo

    def update_spec(self, spec, nsat):
        rand_sat = spec.rand_sat()
        assert self.lower_bound == oo or rand_sat >= self.lower_bound
        self.next_lower_bound = min(rand_sat, self.next_lower_bound)

        curr_score = score(nsat/self.ndemos, rand_sat)
        if curr_score > self.best_score:
            self.best_score, self.best_spec = curr_score, spec

    def update_lowerbound(self):
        assert self.lower_bound == oo or \
            self.lower_bound <= self.next_lower_bound

        self.lower_bound, self.next_lower_bound = self.next_lower_bound, oo

    def prune(self, nsat):
        if self.best_spec is None or self.lower_bound == oo:
            return False

        avg_sat = nsat / self.ndemos
        beats_random = self.lower_bound < avg_sat
        beats_best = score(avg_sat, self.lower_bound) > self.best_score
        return not (beats_best and beats_random)


def _infer(demos, basis, *, pruning=True):
    state = State(len(demos))
    visited = {trc: smallest(contain_trc(basis, trc)) for trc in demos}
    for nsat in reversed(range(1, len(demos) + 1)):
        for trcs in combinations(demos, nsat):
            if pruning and state.prune(nsat):
                break
            trcs_basis = (visited[trc] for trc in trcs)
            spec = smallest(trcs_basis)
            state.update_spec(spec, len(trcs))
            yield state

        state.update_lowerbound()


def infer(demos, basis):
    return fn.last(_infer(demos, basis))
