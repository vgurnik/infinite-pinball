from random import random
import game_context


def effect(chance, arbiters=None):
    game = game_context.game
    if random() < chance:
        for arb in arbiters:
            if arb.shape.type == 'ball':
                game.round_instance.ball_queue.append(arb)
                game.round_instance.ball_queue_coords.append(arb.body.position.y)
                return
