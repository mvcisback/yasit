from itertools import combinations

import networkx as nx

from yasit import chain, equiv_classes


def create_lattice(concept_class):
    clses = equiv_classes.find_equiv_cls(concept_class)
    g = nx.DiGraph()
    for cls1, cls2 in combinations(clses, 2):
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


def infer(concept_class, demos):
    if not isinstance(concept_class, nx.DiGraph):
        concept_class = create_lattice(concept_class)

    return max(
        (chain.chain_inference(c, demos) for c in gen_chains(concept_class)),
        key=lambda x: x[0]
    )
