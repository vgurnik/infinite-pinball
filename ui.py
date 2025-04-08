import sys
from pathlib import Path
import pygame
from game_effects import ContextWindow
from inventory import InventoryItem, PackInventory
from misc import scale, mouse_scale


class Button:
    def __init__(self, text, pos, size, color, font_size=36, offset=(0, 0)):
        font_file = Path(__file__).resolve().with_name("assets").joinpath('terminal-grotesque.ttf')
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
        fontfile = Path(__file__).resolve().with_name("assets").joinpath('terminal-grotesque.ttf')
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
            font = pygame.font.Font(fontfile, 36)
            title_text = font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
            screen.blit(title_text, title_rect)
            option_rects = []
            for idx, option in enumerate(options):
                if idx == selected:
                    opt_font = pygame.font.Font(fontfile, 42)
                    color = (255, 255, 0)
                else:
                    opt_font = pygame.font.Font(fontfile, 36)
                    color = (255, 255, 255)
                text = opt_font.render(option, True, color)
                rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
                screen.blit(text, rect)
                option_rects.append(rect)
            self.game_instance.display.blit(scale(screen, self.game_instance.screen_size), (0, 0))
            pygame.display.flip()

    def open_pack(self, items, start, kind, amount):
        clock = pygame.time.Clock()
        big_font = pygame.font.Font(self.config.fontfile, 36)
        dt = 1.0 / self.config.fps
        opening_inventory = PackInventory(self.game_instance, len(items) * 150)
        for item in items:
            opening_inventory.add_item(InventoryItem(item["name"], properties=item, target_position=start))
        taken = 0
        skip_button = Button("Skip", (opening_inventory.position[0] + opening_inventory.width / 2,
                                      opening_inventory.position[1] + 200), "auto", (0, 255, 100))
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
                        if self.game_instance.inventory.add_item(item):
                            opening_inventory.remove_item(item)
                            taken += 1
                    elif kind == 'all':
                        to_remove = []
                        for item in opening_inventory.items:
                            if self.game_instance.inventory.add_item(item):
                                to_remove.append(item)
                            else:
                                for i in to_remove:
                                    self.game_instance.inventory.remove_item(i)
                                break
                        else:
                            taken = amount

            self.game_instance.screen.fill((20, 20, 70))

            header = big_font.render("In-Game Shop", True, (255, 255, 255))
            self.game_instance.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))
            self.game_instance.ui.draw(self.game_instance.screen)
            self.game_instance.ui.update(dt)
            self.game_instance.inventory.update(dt)
            self.game_instance.inventory.draw(self.game_instance.screen)

            opening_surface = pygame.Surface((self.config.screen_width, self.config.screen_height), pygame.SRCALPHA)
            opening_surface.fill((20, 20, 20, 150))
            opening_inventory.update(dt)
            opening_inventory.draw(opening_surface)

            skip_button.draw(opening_surface)
            if skip_button.is_pressed():
                return "skip"

            self.game_instance.screen.blit(opening_surface, (0, 0))
            self.game_instance.display.blit(scale(self.game_instance.screen, self.game_instance.screen_size), (0, 0))
            pygame.display.flip()
            clock.tick(self.config.fps)
        return "continue"

    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.config = game_instance.config
        self.mode = 'round'
        self.position = self.config.ui_pos
        self.play_button = Button("Play", self.config.ui_continue_pos, (self.config.ui_butt_width_1, 40),
                                  (255, 255, 0), 36, offset=self.position)
        self.field_button = Button("Field", self.config.ui_field_config_pos, (self.config.ui_butt_width_2, 40),
                                   (255, 0, 100), 36, offset=self.position)
        self.reroll_button = Button("Reroll", self.config.ui_reroll_pos, (self.config.ui_butt_width_2, 40),
                                    (0, 255, 100), 36, offset=self.position)
        self.context = ContextWindow()

    def change_mode(self, mode):
        assert mode in ['shop', 'round', 'round_finishable', 'field_modification', 'results']
        self.mode = mode
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
        if self.mode in ['round', 'round_finishable', 'results']:
            if self.mode == 'round_finishable':
                self.play_button.draw(ui_surface)
            score = self.game_instance.round_instance.score
            min_score_text = font.render(f"Required score: {self.game_instance.score_needed}", True, (255, 255, 255))
            score_text = font.render(f"Score: {int(score) if score == int(score) else score}",
                                     True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_score_pos)
            ui_surface.blit(min_score_text, self.config.ui_min_score_pos)

        elif self.mode in ['shop', 'field_modification']:
            self.play_button.draw(ui_surface)
            self.field_button.draw(ui_surface)
            if self.mode == 'shop':
                self.reroll_button.draw(ui_surface, self.game_instance.money < self.game_instance.reroll_cost)
            score_text = font.render(f"Next score: {self.game_instance.score_needed}", True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_min_score_pos)

        money_text = font.render(f"$ {self.game_instance.money}", True, (255, 255, 255))
        ui_surface.blit(money_text, self.config.ui_money_pos)
        surface.blit(ui_surface, self.position)
        self.context.draw(surface)

    def update(self, _dt):
        mpos = mouse_scale(pygame.mouse.get_pos())
        if self.mode in ['shop', 'field_modification'] and self.play_button.is_hovered():
            self.context.update(mpos, self.config.play_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.field_button.is_hovered():
            self.context.update(mpos, self.config.field_description)
            self.context.set_visibility(True)
        elif self.mode == 'field_modification' and self.field_button.is_hovered():
            self.context.update(mpos, self.config.back_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.reroll_button.is_hovered():
            self.context.update(mpos, self.config.reroll_description.format(self.game_instance.reroll_cost))
            self.context.set_visibility(True)
        elif self.mode == 'round_finishable' and self.play_button.is_hovered():
            self.context.update(mpos, self.config.finish_description)
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
            if event.key == pygame.K_r and self.game_instance.debug_mode:
                self.game_instance.textures = self.game_instance.load_textures()
                self.game_instance.field.textures = self.game_instance.textures
                print('textures reloaded')
            if event.key == pygame.K_EQUALS and self.game_instance.debug_mode:
                self.game_instance.money += 1000
                print('+$1000')
            if event.key == pygame.K_MINUS and self.game_instance.debug_mode:
                self.game_instance.round_instance.score += 1000
                print('+1000 score')
        return None
