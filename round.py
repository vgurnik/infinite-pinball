import sys
import pygame
import pymunk
import pymunk.pygame_util
from game_effects import HitEffect
from game_objects import Ball, Bumper, Flipper
from static_objects import StaticObjects
from game_effects import overlay_menu


class PinballRound:
    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.config = game_instance.config
        self.inventory = game_instance.inventory
        self.space = pymunk.Space()
        self.space.gravity = self.config.gravity
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        # Translate drawing so that simulation is offset by UI width.
        self.draw_options.transform = pymunk.Transform.translation(self.config.ui_width, 0)
        self.textures = game_instance.textures

        # Create static boundaries and ramp gates.
        StaticObjects.create_boundaries(self.space, self.config)
        self.ramp_gate, self.ramp_recline = StaticObjects.create_ramp_gates(self.space, self.config)

        # Create bumpers.
        self.objects = []
        for obj in self.config.board_objects:
            if obj["type"] == "bumper":
                bumper_def = self.config.objects_settings["bumper"][obj["class"]]
                bumper_def["pos"] = obj["pos"]
                bumper = Bumper(self.space, bumper_def,
                                textures={"idle": self.textures.get(bumper_def["texture"]),
                                          "bumped": self.textures.get(bumper_def["texture"]+"_bumped")})
                self.objects.append(bumper)
            elif obj["type"] == "flipper":
                flipper_def = self.config.objects_settings["flipper"][obj["class"]]
                flipper_def["pos"] = obj["pos"]
                flipper = Flipper(self.space, flipper_def, obj["is_left"], self.config,
                                  texture=self.textures.get(flipper_def["texture"]))
                if obj["is_left"]:
                    self.left_flipper = flipper
                else:
                    self.right_flipper = flipper
                self.objects.append(flipper)

        # Create the ball.
        self.ball = Ball(self.space, self.config.objects_settings["ball"]["ball_standard"], self.config.ball_start,
                         self.textures.get(self.config.objects_settings["ball"]["ball_standard"]["texture"]))
        self.ball_launched = False
        self.launch_charge = 0.0
        self.launch_key_down = False

        self.score = 0
        self.balls_left = self.config.balls
        self.hit_effects = []
        self.applied_effects = []
        self.immediate = {}

        # Collision handler for bumpers.
        handler = self.space.add_collision_handler(1, 2)
        handler.begin = self.collision

    def collision(self, arbiter, _space, _data):
        self.immediate['score'] = 0
        self.immediate['money'] = 0
        x = 0
        y = 0
        for shape in arbiter.shapes:
            if shape.collision_type == 1:
                if getattr(shape, "bumped", None) is not None:
                    setattr(shape, "bumped", 0.1)
                pos = shape.body.position
                x = pos.x + 20
                y = pos.y
                if shape.effect:
                    shape.effect(self, *shape.effect_params)
            elif shape.collision_type == 2:
                if shape.effect:
                    shape.effect(self, *shape.effect_params)
        for effect in self.applied_effects:
            effect["effect"](self, *effect["params"])
        if self.immediate['score']:
            if self.game_instance.config.score_multiplier != 1:
                s_str = f"+{self.immediate['score']} X {self.game_instance.config.score_multiplier}"
            else:
                s_str = f"+{self.immediate['score']}"
            self.hit_effects.append(HitEffect((x, y), s_str, (0, 255, 0)))
            y += 20
            self.score += self.immediate['score'] * self.game_instance.config.score_multiplier
        if self.immediate['money']:
            self.hit_effects.append(HitEffect((x, y), f"+{self.immediate['money']}", (255, 255, 0)))
            self.game_instance.money += self.immediate['money']
        return True

    def draw(self, dt):
        # Clear screen.
        self.screen.fill((20, 20, 70))
        # For simplicity, we still call debug_draw for static elements.
        self.space.debug_draw(self.draw_options)

        self.left_flipper.draw(self.screen, offset_x=self.config.ui_width)
        self.right_flipper.draw(self.screen, offset_x=self.config.ui_width)

        # Draw board objects
        for obj in self.objects[:]:
            obj.update(dt)
            obj.draw(self.screen, offset_x=self.config.ui_width)

        # Draw hit effects.
        for effect in self.hit_effects[:]:
            effect.update(dt)
            effect.draw(self.screen, offset_x=self.config.ui_width)
            if effect.is_dead():
                self.hit_effects.remove(effect)

        self.ball.draw(self.screen, offset_x=self.config.ui_width)

        # Draw the launch indicator.
        if not self.ball_launched:
            ind_x, ind_y = self.config.launch_indicator_pos
            ind_w, ind_h = self.config.launch_indicator_size
            pygame.draw.rect(self.screen, (255, 255, 255), (ind_x, ind_y, ind_w, ind_h), 2)
            charge_ratio = self.launch_charge / self.config.launch_max_impulse
            fill_height = ind_h * charge_ratio
            pygame.draw.rect(self.screen, (0, 255, 0), (ind_x, ind_y + ind_h - fill_height, ind_w, fill_height))

        # Display UI text.
        font = pygame.font.SysFont("Arial", 24)
        min_score_text = font.render(f"Required score: {self.game_instance.score_needed}", True, (255, 255, 255))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        balls_text = font.render(f"Balls Left: {self.balls_left}", True, (255, 255, 255))
        money_text = font.render(f"$ {self.game_instance.money}", True, (255, 255, 255))
        self.screen.blit(balls_text, self.config.ui_balls_pos)
        self.screen.blit(score_text, self.config.ui_score_pos)
        self.screen.blit(min_score_text, self.config.ui_min_score_pos)
        self.screen.blit(money_text, self.config.ui_money_pos)

        self.inventory.draw(self.screen)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        exit_option = "exit"

        while running:
            dt = 1.0 / self.config.fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
                        if choice == "Exit to Main Menu":
                            exit_option = "menu"
                            running = False
                            break
                    elif event.key == pygame.K_SPACE and not self.ball_launched:
                        self.launch_key_down = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and not self.ball_launched:
                        if self.launch_key_down:
                            if self.ball.body.position.y > self.config.bottom_wall_y - 50:
                                impulse = min(self.launch_charge, self.config.launch_max_impulse)
                                self.ball.body.apply_impulse_at_local_point((0, -impulse), (0, 0))
                            self.launch_charge = 0
                            self.launch_key_down = False
                self.inventory.handle_event(event)

            if not self.ball_launched and self.launch_key_down:
                self.launch_charge += dt * self.config.launch_charge_rate
                self.launch_charge = min(self.launch_charge, self.config.launch_max_impulse)

            if self.ball.body.position.y > self.config.screen_height + 50:
                self.space.remove(self.ball.body, self.ball.shape)
                if self.balls_left > 0:
                    self.ball = Ball(self.space, self.config.objects_settings["ball"]["ball_standard"],
                                     self.config.ball_start, self.textures.get(
                            self.config.objects_settings["ball"]["ball_standard"]["texture"]))
                    self.ball_launched = False
                    self.launch_charge = 0
                    self.launch_key_down = False
                else:
                    exit_option = "round_over"
                    break

            # Ramp gate control.
            if self.ball.body.position.x > self.config.right_wall_x:
                xb = self.ball.body.position.x
                x0 = self.config.right_wall_x
                x1 = self.config.launch_ramp_wall_x
                y0 = self.config.bottom_opening_top
                y1 = self.config.bottom_opening_bottom
                line = y0 + (y1 - y0) * (xb - x0) / (x1 - x0)
                if self.ball.body.position.y + self.ball.radius < line - 5:
                    self.ramp_recline.sensor = False
                if self.ball.body.position.y - self.ball.radius > line + 5:
                    self.ramp_recline.sensor = True
                self.ramp_gate.sensor = True
            else:
                self.ramp_gate.sensor = False
                if not self.ball_launched:
                    self.balls_left -= 1
                self.ball_launched = True

            keys = pygame.key.get_pressed()
            self.left_flipper.spring.rest_angle = (
                self.left_flipper.active_angle if keys[pygame.K_LEFT] else self.left_flipper.default_angle)
            self.right_flipper.spring.rest_angle = (
                self.right_flipper.active_angle if keys[pygame.K_RIGHT] else self.right_flipper.default_angle)

            self.space.step(dt)
            if self.ball.body.velocity.length > 2000:
                self.ball.body.velocity = self.ball.body.velocity * (2000 / self.ball.body.velocity.length)

            self.inventory.update(dt)

            self.draw(dt)
            clock.tick(self.config.fps)
        return exit_option, self.score
