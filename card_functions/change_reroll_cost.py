def effect(game, difference, mode):
    if mode == 's':
        game.config.reroll_start_cost += difference
        game.reroll_cost += difference
    elif mode == 'm':
        game.config.reroll_start_cost *= difference
        game.reroll_cost *= difference
    return True


def negative_effect(game, difference, mode):
    if mode == 's':
        game.config.reroll_start_cost -= difference
        game.reroll_cost -= difference
    elif mode == 'm':
        game.config.reroll_start_cost /= difference
        game.reroll_cost /= difference
    return True
