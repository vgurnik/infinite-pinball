from random import random


def effect(game, chance, arbiter=None):
    if random() < chance:
        game.round_instance.ball_queue.append(arbiter)
        game.round_instance.ball_queue_coords.append(arbiter.body.position.y)
