def negative_effect(game, difference, mode_req):
    if mode_req == 'relative':
        return game.round_instance.score / game.score_needed >= difference
    return game.round_instance.score / mode_req >= difference
