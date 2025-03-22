def effect(game_instance, scale):
    for obj in game_instance.round_instance.objects:
        if obj.type == 'bumper':
            obj.shape.elasticity *= scale
    return True


def negative_effect(game_instance, scale):
    for obj in game_instance.round_instance.objects:
        if obj.type == 'bumper':
            obj.shape.elasticity /= scale
    return True
