from random import random
import game_context


def effect(min_s, max_s, arbiters=None):
    for a in arbiters:
        if a.shape.type == 'bumper':
            a.force = 0.5 + random()
    game_context.game.round_instance.immediate["score"] += int(random() * (max_s - min_s) + min_s)
    game_context.game.sound.play('tmpchime')
