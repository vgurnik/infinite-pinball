def effect(game, difference, mode):
    if mode == 's':
        game.config.extra_award_per_ball += difference
    elif mode == 'm':
        game.config.extra_award_per_ball *= difference
    return True


def negative_effect(game, difference, mode):
    if mode == 's':
        game.config.extra_award_per_ball -= difference
    elif mode == 'm':
        game.config.extra_award_per_ball /= difference
    return True
