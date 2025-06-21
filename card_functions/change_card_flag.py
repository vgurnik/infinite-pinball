def effect(flag, difference, mode, arbiters=None, card=None):
    if mode == 's':
        if flag not in card.flags:
            card.flags[flag] = 0
        card.flags[flag] += difference
    elif mode == 'm':
        if flag not in card.flags:
            card.flags[flag] = 1
        card.flags[flag] *= difference
    elif mode == 'e':
        card.flags[flag] = difference
    return True
