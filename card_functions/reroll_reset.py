import game_context


def effect():
    game = game_context.game
    if game.ui.mode != "shop":
        return False
    game.reroll_cost = game.config.reroll_start_cost
    return True
