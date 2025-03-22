def effect(game_instance, score, money):
    game_instance.immediate["score"] += score
    game_instance.immediate["money"] += money