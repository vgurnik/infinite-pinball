import game_context


def evaluate(flag_name, value=True):
    flag = game_context.game.flags.get(flag_name)
    if flag is None:
        return False
    return flag == value
