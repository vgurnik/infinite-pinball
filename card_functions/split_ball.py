from game_objects import Ball
import game_context


def effect():
    game = game_context.game
    if game.round_instance is not None and game.round_instance.ball_launched:
        for ball in game.round_instance.active_balls:
            game.round_instance.active_balls.append(Ball(ball.config, ball.body.position, ball.sprite))
            game.round_instance.active_balls[-1].activate(game.field.space)
            return True
    return False
