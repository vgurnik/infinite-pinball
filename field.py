import pygame
import pymunk
import pymunk.pygame_util
import game_objects
from static_objects import StaticObjects


class Field:
    def __init__(self, game_instance):
        self.config = game_instance.config
        self.game_instance = game_instance
        self.space = pymunk.Space()
        self.space.gravity = self.config.gravity
        self.position = self.config.field_pos

        StaticObjects.create_boundaries(self.space, self.config)
        self.ramp_gate, self.ramp_recline = StaticObjects.create_ramp_gates(self.space, self.config,
                                                                            self.game_instance.textures.get("ramps"))
        self.shield = StaticObjects.create_shield(self.space, self.config, self.game_instance.textures.get("shield"))

        self.objects = []
        self.textures = game_instance.textures
        for obj in self.config.board_objects:
            if obj["type"] == "bumper":
                bumper_def = self.config.objects_settings["bumper"][obj["class"]]
                bumper_def["pos"] = obj["pos"]
                bumper = game_objects.Bumper(self.space, bumper_def, sprite=self.textures.get(bumper_def["texture"]))
                self.objects.append(bumper)
            elif obj["type"] == "flipper":
                flipper_def = self.config.objects_settings["flipper"][obj["class"]]
                flipper_def["pos"] = obj["pos"]
                flipper = game_objects.Flipper(self.space, flipper_def, obj["is_left"], self.config,
                                               sprite=self.textures.get(flipper_def["texture"]))
                if obj["is_left"]:
                    self.left_flipper = flipper
                else:
                    self.right_flipper = flipper
                self.objects.append(flipper)

        self.space.step(0.1)

        # Create the balls.
        self.balls = [game_objects.Ball(self.config.objects_settings["ball"]["standard"], self.config.ball_start,
                                        self.textures.get(self.config.objects_settings["ball"]["standard"]["texture"])
                                        ) for i in range(self.config.balls)]

        self.hovered_item = None
        self._hovered_object = None

    @property
    def hovered_object(self):
        return self._hovered_object

    @hovered_object.setter
    def hovered_object(self, new_object):
        old_object = self._hovered_object
        self._hovered_object = new_object
        if old_object:
            self.space.remove(old_object.body, old_object.shape)

    def update(self, dt):
        self.shield.sprite.update(dt)
        self.space.step(dt)

    def draw(self, surface, balls=None):
        field_surface = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
        field_surface.fill((20, 20, 70))
        if self.game_instance.debug_mode:
            self.space.debug_draw(pymunk.pygame_util.DrawOptions(field_surface))
        if self.textures.get("field"):
            self.textures.get("field").draw(field_surface, (0, 0), self.config.field_size)
        draw_lf = True
        draw_rf = True

        for obj in self.objects[:]:
            if obj not in [self.left_flipper, self.right_flipper]:
                obj.draw(field_surface)

        self.hovered_object = None
        if self.hovered_item:
            allowed = True
            props = self.hovered_item.properties
            pos = self.hovered_item.pos - self.hovered_item.offset - self.position
            if props["object_type"] == "flipper":
                config = self.config.objects_settings["flipper"][props["class"]]
                config["pos"] = list(pos)
                is_left = True
                if self._try_placing(self.hovered_item):
                    if pos.distance_to(self.config.right_flipper_pos) < 80:
                        draw_rf = False
                        config["pos"] = self.config.right_flipper_pos
                        is_left = False
                    elif pos.distance_to(self.config.left_flipper_pos) < 80:
                        draw_lf = False
                        config["pos"] = self.config.left_flipper_pos
                else:
                    allowed = False
                self.hovered_object = game_objects.Flipper(self.space, config, is_left, self.config,
                                                           sprite=self.textures.get(config.get("texture")),
                                                           additional=True)
                self.hovered_object.draw(field_surface, allowed)
            elif props["object_type"] == "bumper":
                config = self.config.objects_settings["bumper"][props["class"]]
                config["pos"] = list(pos)
                self.hovered_object = game_objects.Bumper(self.space, config,
                                                          sprite=self.textures.get(config.get("texture")))
                if not self._try_placing(self.hovered_item):
                    allowed = False
                self.hovered_object.draw(field_surface, allowed)

        if draw_lf:
            self.left_flipper.draw(field_surface)
        if draw_rf:
            self.right_flipper.draw(field_surface)
        if not self.ramp_gate.sensor and self.ramp_gate.sprite is not None:
            self.ramp_gate.sprite.draw(field_surface, (0, 0), self.config.field_size)
        if not self.shield.sensor and self.shield.sprite is not None:
            self.shield.sprite.draw(field_surface, (self.shield.a[0], self.shield.a[1] - 10),
                                    (self.shield.b[0]-self.shield.a[0], 50))
        if balls:
            for ball in balls:
                ball.draw(field_surface)
        surface.blit(field_surface, self.position)

    def _try_placing(self, item):
        pos = item.pos - item.offset - self.position
        if item.properties["object_type"] == "flipper":
            if pos.distance_to(self.config.left_flipper_pos) < 80:
                return True
            if pos.distance_to(self.config.right_flipper_pos) < 80:
                return True
            return False
        if not (self.config.left_wall_x < pos[0] < self.config.right_wall_x and
                self.config.top_wall_y < pos[1] < self.config.field_height):
            return False
        size = self.config.objects_settings[item.properties["object_type"]][item.properties["class"]]["size"]
        if len(self.space.point_query(tuple(pos), 30 + size, pymunk.ShapeFilter(1))) > 1:
            return False
        for obj in self.objects:
            if pos.distance_to(obj.body.position) < 30 + size + obj.radius:
                return False
        return True

    def place(self, item):
        self.hovered_item = None
        self.hovered_object = None
        if not self._try_placing(item):
            return False

        props = item.properties
        pos = item.pos - item.offset - self.position
        if props["object_type"] == "flipper":
            config = self.config.objects_settings["flipper"][props["class"]]
            config["pos"] = list(pos)
            is_left = True
            if pos.distance_to(self.config.right_flipper_pos) < 80:
                config["pos"] = self.config.right_flipper_pos
                is_left = False
            elif pos.distance_to(self.config.left_flipper_pos) < 80:
                config["pos"] = self.config.left_flipper_pos
            obj = game_objects.Flipper(self.space, config, is_left, self.config,
                                       sprite=self.textures.get(config.get("texture")))
            if is_left:
                self.objects.remove(self.left_flipper)
                self.left_flipper.destroy()
                self.left_flipper = obj
            else:
                self.objects.remove(self.right_flipper)
                self.right_flipper.destroy()
                self.right_flipper = obj
        elif props["object_type"] == "bumper":
            config = self.config.objects_settings["bumper"][props["class"]]
            config["pos"] = list(pos)
            obj = game_objects.Bumper(self.space, config, sprite=self.textures.get(config["texture"]))
        else:
            return False
        self.objects.append(obj)
        return True

    def delete(self, mouse_pos):
        for obj in self.objects[:]:
            if obj.shape.point_query((mouse_pos[0] - self.position[0],
                                      mouse_pos[1] - self.position[1])).distance <= obj.radius:
                if obj.shape.type != 'flipper':
                    self.objects.remove(obj)
                    self.space.remove(obj.body, obj.shape)
                    return True
        return False
