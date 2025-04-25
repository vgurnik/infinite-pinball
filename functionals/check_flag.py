def evaluate(game, flag_name, value=True):
    flag = game.flags.get(flag_name)
    if flag is None:
        return False
    return flag == value
