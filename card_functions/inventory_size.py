import game_context


def effect(difference):
    game_context.game.inventory.max_size += difference
    return True


def negative_effect(difference):
    game_context.game.inventory.max_size -= difference
    return True
