def effect(game, coefficient, cap):
    game.money += min(game.money * (coefficient - 1), cap)
    return True
