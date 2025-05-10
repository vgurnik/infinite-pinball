def effect(game, mult, arbiters=None):
    for arb in arbiters:
        if arb.config["name"] == "object.pinpoint.name":
            arb.flags["sprite"] = 1 - arb.flags["sprite"]
    number = 0
    all_hit = True
    for obj in game.field.objects:
        if obj.config["name"] == "object.pinpoint.name":
            number += 1
            if obj.flags["sprite"] == 0:
                all_hit = False
                break
    if all_hit and number > 1:
        game.round_instance.immediate["score"] += number * mult
        for obj in game.field.objects:
            if obj.config["name"] == "object.pinpoint.name":
                obj.flags["sprite"] = 0
        return True
    if all_hit:
        game.round_instance.immediate["score"] += mult // 10
        return True
    return False
