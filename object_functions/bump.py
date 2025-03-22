def effect(game_instance, score, money):
    game_instance.round_instance.immediate["score"] += score
    game_instance.round_instance.immediate["money"] += money