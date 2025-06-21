import game_context


def effect(difference, mode, arbiters=None, card=None):
    if isinstance(difference, str):
        difference = card.flags.get(difference, 0)
    if mode == 's':
        game_context.game.flags["base_mult"] += difference
    elif mode == '-s':
        game_context.game.flags["base_mult"] -= difference
    elif mode == 'm':
        game_context.game.flags["base_mult"] *= difference
    return True


def negative_effect(difference, mode, arbiters=None, card=None):
    if isinstance(difference, str):
        difference = card.flags.get(difference, 0)
    if mode == 's':
        game_context.game.flags["base_mult"] -= difference
    elif mode == '-s':
        game_context.game.flags["base_mult"] += difference
    elif mode == 'm':
        game_context.game.flags["base_mult"] /= difference
    return True
