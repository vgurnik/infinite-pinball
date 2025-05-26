import os
import pickle
from field import Field
from inventory import PlayerInventory, InventoryItem
import game_context
import game_objects


def save_pref():
    game = game_context.game
    pref_data = {
        "lang": game.config.lang,
        "res": game.screen_size,
        "fs": game.config.fullscreen,
        "debug": game.debug_mode
    }
    with open(game.config.pref_path, 'wb') as file:
        pickle.dump(pref_data, file)


def load_pref(game):
    if not os.path.exists(game.config.pref_path):
        return
    with open(game.config.pref_path, 'rb') as file:
        pref_data = pickle.load(file)
        game.config.lang = pref_data.get("lang", game.config.lang)
        game.screen_size = pref_data.get("res", game.screen_size)
        game.config.fullscreen = pref_data.get("fs", game.config.fullscreen)
        game.debug_mode = pref_data.get("debug", game.debug_mode)


def save(delete=False):
    game = game_context.game
    if delete:
        try:
            os.remove(game.config.save_path)
        except FileNotFoundError:
            pass
        return
    cards = [item.name for item in game.inventory.items]
    balls = [ball.config["name"] for ball in game.field.balls]
    field = []
    save_data = {
        "round": game.round,
        "money": game.money,
        "flags": game.flags,
        "mode": game.ui.mode,
        "inventory": cards,
        "balls": balls,
        "field": field
    }
    with open(game.config.save_path, 'wb') as file:
        pickle.dump(save_data, file)


def load():
    game = game_context.game
    if not os.path.exists(game.config.save_path):
        return False
    with open(game.config.save_path, 'rb') as file:
        save_data = pickle.load(file)
        game.round = save_data.get("round", 0)
        game.money = save_data.get("money", 0)
        game.flags = save_data.get("flags", {})
        game.ui.change_mode(save_data.get("mode", "round"))

        game.inventory = PlayerInventory()
        cards = save_data.get("inventory", [])
        for card_name in cards:
            item = None
            for i in game.config.shop_items["card"]:
                if i.get("name") == card_name:
                    item = i
                    break
            if item is None:
                for i in game.config.shop_items["buildable"]:
                    if i.get("name") == card_name:
                        item = i
                        break
            game.inventory.add_item(InventoryItem(properties=item, sprite=game.textures.get(item.get("sprite"))))

        balls = save_data.get("balls", [])
        game.field = Field()
        game.field.balls.clear()
        for ball_name in balls:
            ball = None
            for name, config in game.config.objects_settings["ball"].items():
                if config.get("name") == ball_name:
                    ball = name
                    break
            game.field.balls.append(game_objects.Ball(
                game.config.objects_settings["ball"][ball], game.config.ball_start,
                game.textures.get(game.config.objects_settings["ball"][ball]["texture"])))
        field = save_data.get("field", [])
    return True