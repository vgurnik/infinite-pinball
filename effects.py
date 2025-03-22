from importlib import import_module


def get_card_function(name):
    if name is None:
        return None
    card_module = import_module('card_functions.'+name)
    return card_module.effect


def get_object_function(name):
    if name is None:
        return None
    obj_module = import_module('object_functions.'+name)
    return obj_module.effect
