from random import random
import game_context
from utils.text import loc


def effect(chance, arbiters=None):
    game = game_context.game
    for arb in arbiters:
        if arb.shape.type == 'ball':
            if arb in game.round_instance.ball_queue:
                return True
            if random() < chance:
                game.round_instance.ball_queue.append(arb)
                game.round_instance.ball_queue_coords.append(arb.body.position.y)
                game.round_instance.immediate["splash"].append([arb.body.position.x, arb.body.position.y - 50,
                                                                loc("effect.splash.yes"), (255, 255, 100)])
                return True
            game.round_instance.immediate["splash"].append([arb.body.position.x, arb.body.position.y - 50,
                                                            loc("effect.splash.no"), (255, 0, 0)])
            return True
