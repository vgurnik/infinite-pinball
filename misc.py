import pygame


def rotoscale(texture, angle, new_size):
    return pygame.transform.rotate(pygame.transform.scale(texture, new_size), round(angle))


def scale(texture, new_size):
    return pygame.transform.scale(texture, new_size)
