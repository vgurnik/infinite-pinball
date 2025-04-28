def effect(game, difference, mode, arbiters=None):
    if game.round_instance is None or not game.round_instance.running:
        return False
    if mode == 's':
        game.round_instance.immediate["multi"] += difference
    elif mode == 'm':
        game.round_instance.immediate["multi"] *= difference
    return True
