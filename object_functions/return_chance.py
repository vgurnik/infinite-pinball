from random import random


def effect(game, chance, arbiters=None):
    if random() < chance:
        for arb in arbiters:
            if arb.shape.type == 'ball':
                game.round_instance.ball_queue.append(arb)
                game.round_instance.ball_queue_coords.append(arb.body.position.y)
                return
