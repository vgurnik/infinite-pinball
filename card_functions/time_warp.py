def effect(game_instance, scale):
    game_instance.field.space.gravity *= scale
    if game_instance.round_instance is not None and game_instance.round_instance.ball_launched:
        for ball in game_instance.round_instance.active_balls:
            ball.body.velocity *= scale
    return True


def negative_effect(game_instance, scale):
    game_instance.field.space.gravity /= scale
    if game_instance.round_instance is not None and game_instance.round_instance.ball_launched:
        for ball in game_instance.round_instance.active_balls:
            ball.body.velocity /= scale
    return True
