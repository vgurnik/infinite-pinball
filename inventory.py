import pygame
from game_effects import ContextWindow
from multiline_text import multiline
from effects import get_card_function


class InventoryItem:
    def __init__(self, name, image=None, properties=None, target_position=(0, 0), card_size=(120, 160), init_pos=None):
        if properties is None:
            properties = {}
        self.name = name
        self.image = image  # Optional pygame.Surface for custom artwork.
        self.properties = properties
        # If no initial position is provided, start at the target position.
        self.pos = pygame.math.Vector2(init_pos if init_pos is not None else target_position)
        self.target_position = pygame.math.Vector2(target_position)
        self.card_size = card_size
        self.rect = pygame.Rect(self.pos.x, self.pos.y, card_size[0], card_size[1])
        self.effect = {
            "effect": get_card_function(properties.get("effect", None)),
            "negative_effect": get_card_function(properties.get("effect", None), negative=True),
            "duration": properties.get("duration", 0),
            "params": properties.get("params", [])
        }
        self.dragging = False
        self.highlighted = False

    def update(self, dt):
        if not self.dragging:
            # Smoothly move toward the target position.
            self.pos += (self.target_position - self.pos) * 50 * dt
            mouse_pos = pygame.mouse.get_pos()
            if not self.rect.collidepoint(mouse_pos):
                self.highlighted = False
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        if self.highlighted:
            rect = self.rect.inflate(10, 10)
        else:
            rect = self.rect
        # If an image is provided, draw the scaled image.
        if self.image:
            img = pygame.transform.smoothscale(self.image, (self.card_size[0] - 10, self.card_size[1] - 40))
            img_rect = img.get_rect(center=rect.center)
            surface.blit(img, img_rect)
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
        font = pygame.font.SysFont("Arial", 20)
        text_surface = font.render(self.name, True, (0, 0, 0))
        x = rect.x + (rect.width - text_surface.get_width()) / 2
        y = rect.y + 5
        surface.blit(text_surface, (x, y))


class Inventory:
    """
    Base Inventory class for an arbitrary shaped table.
    In this version, items are considered immutable – they follow a fixed layout.
    """
    def __init__(self):
        self.items = []
        self.dragging_item = None
        self.context = ContextWindow()

    def clear(self):
        self.items = []

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
                mouse_pos = pygame.mouse.get_pos()
                for item in reversed(self.items):
                    if item.rect.collidepoint(mouse_pos):
                        return item
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for item in self.items:
                item.highlighted = False
            for item in reversed(self.items):
                if item.rect.collidepoint(mouse_pos):
                    item.highlighted = True
                    self.context.update(mouse_pos,
                                        item.properties["description"]+'\n'+'Price: $'+str(item.properties["price"]))
                    self.context.set_visibility(True)
                    break
            else:
                self.context.set_visibility(False)
        return None

    def set_layout(self, positions):
        """
        Arrange items according to a provided list of target positions.
        Each position should be a tuple (x, y) corresponding to each item in order.
        """
        for item, pos in zip(self.items, positions):
            item.target_position = pygame.math.Vector2(pos)


class PlayerInventory(Inventory):
    """
    Inherited PlayerInventory class where items are permutable.
    Items are arranged strictly vertically and can be dragged to re-order.
    """
    def __init__(self, position, width, height, slot_height=170, slot_margin=10):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.width = width
        self.height = height
        self.slot_height = slot_height
        self.slot_margin = slot_margin
        self.max_size = 7
        self.deletion_zone = pygame.Rect(self.position.x, self.position.y + self.height + 100, self.width, 100)

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
        if len(self.items) < self.max_size:
            super().add_item(item)
            self.recalculate_targets()
            return True
        else:
            return False

    def remove_item(self, item: InventoryItem):
        super().remove_item(item)
        self.recalculate_targets()

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
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
                in_quiestion = self.dragging_item
                self.dragging_item = None
                if self.deletion_zone.collidepoint(mouse_pos):
                    self.context.set_visibility(False)
                    return {"try_selling": in_quiestion}
                if mouse_pos[0] > self.width and in_quiestion.properties["type"] == "active_card":
                    self.context.set_visibility(False)
                    return {"try_using": in_quiestion}
                # After dropping, re-sort the items based on their current y-positions.
                self.items.sort(key=lambda x: x.pos.y)
                self.recalculate_targets()
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                self.dragging_item.pos = pygame.math.Vector2(mouse_pos) + self.dragging_item.offset
            for item in self.items:
                item.highlighted = False
            for item in reversed(self.items):
                if item.rect.collidepoint(mouse_pos):
                    item.highlighted = True
                    self.context.update(mouse_pos,
                                        item.properties["description"]+'\n'+'Price: $'+str(item.properties["price"]))
                    self.context.set_visibility(True)
                    break
            else:
                self.context.set_visibility(False)
            if self.deletion_zone.collidepoint(mouse_pos) and self.dragging_item:
                self.context.update(mouse_pos, f"Drop here to sell\nfor ${self.dragging_item.properties['price']//2}")
                self.context.set_visibility(True)

    def draw(self, surface):
        alpha_surface = pygame.Surface(self.deletion_zone.size)
        alpha_surface.fill((255, 100, 100))
        alpha_surface.set_alpha(50)
        font = pygame.font.SysFont("Arial", 25)
        text_surface = multiline("Drop item here\nto sell it", font, (0, 0, 0), (255, 100, 100))
        alpha_surface.blit(text_surface, ((self.deletion_zone.width - text_surface.get_width()) / 2,
                                          (self.deletion_zone.height - text_surface.get_height()) / 2))
        surface.blit(alpha_surface, self.deletion_zone.topleft)
        super().draw(surface)
