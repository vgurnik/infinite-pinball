import game_context


def effect(scale):
    for obj in game_context.game.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity *= scale
    return True


def negative_effect(scale):
    for obj in game_context.game.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity /= scale
    return True
