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
    return max(
        find_bots(chain, demos), 
        key=lambda x: score(x[0], x[1].rand_sat())
    )
