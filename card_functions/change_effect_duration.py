def effect(name, difference, mode, arbiters=None, card=None):
    if mode == 's':
        for eff in card.effects:
            if eff["name"] == name:
                eff["duration"] += difference
    elif mode == 'm':
        for eff in card.effects:
            if eff["name"] == name:
                eff["duration"] *= difference
    elif mode == 'e':
        for eff in card.effects:
            if eff["name"] == name:
                eff["duration"] = difference
    card.duration = max(card.duration, max(e.get("duration", 0) for e in card.effects))
    return True
