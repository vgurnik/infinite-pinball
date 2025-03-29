import pygame
import pymunk
import pymunk.pygame_util
import game_objects
from static_objects import StaticObjects


class Field:
    def __init__(self, game_instance):
        self.config = game_instance.config
        self.space = pymunk.Space()
        self.space.gravity = self.config.gravity
        self.position = self.config.field_pos

        StaticObjects.create_boundaries(self.space, self.config)
        self.ramp_gate, self.ramp_recline = StaticObjects.create_ramp_gates(self.space, self.config)
        self.shield = StaticObjects.create_shield(self.space, self.config)

        self.objects = []
        self.textures = game_instance.textures
        for obj in self.config.board_objects:
            if obj["type"] == "bumper":
                bumper_def = self.config.objects_settings["bumper"][obj["class"]]
                bumper_def["pos"] = obj["pos"]
                bumper = game_objects.Bumper(self.space, bumper_def,
                                             texture={"idle": self.textures.get(bumper_def["texture"]),
                                                      "bumped": self.textures.get(bumper_def["texture"]+"_bumped")})
                self.objects.append(bumper)
            elif obj["type"] == "flipper":
                flipper_def = self.config.objects_settings["flipper"][obj["class"]]
                flipper_def["pos"] = obj["pos"]
                flipper = game_objects.Flipper(self.space, flipper_def, obj["is_left"], self.config,
                                               texture=self.textures.get(flipper_def["texture"]))
                if obj["is_left"]:
                    self.left_flipper = flipper
                else:
                    self.right_flipper = flipper
                self.objects.append(flipper)

        self.space.step(0.1)

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
            if hasattr(old_object, "limit_joint"):
                self.space.remove(old_object.limit_joint)
            if hasattr(old_object, "spring"):
                self.space.remove(old_object.spring)
            self.space.remove(old_object.body, old_object.shape)

    def draw(self, surface, ball=None):
        field_surface = pygame.Surface((self.config.screen_width, self.config.screen_height))
        field_surface.fill((20, 20, 70))
        self.space.debug_draw(pymunk.pygame_util.DrawOptions(field_surface))
        draw_lf = True
        draw_rf = True

        for obj in self.objects[:]:
            if obj not in [self.left_flipper, self.right_flipper]:
                obj.draw(field_surface)

        self.hovered_object = None
        if self.hovered_item:
            props = self.hovered_item.properties
            pos = self.hovered_item.pos - self.hovered_item.offset - self.position
            if props["object_type"] == "flipper":
                config = self.config.objects_settings["flipper"][props["class"]]
                config["pos"] = list(pos)
                is_left = True
                if self.try_placing(self.hovered_item):
                    if pos.distance_to(self.config.right_flipper_pos) < 50:
                        draw_rf = False
                        config["pos"] = self.config.right_flipper_pos
                        is_left = False
                    elif pos.distance_to(self.config.left_flipper_pos) < 50:
                        draw_lf = False
                        config["pos"] = self.config.left_flipper_pos
                self.hovered_object = game_objects.Flipper(self.space, config, is_left, self.config,
                                                           texture=self.textures.get(config.get("texture")))
                self.hovered_object.draw(field_surface)
            elif props["object_type"] == "bumper":
                config = self.config.objects_settings["bumper"][props["class"]]
                config["pos"] = list(pos)
                self.hovered_object = game_objects.Bumper(self.space, config,
                                                          texture={"idle": self.textures.get(config.get("texture"))})
                self.hovered_object.draw(field_surface)

        if draw_lf:
            self.left_flipper.draw(field_surface)
        if draw_rf:
            self.right_flipper.draw(field_surface)

        if ball:
            ball.draw(field_surface)
        surface.blit(field_surface, self.position)

    def try_placing(self, item):
        pos = item.pos - item.offset - self.position
        if item.properties["object_type"] == "flipper":
            if pos.distance_to(self.config.left_flipper_pos) < 80:
                return True
            if pos.distance_to(self.config.right_flipper_pos) < 80:
                return True
            return False
        else:
            size = self.config.objects_settings[item.properties["object_type"]][item.properties["class"]]["size"]
            for obj in self.objects:
                if pos.distance_to(obj.body.position) < 10 + size + obj.radius:
                    return False
            return True

    def place(self, item):
        self.hovered_item = None
        self.hovered_object = None
        if not self.try_placing(item):
            return False

        props = item.properties
        pos = item.pos - item.offset - self.position
        if props["object_type"] == "flipper":
            config = self.config.objects_settings["flipper"][props["class"]]
            config["pos"] = list(pos)
            is_left = True
            if pos.distance_to(self.config.right_flipper_pos) < 50:
                config["pos"] = self.config.right_flipper_pos
                is_left = False
            elif pos.distance_to(self.config.left_flipper_pos) < 50:
                config["pos"] = self.config.left_flipper_pos
            obj = game_objects.Flipper(self.space, config, is_left, self.config,
                                       texture=self.textures.get(config.get("texture")))
        elif props["object_type"] == "bumper":
            config = self.config.objects_settings["bumper"][props["class"]]
            config["pos"] = list(pos)
            obj = game_objects.Bumper(self.space, config, texture={"idle": self.textures.get(config["texture"]),
                                                  "bumped": self.textures.get(config["texture"]+"_bumped")})
        else:
            return False
        self.objects.append(obj)
        return True
