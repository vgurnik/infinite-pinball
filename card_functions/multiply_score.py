def effect(game_instance, difference, mode):
    if mode == 's':
        game_instance.round_instance.immediate["multi"] += difference
    elif mode == 'm':
        game_instance.round_instance.immediate["multi"] *= difference
    return True
