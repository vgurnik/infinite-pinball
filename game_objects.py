import math
import pygame
import pymunk


class Ball:
    def __init__(self, space, config, pos, texture=None):
        self.config = config
        self.space = space
        self.mass = config.ball_mass
        self.radius = config.ball_radius
        inertia = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, inertia)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = 0.95
        self.shape.friction = 0.9
        self.shape.collision_type = 2  # for collisions with bumpers
        space.add(self.body, self.shape)
        self.texture = texture

    def draw(self, screen, offset_x=0):
        if self.texture:
            rotated = pygame.transform.rotozoom(self.texture, -math.degrees(self.body.angle), 1)
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (200, 50, 50),
                               (int(self.body.position.x + offset_x), int(self.body.position.y)), self.radius)


class Bumper:
    def __init__(self, space, bumper_def, texture=None):
        self.config = bumper_def
        self.space = space
        self.pos = bumper_def["pos"]
        self.radius = bumper_def["radius"]
        self.force = bumper_def["force"]
        self.score_value = bumper_def["score"]
        self.money_value = bumper_def["money"]
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = self.pos
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = self.force
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        # Attach custom properties.
        self.shape.score_value = self.score_value
        self.shape.money_value = self.money_value
        space.add(self.body, self.shape)
        self.texture = texture

    def draw(self, screen, offset_x=0):
        if self.texture:
            rotated = pygame.transform.rotozoom(self.texture, 0, 1)
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, (50, 200, 50),
                               (int(self.body.position.x + offset_x), int(self.body.position.y)), self.radius)


class Flipper:
    def __init__(self, space, pos, is_left, config, texture=None):
        self.space = space
        self.config = config
        self.is_left = is_left
        self.mass = 100
        self.length = config.flipper_length
        self.width = config.flipper_width
        vertices = [(-self.length/2, -self.width/2), (self.length/2, -self.width/2),
                    (self.length/2, self.width/2), (-self.length/2, self.width/2)]
        moment = pymunk.moment_for_poly(self.mass, vertices)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = pos
        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.elasticity = 0.99
        self.shape.friction = 0.8
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
            rotated = pygame.transform.rotozoom(self.texture, -math.degrees(self.body.angle), 1)
            rect = rotated.get_rect(center=(self.body.position.x + offset_x, self.body.position.y))
            screen.blit(rotated, rect)
        else:
            points = [(p.x + offset_x, p.y) for p in self.shape.get_vertices()]
            pygame.draw.polygon(screen, (200, 200, 50), points)
