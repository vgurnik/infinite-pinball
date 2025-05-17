import game_context


def effect(difference, mode):
    if mode == 's':
        game_context.game.config.interest_cap += difference
    elif mode == 'm':
        game_context.game.config.interest_cap *= difference
    return True


def negative_effect(game, difference, mode):
    if mode == 's':
        game_context.game.config.interest_cap -= difference
    elif mode == 'm':
        game_context.game.config.interest_cap /= difference
    return True
