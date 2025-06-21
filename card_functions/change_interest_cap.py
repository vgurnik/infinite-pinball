import game_context


def effect(difference, mode, arbiters=None, card=None):
    if mode == 's':
        game_context.game.config.interest_cap += difference
    elif mode == 'm':
        game_context.game.config.interest_cap *= difference
    return True


def negative_effect(difference, mode, arbiters=None, card=None):
    if mode == 's':
        game_context.game.config.interest_cap -= difference
    elif mode == 'm':
        game_context.game.config.interest_cap /= difference
    return True
