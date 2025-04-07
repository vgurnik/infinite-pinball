from importlib import import_module


def get_card_function(name, negative=False):
    if name is None:
        return None
    try:
        card_module = import_module('card_functions.'+name)
    except ModuleNotFoundError:
        return None
    if negative:
        if getattr(card_module, 'negative_effect', None) is None:
            return None
        return card_module.negative_effect
    return card_module.effect


def get_object_function(name):
    if name is None:
        return None
    try:
        obj_module = import_module('object_functions.'+name)
    except ModuleNotFoundError:
        return None
    return obj_module.effect


def call(effect, game, arbiter=None):
    if effect["effect"] is not None:
        if arbiter is not None:
            return effect["effect"](game, *effect["params"], arbiter=arbiter)
        return effect["effect"](game, *effect["params"])
    return True


def recall(effect, game, arbiter=None):
    if effect["negative_effect"] is not None:
        if arbiter is not None:
            return effect["negative_effect"](game, *effect["params"], arbiter=arbiter)
        return effect["negative_effect"](game, *effect["params"])
    return True
