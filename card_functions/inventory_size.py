import game_context


def effect(difference, arbiters=None, card=None):
    game_context.game.inventory.max_size += difference
    return True


def negative_effect(difference, arbiters=None, card=None):
    game_context.game.inventory.max_size -= difference
    return True
