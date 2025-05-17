from random import random
import game_context


def effect(chance, arbiters=None):
    if random() < chance:
        for arb in arbiters:
            if arb.shape.type == 'ball':
                game_context.game.round_instance.ball_queue.append(arb)
                game_context.game.round_instance.ball_queue_coords.append(arb.body.position.y)
                return
