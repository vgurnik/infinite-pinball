def effect(game, sell_for):
    if game.round_instance is None or not game.round_instance.running:
        return False
    for ball in game.round_instance.active_balls[:]:
        game.round_instance.active_balls.remove(ball)
        game.field.balls.remove(ball)
        ball.remove(game.field.space)
        game.money += sell_for
        return True
