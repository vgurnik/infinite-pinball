import pygame
import pymunk
import pymunk.pygame_util
from effects import HitEffect
from game_objects import Ball, Bumper, Flipper
from static_objects import StaticObjects


class PinballRound:
    def __init__(self, screen, config, money, textures):
        self.screen = screen
        self.config = config
        self.money = money
        self.space = pymunk.Space()
        self.space.gravity = config.gravity
        self.draw_options = pymunk.pygame_util.DrawOptions(screen)
        # Translate drawing so that simulation is offset by UI width.
        self.draw_options.transform = pymunk.Transform.translation(config.ui_width, 0)
        self.textures = textures

        # Create static boundaries and ramp gates.
        StaticObjects.create_boundaries(self.space, config)
        self.ramp_gate, self.ramp_recline = StaticObjects.create_ramp_gates(self.space, config)

        # Create bumpers.
        self.bumpers = []
        for bumper_def in config.bumpers:
            bumper = Bumper(self.space, bumper_def, texture=self.textures.get("bumper"))
            self.bumpers.append(bumper)

        # Create flippers.
        self.left_flipper = Flipper(self.space, config.left_flipper_pos, True,
                                    config, texture=self.textures.get("flipper"))
        self.right_flipper = Flipper(self.space, config.right_flipper_pos, False,
                                     config, texture=self.textures.get("flipper"))

        # Create the ball.
        self.ball = Ball(self.space, config, config.ball_start, texture=self.textures.get("ball"))
        self.ball_launched = False
        self.launch_charge = 0.0
        self.launch_key_down = False

        self.score = 0
        self.balls_left = config.balls
        self.hit_effects = []

        # Collision handler for bumpers.
        handler = self.space.add_collision_handler(1, 2)
        handler.begin = self.bumper_collision

    def bumper_collision(self, arbiter, _space, _data):
        for shape in arbiter.shapes:
            if shape.collision_type == 1:
                s_val = getattr(shape, "score_value", 0)
                m_val = getattr(shape, "money_value", 0)
                pos = shape.body.position
                x = pos.x + 20
                y = pos.y
                if s_val:
                    self.hit_effects.append(HitEffect((x, y), f"+{s_val}", (0, 255, 0)))
                    y += 20
                    self.score += s_val
                if m_val:
                    self.hit_effects.append(HitEffect((x, y), f"+{m_val}", (255, 255, 0)))
                    self.money += m_val
                break
        return True

    def run(self):
        clock = pygame.time.Clock()
        running = True
        exit_option = "exit"

        while running:
            dt = 1.0 / self.config.fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = PinballRound.overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
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

            if not self.ball_launched and self.launch_key_down:
                self.launch_charge += dt * self.config.launch_charge_rate
                if self.launch_charge > self.config.launch_max_impulse:
                    self.launch_charge = self.config.launch_max_impulse

            if self.ball.body.position.y > self.config.screen_height + 50:
                self.space.remove(self.ball.body, self.ball.shape)
                if self.balls_left > 0:
                    self.ball = Ball(self.space, self.config, self.config.ball_start, texture=self.textures.get("ball"))
                    self.ball_launched = False
                    self.launch_charge = 0
                    self.launch_key_down = False
                else:
                    exit_option = "round_over"
                    break

            # Ramp gate control.
            if self.ball.body.position.x > self.config.right_wall_x:
                if self.ball.body.position.y < self.config.bottom_opening_top:
                    self.ramp_recline.sensor = False
                if self.ball.body.position.y > self.config.bottom_opening_bottom:
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

            # Snap flippers to their target angles if within a small tolerance to avoid jiggle.
            self.left_flipper.snap()
            self.right_flipper.snap()

            self.space.step(dt)
            if self.ball.body.velocity.length > 2000:
                self.ball.body.velocity = self.ball.body.velocity * (2000 / self.ball.body.velocity.length)

            self.screen.fill((20, 20, 70))
            self.space.debug_draw(self.draw_options)

            for effect in self.hit_effects[:]:
                effect.update(dt)
                effect.draw(self.screen, offset_x=self.config.ui_width)
                if effect.is_dead():
                    self.hit_effects.remove(effect)

            if not self.ball_launched:
                ind_x, ind_y = self.config.launch_indicator_pos
                ind_w, ind_h = self.config.launch_indicator_size
                pygame.draw.rect(self.screen, (255, 255, 255), (ind_x, ind_y, ind_w, ind_h), 2)
                charge_ratio = self.launch_charge / self.config.launch_max_impulse
                fill_height = ind_h * charge_ratio
                pygame.draw.rect(self.screen, (0, 255, 0), (ind_x, ind_y + ind_h - fill_height, ind_w, fill_height))

            font = pygame.font.SysFont("Arial", 24)
            min_score_text = font.render(f"Required score: {self.config.min_score}", True, (255, 255, 255))
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            balls_text = font.render(f"Balls Left: {self.balls_left}", True, (255, 255, 255))
            money_text = font.render(f"$ {self.money}", True, (255, 255, 255))
            self.screen.blit(balls_text, self.config.ui_balls_pos)
            self.screen.blit(score_text, self.config.ui_score_pos)
            self.screen.blit(min_score_text, self.config.ui_min_score_pos)
            self.screen.blit(money_text, self.config.ui_money_pos)

            pygame.display.flip()
            clock.tick(self.config.fps)
        return exit_option, self.score, self.money

    @staticmethod
    def overlay_menu(screen, title, options):
        clock = pygame.time.Clock()
        selected = 0
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        option_rects = []

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return options[selected]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(mouse_pos):
                            return options[i]
                elif event.type == pygame.MOUSEMOTION:
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(mouse_pos):
                            selected = i

            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont("Arial", 36)
            title_text = font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
            screen.blit(title_text, title_rect)
            option_rects = []
            for idx, option in enumerate(options):
                if idx == selected:
                    opt_font = pygame.font.SysFont("Arial", 42)
                    color = (255, 255, 0)
                else:
                    opt_font = pygame.font.SysFont("Arial", 36)
                    color = (255, 255, 255)
                text = opt_font.render(option, True, color)
                rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
                screen.blit(text, rect)
                option_rects.append(rect)
            pygame.display.flip()
            clock.tick(30)
