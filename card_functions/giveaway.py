from random import randint


def effect(game, amount, arbiter=None):
    shop = arbiter
    appropriate = []
    for item in shop.items:
        if item.properties["type"] in ["card", "buildable"] and item.properties["price"] > 0:
            appropriate.append(item)
    if len(appropriate) == 0:
        return False
    for _ in range(min(amount, len(appropriate))):
        item = appropriate[randint(0, len(appropriate) - 1)]
        item.properties["buy_price"] = 0
        item.properties["price"] = 0
        appropriate.remove(item)
    return True
