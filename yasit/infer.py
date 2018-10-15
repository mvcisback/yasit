import operator as op

import attr
import funcy as fn


@attr.s(auto_attribs=True)
class State:
    rand_sat_oracle: "Oracle"
    ndemos: int
    best_spec: "Spec" = None
    best_score: float = 0
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
    if data < rand:
        return 0

    return info_gain(data, rand)


def smallest(concept_class):
    return reduce(op.and_, concept_class)


def contain_trc(concept_class, trc):
    return (spec for spec in concept_class if spec(trc))


def prune(nsat, low, best_score):
    return False


def score_frontier(n_sat, ):
    pass



@lru_cache()
def rand_sat():
    pass


def infer(demos, basis, n_sat, rand_sat):
    visited = {smallest(contain_trc(trc)) for trc in demos}

    state = State(rand_sat, len(demos))
    for nsat in range(len(demos)):
        state.update_nsat(nsat)
        if prune(nsat, low, best_score):
            continue
