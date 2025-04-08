import sys
import random
import pygame

import effects
from inventory import PlayerInventory
from game_effects import HitEffect, DisappearingItem
from misc import scale


class PinballRound:
    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.screen = game_instance.screen
        self.config = game_instance.config
        self.real_fps = self.config.fps
        self.ui = game_instance.ui
        self.inventory = game_instance.inventory
        self.field = game_instance.field
        self.textures = game_instance.textures

        self.ball_queue = self.field.balls.copy()
        if len(self.ball_queue) * 35 > 600:
            spacing = 600 / len(self.ball_queue)
        else:
            spacing = 35
        self.ball_queue_coords = [self.config.ball_queue_lower_y - (len(self.ball_queue) - i) * spacing
                                  for i in range(len(self.ball_queue))]
        random.shuffle(self.ball_queue)
        self.active_balls = []
        self.ball_launched = False
        self.launch_charge = 0.0
        self.launch_key_down = False

        self.score = 0
        self.hit_effects = []
        self.applied_cards = PlayerInventory(self.game_instance, overrides=self.config.applied_effects_settings)
        self.immediate = {}

        # Collision handler for objects.
        self.field.space.add_collision_handler(1, 2).begin = self.collision

    def collision(self, arbiter, _space, _data):
        self.immediate['score'] = 0
        self.immediate['money'] = 0
        x = 0
        y = 0
        arbiter_object = None
        for shape in arbiter.shapes:
            match shape.collision_type:
                case 1:
                    for effect in shape.parent.effects:
                        if effect["trigger"] == "collision":
                            effects.call(effect, self.game_instance, arbiter=shape.parent)
                case 2:
                    if getattr(shape.parent, "bumped", None) is not None:
                        setattr(shape.parent, "bumped", 0.1)
                    pos = shape.body.position
                    arbiter_object = shape.parent
                    x = pos.x + 20
                    y = pos.y
                    if shape.parent.cooldown == 0:
                        for effect in shape.parent.effects:
                            if effect["trigger"] == "collision":
                                effects.call(effect, self.game_instance, arbiter=arbiter_object)
                    if shape.parent.cooldown > 0:
                        shape.parent.cooldown_timer = shape.parent.cooldown
        self.game_instance.callback("collision", arbiter_object)
        if self.immediate['score']:
            add = self.immediate['score'] * self.config.score_multiplier
            s_v = int(self.immediate['score']) if self.immediate['score'] == int(self.immediate['score']) \
                else self.immediate['score']
            m_v = int(self.config.score_multiplier) if self.config.score_multiplier == int(
                self.config.score_multiplier) else self.config.score_multiplier
            if self.config.score_multiplier != 1:
                s_str = f"{'+' if add >= 0 else ''}{s_v} X {m_v}"
            else:
                s_str = f"{'+' if add >= 0 else ''}{s_v}"
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]), s_str, (0, 255, 0)))
            y += 20
            self.score += self.immediate['score'] * self.config.score_multiplier
        if self.immediate['money']:
            m_v = int(self.immediate['money']) if self.immediate['money'] == int(self.immediate['money']) \
                else self.immediate['money']
            self.hit_effects.append(HitEffect((x+self.field.position[0], y+self.field.position[1]),
                                              f"{'+' if self.immediate['money'] >= 0 else ''}{m_v}", (255, 255, 0)))
            self.game_instance.money += self.immediate['money']
        return True

    def recharge(self):
        if len(self.ball_queue) == 0:
            return False
        self.active_balls.append(self.ball_queue.pop())
        self.ball_queue_coords.pop()
        self.active_balls[-1].activate(self.field.space, self.config.ball_start)
        self.ball_launched = False
        self.launch_charge = 0
        self.launch_key_down = False
        return True

    def draw(self, dt):
        # Clear screen.
        self.screen.fill((20, 20, 70))
        self.field.draw(self.screen, self.active_balls)

        # Update board objects
        for obj in self.field.objects:
            obj.update(dt)

        for card in self.applied_cards.items[:]:
            any_active = False
            for effect in card.effects:
                effect["duration"] = max(0, effect["duration"] - dt)
                if effect["duration"] > 0:
                    any_active = True
            if not any_active:
                card.end_use(self.game_instance)
                self.applied_cards.remove_item(card)
                self.hit_effects.append(DisappearingItem(card, 0.5))

        # Draw the launch indicator.
        if not self.ball_launched:
            ind_x, ind_y = (self.config.launch_indicator_pos[0] + self.field.position[0],
                            self.config.launch_indicator_pos[1] + self.field.position[1])
            ind_w, ind_h = self.config.launch_indicator_size
            pygame.draw.rect(self.screen, (255, 255, 255), (ind_x, ind_y, ind_w, ind_h), 2)
            charge_ratio = self.launch_charge / self.config.launch_max_impulse
            fill_height = ind_h * charge_ratio
            pygame.draw.rect(self.screen, (0, 255, 0), (ind_x, ind_y + ind_h - fill_height, ind_w, fill_height))

        self.ui.draw(self.screen)
        self.ui.update(dt)
        self.inventory.draw(self.screen)
        self.applied_cards.draw(self.screen)

        if len(self.ball_queue) * 35 > 600:
            spacing = 600 / len(self.ball_queue)
        else:
            spacing = 35

        for i, ball in enumerate(self.ball_queue):
            true_y = self.config.ball_queue_lower_y - (len(self.ball_queue) - i) * spacing
            self.ball_queue_coords[i] += (true_y - self.ball_queue_coords[i]) * 30 * dt
            ball.move((self.config.ball_queue_x + self.field.position[0],
                       self.ball_queue_coords[i] + self.field.position[1]))
            ball.draw(self.screen)

        # Draw hit effects.
        for effect in self.hit_effects[:]:
            effect.update(dt)
            effect.draw(self.screen)
            if effect.is_dead():
                self.hit_effects.remove(effect)

        self.game_instance.display.blit(scale(self.screen, self.game_instance.screen_size), (0, 0))
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        exit_option = "exit"
        self.ui.change_mode("round")
        self.recharge()

        while running:
            dt = 1.0 / (self.real_fps if self.real_fps > 50 else self.config.fps)
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return == "round_over":
                    for ball in self.active_balls:
                        ball.remove(self.field.space)
                    exit_option = ui_return
                    running = False
                    break
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = self.ui.overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
                            if choice == "Exit to Main Menu":
                                exit_option = "menu"
                                running = False
                                break
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
                    if "try_selling" in ret:
                        item = ret["try_selling"]
                        if item.sell(self.game_instance):
                            self.game_instance.money += item.properties["price"] // 2
                            self.inventory.remove_item(item)
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        allow = False
                        for effect in item.effects:
                            if effect["usage"] == "active":
                                allow = True
                        if allow and item.use(self.game_instance):
                            self.applied_cards.add_item(item)
                            self.applied_cards.recalculate_targets()
                            self.inventory.remove_item(item)
                            self.hit_effects.append(DisappearingItem(item, 0.5))

            if not self.ball_launched and self.launch_key_down:
                self.launch_charge += dt * self.config.launch_charge_rate
                self.launch_charge = min(self.launch_charge, self.config.launch_max_impulse)

            for ball in self.active_balls[:]:
                if ball.body.position.y > self.config.screen_height + 50:
                    ball.remove(self.field.space)
                    self.active_balls.remove(ball)

            if len(self.active_balls) == 0 and not self.recharge():
                exit_option = "round_over"
                break

            # Ramp gate control.
            all_launched = True
            for ball in self.active_balls:
                if ball.body.velocity.length > self.config.max_ball_velocity:
                    ball.body.velocity = ball.body.velocity * (self.config.max_ball_velocity /
                                                               ball.body.velocity.length)
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

            if all_launched and not self.ball_launched:
                self.field.ramp_gate.sensor = False
                self.ball_launched = True

            keys = pygame.key.get_pressed()
            self.field.left_flipper.spring.rest_angle = (
                self.field.left_flipper.active_angle if keys[pygame.K_LEFT]
                else self.field.left_flipper.default_angle)
            self.field.right_flipper.spring.rest_angle = (
                self.field.right_flipper.active_angle if keys[pygame.K_RIGHT]
                else self.field.right_flipper.default_angle)

            self.field.update(dt)

            if self.score >= self.game_instance.score_needed:
                self.ui.change_mode("round_finishable")

            self.inventory.update(dt)
            self.applied_cards.update(dt)

            self.draw(dt)
            clock.tick(self.real_fps if self.real_fps > 50 else self.config.fps)
            self.real_fps = clock.get_fps()

        for applied_effect in self.applied_cards.items:
            applied_effect.end_use(self.game_instance)
        return exit_option, self.score
