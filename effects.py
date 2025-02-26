import pygame
import sys


def overlay_menu(screen, title, options):
    clock = pygame.time.Clock()
    selected = 0
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    option_rects = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        return options[i]
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = i

        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 36)
        title_text = font.render(title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_text, title_rect)
        option_rects = []
        for idx, option in enumerate(options):
            if idx == selected:
                opt_font = pygame.font.SysFont("Arial", 42)
                color = (255, 255, 0)
            else:
                opt_font = pygame.font.SysFont("Arial", 36)
                color = (255, 255, 255)
            text = opt_font.render(option, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
            screen.blit(text, rect)
            option_rects.append(rect)
        pygame.display.flip()
        clock.tick(30)


class HitEffect:
    def __init__(self, pos, text, color, lifetime=1.0):
        self.x, self.y = pos
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.font = pygame.font.SysFont("Arial", 24)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        self.age += dt
        self.y -= 30 * dt
        self.rect.center = (self.x, self.y)

    def draw(self, surface, offset_x=0):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        image = self.font.render(self.text, True, self.color)
        image.set_alpha(alpha)
        surface.blit(image, (self.rect.x + offset_x, self.rect.y))

    def is_dead(self):
        return self.age >= self.lifetime
