def effect(game_instance, difference):
    game_instance.inventory.max_size += difference
    return True


def negative_effect(game_instance, difference):
    game_instance.inventory.max_size -= difference
    return True
