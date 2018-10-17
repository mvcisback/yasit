[![Build Status](https://travis-ci.org/mvcisback/yasit.svg?branch=master)](https://travis-ci.org/mvcisback/yasit)
[![codecov](https://codecov.io/gh/mvcisback/yasit/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/yasit)
[![Updates](https://pyup.io/repos/github/mvcisback/yasit/shield.svg)](https://pyup.io/repos/github/mvcisback/yasit/)

[![PyPI version](https://badge.fury.io/py/yasit.svg)](https://badge.fury.io/py/yasit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# yasit
(Y)et (a)nother (s)pecification (i)nference (t)ool

## About

## (Tentative) Usage

`yasit`'s api centers around the `infer` function. For example, let
`concept_class` denote an iterable container (e.g., a `Set` or `List`)
of python objects, supporting the `__call__` and `__leq__` dunder
methods. For example,

```
class TraceProperty:
    def __call__(self, demonstration) -> bool:
        '''
        Evaluate if the provided demonstration satisifies this property.
        '''

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

```
from yasit import infer

spec, score = infer(concept_class, demonstrations)
```
