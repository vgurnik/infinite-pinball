def effect(game_instance, difference, mode):
    if mode == 's':
        game_instance.config.score_multiplier += difference
    elif mode == 'm':
        game_instance.config.score_multiplier *= difference
    return True


def negative_effect(game_instance, difference, mode):
    if mode == 's':
        game_instance.config.score_multiplier -= difference
    elif mode == 'm':
        game_instance.config.score_multiplier /= difference
    return True
