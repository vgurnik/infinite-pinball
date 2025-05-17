import pygame
import game_context


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


def display_screen(screen):
    game = game_context.game
    display = game.display
    screen_size = game.screen_size
    if screen_size[1] / screen_size[0] == 720 / 1280:
        display.blit(scale(screen, screen_size), (0, 0))
    elif screen_size[1] / screen_size[0] > 720 / 1280:
        diff = round(screen_size[1] - screen_size[0] * 720 / 1280)
        display.blit(scale(screen, (screen_size[0], screen_size[1] - diff)), (0, diff // 2))
    else:
        diff = round(screen_size[0] - screen_size[1] * 1280 / 720)
        display.blit(scale(screen, (screen_size[0] - diff, screen_size[1])), (diff // 2, 0))
    pygame.display.flip()