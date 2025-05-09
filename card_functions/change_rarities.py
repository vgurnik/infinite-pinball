def effect(game, rarities, difference):
    for category in game.config.rarities.values():
        for rarity in category:
            if rarity in rarities or rarity == rarities:
                category[rarity]["value"] *= difference
    return True


def negative_effect(game, rarities, difference):
    for category in game.config.rarities.values():
        for rarity in category:
            if rarity in rarities or rarity == rarities:
                category[rarity]["value"] /= difference
    return True
