def effect(game_instance, obj, score, money):
    game_instance.round_instance.immediate["score"] += score
    game_instance.round_instance.immediate["money"] += money
    obj.cooldown = 0.1
