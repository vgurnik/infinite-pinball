import game_context


def effect(arbiters=None, card=None):
    game_context.game.field.shield.sensor = False
    return True


def negative_effect(arbiters=None, card=None):
    game_context.game.field.shield.sensor = True
    return True
