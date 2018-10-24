from collections import defaultdict
from itertools import combinations

import funcy as fn


def possible_edges(concept_class):
    return combinations(concept_class, 2)


def get_edges(specs):
    edges = []
    if specs[0] <= specs[1]:
        edges.append(specs)
    if specs[1] <= specs[0]:
        edges.append(reversed(specs))
    return edges


def adj_list(concept_class, parallel=True):
    if parallel:
        from pathos.multiprocessing import ProcessingPool
        pool = ProcessingPool()
        mapper = pool.map
    else:
        mapper = map

    edge_generator = fn.cat(mapper(get_edges, possible_edges(concept_class)))
    edge_lists = fn.walk_values(set, fn.group_values(edge_generator))
    return defaultdict(set, edge_lists)
