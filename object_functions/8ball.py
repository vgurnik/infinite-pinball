import random


def effect(game, score, chance, arbiters=None):
    for arb in arbiters:
        if arb.shape.type == "flipper":
            return False
    hits = 0
    for arb in arbiters:
        if arb.shape.type == "ball":
            arb.flags["hits"] += 1
            hits = arb.flags["hits"]
            needed = 0
            for eff in arb.effects:
                if eff["name"] == "8ball_lost":
                    needed = eff["params"][0]
    if hits < needed:
        game.round_instance.immediate["hits"].append((str(hits), (255, 0, 0)))
    elif hits == needed:
        game.round_instance.immediate["hits"].append((str(hits), (10, 255, 100)))
    if random.random() < chance:
        game.round_instance.immediate["score"] += score
    return True
