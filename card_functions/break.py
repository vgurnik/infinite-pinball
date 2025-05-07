def effect(game, arbiters=None):
    if arbiters is None:
        return True
    for arb in arbiters:
        game.field.delete(arb)
        if "broken" not in game.flags:
            game.flags["broken"] = 0
        game.flags["broken"] += 1
    return True


def negative_effect(game, arbiters=None):
    if game.flags.get("broken", 0) > 0:
        game.flags["broken"] = 0
        return True
    return False
