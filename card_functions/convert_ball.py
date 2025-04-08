from game_objects import Ball


def effect(game, ball_name):
    if game.round_instance is not None:
        for ball in game.round_instance.active_balls[:]:
            new_ball = Ball(game.config.objects_settings["ball"][ball_name], game.config.ball_start,
                            game.textures.get(game.config.objects_settings["ball"][ball_name]["texture"]))
            game.round_instance.active_balls.remove(ball)
            game.field.balls.remove(ball)
            ball.remove(game.field.space)
            game.round_instance.active_balls.append(new_ball)
            game.field.balls.append(new_ball)
            new_ball.activate(game.field.space, ball.body.position)
            new_ball.body.velocity = ball.body.velocity
            return True
    return False
