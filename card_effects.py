from importlib import import_module


def get_card_function(name):
    card_module = import_module('card_functions.'+name)
    return card_module.effect
