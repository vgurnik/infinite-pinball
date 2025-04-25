def effect(game_instance, score, money, arbiter=None):
    game_instance.round_instance.immediate["score"] += score
    game_instance.round_instance.immediate["money"] += money
    arbiter.cooldown = 0.3
