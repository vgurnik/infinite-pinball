def effect(game_instance):
    game_instance.field.shield.sensor = False
    return True


def negative_effect(game_instance):
    game_instance.field.shield.sensor = True
    return True
