import math
import pygame
from game_effects import ContextWindow
from utils.text import multiline, loc
from utils.textures import mouse_scale
import effects
import game_context


class InventoryItem:
    def __init__(self, properties=None, sprite=None, target_position=(0, 0), card_size=(120, 160),
                 init_pos=None, for_buildable=None):
        if properties is None:
            properties = {}
        self.sprite = sprite
        self.properties = properties.copy()
        self.name = properties["name"]
        if self.properties.get("type") == "buildable":
            if hasattr(for_buildable, "copy"):
                self.buildable_sprite = for_buildable.copy()
            else:
                self.buildable_sprite = for_buildable
        self.properties["buy_price"] = properties.get("price", 0)
        # If no initial position is provided, start at the target position.
        self.pos = pygame.math.Vector2(init_pos if init_pos is not None else target_position)
        self.target_position = pygame.math.Vector2(target_position)
        self.card_size = card_size
        self.rect = pygame.Rect(self.pos.x, self.pos.y, card_size[0], card_size[1])
        self.effects = [{
            "name": effect.get("effect", None),
            "effect": effects.get_card_function(effect.get("effect", None)),
            "negative_effect": effects.get_card_function(effect.get("effect", None), negative=True),
            "trigger": effect.get("trigger", "use"),
            "usage": effect.get("usage", "passive"),
            "is_negative": effect.get("negative", False),
            "duration": effect.get("duration", 0),
            "params": effect.get("params", [])
        } for effect in properties.get("effects", [])]
        self.active = False
        self.duration = 0
        self.dragging = False
        self.highlighted = False
        self.visibility = True

    def use(self):
        """activate all usage:active trigger:use\n
        recall all usage:passive trigger:use (=self.sell) is assumed to be called too"""

        called = []
        for effect in self.effects:
            if effect["usage"] == "active" and effect["trigger"] == "use":
                if effects.call(effect):
                    called.append(effect)
                else:
                    break
        else:
            self.active = True
            self.duration = 0
            for effect in self.effects:
                if effect["duration"] == -1:
                    self.duration = -1
                    break
                self.duration = max(self.duration, effect["duration"])
            return True
        for effect in called:
            if not effects.recall(effect):
                raise RuntimeError("Failed to recall just called effect (?) probably a design error")
        return False

    def end_use(self):
        """recall all usage:active trigger:use"""
        for effect in self.effects:
            if effect["usage"] == "active" and effect["trigger"] == "use":
                if not effects.recall(effect):
                    raise RuntimeError("Failed to recall lasting effect (?) probably a design error")
        return True

    def add(self, negative=None):
        """activate all usage:passive trigger:use"""
        if negative is None:
            return self.sell(negative=True) and self.sell(negative=False)
        called = []
        for effect in self.effects:
            if negative and effect["is_negative"] or not negative and not effect["is_negative"]:
                if effect["usage"] == "passive" and effect["trigger"] == "use":
                    if effects.call(effect):
                        called.append(effect)
                    else:
                        break
        else:
            return True
        for effect in called:
            if not effects.recall(effect):
                raise RuntimeError("Failed to recall just called effect (?) probably a design error")
        return False

    def sell(self, negative=None):
        """recall all usage:passive trigger:use"""
        if negative is None:
            return self.sell(negative=True) and self.sell(negative=False)
        recalled = []
        for effect in self.effects:
            if negative and effect["is_negative"] or (not negative and not effect["is_negative"]):
                if effect["usage"] == "passive" and effect["trigger"] == "use":
                    if effects.recall(effect):
                        recalled.append(effect)
                    else:
                        break
        else:
            return True
        for effect in recalled:
            if not effects.call(effect):
                raise RuntimeError("Failed to call just recalled effect (?) probably a design error")
        return False

    def update(self, dt):
        if not self.dragging:
            # Smoothly move toward the target position.
            self.pos += (self.target_position - self.pos) * min(10 * dt, 1)
            if not self.rect.collidepoint(mouse_scale(pygame.mouse.get_pos())):
                self.highlighted = False
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface, lang='en'):
        if not self.visibility:
            return
        if self.highlighted:
            rect = self.rect.inflate(10, 10)
        else:
            rect = self.rect
        # If an image is provided, draw the scaled image.
        if self.sprite:
            if self.properties.get("type") == "buildable":
                center = self.rect.center
                if hasattr(self.buildable_sprite, "texture"):
                    texture_size = self.buildable_sprite.texture.get_size()
                else:
                    texture_size = self.buildable_sprite.sprites[0].texture.get_size()
                # scale = self.card_size[0] * 0.5 / texture_size[0]         # if I want to normalize to card size
                scale = 2                                                   # if I want to normalize to same size
                texture_size = (int(texture_size[0] * scale), int(texture_size[1] * scale))
                self.buildable_sprite.draw(surface, (center[0] - texture_size[0]//2,
                                                     center[1] - texture_size[1]//2), texture_size)
                self.sprite.draw(surface, rect.topleft, rect.size, alpha=100)
            else:
                self.sprite.draw(surface, rect.topleft, rect.size)
        else:
            # Draw a simple card background.
            match self.properties["type"]:
                case "immediate":
                    color = (255, 100, 100)
                case "buildable":
                    color = (100, 100, 255)
                case "pack":
                    color = (100, 255, 100)
                case _:
                    color = (200, 200, 200)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=5)
            # Draw the item name centered at the top of the card.
            font = pygame.font.Font(game_context.game.config.fontfile, 20)
            text_surface = font.render(loc(self.name, lang), True, (0, 0, 0))
            x = rect.x + (rect.width - text_surface.get_width()) / 2
            y = rect.y + 5
            surface.blit(text_surface, (x, y))

        if self.active:
            max_left = 0
            for effect in self.effects:
                max_left = max(max_left, effect["duration"])
            angle = int(360 * (1 - max_left / self.duration)) if self.duration > 0 else 0
            if angle > 0:
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                center = (rect.width // 2, rect.height // 2)
                radius = (rect.width ** 2 + rect.height ** 2) ** 0.5 / 2
                points = [center]
                for a in range(-90, -90 + angle + 1, 1):
                    rad = math.radians(a)
                    x = center[0] + radius * math.cos(rad)
                    y = center[1] + radius * math.sin(rad)
                    points.append((x, y))

                pygame.draw.polygon(overlay, (0, 0, 0, 100), points)
                surface.blit(overlay, rect.topleft)


class Inventory:
    """
    Base Inventory class for an arbitrary shaped table.
    In this version, items are considered immutable – they follow a fixed layout.
    """
    def __init__(self):
        self.items = []
        self.dragging_item = None
        self.clicked_item = None
        self.context = ContextWindow()

    def add_item(self, item: InventoryItem):
        self.items.append(item)

    def remove_item(self, item: InventoryItem):
        if item in self.items:
            self.items.remove(item)

    def update(self, dt):
        for item in self.items:
            item.update(dt)

    def draw(self, surface):
        for item in self.items:
            if not item.dragging:
                item.draw(surface)
        if self.dragging_item is not None:
            self.dragging_item.draw(surface)
        self.context.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mouse_pos = mouse_scale(pygame.mouse.get_pos())
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos):
                        self.clicked_item = item
                        return None
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left click
                mouse_pos = mouse_scale(pygame.mouse.get_pos())
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos) and item == self.clicked_item:
                        self.context.set_visibility(False)
                        self.clicked_item = None
                        return item
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = mouse_scale(pygame.mouse.get_pos())
            for item in self.items:
                item.highlighted = False
            for item in reversed(self.items):
                if item.rect.collidepoint(mouse_pos):
                    item.highlighted = True
                    self.context.update(mouse_pos, 'description', item)
                    self.context.set_visibility(True)
                    break
            else:
                self.context.set_visibility(False)
        return None


class PackInventory(Inventory):
    def __init__(self, width=400, slot_margin=10):
        super().__init__()
        self.position = pygame.math.Vector2(game_context.game.config.pack_opening_pos)
        self.width = width
        self.slot_margin = slot_margin

    def recalculate_targets(self):
        if len(self.items) == 0:
            return
        # Arrange items horizontally.
        spacing = min(150. + self.slot_margin, self.width / len(self.items))
        for index, item in enumerate(self.items):
            target_x = self.position.x + index * spacing
            target_y = self.position.y
            item.target_position = pygame.math.Vector2(target_x, target_y)


class PlayerInventory(Inventory):
    """
    Inherited PlayerInventory class where items are permutable.
    Items are arranged strictly vertically and can be dragged to re-order.
    """
    def __init__(self, slot_height=170, slot_margin=10, overrides=None):
        super().__init__()
        self.config = game_context.game.config
        self.position = pygame.math.Vector2(self.config.ui_inventory_pos)
        self.width = self.config.ui_width
        self.height = self.config.ui_inventory_height
        self.max_size = self.config.inventory_size
        self.deletion_zone = pygame.Rect(self.config.ui_deletion_pos, self.config.ui_deletion_size)
        self.explicit = False
        if overrides is not None:
            self.position = pygame.math.Vector2(overrides.get("pos", self.position))
            self.width = overrides.get("width", self.width)
            self.height = overrides.get("height", self.height)
            self.max_size = overrides.get("max_size", self.max_size)
            self.explicit = True
            self.deletion_zone = None
        self.slot_height = slot_height
        self.slot_margin = slot_margin

    def recalculate_targets(self):
        if len(self.items) == 0:
            return
        # Arrange items vertically.
        spacing = min(self.slot_height + self.slot_margin, self.height / len(self.items))
        for index, item in enumerate(self.items):
            target_y = self.position.y + index * spacing
            target_x = self.position.x
            item.target_position = pygame.math.Vector2(target_x, target_y)

    def add_item(self, item: InventoryItem):
        if self.explicit:
            super().add_item(item)
            self.recalculate_targets()
            return True
        if not item.add(negative=False):
            return False
        if len(self.items) < self.max_size:
            if not item.add(negative=True):
                return False
            super().add_item(item)
            self.recalculate_targets()
            if item.properties["rarity"] != "negative" and item.properties["price"] > 1:
                item.properties["price"] = max(item.properties["price"] // 2, 1)
            return True
        item.sell(negative=False)
        return False

    def remove_item(self, item: InventoryItem):
        if self.explicit:
            super().remove_item(item)
            self.recalculate_targets()
            return True
        if not item.sell(negative=False):
            return False
        if len(self.items) <= self.max_size and item.sell(negative=True):
            super().remove_item(item)
            self.recalculate_targets()
            return True
        item.add(negative=False)
        return False

    def handle_event(self, event):
        mouse_pos = mouse_scale(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                # Iterate in reverse so that top-most drawn items are prioritized.
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos):
                        item.dragging = True
                        self.dragging_item = item
                        item.offset = pygame.math.Vector2(item.pos) - pygame.math.Vector2(mouse_pos)
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_item:
                self.dragging_item.dragging = False
                self.dragging_item.visibility = True
                in_quiestion = self.dragging_item
                self.dragging_item = None
                if self.deletion_zone.collidepoint(mouse_pos):
                    self.context.set_visibility(False)
                    return {"try_selling": in_quiestion}
                if mouse_pos[0] > self.width and in_quiestion.properties["type"] in ["card", "buildable"]:
                    self.context.set_visibility(False)
                    return {"try_using": in_quiestion}
                # After dropping, re-sort the items based on their current y-positions.
                self.items.sort(key=lambda x: x.pos.y)
                self.recalculate_targets()
            if event.button in [2, 3]:
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos):
                        if event.button == 2:
                            self.context.set_visibility(False)
                            return {"try_selling": item}
                        if event.button == 3 and item.properties["type"] == "card":
                            self.context.set_visibility(False)
                            return {"try_using": item}
                        break
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                self.dragging_item.pos = pygame.math.Vector2(mouse_pos) + self.dragging_item.offset
                if self.dragging_item.properties["type"] == "buildable" and mouse_pos[0] > self.width \
                        and game_context.game.ui.mode == 'field_modification':
                    self.context.set_visibility(False)
                    self.dragging_item.visibility = False
                    return {"hovering": self.dragging_item}
            for item in self.items:
                item.highlighted = False
            for item in reversed(self.items):
                if item.rect.collidepoint(mouse_pos) and item != self.dragging_item:
                    item.highlighted = True
                    self.context.update(mouse_pos, 'description', item)
                    self.context.set_visibility(True)
                    break
            else:
                if self.dragging_item is not None and self.dragging_item.rect.collidepoint(mouse_pos):
                    self.dragging_item.highlighted = True
                    self.context.update(mouse_pos, 'description', self.dragging_item)
                    self.context.set_visibility(True)
                else:
                    self.context.set_visibility(False)
            if self.deletion_zone.collidepoint(mouse_pos) and self.dragging_item:
                self.context.update(mouse_pos, 'sell', self.dragging_item.properties['price'])
                self.context.set_visibility(True)

    def draw(self, surface):
        font = pygame.font.Font(self.config.fontfile, 25)
        if self.deletion_zone is not None:
            alpha_surface = pygame.Surface(self.deletion_zone.size, pygame.SRCALPHA)
            alpha_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(alpha_surface, (255, 100, 100, 100), alpha_surface.get_rect(), border_radius=10)
            text_surface = multiline(loc("ui.text.sell_zone", self.config.lang), font, (0, 0, 0, 255), justification=1)
            alpha_surface.blit(text_surface, ((self.deletion_zone.width - text_surface.get_width()) / 2,
                                              (self.deletion_zone.height - text_surface.get_height()) / 2))
            surface.blit(alpha_surface, self.deletion_zone.topleft)

            font = pygame.font.Font(self.config.fontfile, 16)
            fullness = multiline(f"{len(self.items)} / {self.max_size}", font, (255, 255, 255, 255), justification=1)
            surface.blit(fullness, (self.position.x, self.position.y - 20))
        super().draw(surface)
