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


def gen_chains(lat):
    stack = [n for n, d in lat.in_degree() if d == 0]
    visited = set()
    curr_chain = []
    while stack:
        curr = stack.pop()
        curr_chain.append(curr)
        visited.add(curr)
        children = list(lat[curr])
        stack += [c for c in children if c not in visited]

        if set(children) <= visited:
            yield curr_chain
            curr_chain = []


def traverse(concept_class, demos):
    if not isinstance(concept_class, nx.DiGraph):
        concept_class = create_lattice(concept_class).reverse()

    new_edges = [(None, n) for n, d in concept_class.in_degree() if d == 0]
    concept_class.add_edges_from(new_edges)
    traversal = nx.bfs_successors(concept_class, None)
    next(traversal) # First element is None which is a fake specification.
    yield from traversal


@fn.curry
def is_candidate(demos, node_and_parents):
    node, parents = node_and_parents
    psat = percent_sat(node, demos)
    return True
    return all(percent_sat(p, demos) != psat for p in parents)


@fn.curry
def score_candidate(demos, spec):
    psat = percent_sat(spec, demos)
    return score(psat, spec.rand_sat())


def infer(concept_class, demos, brute_force=False):
    candidates = traverse(concept_class, demos)
    if not brute_force:
        candidates = filter(is_candidate(demos), candidates)

    candidates = fn.pluck(0, candidates)
    return max(candidates, key=score_candidate(demos))
