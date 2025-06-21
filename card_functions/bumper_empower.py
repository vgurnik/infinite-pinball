import game_context


def effect(scale, arbiters=None, card=None):
    for obj in game_context.game.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity *= scale
    return True


def negative_effect(scale, arbiters=None, card=None):
    for obj in game_context.game.field.objects:
        if obj.shape.type == 'bumper':
            obj.shape.elasticity /= scale
    return True
