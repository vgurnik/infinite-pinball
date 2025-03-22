from importlib import import_module


def get_card_function(name, negative=False):
    if name is None:
        return None
    card_module = import_module('card_functions.'+name)
    if negative:
        if getattr(card_module, 'negative_effect', None) is None:
            return None
        return card_module.negative_effect
    return card_module.effect


def get_object_function(name):
    if name is None:
        return None
    obj_module = import_module('object_functions.'+name)
    return obj_module.effect
