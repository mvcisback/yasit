from typing import List

import attr

from yasit import infer


@attr.s(auto_attribs=True, frozen=True, cmp=False)
class Lattice:
    children: List['Spec']
    spec: 'Spec'

    def gen_chains(self):
        stack, visited = [self], set()
        curr_chain = []
        while stack:
            curr = stack.pop()
            curr_chain.append(curr.spec)
            visited.add(curr)
            stack += [c for c in curr.children if c not in visited]

            if set(curr.children) <= visited:
                yield curr_chain
                curr_chain = []

    def infer(self, demos):
        return max(
            (infer.chain_inference(c, demos) for c in self.gen_chains()),
            key=lambda x: x[0]
        )
