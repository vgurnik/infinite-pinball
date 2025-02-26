import pygame


class InventoryItem:
    def __init__(self, name, image=None, description="", target_position=(0, 0), card_size=(120, 160), init_pos=None):
        self.name = name
        self.image = image  # Optional pygame.Surface for custom artwork.
        self.description = description
        if init_pos is None:
            self.pos = pygame.math.Vector2(target_position)  # current position (float for smooth movement)
        else:
            self.pos = pygame.math.Vector2(init_pos)  # current position (float for smooth movement)
        self.target_position = pygame.math.Vector2(target_position)
        self.card_size = card_size
        self.rect = pygame.Rect(self.pos.x, self.pos.y, card_size[0], card_size[1])
        self.dragging = False
        self.offset = pygame.math.Vector2(0, 0)

    def update(self, dt):
        if not self.dragging:
            # Smoothly move towards the target position.
            self.pos += (self.target_position - self.pos) * 50 * dt  # 5 is a smoothing factor
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        # Optionally, draw an image (scaled to leave a small margin).
        if self.image:
            img = pygame.transform.smoothscale(
                self.image, (self.card_size[0] - 10, self.card_size[1] - 40)
            )
            img_rect = img.get_rect(center=self.rect.center)
            surface.blit(img, img_rect)
        else:
            # Draw card background.
            pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=5)
            pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=5)
        # Draw the name of the item at the top of the card.
        font = pygame.font.SysFont("Arial", 20)
        text_surface = font.render(self.name, True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + self.rect.width / 2 - text_surface.get_width() / 2, self.rect.y + 5))


class Inventory:
    def __init__(self, position, width, height, slot_height=170, slot_margin=10):
        """
        position: (x, y) of the inventory panel.
        width, height: dimensions of the inventory panel.
        slot_height: height allocated for each item slot.
        slot_margin: vertical spacing between slots.
        """
        self.position = pygame.math.Vector2(position)
        self.width = width
        self.height = height
        self.slot_height = slot_height
        self.slot_margin = slot_margin
        self.items = []
        self.dragging_item = None

    def add_item(self, item):
        self.items.append(item)
        self.recalculate_targets()

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.recalculate_targets()

    def recalculate_targets(self):
        # Arrange items vertically.
        spacing = min(self.slot_height + self.slot_margin, self.height / len(self.items))
        for index, item in enumerate(self.items):
            target_y = self.position.y + index * spacing
            target_x = self.position.x
            item.target_position = pygame.math.Vector2(target_x, target_y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mouse_pos = pygame.mouse.get_pos()
                for item in self.items[::-1]:
                    if item.rect.collidepoint(mouse_pos):
                        item.dragging = True
                        self.dragging_item = item
                        item.offset = pygame.math.Vector2(item.pos) - pygame.math.Vector2(mouse_pos)
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging_item:
                    self.dragging_item.dragging = False
                    self.dragging_item = None
                    self.recalculate_targets()
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_item:
                mouse_pos = pygame.mouse.get_pos()
                self.dragging_item.pos = pygame.math.Vector2(mouse_pos) + self.dragging_item.offset

    def update(self, dt):
        for item in self.items:
            item.update(dt)

    def draw(self, surface):
        # Draw inventory panel background.
        # panel_rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        # pygame.draw.rect(surface, (0, 0, 0, 255), panel_rect, border_radius=5)
        # Draw each inventory item.
        for item in self.items:
            if not item.dragging:
                item.draw(surface)
        if self.dragging_item is not None:
            self.dragging_item.draw(surface)
