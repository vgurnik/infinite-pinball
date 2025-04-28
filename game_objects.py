import math
import pygame
import pymunk
import effects


class GameObject:
    def __init__(self, config, pos, sprite=None, space=None):
        self.space = space
        self.config = config
        self.sprite = sprite
        if hasattr(self.sprite, "copy"):
            self.sprite = sprite.copy()
        self.effects = [{
            "name": effect.get("effect", None),
            "effect": effects.get_object_function(effect.get("effect", None)),
            "trigger": effect.get("trigger", "collision"),
            "params": effect.get("params", []).copy(),
            "cooldown": effect.get("cooldown", 0)
        } for effect in config.get("effects", [])]
        self.radius = config["size"] if isinstance(config["size"], int) else max(config["size"])
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos
        self.cooldown = 0
        self.cooldown_timer = 0
        self.activations = 0
        self.activations_dt_accum = 0

    def move(self, pos):
        self.body.position = pos

    def update(self, dt):
        self.activations_dt_accum += dt
        self.activations = max(0, self.activations - int(self.activations_dt_accum // 0.5))
        self.activations_dt_accum = self.activations_dt_accum % 0.5
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0, self.cooldown_timer - dt)
        if self.cooldown_timer == 0:
            self.cooldown = 0
        if self.activations > 6:
            self.activations = 6
            self.cooldown = 5
            self.cooldown_timer = 5
        if hasattr(self, "shape") and self.shape.type not in ['flipper', 'ball']:
            if self.cooldown_timer > 0.3:
                self.shape.sensor = True
            else:
                self.shape.sensor = False


class Ball(GameObject):
    def __init__(self, config, pos, sprite=None):
        super().__init__(config, pos, sprite, space=None)
        self.mass = config["mass"]
        self.max_speed = config.get("max_speed", 1000)
        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius))
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.parent = self
        self.shape.type = 'ball'
        self.shape.elasticity = config.get("force", 0.95)
        self.shape.friction = config.get("friction", 0.9)
        self.shape.collision_type = 1  # for collisions

    def activate(self, space, position=None):
        old_pos = self.body.position
        self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius))
        if position is not None:
            self.body.position = position
        else:
            self.body.position = old_pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.parent = self
        self.shape.type = 'ball'
        self.shape.elasticity = self.config.get("force", 0.95)
        self.shape.friction = 0.9
        self.shape.collision_type = 1  # for collisions
        space.add(self.body, self.shape)

    def remove(self, space):
        space.remove(self.body, self.shape)

    def draw(self, screen):
        if self.sprite:
            self.sprite.draw(screen, (self.body.position.x - self.radius, self.body.position.y - self.radius),
                             (self.radius * 2, self.radius * 2))
        else:
            pygame.draw.circle(screen, (200, 50, 50),
                               (int(self.body.position.x), int(self.body.position.y)), self.radius)


class Bumper(GameObject):
    def __init__(self, space, config, sprite=None):
        super().__init__(config, (0, 0), sprite, space)
        self.config = config
        self.space = space
        self.pos = config["pos"]
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = config["force"]
        self.shape.friction = 0.5
        self.shape.collision_type = 2
        # Attach custom properties.
        self.shape.parent = self
        self.shape.type = 'bumper'
        space.add(self.body, self.shape)
        self.bumped = 0

    def update(self, dt):
        super().update(dt)
        if self.bumped > 0:
            self.bumped = max(0, self.bumped - dt)

    def draw(self, screen, allowed=True):
        if self.sprite:
            if self.bumped:
                self.sprite.set_frame(1)
            else:
                self.sprite.set_frame(0)
            if not allowed:
                pygame.draw.circle(screen, (255, 0, 0, 100),
                                   (int(self.body.position.x), int(self.body.position.y)), self.radius)
            self.sprite.draw(screen, (self.body.position.x - self.radius, self.body.position.y - self.radius),
                             (self.radius * 2, self.radius * 2), alpha=100 + allowed*155)
        else:
            pygame.draw.circle(screen, (50, 200, 50, 255),
                               (int(self.body.position.x), int(self.body.position.y)), self.radius)
            if not allowed:
                pygame.draw.circle(screen, (255, 0, 0, 100),
                                   (int(self.body.position.x), int(self.body.position.y)), self.radius)
        if self.cooldown > 0.5:
            angle = int(360 * self.cooldown_timer / self.cooldown)
            if angle > 0:
                overlay = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                center = (self.radius, self.radius)
                points = [center]
                for a in range(-90, -90 + angle + 1, 1):
                    rad = math.radians(a)
                    x = center[0] + self.radius * math.cos(rad)
                    y = center[1] + self.radius * math.sin(rad)
                    points.append((x, y))

                pygame.draw.polygon(overlay, (0, 0, 0, 100), points)
                screen.blit(overlay, (self.body.position.x - self.radius, self.body.position.y - self.radius))


class Pin(GameObject):
    def __init__(self, space, config, sprite=None):
        super().__init__(config, (0, 0), sprite, space)
        self.config = config
        self.space = space
        self.pos = config["pos"]
        self.len = config["size"]
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Segment(self.body, (0, 0), (0, self.len), 5)
        self.shape.elasticity = config.get("force", 0.95)
        self.shape.friction = 0.5
        self.shape.collision_type = 2
        # Attach custom properties.
        self.shape.parent = self
        self.shape.type = 'pin'
        space.add(self.body, self.shape)

    def draw(self, screen, allowed=True):
        if self.sprite:
            if not allowed:
                pygame.draw.rect(screen, (255, 0, 0, 10), (self.body.position.x - 5,
                                                           self.body.position.y - self.len // 2, 10, self.len))
            self.sprite.draw(screen, (self.body.position.x - 5, self.body.position.y - self.len // 2), (10, self.len),
                             alpha=100 + allowed*155)
        if self.cooldown > 0.5:
            angle = int(360 * self.cooldown_timer / self.cooldown)
            if angle > 0:
                overlay = pygame.Surface((10, self.len), pygame.SRCALPHA)
                center = (5, self.len // 2)
                points = [center]
                for a in range(-90, -90 + angle + 1, 1):
                    rad = math.radians(a)
                    x = center[0] + self.radius * math.cos(rad)
                    y = center[1] + self.radius * math.sin(rad)
                    points.append((x, y))

                pygame.draw.polygon(overlay, (0, 0, 0, 100), points)
                screen.blit(overlay, (self.body.position.x - 5, self.body.position.y - self.len // 2))


class Flipper(GameObject):

    def __init__(self, space, flipper_def, is_left, config, sprite=None, additional=False):
        super().__init__(flipper_def, (0, 0), sprite, space)
        self.space = space
        self.config = config
        self.is_left = is_left
        self.mass = 100
        self.length, self.width = flipper_def["size"]
        vertices = [(-self.length/2, -self.width/2), (self.length/2, -self.width/2),
                    (self.length/2, self.width/2), (-self.length/2, self.width/2)]
        moment = pymunk.moment_for_poly(self.mass, vertices)
        self.body = pymunk.Body(self.mass, moment)
        pos = flipper_def["pos"]
        if is_left:
            self.body.position = (pos[0] + self.length/2, pos[1] + self.width/2)
        else:
            self.body.position = (pos[0] - self.length/2, pos[1] + self.width/2)
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.parent = self
        self.shape.collision_type = 2
        self.shape.type = 'flipper'
        self.shape.elasticity = flipper_def["force"]
        self.shape.friction = 0.1
        space.add(self.body, self.shape)

        if not additional:
            if is_left:
                pivot_point = (pos[0], pos[1])
                pivot_anchor = (-self.length/2, -self.width/2)
                self.default_angle = math.radians(config.left_flipper_default_angle)
                self.active_angle = math.radians(config.left_flipper_active_angle)
            else:
                pivot_point = (pos[0], pos[1])
                pivot_anchor = (self.length/2, -self.width/2)
                self.default_angle = math.radians(config.right_flipper_default_angle)
                self.active_angle = math.radians(config.right_flipper_active_angle)

            pivot = pymunk.PinJoint(space.static_body, self.body, pivot_point, pivot_anchor)
            pivot.error_bias = 0
            space.add(pivot)
            self.body.angle = self.default_angle

            lower_limit = min(self.default_angle, self.active_angle)
            upper_limit = max(self.default_angle, self.active_angle)
            self.limit_joint = pymunk.RotaryLimitJoint(self.body, space.static_body, lower_limit, upper_limit)
            space.add(self.limit_joint)

            self.spring = pymunk.DampedRotarySpring(
                self.body, space.static_body, self.default_angle,
                stiffness=config.flipper_stiffness,
                damping=config.flipper_damping
            )
            space.add(self.spring)
            self.snap()
        if self.is_left:
            self.sprite.set_frame(0)
        else:
            self.sprite.set_frame(1)

    def update(self, dt):
        super().update(dt)
        self.snap()

    def destroy(self):
        self.space.remove(self.limit_joint)
        self.space.remove(self.spring)
        self.space.remove(self.body, self.shape)

    def snap(self, tolerance=0):
        """Eliminate jiggle by snapping to target angle if within a small tolerance."""
        target_angle = self.active_angle if self.is_active() else self.default_angle
        if abs(self.body.angle - target_angle) < tolerance:
            self.body.angle = target_angle
            self.body.angular_velocity = 0

    def is_active(self):
        """Determine active state based on the spring's rest_angle."""
        return self.spring.rest_angle == self.active_angle

    def draw(self, screen, allowed=True):
        points = [(self.body.position.x + self.length / 2 + p.x,
                   self.body.position.y + self.width / 2 + p.y) for p in self.shape.get_vertices()]
        if self.sprite:
            if not allowed:
                pygame.draw.polygon(screen, (255, 0, 0, 100), points)
            self.sprite.draw(screen, (round(self.body.position.x*2)/2, round(self.body.position.y*2)/2),
                             (self.length, self.width), -math.degrees(self.body.angle), alpha=100 + allowed*155)
        else:
            pygame.draw.polygon(screen, (200, 200, 50), points)
            if not allowed:
                pygame.draw.polygon(screen, (255, 0, 0, 100), points)
        # if self.cooldown > 0.5: # not really needed with current SOTG
        #     angle = int(360 * self.cooldown_timer / self.cooldown)
        #     if angle > 0:
        #         overlay = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        #         center = (self.length // 2, self.width // 2)
        #         points = [center]
        #         for a in range(-90, -90 + angle + 1, 1):
        #             rad = math.radians(a)
        #             x = center[0] + self.radius * math.cos(rad)
        #             y = center[1] + self.radius * math.sin(rad)
        #             points.append((x, y))
        #
        #         pygame.draw.polygon(overlay, (0, 0, 0, 60), points)
        #         overlay = pygame.transform.rotate(overlay, -math.degrees(self.body.angle))
        #         screen.blit(overlay, (self.body.position.x - self.length / 2,
        #                               self.body.position.y - self.width))
