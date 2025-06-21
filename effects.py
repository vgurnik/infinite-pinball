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
    if getattr(card_module, 'effect', None) is None:
        return None
    return card_module.effect


def get_object_function(name):
    if name is None:
        return None
    try:
        obj_module = import_module('object_functions.'+name)
    except ModuleNotFoundError:
        return None
    return obj_module.effect


def get_functional(name):
    if name is None:
        return None
    try:
        func_module = import_module('functionals.'+name)
    except ModuleNotFoundError:
        return None
    return func_module.evaluate


def call(effect, arbiters=None, card=None):
    if effect["effect"] is None:
        return True
    e = effect["effect"]
    p = effect["params"]
    if arbiters is not None:
        if card is not None:
            return e(*p, arbiters=arbiters, card=card)
        return e(*p, arbiters=arbiters)
    if card is not None:
        return e(*p, card=card)
    return e(*p)


def recall(effect, arbiters=None, card=None):
    if effect["negative_effect"] is None:
        return True
    e = effect["negative_effect"]
    p = effect["params"]
    if arbiters is not None:
        if card is not None:
            return e(*p, arbiters=arbiters, card=card)
        return e(*p, arbiters=arbiters)
    if card is not None:
        return e(*p, card=card)
    return e(*p)
