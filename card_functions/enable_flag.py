import game_context


def effect(flag_name, flag_value=True):
    game_context.game.flags[flag_name] = flag_value
    return True
