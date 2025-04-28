def effect(game_instance, money, arbiters=None):
    game_instance.round_instance.immediate["money"] += money
