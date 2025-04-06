def effect(game_instance, scale):
    game_instance.field.space.gravity *= scale
    if game_instance.round_instance is not None and game_instance.round_instance.ball is not None:
        game_instance.round_instance.ball.body.velocity *= scale
    return True


def negative_effect(game_instance, scale):
    game_instance.field.space.gravity /= scale
    if game_instance.round_instance is not None and game_instance.round_instance.ball is not None:
        game_instance.round_instance.ball.body.velocity /= scale
    return True
