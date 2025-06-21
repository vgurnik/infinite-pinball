import random
import game_context


def effect(arbiters=None, card=None):
    game = game_context.game
    balls = game.round_instance.ball_queue
    charged = not game.round_instance.ball_launched and len(game.round_instance.active_balls) == 1
    if charged:
        game.round_instance.active_balls[0].remove(game.field.space)
        balls.append(game.round_instance.active_balls[0])
        game.round_instance.active_balls.clear()
    if len(balls) == 0:
        return False
    random.shuffle(balls)
    if len(balls) * 35 > 600:
        spacing = 600 / len(balls)
    else:
        spacing = 35
    game.round_instance.ball_queue = balls
    game.round_instance.ball_queue_coords = [game.config.ball_queue_lower_y - (len(game.round_instance.ball_queue) - i)
                                             * spacing for i in range(len(balls))]
    if charged:
        game.round_instance.recharge()
    return True