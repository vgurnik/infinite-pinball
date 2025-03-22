def effect(game_instance, difference):
    game_instance.config.balls += difference
    game_instance.round_instance.balls_left += difference
    return True


def negative_effect(game_instance, difference):
    if game_instance.config.balls - difference < 0 or game_instance.round_instance.balls_left - difference < 0:
        return False
    game_instance.config.balls -= difference
    game_instance.round_instance.balls_left -= difference
    return True
