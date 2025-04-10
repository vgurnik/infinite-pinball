def effect(game, difference, mode):
    if mode == 's':
        game.config.interest_cap += difference
    elif mode == 'm':
        game.config.interest_cap *= difference
    return True


def negative_effect(game, difference, mode):
    if mode == 's':
        game.config.interest_cap -= difference
    elif mode == 'm':
        game.config.interest_cap /= difference
    return True
