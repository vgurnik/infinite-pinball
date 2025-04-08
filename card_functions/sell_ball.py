def effect(game, sell_for):
    if game.round_instance is not None:
        for ball in game.round_instance.active_balls[:]:
            game.round_instance.active_balls.remove(ball)
            game.field.balls.remove(ball)
            game.money += sell_for
            return True
    return False
