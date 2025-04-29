import random
from effects import get_functional
import sprites


def _is_allowed(card, game):
    """check if the item is allowed to show up in the current game state"""
    _allowed = [{
        "eval": get_functional(functonal["name"]),
        "params": functonal.get("params", [])
    } for functonal in card.get("functional", [])]
    if len(_allowed) == 0:
        return True
    for func in _allowed:
        if not func["eval"](game, *func["params"]):
            return False
    return True


def choose_items(game, count, pool, rarity_scoring, unique=True):
    rarity_pools = {rarity: [] for rarity in rarity_scoring}
    for item in pool:
        if item["rarity"] in rarity_scoring and _is_allowed(item, game):
            rarity_pools[item["rarity"]].append(item)
    weights = [rarity_scoring[rarity]["value"] for rarity in rarity_pools.keys()]
    weights = [sum(weights[:i])/sum(weights) for i in range(1, len(weights)+1)]
    items = []
    for _ in range(count):
        rnd = random.random()
        for i, w in enumerate(weights):
            if rnd <= w:
                rarity = list(rarity_pools.keys())[i]
                break
        items.append(random.choice(rarity_pools[rarity]))
        if unique:
            rarity_pools[rarity].remove(items[-1])
            if len(rarity_pools[rarity]) == 0:
                del rarity_pools[rarity]
                weights = [rarity_scoring[rarity]["value"] for rarity in rarity_pools.keys()]
                if len(weights) == 0:
                    return items
                weights = [sum(weights[:i])/sum(weights) for i in range(1, len(weights)+1)]
    return items


def load_textures(sprite_config):
    # Load textures
    textures = {sprite: sprites.Sprite(sprite+'.bmp') for sprite in sprite_config["simple"]}
    # Load animated sprites
    for sprite in sprite_config["animated"]:
        file = sprite_config["animated"][sprite]["file"]
        uvs = sprite_config["animated"][sprite]["uvs"]
        wh = sprite_config["animated"][sprite]["wh"]
        ft = sprite_config["animated"][sprite].get("ft", -1)
        textures[sprite] = sprites.AnimatedSprite(file, uvs=uvs, wh=wh, ft=ft)
    # Load sprite sheets
    for sheet_name in sprite_config["spritesheets"]:
        sheet = sprites.Sprite(sheet_name + ".bmp")
        for sprite in sprite_config["sheet_static"].get(sheet_name, []):
            textures[sprite] = sprites.Sprite(sheet, *sprite_config["sheet_static"][sheet_name][sprite])
        for sprite in sprite_config["sheet_animated"].get(sheet_name, []):
            uvs = sprite_config["sheet_animated"][sheet_name][sprite]["uvs"]
            wh = sprite_config["sheet_animated"][sheet_name][sprite]["wh"]
            ft = sprite_config["sheet_animated"][sheet_name][sprite].get("ft", -1)
            textures[sprite] = sprites.AnimatedSprite(sheet, uvs=uvs, wh=wh, ft=ft)
    return textures
