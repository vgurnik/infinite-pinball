import game_context


def effect(coefficient, arbiters=None, card=None):
    game_context.game.immediate["$additional"].append([card.properties["price"] * coefficient, card.name])
    return True
