import os
import pickle
import game_context


def save(delete=False):
    game = game_context.game
    if delete:
        try:
            os.remove(game.config.save_path)
        except FileNotFoundError:
            pass
        return
    save_data = {
        "round": game.round,
        "money": game.money,
        "flags": game.flags,
        "mode": game.ui.mode
    }
    with open(game.config.save_path, 'wb') as file:
        pickle.dump(save_data, file)


def load():
    game = game_context.game
    if not os.path.exists(game.config.save_path):
        return False
    with open(game.config.save_path, 'rb') as file:
        save_data = pickle.load(file)
        game.round = save_data["round"]
        game.money = save_data["money"]
        game.flags = save_data["flags"]
        game.ui.mode = save_data["mode"]
    return True