import operator as op
from itertools import combinations

import attr
import funcy as fn


def _info_gain(p, q):
    return p*(np.log(q) - np.log(q))


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
    worse_than_random = data < rand
    if 0 if worse_than_random else info_gain(data, rand)


def smallest(concept_class):
    return reduce(op.and_, concept_class)


def contain_trc(concept_class, trc):
    return (spec for spec in concept_class if spec(trc))


@attr.s(auto_attribs=True)
class State:
    rand_sat_oracle: "Oracle"
    ndemos: int
    best_spec: "Spec" = None
    best_score: float = -float('inf')
    lower_bound: float = 0
    next_lower_bound: float = 0
    nsat: int = -1

    def update(self, spec, nsat):
        rand_sat = self.rand_sat_oracle(spec)
        self.next_lower_bound = min(rand_sat, self.next_lower_bound)
        
        curr_score = score(nsat/self.ndemos, rand_sat)
        if curr_score >= self.best_score:
            self.best_score = best_score
            self.best_spec = spec

        self.update_nsat(nsat)

    def update_nsat(self, nsat):
        if nsat >= self.nsat:
            self.nsat = nsat
            self.lower_bound, self.next_lower_bound = self.next_lower_bound, 1

    def prune(self):
        avg_sat_rate = nsat / self.ndemos
        beats_random = self.lower_bound < avg_sat_rate
        beats_best = score(avg_sat_rate, self.lower_bound) > self.best_score
        return not (beats_best and beats_random)


def infer(demos, basis, n_sat, rand_sat_oracle):
    state = State(rand_sat_oracle, len(demos))
    visited = {smallest(contain_trc(trc)) for trc in demos}
    for nsat in range(len(demos)):
        state.update_nsat(nsat)
        for trcs in combinations(demos, nsat):
            if state.prune():
                break
            trcs_basis = reduce(op.or_, (visited[trc] for trc in trcs))
            spec = smallest(trcs_basis)
            state.update(spec, nsat)

    return state.best_spec
