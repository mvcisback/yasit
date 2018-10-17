from math import log


def _info_gain(p, q):
    return p*(log(p) - log(q))


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
    assert data == 0 or rand > 0  # Cannot satisfy spec if rand == 0.
    worse_than_random = data < rand
    return 0 if worse_than_random else info_gain(data, rand)
