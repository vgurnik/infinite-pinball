def effect(game, difference):
    game.inventory.max_size += difference
    return True


def negative_effect(game, difference):
    game.inventory.max_size -= difference
    return True
