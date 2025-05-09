def effect(game, difference, mode, arbiters=None):
    balls = [ball.config["name"] for ball in game.field.balls]
    if len(balls) != len(set(balls)):
        return False
    if mode == 's':
        game.round_instance.immediate["multi"] += difference
    elif mode == 'm':
        game.round_instance.immediate["multi"] *= difference
    return True
