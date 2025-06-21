import game_context


def effect(flag_name, flag_value=True, arbiters=None, card=None):
    game_context.game.flags[flag_name] = flag_value
    return True
