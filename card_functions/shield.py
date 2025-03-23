def effect(game_instance):
    game_instance.round_instance.shield.sensor = False
    return True


def negative_effect(game_instance):
    game_instance.round_instance.shield.sensor = True
    return True
