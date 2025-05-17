import game_context


def effect(coefficient, cap):
    game_context.game.money += min(game_context.game.money * (coefficient - 1), cap)
    return True
