from itertools import product
from typing import Set

import attr
import funcy as fn

from yasit.edges import adj_list, possible_edges


def find_equiv_cls(concept_class, *, child_map=None, parallel=True):
    if child_map is None:
        child_map = adj_list(concept_class)

    @attr.s(auto_attribs=True, frozen=True, cmp=False)
    class EquivCls:
        elements: Set['Spec']

        def __or__(self, other):
            return attr.evolve(self, elements=self.elements | other.elements)

        def __le__(self, other):
            pairwise = product(self.elements, other.elements)
            return any(x2 in child_map[x1] for x1, x2 in pairwise)

        @property
        def rep(self):
            return fn.first(self.elements)

    clses = {spec: EquivCls(frozenset({spec})) for spec in concept_class}

    # TODO: implement this via a parallel reduction.
    for spec1, spec2 in possible_edges(concept_class):
        if (spec2 in child_map[spec1]) and (spec1 in child_map[spec2]):
            clses[spec1] |= clses[spec2]
            clses[spec2] = clses[spec1]

    return set(clses.values())
