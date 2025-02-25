import pygame


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
