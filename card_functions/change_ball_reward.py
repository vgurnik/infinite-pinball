import game_context


def effect(difference, mode):
    if mode == 's':
        game_context.game.config.extra_award_per_ball += difference
    elif mode == 'm':
        game_context.game.config.extra_award_per_ball *= difference
    return True


def negative_effect(difference, mode):
    if mode == 's':
        game_context.game.config.extra_award_per_ball -= difference
    elif mode == 'm':
        game_context.game.config.extra_award_per_ball /= difference
    return True
