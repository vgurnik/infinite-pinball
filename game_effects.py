import pygame
import sys
from multiline_text import multiline


def overlay_menu(screen, title, options):
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
        font = pygame.font.Font("assets/terminal-grotesque.ttf", 36)
        title_text = font.render(title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_text, title_rect)
        option_rects = []
        for idx, option in enumerate(options):
            if idx == selected:
                opt_font = pygame.font.Font("assets/terminal-grotesque.ttf", 42)
                color = (255, 255, 0)
            else:
                opt_font = pygame.font.Font("assets/terminal-grotesque.ttf", 36)
                color = (255, 255, 255)
            text = opt_font.render(option, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
            screen.blit(text, rect)
            option_rects.append(rect)
        pygame.display.flip()


class ContextWindow:
    def __init__(self, pos=(0, 0), text=None, visible=False):
        self.x, self.y = pos
        self.text = text
        self.visible = visible

    def update(self, pos, text):
        self.x, self.y = pos
        self.text = text

    def set_visibility(self, visibility):
        self.visible = visibility

    def draw(self, surface):
        if self.visible:
            font = pygame.font.Font("assets/terminal-grotesque.ttf", 20)
            text_surface = multiline(self.text, font, (0, 0, 0), (200, 200, 200))
            rect = text_surface.get_rect().inflate((6, 6))
            if self.x + rect.width > surface.get_width():
                self.x = surface.get_width() - rect.width
            if self.y + rect.height > surface.get_height():
                self.y = surface.get_height() - rect.height
            rect.topleft = (self.x, self.y)
            pygame.draw.rect(surface, (200, 200, 200), rect, border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=5)
            # Draw the item name centered at the top of the card.
            surface.blit(text_surface, (rect.x + 3, rect.y + 3))


class BaseEffect:
    def __init__(self, pos, lifetime=1.0, image=None):
        self.x, self.y = pos
        self.lifetime = lifetime
        self.age = 0.0
        self.image = image
        self.rect = self.image.get_rect(center=(self.x, self.y)) if image is not None else pygame.Rect((0, 0), (0, 0))

    def is_dead(self):
        return self.age >= self.lifetime

    def update(self, dt):
        self.age += dt

    def draw(self, surface, offset_x=0):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        self.image.set_alpha(alpha)
        surface.blit(self.image, (self.rect.x + offset_x, self.rect.y))


class HitEffect(BaseEffect):
    def __init__(self, pos, text, color, lifetime=1.0):
        super().__init__(pos, lifetime)
        self.text = text
        self.color = color
        self.font = pygame.font.Font("assets/terminal-grotesque.ttf", 24)
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


class DisappearingItem(BaseEffect):
    def __init__(self, original_item, lifetime=1.0):
        super().__init__(original_item.pos, lifetime)
        self.item = original_item

    def draw(self, surface, offset_x=0):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        new_surface = pygame.Surface(self.item.card_size)
        new_surface.set_alpha(alpha)
        rect = pygame.Rect(0, 0, self.item.rect.width, self.item.rect.height)
        if self.item.image:
            img = pygame.transform.smoothscale(self.image, (self.item.card_size[0] - 10, self.item.card_size[1] - 40))
            img_rect = img.get_rect(center=rect.center)
            surface.blit(img, img_rect)
        else:
            # Draw a simple card background.
            match self.item.properties["type"]:
                case "immediate":
                    color = (255, 100, 100)
                case "buildable":
                    color = (100, 100, 255)
                case "pack":
                    color = (100, 255, 100)
                case _:
                    color = (200, 200, 200)
            pygame.draw.rect(new_surface, color, rect, border_radius=5)
            pygame.draw.rect(new_surface, (255, 255, 255), rect, 2, border_radius=5)
        # Draw the item name centered at the top of the card.
        font = pygame.font.Font("assets/terminal-grotesque.ttf", 20)
        text_surface = font.render(self.item.name, True, (0, 0, 0))
        new_surface.blit(text_surface, ((rect.width - text_surface.get_width()) / 2, 5))
        surface.blit(new_surface, self.item.rect.topleft)
