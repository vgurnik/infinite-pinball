from game_objects import Ball
import game_context


def effect(difference):
    game = game_context.game
    game.config.balls += difference
    for _ in range(difference):
        game.field.balls.append(Ball(game.config.objects_settings["ball"]["standard"],
                                     game.config.ball_start, game.textures.get(
                game.config.objects_settings["ball"]["standard"]["texture"])))
        if game.round_instance is not None:
            game.round_instance.ball_queue.append(game.field.balls[-1])
    return True


def negative_effect(difference):
    game = game_context.game
    if len(game.field.balls) < difference or (game.round_instance is not None
                                              and len(game.round_instance.ball_queue) < difference):
        return False
    for _ in range(difference):
        game.field.balls.pop()
        if game.round_instance is not None:
            game.round_instance.ball_queue.pop()
    return True
