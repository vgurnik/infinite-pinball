import game_context


def effect(difference, mode):
    if mode == 's':
        game_context.game.config.interest_rate += difference
    elif mode == 'm':
        game_context.game.config.interest_rate *= difference
    return True


def negative_effect(difference, mode):
    if mode == 's':
        game_context.game.config.interest_rate -= difference
    elif mode == 'm':
        game_context.game.config.interest_rate /= difference
    return True
