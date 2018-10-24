from yasit.scoring import score


def percent_sat(spec, demos):
    return sum(map(spec, demos)) / len(demos)


def find_bots(chain, demos):
    # TODO: implement as binary search.
    psat_prev = None
    for spec in chain:
        psat = percent_sat(spec, demos)
        if psat != psat_prev:
            yield psat, spec
        psat_prev = psat


def chain_inference(chain, demos):
    bots = find_bots(chain, demos)
    scored = ((score(psat, spec.rand_sat()), spec) for psat, spec in bots)
    return max(scored, key=lambda x: x[0], default=(0, None))
