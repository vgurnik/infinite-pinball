import sys
import random
import pygame
import pymunk

from inventory import PlayerInventory
from game_effects import HitEffect, DisappearingItem
from utils.textures import display_screen
from utils.text import format_number
import screens
from config import fontfile
from save_system import save
import game_context


class PinballRound:
    def __init__(self):
        game = game_context.game
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
        self.applied_cards = PlayerInventory(overrides=self.config.applied_effects_settings)
        self.immediate = {}

        # Collision handler for objects.
        self.field.space.add_collision_handler(1, 2).begin = self.collision
        self.field.space.add_collision_handler(2, 3).begin = lambda arbiter, space, data: False

        self.time_accumulator = 0

    def collision(self, arbiter, _space, _data):
        game = game_context.game
        self.immediate['score'] = 0
        self.immediate['money'] = 0
        self.immediate['multi'] = 1
        self.immediate['hits'] = []
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
        game.callback("collision", arbiters=arbiters)
        for arb in arbiters:
            if arb.shape.type not in ['flipper', 'ball'] and arb.cooldown > 1:
                game.callback("cooldown", arbiters=[arb])
        if self.immediate['score'] or self.immediate['money']:
            game.callback("scoring_collision", arbiters=arbiters)
        if self.immediate['score']:
            add = self.immediate['score'] * self.immediate['multi'] * game.flags["base_mult"]
            s_v = format_number(abs(self.immediate['score']))
            m_v = format_number(abs(self.immediate['multi'] * game.flags["base_mult"]))
            if m_v != '1':
                s_str = f"{'+' if add >= 0 else '-'}{s_v} X {m_v}"
            else:
                s_str = f"{'+' if add >= 0 else '-'}{s_v}"
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]), s_str, (0, 255, 0)
            if add > 0 else (255, 0, 0)))
            y += 20
            self.score += add
        if self.immediate['money']:
            m_v = format_number(self.immediate['money'])
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]),
                                              f"{'+' if self.immediate['money'] >= 0 else ''}{m_v}", (255, 255, 0)))
            y += 20
            game.money += self.immediate['money']
        for hit, color in self.immediate['hits']:
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]), hit, color))
            y += 20
        return True

    def recharge(self):
        if len(self.ball_queue) == 0:
            return False
        self.active_balls.append(self.ball_queue.pop())
        self.ball_queue_coords.pop()
        self.active_balls[-1].activate(self.field.space, self.config.ball_start)
        game_context.game.callback("recharge", arbiters=[self.active_balls[-1]])
        self.ball_launched = False
        self.launch_charge = 0
        self.launch_indicators = 0
        self.launch_key_down = False
        return True

    def draw(self, dt):
        game = game_context.game
        # Clear screen.
        self.screen.fill((20, 20, 70))
        field_surface = self.field.draw()

        # Update board objects
        for obj in self.field.objects:
            obj.update(dt)

        if game.flags.get("charge_bonus", False):
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
            all_active = True
            for effect in card.effects:
                if effect["duration"] < 0:
                    continue
                effect["duration"] = max(0, effect["duration"] - dt)
                if effect["duration"] == 0:
                    all_active = False
                    break
            if not all_active:
                card.end_use()
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

        for splash in self.immediate.get("splash", []):
            self.hit_effects.append(HitEffect((splash[0] + self.field.position[0], splash[1] + self.field.position[1]),
                                              splash[2], splash[3]))

        # Draw hit effects.
        for effect in self.hit_effects[:]:
            effect.update(dt)
            effect.draw(self.screen)
            if effect.is_dead():
                self.hit_effects.remove(effect)

        if game.debug_mode:
            # Draw the FPS counter.
            font = pygame.font.Font(fontfile, 24)
            fps_text = font.render(f"FPS: {int(self.real_fps)}", True, (255, 255, 255))
            self.screen.blit(fps_text, (game.screen_size[0] - fps_text.get_width() - 10, 10))

        display_screen(self.screen)

    def run(self):
        game = game_context.game
        clock = pygame.time.Clock()
        self.running = True
        exit_option = "exit"
        self.ui.change_mode("round")
        self.recharge()
        game.callback("round_start", arbiters=self.field.objects + self.active_balls)
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)

        while self.running:
            self.immediate["splash"] = []
            self.time_accumulator += dt
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return == "round_over":
                    exit_option = ui_return
                    self.running = False
                    break
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = screens.overlay_menu(self.screen, "ui.text.pause", [
                                "ui.button.resume", "ui.button.settings", "ui.button.main"])
                            if choice == "ui.button.main":
                                exit_option = "menu"
                                self.running = False
                                break
                            if choice == "ui.button.settings":
                                screens.settings_menu()
                            _ = clock.tick(self.config.fps)
                        elif event.key == pygame.K_SPACE and not self.ball_launched:
                            self.launch_key_down = True
                        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_a, pygame.K_s,
                                           pygame.K_d]:
                            game.sound.play('flipper_on')
                    case pygame.KEYUP:
                        if event.key == pygame.K_SPACE and not self.ball_launched:
                            if self.launch_key_down:
                                for ball in self.active_balls:
                                    if ball.body.position.y > self.config.bottom_wall_y - ball.radius * 2:
                                        impulse = min(self.launch_charge, self.config.launch_max_impulse)
                                        ball.body.apply_impulse_at_local_point((0, -impulse), (0, 0))
                                        game.sound.play("launch")
                                self.launch_charge = 0
                                self.launch_key_down = False
                        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_a, pygame.K_s,
                                           pygame.K_d]:
                            game.sound.play('flipper_off')
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        game.money += ret["try_selling"].properties["price"]
                        self.hit_effects.append(DisappearingItem(ret["try_selling"], 0.5))
                        game.sound.play("coins+")
                    elif "try_using" in ret:
                        allow = False
                        lasting = False
                        for effect in ret["try_using"].effects:
                            if effect["usage"] == "active":
                                allow = True
                            if effect["duration"] != 0:
                                lasting = True
                        if allow and ret["try_using"].use() and self.inventory.remove_item(ret["try_using"]):
                            if lasting:
                                self.applied_cards.add_item(ret["try_using"])
                                self.applied_cards.recalculate_targets()
                            self.hit_effects.append(DisappearingItem(ret["try_using"], 0.5))

            for ball in self.active_balls[:]:
                if ball.body.position.y > self.config.screen_height + 15:
                    ball.remove(self.field.space)
                    self.active_balls.remove(ball)
                    game.sound.play('buzz_high', 'round')
                    game.callback("ball_lost", arbiters=[ball])

            if len(self.active_balls) == 0 and not self.recharge():
                exit_option = "round_over"
                self.running = False

            # Ramp gate control.
            all_launched = True
            for ball in self.active_balls:
                if ball.body.is_sleeping and self.ball_launched:
                    bbs = self.field.space.bb_query(ball.shape.bb, pymunk.ShapeFilter(1))
                    for other in bbs:
                        if other.body is not ball.body and other.collision_type == 2:
                            if ball.shape.shapes_collide(other).points:  # non‐empty list means real contact
                                other.parent.activations = 10
                                game.callback("cooldown", arbiters=[other.parent])
                    ball.body.activate()
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
                    if game.flags.get("charge_bonus", False):
                        self.launch_indicators = min(max((self.config.ramp_recline_end[1] - 40 - ball.body.position.y +
                                                          ball.radius) // 25, self.launch_indicators), 10)

            if all_launched and not self.ball_launched:
                self.field.ramp_gate.sensor = False
                self.ball_launched = True
                if game.flags.get("charge_bonus", False) and self.active_balls[0].body.position.y >\
                        self.config.ramp_recline_end[1] - 50:
                    bonus = self.launch_indicators * self.config.charge_bonus
                    if bonus > 0:
                        game.sound.play('coins+')
                        game.money += bonus
                    bonus = str(int(bonus)) if bonus == int(bonus) else str(bonus)
                    self.hit_effects.append(HitEffect((self.field.position[0] + self.config.right_wall_x + 12,
                                                       self.field.position[1] + self.config.ramp_recline_end[1] - 40
                                                       - self.launch_indicators * 25), '$'+bonus, (255, 255, 0)))
                self.launch_indicators = 0

            keys = pygame.key.get_pressed()
            self.field.left_flipper.spring.rest_angle = (self.field.left_flipper.active_angle if keys[pygame.K_LEFT]
                                                         or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_DOWN]
                                                         else self.field.left_flipper.default_angle)
            self.field.right_flipper.spring.rest_angle = (self.field.right_flipper.active_angle if keys[pygame.K_RIGHT]
                                                          or keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_DOWN]
                                                          else self.field.right_flipper.default_angle)
            if self.score >= game.score_needed and self.ui.mode != "round_finishable":
                self.ui.change_mode("round_finishable")
            if self.score < game.score_needed and self.ui.mode == "round_finishable":
                self.ui.change_mode("round")

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
            applied_effect.end_use()
        for ball in self.active_balls:
            ball.remove(self.field.space)
        save()
        return exit_option, self.score
