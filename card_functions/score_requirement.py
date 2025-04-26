def effect(game, difference, mode, arbiter=None):
    if mode == 's':
        game.score_needed += difference
    elif mode == 'm':
        game.score_needed *= difference
    return True


def negative_effect(game, difference, mode, arbiter=None):
    if mode == 's':
        game.score_needed -= difference
    elif mode == 'm':
        game.score_needed /= difference
    return True
