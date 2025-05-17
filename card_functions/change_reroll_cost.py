import game_context


def effect(difference, mode):
    game = game_context.game
    if mode == 's':
        game.config.reroll_start_cost += difference
        game.reroll_cost += difference
    elif mode == 'm':
        game.config.reroll_start_cost *= difference
        game.reroll_cost *= difference
    return True


def negative_effect(difference, mode):
    game = game_context.game
    if mode == 's':
        game.config.reroll_start_cost -= difference
        game.reroll_cost -= difference
    elif mode == 'm':
        game.config.reroll_start_cost /= difference
        game.reroll_cost /= difference
    return True
