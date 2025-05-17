import game_context


def effect(difference, mode, arbiters=None):
    if mode == 's':
        game_context.game.score_needed += difference
    elif mode == 'm':
        game_context.game.score_needed *= difference
    return True


def negative_effect(difference, mode, arbiters=None):
    if mode == 's':
        game_context.game.score_needed -= difference
    elif mode == 'm':
        game_context.game.score_needed /= difference
    return True
