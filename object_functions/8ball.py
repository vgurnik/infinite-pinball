import random


def effect(game, score, chance, arbiters=None):
    for arb in arbiters:
        if arb.shape.type == "ball":
            arb.params["hits"] += 1
    if random.random() < chance:
        game.round_instance.immediate["score"] += score
    return True
