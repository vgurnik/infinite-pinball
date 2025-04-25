def effect(game, flag_name, flag_value=True):
    game.flags[flag_name] = flag_value
    return True
