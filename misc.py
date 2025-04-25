import random
import pygame
from effects import get_functional


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


def rotoscale(texture, angle, new_size):
    return pygame.transform.rotate(pygame.transform.scale(texture, new_size), round(angle))


def scale(texture, new_size):
    return pygame.transform.scale(texture, new_size)


def mouse_scale(mouse_pos):
    """Scale mouse position from screen coordinates to game coordinates."""
    screen_size = pygame.display.get_window_size()
    x = mouse_pos[0] * 1280. / screen_size[0]
    y = mouse_pos[1] * 720. / screen_size[1]
    return x, y


def color(hex_color):
    return [int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:], 16)]


def display_screen(display, screen, screen_size):
    if screen_size[1] / screen_size[0] == 720 / 1280:
        display.blit(scale(screen, screen_size), (0, 0))
    elif screen_size[1] / screen_size[0] > 720 / 1280:
        diff = round(screen_size[1] - screen_size[0] * 720 / 1280)
        display.blit(scale(screen, (screen_size[0], screen_size[1] - diff)), (0, diff // 2))
    else:
        diff = round(screen_size[0] - screen_size[1] * 1280 / 720)
        display.blit(scale(screen, (screen_size[0] - diff, screen_size[1])), (diff // 2, 0))
    pygame.display.flip()
