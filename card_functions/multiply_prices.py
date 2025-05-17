import game_context


def effect(coefficient, positive_only):
    for item in game_context.game.inventory.items:
        if not positive_only or item.properties["price"] > 0:
            item.properties["price"] = round(item.properties["price"] * coefficient)
    return True
