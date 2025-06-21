import game_context


def effect(scale, arbiters=None, card=None):
    game = game_context.game
    if game.round_instance is None or not game.round_instance.running:
        return False
    game.field.space.gravity *= scale
    if game.round_instance is not None and game.round_instance.ball_launched:
        for ball in game.round_instance.active_balls:
            ball.body.velocity *= scale
    return True


def negative_effect(scale, arbiters=None, card=None):
    game = game_context.game
    if game.round_instance is None:
        return False
    game.field.space.gravity /= scale
    if game.round_instance is not None and game.round_instance.ball_launched:
        for ball in game.round_instance.active_balls:
            ball.body.velocity /= scale
    return True
