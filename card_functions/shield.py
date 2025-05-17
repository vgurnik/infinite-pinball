import game_context


def effect():
    game_context.game.field.shield.sensor = False
    return True


def negative_effect():
    game_context.game.field.shield.sensor = True
    return True
