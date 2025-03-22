def effect(game_instance, scale):
    game_instance.round_instance.space.gravity *= scale
    game_instance.round_instance.ball.body.velocity *= scale
    return True


def negative_effect(game_instance, scale):
    game_instance.round_instance.space.gravity /= scale
    game_instance.round_instance.ball.body.velocity /= scale
    return True
