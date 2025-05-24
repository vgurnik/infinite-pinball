import game_context


def effect(score, money, arbiters=None):
    game = game_context.game
    game.round_instance.immediate["score"] += score
    game.round_instance.immediate["money"] += money
    game.sound.play('tmpchime')
