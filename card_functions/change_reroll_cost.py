import game_context


def effect(difference, mode, arbiters=None, card=None):
    game = game_context.game
    if mode == 's':
        game.flags["reroll_start_cost"] += difference
        game.reroll_cost += difference
    elif mode == 'm':
        game.flags["reroll_start_cost"] *= difference
        game.reroll_cost *= difference
    return True


def negative_effect(difference, mode, arbiters=None, card=None):
    game = game_context.game
    if mode == 's':
        game.flags["reroll_start_cost"] -= difference
        game.reroll_cost -= difference
    elif mode == 'm':
        game.flags["reroll_start_cost"] /= difference
        game.reroll_cost /= difference
    return True
