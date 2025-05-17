import pygame
from utils.text import multiline, loc
import utils.textures
import game_context


class ContextWindow:
    def __init__(self, pos=(0, 0), item=None, visible=False):
        config = game_context.game.config
        self.rarities = config.rarities
        self.lang = config.lang
        self.x, self.y = pos
        self.item = item
        self.visible = visible
        self.mode = 'text'

    def update(self, pos, mode, item):
        self.x, self.y = pos
        self.x += 10
        self.mode = mode
        self.item = item

    def set_visibility(self, visibility):
        self.visible = visibility

    def draw(self, surface):
        if self.visible:
            font = pygame.font.Font(game_context.game.config.fontfile, 20)
            match self.mode:
                case 'text':
                    text_surface = multiline(loc(self.item, self.lang), font, (0, 0, 0), (200, 200, 200))
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
                case 'description':
                    header = multiline(loc(self.item.name, self.lang), font, (50, 50, 50))
                    description = multiline(loc(self.item.properties["description"], self.lang), font, (0, 0, 0))
                    price = font.render("$" + str(self.item.properties["price"]), 1, (255, 255, 0))
                    price_shadow = font.render("$" + str(self.item.properties["price"]), 1, (0, 0, 0))
                    width = max(header.get_width(), price.get_width(), description.get_width()) + 12
                    height = header.get_height() + price.get_height() + description.get_height() + 18
                    rarity = self.item.properties.get("rarity", None)
                    if rarity is not None:
                        rarity = self.rarities[self.item.properties["type"]][rarity]
                        rarity_shadow = font.render(loc(rarity["name"], self.lang), 1, (0, 0, 0))
                        rarity = font.render(loc(rarity["name"], self.lang), 1, utils.textures.color(rarity["color"]))
                        height += rarity.get_height() + 6
                    if self.x + width > surface.get_width():
                        self.x = surface.get_width() - width
                    if self.y + height > surface.get_height():
                        self.y = surface.get_height() - height
                    rect = pygame.Rect(self.x, self.y, width, height)
                    pygame.draw.rect(surface, (200, 200, 200), rect, border_radius=5)
                    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=5)
                    pygame.draw.rect(surface, (110, 110, 110), description.get_rect(topleft=(
                        self.x + 6, self.y + header.get_height() + 9)).inflate((6, 6)), border_radius=5)
                    surface.blit(header, (self.x + (width - header.get_width()) / 2, self.y + 3))
                    surface.blit(description, (self.x + 6, self.y + 9 + header.get_height()))
                    for x, y in zip((0, -1, 0, 1), (-1, 0, 1, 0)):
                        surface.blit(price_shadow, (self.x + (width - price.get_width()) / 2 + x,
                                                    self.y + 15 + header.get_height() + description.get_height() + y))
                    surface.blit(price, (self.x + (width - price.get_width()) / 2,
                                         self.y + 15 + header.get_height() + description.get_height()))
                    if rarity is not None:
                        for x, y in zip((0, -1, 0, 1), (-1, 0, 1, 0)):
                            surface.blit(rarity_shadow, (self.x + (width - rarity.get_width()) / 2 + x,
                                                        self.y + height - rarity.get_height() - 3 + y))
                        surface.blit(rarity, (self.x + (width - rarity.get_width()) / 2,
                                              self.y + height - rarity.get_height() - 3))
                case 'sell':
                    if self.item >= 0:
                        text_surface = multiline(loc("ui.text.sell+", self.lang).format(self.item), font, (0, 0, 0),
                                                 (200, 200, 200))
                    else:
                        text_surface = multiline(loc("ui.text.sell-", self.lang).format(-self.item), font, (0, 0, 0),
                                                 (200, 200, 200))
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

    def draw(self, surface):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        self.image.set_alpha(alpha)
        surface.blit(self.image, (self.rect.x, self.rect.y))


class HitEffect(BaseEffect):
    def __init__(self, pos, text, color, lifetime=1.0):
        super().__init__(pos, lifetime)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(game_context.game.config.fontfile, 24)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        self.age += dt
        self.y -= 30 * dt
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        image = self.font.render(self.text, True, self.color)
        image.set_alpha(alpha)
        surface.blit(image, (self.rect.x, self.rect.y))


class DisappearingItem(BaseEffect):
    def __init__(self, original_item, lifetime=1.0):
        super().__init__(original_item.pos, lifetime)
        self.item = original_item

    def draw(self, surface):
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        new_surface = pygame.Surface(self.item.card_size, pygame.SRCALPHA)
        new_surface.set_alpha(alpha)
        rect = pygame.Rect(0, 0, self.item.rect.width, self.item.rect.height)
        if self.item.sprite:
            self.item.sprite.draw(new_surface, rect.topleft, rect.size)
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
            font = pygame.font.Font(game_context.game.config.fontfile, 20)
            text_surface = font.render(self.item.name, True, (0, 0, 0))
            new_surface.blit(text_surface, ((rect.width - text_surface.get_width()) / 2, 5))
        surface.blit(new_surface, self.item.rect.topleft)


class AnimatedEffect:

    def __init__(self, display, screen_size):
        self.display = display
        self.screen_size = screen_size

    def start(self, screen, sprite, pos, size):
        clock = pygame.time.Clock()
        sprite.set_frame(0)
        while True:
            dt = clock.tick() / 1000
            new_screen = pygame.Surface(self.screen_size)
            new_screen.blit(screen, (0, 0))
            if sprite.update(dt, end_stop=True):
                break
            sprite.draw(new_screen, pos, size)
            utils.textures.display_screen(self.display, new_screen, self.screen_size)
