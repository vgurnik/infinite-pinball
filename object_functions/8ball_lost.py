import game_context
from utils.text import loc


def effect(hits, arbiters=None):
    game = game_context.game
    for arb in arbiters:
        if arb.shape.type == "ball":
            if arb.flags["hits"] < hits:
                game.round_instance.score = 0
                game.money = 0
                game.round_instance.immediate["splash"].append([arb.body.position.x, arb.body.position.y - 50,
                                                                loc("effect.splash.punish"), (255, 0, 0)])
            else:
                game.round_instance.immediate["splash"].append([arb.body.position.x, arb.body.position.y - 50,
                                                                loc("effect.splash.safe"), (255, 255, 100)])
    return True
