import game_context
from utils.text import loc


def effect(relative, position, text, color, arbiters=None, card=None):
    if isinstance(relative, str):
        if relative == 'ball':
            for arb in arbiters:
                if arb.shape.type == "ball":
                    position = [arb.body.position.x + position[0], arb.body.position.y + position[1]]
    elif isinstance(relative, list) and len(relative) == 2:
        position = [relative[0] + position[0], relative[1] + position[1]]
    game_context.game.round_instance.immediate["splash"].append([*position, loc(text), color])
    return True
