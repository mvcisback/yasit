from itertools import combinations

import funcy as fn
import networkx as nx

from yasit import chain, equiv_classes
from yasit.chain import percent_sat
from yasit.edges import possible_edges, adj_list
from yasit.scoring import score


def create_lattice(concept_class, *, parallel=True):
    child_map = adj_list(concept_class)
    clses = equiv_classes.find_equiv_cls(
        concept_class, child_map=child_map, parallel=parallel
    )
    g = nx.DiGraph()
    for cls1, cls2 in possible_edges(clses):
        if cls1 <= cls2:
            g.add_edge(cls1.rep, cls2.rep)
        if cls2 <= cls1:
            g.add_edge(cls2.rep, cls1.rep)

    return nx.transitive_reduction(g)


def traverse(concept_class, demos):
    if not isinstance(concept_class, nx.DiGraph):
        concept_class = create_lattice(concept_class).reverse()

    yield from ((n, tuple(concept_class[n])) for n in concept_class)


@fn.curry
def is_candidate(demos, node_and_parents):
    node, parents = node_and_parents
    psat = percent_sat(node, demos)
    return any(percent_sat(p, demos) != psat for p in parents)


@fn.curry
def score_candidate(demos, spec):
    psat = percent_sat(spec, demos)
    return score(psat, spec.rand_sat())


def infer(concept_class, demos, brute_force=False):
    candidates = list(traverse(concept_class, demos))
    assert len(candidates) == 6
    if not brute_force:
        candidates = list(filter(is_candidate(demos), candidates))

    candidates = list(fn.pluck(0, candidates))
    print([score_candidate(demos)(c) for c in candidates])
    return max(candidates, key=score_candidate(demos))
