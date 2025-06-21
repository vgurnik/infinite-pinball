import game_context


def effect(rarities, difference, arbiters=None, card=None):
    for category in game_context.game.config.rarities.values():
        for rarity in category:
            if rarity in rarities or rarity == rarities:
                category[rarity]["value"] *= difference
    return True


def negative_effect(rarities, difference, arbiters=None, card=None):
    for category in game_context.game.config.rarities.values():
        for rarity in category:
            if rarity in rarities or rarity == rarities:
                category[rarity]["value"] /= difference
    return True
