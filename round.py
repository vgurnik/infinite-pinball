import sys
import random
import pygame

import effects
from inventory import PlayerInventory
from game_effects import HitEffect, DisappearingItem
from misc import display_screen


class PinballRound:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.config = game.config
        self.real_fps = self.config.fps
        self.ui = game.ui
        self.inventory = game.inventory
        self.field = game.field
        self.textures = game.textures

        self.ball_queue = self.field.balls.copy()
        if len(self.ball_queue) * 35 > 600:
            spacing = 600 / len(self.ball_queue)
        else:
            spacing = 35
        self.ball_queue_coords = [self.config.ball_queue_lower_y - (len(self.ball_queue) - i) * spacing
                                  for i in range(len(self.ball_queue))]
        random.shuffle(self.ball_queue)
        self.running = False
        self.active_balls = []
        self.ball_launched = False
        self.launch_charge = 0.0
        self.launch_indicators = 0
        self.launch_key_down = False

        self.score = 0
        self.hit_effects = []
        self.applied_cards = PlayerInventory(self.game, overrides=self.config.applied_effects_settings)
        self.immediate = {}

        # Collision handler for objects.
        self.field.space.add_collision_handler(1, 2).begin = self.collision
        self.field.space.add_collision_handler(2, 3).begin = lambda arbiter, space, data: False

        self.time_accumulator = 0

    def collision(self, arbiter, _space, _data):
        self.immediate['score'] = 0
        self.immediate['money'] = 0
        self.immediate['multi'] = 1
        x = 0
        y = 0
        arbiters = []
        for shape in arbiter.shapes:
            match shape.collision_type:
                case 1:
                    arbiters.append(shape.parent)
                case 2:
                    if getattr(shape.parent, "bumped", None) is not None:
                        setattr(shape.parent, "bumped", 0.1)
                    pos = shape.body.position
                    arbiters.append(shape.parent)
                    shape.parent.activations += 1
                    x = pos.x + 20
                    y = pos.y
        self.game.callback("collision", arbiters=arbiters)
        if self.immediate['score']:
            add = self.immediate['score'] * self.immediate['multi'] * self.config.score_multiplier
            s_v = int(self.immediate['score']) if self.immediate['score'] == int(self.immediate['score']) \
                else self.immediate['score']
            if self.immediate['multi'] * self.config.score_multiplier == int(
                    self.immediate['multi'] * self.config.score_multiplier):
                m_v = int(self.immediate['multi'] * self.config.score_multiplier)
            else:
                m_v = self.immediate['multi'] * self.config.score_multiplier
            if m_v != 1:
                s_str = f"{'+' if add >= 0 else ''}{s_v} X {m_v}"
            else:
                s_str = f"{'+' if add >= 0 else ''}{s_v}"
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]), s_str, (0, 255, 0)))
            y += 20
            self.score += s_v * m_v
        if self.immediate['money']:
            m_v = int(self.immediate['money']) if self.immediate['money'] == int(self.immediate['money']) \
                else self.immediate['money']
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]),
                                              f"{'+' if self.immediate['money'] >= 0 else ''}{m_v}", (255, 255, 0)))
            self.game.money += self.immediate['money']
        return True

    def recharge(self):
        if len(self.ball_queue) == 0:
            return False
        self.active_balls.append(self.ball_queue.pop())
        self.ball_queue_coords.pop()
        self.active_balls[-1].activate(self.field.space, self.config.ball_start)
        self.ball_launched = False
        self.launch_charge = 0
        self.launch_indicators = 0
        self.launch_key_down = False
        return True

    def draw(self, dt):
        # Clear screen.
        self.screen.fill((20, 20, 70))
        field_surface = self.field.draw()

        # Update board objects
        for obj in self.field.objects:
            obj.update(dt)

        if self.game.flags.get("charge_bonus", False):
            for i in range(10):
                if self.launch_indicators > i:
                    self.textures["charge_indicator"].set_frame(1)
                else:
                    self.textures["charge_indicator"].set_frame(0)
                self.textures["charge_indicator"].draw(field_surface, (self.config.right_wall_x + 12,
                                                                       self.config.ramp_recline_end[1] - 40 - i * 25))

        for ball in self.active_balls:
            ball.draw(field_surface)

        for card in self.applied_cards.items[:]:
            any_active = False
            for effect in card.effects:
                if effect["duration"] < 0:
                    any_active = True
                    continue
                effect["duration"] = max(0, effect["duration"] - dt)
                if effect["duration"] > 0:
                    any_active = True
            if not any_active:
                card.end_use(self.game)
                self.applied_cards.remove_item(card)
                self.hit_effects.append(DisappearingItem(card, 0.5))

        # Draw the launch indicator.
        if self.textures.get("spring") is not None:
            self.textures["spring"].set_frame(round(self.launch_charge / self.config.launch_max_impulse * 6))
            self.textures["spring"].draw(field_surface, self.config.launch_indicator_pos,
                                         self.config.launch_indicator_size)
        else:
            if not self.ball_launched:
                ind_x, ind_y = self.config.launch_indicator_pos
                ind_w, ind_h = self.config.launch_indicator_size
                pygame.draw.rect(self.screen, (255, 255, 255), (ind_x, ind_y, ind_w, ind_h), 2)
                charge_ratio = self.launch_charge / self.config.launch_max_impulse
                fill_height = ind_h * charge_ratio
                pygame.draw.rect(self.screen, (0, 255, 0), (ind_x, ind_y + ind_h - fill_height, ind_w, fill_height))

        if len(self.ball_queue) * 35 > 600:
            spacing = 600 / len(self.ball_queue)
        else:
            spacing = 35
        for i, ball in enumerate(self.ball_queue):
            true_y = self.config.ball_queue_lower_y - (len(self.ball_queue) - i) * spacing
            self.ball_queue_coords[i] += (true_y - self.ball_queue_coords[i]) * 30 * dt
            ball.move((self.config.ball_queue_x, self.ball_queue_coords[i]))
            ball.draw(field_surface)

        self.screen.blit(field_surface, self.field.position)

        self.ui.draw(self.screen)
        self.ui.update(dt)
        self.inventory.draw(self.screen)
        self.applied_cards.draw(self.screen)

        # Draw hit effects.
        for effect in self.hit_effects[:]:
            effect.update(dt)
            effect.draw(self.screen)
            if effect.is_dead():
                self.hit_effects.remove(effect)

        if self.game.debug_mode:
            # Draw the FPS counter.
            font = pygame.font.Font(self.config.fontfile, 24)
            fps_text = font.render(f"FPS: {int(self.real_fps)}", True, (255, 255, 255))
            self.screen.blit(fps_text, (self.game.screen_size[0] - fps_text.get_width() - 10, 10))

        display_screen(self.game.display, self.screen, self.game.screen_size)

    def run(self):
        clock = pygame.time.Clock()
        self.running = True
        exit_option = "exit"
        self.ui.change_mode("round")
        self.recharge()
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)

        while self.running:
            self.time_accumulator += dt
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return == "round_over":
                    for ball in self.active_balls:
                        ball.remove(self.field.space)
                    exit_option = ui_return
                    self.running = False
                    break
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = self.ui.overlay_menu(self.screen, "Paused", [
                                "Resume", "Settings", "Exit to Main Menu"])
                            if choice == "Exit to Main Menu":
                                exit_option = "menu"
                                self.running = False
                                break
                            if choice == "Settings":
                                self.game.ui.settings_menu()
                            _ = clock.tick(self.config.fps)
                        elif event.key == pygame.K_SPACE and not self.ball_launched:
                            self.launch_key_down = True
                    case pygame.KEYUP:
                        if event.key == pygame.K_SPACE and not self.ball_launched:
                            if self.launch_key_down:
                                for ball in self.active_balls:
                                    if ball.body.position.y > self.config.bottom_wall_y - ball.radius * 2:
                                        impulse = min(self.launch_charge, self.config.launch_max_impulse)
                                        ball.body.apply_impulse_at_local_point((0, -impulse), (0, 0))
                                self.launch_charge = 0
                                self.launch_key_down = False
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        self.game.money += ret["try_selling"].properties["price"]
                        self.hit_effects.append(DisappearingItem(ret["try_selling"], 0.5))
                    elif "try_using" in ret:
                        allow = False
                        lasting = False
                        for effect in ret["try_using"].effects:
                            if effect["usage"] == "active":
                                allow = True
                            if effect["duration"] != 0:
                                lasting = True
                        if allow and ret["try_using"].use(self.game) and self.inventory.remove_item(ret["try_using"]):
                            if lasting:
                                self.applied_cards.add_item(ret["try_using"])
                                self.applied_cards.recalculate_targets()
                            self.hit_effects.append(DisappearingItem(ret["try_using"], 0.5))

            for ball in self.active_balls[:]:
                if ball.body.position.y > self.config.screen_height + 50:
                    ball.remove(self.field.space)
                    self.active_balls.remove(ball)
                    self.game.callback("ball_lost", arbiters=[ball])

            if len(self.active_balls) == 0 and not self.recharge():
                exit_option = "round_over"
                self.running = False

            # Ramp gate control.
            all_launched = True
            for ball in self.active_balls:
                ball.update(dt)
                if ball.body.velocity.length > ball.max_speed:
                    ball.body.velocity = ball.body.velocity * (ball.max_speed / ball.body.velocity.length)
                if ball.body.position.x > self.config.right_wall_x:
                    xb = ball.body.position.x
                    x0 = self.config.right_wall_x
                    x1 = self.config.launch_ramp_wall_x
                    y0 = self.config.bottom_opening_top
                    y1 = self.config.bottom_opening_bottom
                    line = y0 + (y1 - y0) * (xb - x0) / (x1 - x0)
                    if ball.body.position.y + ball.radius < line - 5:
                        self.field.ramp_recline.sensor = False
                    if ball.body.position.y - ball.radius > line + 5:
                        self.field.ramp_recline.sensor = True
                    self.field.ramp_gate.sensor = True
                    all_launched = False
                    if self.game.flags.get("charge_bonus", False):
                        self.launch_indicators = min(max((self.config.ramp_recline_end[1] - 40 - ball.body.position.y +
                                                          ball.radius) // 25, self.launch_indicators), 10)

            if all_launched and not self.ball_launched:
                self.field.ramp_gate.sensor = False
                self.ball_launched = True
                if self.game.flags.get("charge_bonus", False) and self.active_balls[0].body.position.y >\
                        self.config.ramp_recline_end[1] - 50:
                    bonus = self.launch_indicators * self.config.charge_bonus
                    self.game.money += bonus
                    bonus = str(int(bonus)) if bonus == int(bonus) else str(bonus)
                    self.hit_effects.append(HitEffect((self.field.position[0] + self.config.right_wall_x + 12,
                                                       self.field.position[1] + self.config.ramp_recline_end[1] - 40
                                                       - self.launch_indicators * 25), '$'+bonus, (255, 255, 0)))
                self.launch_indicators = 0

            keys = pygame.key.get_pressed()
            self.field.left_flipper.spring.rest_angle = (
                self.field.left_flipper.active_angle if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_s]
                else self.field.left_flipper.default_angle)
            self.field.right_flipper.spring.rest_angle = (
                self.field.right_flipper.active_angle if keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_s]
                else self.field.right_flipper.default_angle)

            if self.score >= self.game.score_needed and self.ui.mode != "round_finishable":
                self.ui.change_mode("round_finishable")

            # Simulate game physics.
            while self.time_accumulator >= self.config.max_dt:
                if not self.ball_launched and self.launch_key_down:
                    self.launch_charge += self.config.max_dt * self.config.launch_charge_rate
                    self.launch_charge = min(self.launch_charge, self.config.launch_max_impulse)

                self.field.update(self.config.max_dt)
                self.inventory.update(self.config.max_dt)
                self.applied_cards.update(self.config.max_dt)

                self.time_accumulator -= self.config.max_dt

            self.draw(dt)
            dt = clock.tick(self.config.fps) / 1000
            self.real_fps = clock.get_fps()

        for applied_effect in self.applied_cards.items:
            applied_effect.end_use(self.game)

        return exit_option, self.score
