import game_context


def negative_effect(difference, mode_req, arbiters=None, card=None):
    game = game_context.game
    if mode_req == 'relative':
        return game.round_instance.score / game.score_needed >= difference
    return game.round_instance.score / mode_req >= difference
