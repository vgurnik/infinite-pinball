def effect(game, difference, mode, arbiters=None):
    for arb in arbiters:
        if arb.shape.type != "ball":
            is_bump = False
            for e in arb.effects:
                if e["name"] == "bump":
                    is_bump = True
                    if mode == "s":
                        e["params"][0] += difference
                    else:
                        e["params"][0] *= difference
            if not is_bump and mode == "s":
                arb.effects.append({
                    "name": "bump",
                    "params": [difference, 0]
                })
