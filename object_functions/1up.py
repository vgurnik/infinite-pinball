import effects


def effect(difference, mode, arbiters=None):
    for arb in arbiters:
        if arb.shape.type not in ["ball", "flipper"] and arb.cooldown == 0:
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
                    "effect": effects.get_object_function("bump"),
                    "params": [difference, 0],
                    "trigger": "collision",
                    "cooldown": 0.3
                })
