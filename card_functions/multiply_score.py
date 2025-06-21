import game_context


def effect(difference, mode, arbiters=None, card=None):
    game = game_context.game
    if game.round_instance is None or not game.round_instance.running:
        return False
    if isinstance(difference, str):
        difference = card.flags.get(difference, 0)
    if mode == 's':
        game.round_instance.immediate["multi"] += difference
    elif mode == 'm':
        game.round_instance.immediate["multi"] *= difference
    return True
