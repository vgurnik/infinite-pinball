import math
import pygame
import pymunk
from effects import get_object_function


class Ball:
    def __init__(self, space, config, pos, texture=None):
        self.space = space
        self.mass = config["mass"]
        self.radius = config["size"]
        inertia = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, inertia)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        self.shape.collision_type = 1  # for collisions with bumpers
        self.shape.effect = get_object_function(config["effect"])
        self.shape.effect_params = config.get("params", [])
        space.add(self.body, self.shape)
        self.texture = texture

    def draw(self, screen, offset_x=0):
        if self.texture:
            rotated = pygame.transform.rotozoom(self.texture, 0, self.radius * 2 / 16)
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (200, 50, 50),
                               (int(self.body.position.x + offset_x), int(self.body.position.y)), self.radius)


class Bumper:
    def __init__(self, space, bumper_def, textures=None):
        self.config = bumper_def
        self.space = space
        self.pos = bumper_def["pos"]
        self.radius = bumper_def["size"]
        self.type = 'bumper'
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = bumper_def["force"]
        self.shape.friction = 0.5
        self.shape.collision_type = 2
        # Attach custom properties.
        self.shape.effect = get_object_function(bumper_def["effect"])
        self.shape.effect_params = bumper_def.get("params", [])
        space.add(self.body, self.shape)
        self.textures = textures
        self.shape.bumped = 0

    def update(self, dt):
        if self.shape.bumped > 0:
            self.shape.bumped = max(0, self.shape.bumped - dt)

    def draw(self, screen, offset_x=0):
        if self.textures:
            if self.shape.bumped:
                rotated = pygame.transform.rotozoom(self.textures["bumped"], 0,
                                                    self.radius * 2 / self.textures["bumped"].get_size()[0])
            else:
                rotated = pygame.transform.rotozoom(self.textures["idle"], 0,
                                                    self.radius * 2 / self.textures["idle"].get_size()[0])
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (50, 200, 50),
                               (int(self.body.position.x + offset_x), int(self.body.position.y)), self.radius)


class Flipper:
    def __init__(self, space, flipper_def, is_left, config, texture=None):
        self.space = space
        self.config = config
        self.is_left = is_left
        self.mass = 100
        self.type = 'flipper'
        self.effect = flipper_def["effect"]
        self.length = config.flipper_length
        self.width = config.flipper_width
        vertices = [(-self.length/2, -self.width/2), (self.length/2, -self.width/2),
                    (self.length/2, self.width/2), (-self.length/2, self.width/2)]
        moment = pymunk.moment_for_poly(self.mass, vertices)
        self.body = pymunk.Body(self.mass, moment)
        pos = flipper_def["pos"]
        self.body.position = pos
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.collision_type = 2
        self.shape.effect = get_object_function(flipper_def["effect"])
        self.shape.effect_params = flipper_def.get("params", [])
        self.shape.elasticity = flipper_def["force"]
        self.shape.friction = 0.1
        space.add(self.body, self.shape)

        if is_left:
            pivot_point = (pos[0] - self.length/2, pos[1] - self.width/2)
            pivot_anchor = (-self.length/2, -self.width/2)
            self.default_angle = math.radians(config.left_flipper_default_angle)
            self.active_angle = math.radians(config.left_flipper_active_angle)
        else:
            pivot_point = (pos[0] + self.length/2, pos[1] - self.width/2)
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
        self.texture = texture
        if not self.is_left:
            self.texture = pygame.transform.flip(self.texture, flip_x=True, flip_y=False)

    def update(self, dt):
        self.snap()

    def snap(self, tolerance=0):
        """Eliminate jiggle by snapping to target angle if within a small tolerance."""
        target_angle = self.active_angle if self.is_active() else self.default_angle
        if abs(self.body.angle - target_angle) < tolerance:
            self.body.angle = target_angle
            self.body.angular_velocity = 0

    def is_active(self):
        """Determine active state based on the spring's rest_angle."""
        return self.spring.rest_angle == self.active_angle

    def draw(self, screen, offset_x=0):
        if self.texture:
            rotated = pygame.transform.rotozoom(self.texture, -math.degrees(self.body.angle), self.length / 40)
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            points = [(p.x + offset_x, p.y) for p in self.shape.get_vertices()]
            pygame.draw.polygon(screen, (200, 200, 50), points)
