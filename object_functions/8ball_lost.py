import game_context

def effect(hits, arbiters=None):
    game = game_context.game
    for arb in arbiters:
        if arb.shape.type == "ball":
            if arb.flags["hits"] < hits:
                game.round_instance.score = 0
                game.money = 0
    return True
