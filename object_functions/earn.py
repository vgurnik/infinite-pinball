def effect(game_instance, obj, money):
    game_instance.round_instance.immediate["money"] += money
    obj.cooldown = 0.2
