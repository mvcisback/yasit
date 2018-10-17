from itertools import combinations, product
from typing import Set

import attr


@attr.s(auto_attribs=True, frozen=True)
class EquivCls:
    rep: 'Spec'
    elements: Set['Spec']

    def __or__(self, other):
        return attr.evolve(self, elements=self.elements | other.elements)

    def __leq__(self, other):
        return any(x1 <= x2 for x1, x2 in product(self.elements, other.elements))


def find_equiv_cls(concept_class):
    clses = {spec: EquivCls(spec, frozenset({spec})) for spec in concept_class}
    for spec1, spec2 in combinations(concept_class, 2):
        if spec1 <= spec2 and spec2 <= spec1:
            clses[spec1] |= clses[spec2]
            clses[spec2] = clses[spec1]

    return set(clses.values())
