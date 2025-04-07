def effect(game_instance, scale):
    for obj in game_instance.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity *= scale
    return True


def negative_effect(game_instance, scale):
    for obj in game_instance.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity /= scale
    return True
