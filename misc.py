import pygame


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
