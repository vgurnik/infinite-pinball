import sys
from pathlib import Path
import pygame
from game_effects import ContextWindow, AnimatedEffect
from inventory import InventoryItem, PackInventory
from utils.textures import mouse_scale, display_screen
from utils.text import format_text


class Button:
    def __init__(self, text, pos, size, color, font_size=36, offset=(0, 0)):
        font_file = Path(__file__).resolve().with_name("assets").joinpath('lang/terminal-grotesque.ttf')
        font = pygame.font.Font(font_file, font_size)
        self.color = color
        self.text = font.render(text, True, (0, 0, 0))
        self.button = self.text.get_rect()
        if size != "auto":
            self.button.size = size
        self.button.topleft = pos
        self.offset = offset
        self.pressed = False

    def is_pressed(self):
        if self.pressed and not pygame.mouse.get_pressed()[0]:
            self.pressed = False
            return True
        return False

    def is_hovered(self):
        return self.button.inflate(20, 10).move(self.offset).collidepoint(mouse_scale(pygame.mouse.get_pos()))

    def update(self):
        if self.is_hovered() and pygame.mouse.get_pressed()[0]:
            self.pressed = True
        if not self.is_hovered():
            self.pressed = False

    def draw(self, surface, disabled=False):
        self.update()
        if disabled:
            avg = sum(self.color) / 3
            color = [round((avg + c) / 2) for c in self.color]
        else:
            color = self.color
        pygame.draw.rect(surface, (0, 0, 0, 100), self.button.inflate(20 + (self.is_hovered() and not disabled) * 3,
                                                                      10 + (self.is_hovered() and not disabled) * 3
                                                                      ).move(0, 5), border_radius=5)
        pygame.draw.rect(surface, color, self.button.inflate(20 + (self.is_hovered() and not disabled) * 3,
                                                             10 + (self.is_hovered() and not disabled) * 3
                                                             ).move(0, 5 * (self.pressed or disabled)), border_radius=5)
        surface.blit(self.text, self.button.move(0, 5 * (self.pressed or disabled)))


class Ui:

    def overlay_menu(self, screen, title, options):
        selected = 0
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        option_rects = []

        while True:
            mouse_pos = mouse_scale(pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
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
            font = pygame.font.Font(self.config.fontfile, 36)
            title_text = font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
            screen.blit(title_text, title_rect)
            option_rects = []
            for idx, option in enumerate(options):
                if idx == selected:
                    opt_font = pygame.font.Font(self.config.fontfile, 42)
                    color = (255, 255, 0)
                else:
                    opt_font = pygame.font.Font(self.config.fontfile, 36)
                    color = (255, 255, 255)
                text = opt_font.render(option, True, color)
                rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
                screen.blit(text, rect)
                option_rects.append(rect)
            display_screen(self.game.display, screen, self.game.screen_size)

    def open_pack(self, items, start, kind, amount, opening_sprite):
        clock = pygame.time.Clock()
        dt = 1.0 / (self.game.real_fps if self.game.real_fps > 1 else self.config.fps)
        big_font = pygame.font.Font(self.config.fontfile, 36)
        opening_inventory = PackInventory(self.game, len(items) * 150)
        for item in items:
            if item["type"] == "buildable":
                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                opening_inventory.add_item(InventoryItem(item["name"], sprite=self.game.textures.get("buildable_pack"),
                                                         properties=item, target_position=start, for_buildable=
                                                         self.game.textures.get(obj_def["texture"])))
            else:
                opening_inventory.add_item(InventoryItem(item["name"], sprite=self.game.textures.get(
                    item.get("sprite")), properties=item, target_position=start))
        taken = 0
        skip_button = Button("Skip", (opening_inventory.position[0] + opening_inventory.width / 2,
                                      opening_inventory.position[1] + 200), "auto", (0, 255, 100))
        opening_effect = AnimatedEffect(self.game.display, self.game.screen_size)
        self.game.screen.fill((20, 20, 70))

        header = big_font.render("Game Shop", True, (255, 255, 255))
        self.game.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))
        self.game.ui.draw(self.game.screen)
        self.game.ui.update(dt)
        self.game.inventory.update(dt)
        self.game.inventory.draw(self.game.screen)
        opening_inventory.draw(self.game.screen)
        opening_effect.start(self.game.screen, opening_sprite, (start.x - 3, start.y - 23),
                             (126, 188))
        clock.tick(self.config.fps)
        dt = 0
        while taken < amount:
            opening_inventory.recalculate_targets()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "skip"
                item = opening_inventory.handle_event(event)
                if item is not None:
                    if kind == 'oneof':
                        if self.game.inventory.add_item(item):
                            opening_inventory.remove_item(item)
                            taken += 1
                    elif kind == 'all':
                        to_remove = []
                        for item in opening_inventory.items:
                            if self.game.inventory.add_item(item):
                                to_remove.append(item)
                            else:
                                for i in to_remove:
                                    self.game.inventory.remove_item(i)
                                break
                        else:
                            taken = amount

            self.game.screen.fill((20, 20, 70))

            header = big_font.render("Game Shop", True, (255, 255, 255))
            self.game.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))
            self.game.ui.draw(self.game.screen)
            self.game.ui.update(dt)
            self.game.inventory.update(dt)
            self.game.inventory.draw(self.game.screen)

            opening_surface = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
            opening_surface.fill((20, 20, 20, 150))
            skip_button.draw(opening_surface)
            if skip_button.is_pressed():
                return "skip"

            opening_inventory.update(dt)
            opening_inventory.draw(opening_surface)
            if kind == 'oneof':
                pack_header = big_font.render(f"Take {taken}/{amount}", True, (255, 255, 255))
            else:
                pack_header = big_font.render("Take all or skip", True, (255, 255, 255))
            opening_surface.blit(pack_header, (opening_inventory.position[0] + (opening_inventory.width -
                                                                                pack_header.get_width()) / 2,
                                               opening_inventory.position[1] - 50))

            self.game.screen.blit(opening_surface, (0, 0))
            display_screen(self.game.display, self.game.screen, self.game.screen_size)
            dt = clock.tick(self.config.fps) / 1000
            self.game.real_fps = clock.get_fps()
        return "continue"

    def settings_menu(self):
        font = pygame.font.Font(self.config.fontfile, 28)
        bigger_font = pygame.font.Font(self.config.fontfile, 30)
        pref_running = True
        resolution_index = self.config.resolutions.index(self.game.screen_size)
        options = ["resolution", "fullscreen", "debug_mode", "back"]
        selected_option = 0

        while pref_running:
            reload = False
            self.game.screen.fill((20, 20, 70))
            pref_text = font.render("Settings", True, (255, 255, 255))
            resolution_text = font.render(f"Resolution: {self.config.resolutions[resolution_index]}", True,
                                          (255, 255, 255))
            fullscreen_text = font.render(f"Fullscreen: {'On' if self.config.fullscreen else 'Off'}", True,
                                          (255, 255, 255))
            debug_text = font.render(f"Debug Mode: {'On' if self.game.debug_mode else 'Off'}", True, (255, 255, 255))
            back_text = font.render("Go back", True, (255, 255, 255))
            match selected_option:
                case 0:
                    resolution_text = bigger_font.render(f"Resolution: {self.config.resolutions[resolution_index]}",
                                                         True, (255, 255, 0))
                case 1:
                    fullscreen_text = bigger_font.render(f"Fullscreen: {'On' if self.config.fullscreen else 'Off'}",
                                                         True, (255, 255, 0))
                case 2:
                    debug_text = bigger_font.render(f"Debug Mode: {'On' if self.game.debug_mode else 'Off'}", True,
                                                    (255, 255, 0))
                case 3:
                    back_text = bigger_font.render("Go back", True, (255, 255, 0))

            self.game.screen.blit(pref_text, (self.config.screen_width // 2 - pref_text.get_width() // 2, 100))
            self.game.screen.blit(resolution_text, (self.config.screen_width // 2 -
                                                    resolution_text.get_width() // 2, 200))
            self.game.screen.blit(fullscreen_text, (self.config.screen_width // 2 -
                                                    fullscreen_text.get_width() // 2, 250))
            self.game.screen.blit(debug_text, (self.config.screen_width // 2 - debug_text.get_width() // 2, 300))
            self.game.screen.blit(back_text, (self.config.screen_width // 2 - back_text.get_width() // 2, 350))

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_UP:
                                selected_option = (selected_option - 1) % len(options)
                            case pygame.K_DOWN:
                                selected_option = (selected_option + 1) % len(options)
                            case pygame.K_RETURN:
                                match options[selected_option]:
                                    case "resolution":
                                        resolution_index = (resolution_index + 1) % len(self.config.resolutions)
                                        self.game.screen_size = self.config.resolutions[resolution_index]
                                        reload = True
                                    case "fullscreen":
                                        self.config.fullscreen = not self.config.fullscreen
                                        reload = True
                                    case "debug_mode":
                                        self.game.debug_mode = not self.game.debug_mode
                                    case "back":
                                        pref_running = False
                            case pygame.K_ESCAPE:
                                pref_running = False
                        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                            match options[selected_option]:
                                case "resolution":
                                    resolution_index = (resolution_index + (2 * (event.key == pygame.K_LEFT) - 1))\
                                                       % len(self.config.resolutions)
                                    self.game.screen_size = self.config.resolutions[resolution_index]
                                    reload = True
                                case "fullscreen":
                                    self.config.fullscreen = not self.config.fullscreen
                                    reload = True
                                case "debug_mode":
                                    self.game.debug_mode = not self.game.debug_mode
                                case "back":
                                    pref_running = False
                    case pygame.MOUSEBUTTONDOWN:
                        _, mouse_y = mouse_scale(event.pos)
                        if 200 <= mouse_y <= 230:
                            selected_option = 0
                        elif 250 <= mouse_y <= 280:
                            selected_option = 1
                        elif 300 <= mouse_y <= 330:
                            selected_option = 2
                        elif 350 <= mouse_y <= 380:
                            selected_option = 3
                        match options[selected_option]:
                            case "resolution":
                                resolution_index = (resolution_index + 1) % len(self.config.resolutions)
                                self.game.screen_size = self.config.resolutions[resolution_index]
                                reload = True
                            case "fullscreen":
                                self.config.fullscreen = not self.config.fullscreen
                                reload = True
                            case "debug_mode":
                                self.game.debug_mode = not self.game.debug_mode
                            case "back":
                                pref_running = False
                    case pygame.MOUSEMOTION:
                        _, mouse_y = mouse_scale(event.pos)
                        if 200 <= mouse_y <= 230:
                            selected_option = 0
                        elif 250 <= mouse_y <= 280:
                            selected_option = 1
                        elif 300 <= mouse_y <= 330:
                            selected_option = 2
                        elif 350 <= mouse_y <= 380:
                            selected_option = 3
            if reload:
                self.game.display = pygame.display.set_mode(self.game.screen_size, (
                    pygame.FULLSCREEN if self.config.fullscreen else 0))
            display_screen(self.game.display, self.game.screen, self.game.screen_size)

    def __init__(self, game):
        self.game = game
        self.config = game.config
        self.mode = 'round'
        self.position = self.config.ui_pos
        self.play_button = Button("Play", self.config.ui_continue_pos, (self.config.ui_butt_width_1, 40),
                                  (255, 255, 0), 36, offset=self.position)
        self.field_button = Button("Field", self.config.ui_field_config_pos, (self.config.ui_butt_width_2, 40),
                                   (255, 0, 100), 36, offset=self.position)
        self.reroll_button = Button("Reroll", self.config.ui_reroll_pos, (self.config.ui_butt_width_2, 40),
                                    (0, 255, 100), 36, offset=self.position)
        self.context = ContextWindow(self.config)

    def change_mode(self, mode):
        assert mode in ['shop', 'round', 'round_finishable', 'field_modification', 'results']
        self.mode = mode
        self.context.set_visibility(False)
        if self.mode == 'round_finishable':
            self.play_button = Button("Finish", self.config.ui_continue_pos, (self.config.ui_butt_width_1, 40),
                                      (255, 255, 0), offset=self.position)
        elif self.mode in ['shop', 'field_modification']:
            self.play_button = Button("Play", self.config.ui_continue_pos, (self.config.ui_butt_width_1, 40),
                                      (255, 255, 0), offset=self.position)
            if self.mode == 'shop':
                self.field_button = Button("Field", self.config.ui_field_config_pos, (self.config.ui_butt_width_2, 40),
                                           (255, 0, 100), offset=self.position)
            else:
                self.field_button = Button("Back", self.config.ui_field_config_pos, (self.config.ui_butt_width_2, 40),
                                           (255, 0, 100), offset=self.position)

    def draw(self, surface):
        font = pygame.font.Font(self.config.fontfile, 24)
        ui_surface = pygame.Surface((self.config.ui_width, self.config.screen_height))
        ui_surface.fill((20, 10, 60))
        req = int(self.game.score_needed) if (self.game.score_needed == int(self.game.score_needed)
                                              ) else self.game.score_needed
        if self.mode in ['round', 'round_finishable', 'results']:
            if self.mode == 'round_finishable':
                self.play_button.draw(ui_surface)
            score = self.game.round_instance.score
            min_score_text = font.render(format_text("Required score: {}", req), True, (255, 255, 255))
            score_text = font.render(format_text("Score: {}", score), True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_score_pos)
            ui_surface.blit(min_score_text, self.config.ui_min_score_pos)

        elif self.mode in ['shop', 'field_modification']:
            self.play_button.draw(ui_surface)
            self.field_button.draw(ui_surface)
            if self.mode == 'shop':
                self.reroll_button.draw(ui_surface, self.game.money < self.game.reroll_cost)
            score_text = font.render(format_text("Next score: {}", req), True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_min_score_pos)

        round_text = font.render(format_text("Round: {}", self.game.round + 1), True, (255, 100, 200))
        ui_surface.blit(round_text, self.config.ui_round_pos)
        money_text = font.render(
            f"$ {round(self.game.money) if self.game.money == round(self.game.money) else self.game.money}",
            True, (255, 255, 0))
        ui_surface.blit(money_text, self.config.ui_money_pos)
        surface.blit(ui_surface, self.position)
        self.context.draw(surface)

    def update(self, _dt):
        mpos = mouse_scale(pygame.mouse.get_pos())
        if self.mode in ['shop', 'field_modification'] and self.play_button.is_hovered():
            self.context.update(mpos, 'text', self.config.play_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.field_button.is_hovered():
            self.context.update(mpos, 'text', self.config.field_description)
            self.context.set_visibility(True)
        elif self.mode == 'field_modification' and self.field_button.is_hovered():
            self.context.update(mpos, 'text', self.config.back_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.reroll_button.is_hovered():
            self.context.update(mpos, 'text', self.config.reroll_description.format(self.game.reroll_cost))
            self.context.set_visibility(True)
        elif self.mode == 'round_finishable' and self.play_button.is_hovered():
            self.context.update(mpos, 'text', self.config.finish_description)
            self.context.set_visibility(True)
        else:
            self.context.set_visibility(False)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.mode in ['shop', 'field_modification'] and self.play_button.is_pressed():
                return "continue"
            if self.mode in ['shop', 'field_modification'] and self.field_button.is_pressed():
                return "field_setup"
            if self.mode == 'shop' and self.reroll_button.is_pressed():
                return "reroll"
            if self.mode == 'round_finishable' and self.play_button.is_pressed():
                return "round_over"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game.debug_mode:
                self.game.textures = self.game.load_textures()
                self.game.field.textures = self.game.textures
                print('textures reloaded')
            if event.key == pygame.K_EQUALS and self.game.debug_mode:
                self.game.money += 1000
                print('+$1000')
            if event.key == pygame.K_MINUS and self.game.debug_mode:
                self.game.round_instance.score += 1000
                print('+1000 score')
        return None
