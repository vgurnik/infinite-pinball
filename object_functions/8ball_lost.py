def effect(game, hits, arbiters=None):
    for arb in arbiters:
        if arb.shape.type == "ball":
            if arb.flags["hits"] < hits:
                game.round_instance.score = 0
                game.money = 0
    return True
