def negative_effect(flag, value, mode, arbiters=None, card=None):
    if mode == '=':
        return card.flags.get(flag, None) == value
    if mode == '>':
        return card.flags.get(flag, None) > value
    return True
