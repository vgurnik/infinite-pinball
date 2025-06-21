import game_context


def effect(category, arbiters=None, card=None):
    game_context.game.config.shop_size[category] += 1
    return True
