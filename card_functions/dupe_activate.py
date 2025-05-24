from game_effects import DisappearingItem
from inventory import InventoryItem
import game_context


def effect(arbiters=None):
    game = game_context.game
    for item in game.inventory.items:
        allow = False
        lasting = False
        for e in item.effects:
            if e["usage"] == "active":
                allow = True
            if e["duration"] != 0:
                lasting = True
        item_copy = InventoryItem(item.properties, item.sprite, init_pos=(item.pos[0]+20, item.pos[1]))
        if allow and item_copy.use():
            if lasting:
                game.round_instance.applied_cards.add_item(item_copy)
                game.round_instance.applied_cards.recalculate_targets()
            else:
                game.round_instance.hit_effects.append(DisappearingItem(item_copy, 0.5))
            return True
    return False
