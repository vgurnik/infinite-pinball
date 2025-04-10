def effect(game_instance, money, arbiter=None):
    game_instance.round_instance.immediate["money"] += money
    arbiter.cooldown = 0.5
