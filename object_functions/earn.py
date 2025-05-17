import game_context


def effect(money, arbiters=None):
    game = game_context.game
    game.round_instance.immediate["money"] += money
