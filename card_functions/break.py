import game_context


def effect(arbiters=None, card=None):
    game = game_context.game
    if arbiters is None:
        return True
    for arb in arbiters:
        game.field.delete(arb)
    return True
