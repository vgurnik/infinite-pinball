def effect(game, difference, mode, arbiter=None):
    if game.round_instance is None:
        return False
    if mode == 's':
        game.round_instance.immediate["multi"] += difference
    elif mode == 'm':
        game.round_instance.immediate["multi"] *= difference
    return True
