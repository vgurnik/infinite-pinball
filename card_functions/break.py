import game_context


def effect(arbiters=None):
    game = game_context.game
    if arbiters is None:
        return True
    for arb in arbiters:
        game.field.delete(arb)
        if "broken" not in game.flags:
            game.flags["broken"] = 0
        game.flags["broken"] += 1
    return True


def negative_effect(arbiters=None):
    game = game_context.game
    if game.flags.get("broken", 0) > 0:
        game.flags["broken"] = 0
        return True
    return False
