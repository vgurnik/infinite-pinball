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
        textures = game_instance.textures
        for obj in self.config.board_objects:
            if obj["type"] == "bumper":
                bumper_def = self.config.objects_settings["bumper"][obj["class"]]
                bumper_def["pos"] = obj["pos"]
                bumper = game_objects.Bumper(self.space, bumper_def,
                                             textures={"idle": textures.get(bumper_def["texture"]),
                                                       "bumped": textures.get(bumper_def["texture"]+"_bumped")})
                self.objects.append(bumper)
            elif obj["type"] == "flipper":
                flipper_def = self.config.objects_settings["flipper"][obj["class"]]
                flipper_def["pos"] = obj["pos"]
                flipper = game_objects.Flipper(self.space, flipper_def, obj["is_left"], self.config,
                                               texture=textures.get(flipper_def["texture"]))
                if obj["is_left"]:
                    self.left_flipper = flipper
                else:
                    self.right_flipper = flipper
                self.objects.append(flipper)

    def draw(self, surface, ball=None):
        field_surface = pygame.Surface((self.config.screen_width, self.config.screen_height))
        field_surface.fill((20, 20, 70))
        self.space.debug_draw(pymunk.pygame_util.DrawOptions(field_surface))
        for obj in self.objects[:]:
            obj.draw(field_surface)

        if ball:
            ball.draw(field_surface)
        surface.blit(field_surface, self.position)
