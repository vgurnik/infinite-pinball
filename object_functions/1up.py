def effect(game, difference, mode, arbiters=None):
    for arb in arbiters:
        if arb.shape.type != "ball":
            for e in arb.effects:
                if e["name"] == "bump":
                    if mode == "s":
                        e["params"][0] += difference
                    else:
                        e["params"][0] *= difference
