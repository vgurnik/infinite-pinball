import game_context


def effect(category):
    game_context.game.config.shop_size[category] += 1
    return True
