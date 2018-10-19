[![Build Status](https://travis-ci.org/mvcisback/yasit.svg?branch=master)](https://travis-ci.org/mvcisback/yasit)
[![codecov](https://codecov.io/gh/mvcisback/yasit/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/yasit)
[![Updates](https://pyup.io/repos/github/mvcisback/yasit/shield.svg)](https://pyup.io/repos/github/mvcisback/yasit/)

[![PyPI version](https://badge.fury.io/py/yasit.svg)](https://badge.fury.io/py/yasit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# (Y)et (a)nother (s)pecification (i)nference (t)ool

Yasit is a tool for learning "Boolean Specifications" from
demonstrations. In particular, we are given a set of examples from an
agent (also called the teacher) who is performing some task in an
enviroment and ask what is the most likey task given the examples
(also called the demonstrations).

<figure>
  <img src="assets/overview.png" alt="overview.png" width=800px>
</figure>

In this context, a "Boolean Specification" (also called bounded trace
properties) is a set of demonstrations, where one says a demonstration
satisifies the specification if the demonstration lies in the
set. Currently, we assume all demonstrations have the same length. For
example, consider an agent operating in a gridworld with lava, water,
drying tiles, and recharge tiles. The following are example
demonstrations of the following specification: "eventually recharge,
avoid lava, and if you get wet visit a drying tile before recharging".
Each demonstration is visualized using
[github.com/mvcisback/gridworld-visualizer](github.com/mvcisback/gridworld-visualizer).

<object data="assets/example1.svg" type="image/svg+xml">
  <img src="assets/example1.svg" />
</object>
<object data="assets/example2.svg" type="image/svg+xml">
  <img src="assets/example2.svg" />
</object>
<object data="assets/example2.svg" type="image/svg+xml">
  <img src="assets/example2.svg" />
</object>
<object data="assets/example2.svg" type="image/svg+xml">
  <img src="assets/example2.svg" />
</object>

The main purpose of `yasit` is to take a collection of demonstrations
and collection of candidate specifications and find the most probable
one specification. In cartoon math, `yasit` optimizes:

<figure>
  <img src="assets/cartoon_math.png" alt="cartoon math" width=500px>
</figure>

For details on the posteori probability model and algorithm see:
[Vazquez-Chanlatte, Marcell, et al. "Learning Task Specifications from
Demonstrations.", Advances in Neural Information Processing Systems,
NIPS, 2018](https://arxiv.org/abs/1710.03875).

## Usage

`yasit`'s api centers around the `infer` function. For example, let
`concept_class` denote an iterable container (e.g., a `Set` or `List`)
of python objects, supporting the `__call__` and `__leq__` dunder
methods. For example,

```python
class TraceProperty:
    def __hash__(self):
        '''Must be hashable.'''

    def __call__(self, demonstration) -> bool:
        '''Evaluate if the provided demonstration satisifies this property.'''

    def __leq__(self, other) -> bool:
        '''
        Evaluate if this property (self) implies (other).
        - As sets, this corresponds to subset inclusion.
        '''

    def rand_sat(self) -> [0, 1]:
        '''
        Return the probability (in interval [0, 1]) of randomly satisifying 
        the property if one applies actions uniformly at random.
        '''
```

Then if `concept_class` is an iterable of objects conforming to
`TraceProperty`'s API, and `demonstrations` is an iterable of
demonstrations (inputs to `__call__`), finding the most probable
specification is done by:

```python
from yasit import infer

spec, score = infer(concept_class, demonstrations)
```

`infer` also supports taking in a `networkx.DiGraph`. Infact, if
`concept_class` is not a `DiGraph`, the first thing `infer` does it
make it one. The currently procedure to do this is fairly slow and
makes numerous `<=` queries. If these are slow, you may wish to
implement your own `concept_class` to `DiGraph` convertor. Note, that
the resulting graph should be transitively reduced. This can be done
using `networkx.transitive_reduction`.
