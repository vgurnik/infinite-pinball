import sys
from pathlib import Path
import pygame
from game_effects import ContextWindow
from inventory import InventoryItem, PackInventory


class Ui:
    @staticmethod
    def overlay_menu(screen, title, options):
        fontfile = Path(__file__).resolve().with_name("assets").joinpath('terminal-grotesque.ttf')
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
            pygame.display.flip()

    def open_pack(self, items, start, kind, amount):
        clock = pygame.time.Clock()
        big_font = pygame.font.Font(self.config.fontfile, 36)
        dt = 1.0 / self.config.fps
        opening_inventory = PackInventory(self.game_instance, len(items) * 150)
        for item in items:
            opening_inventory.add_item(InventoryItem(item["name"], properties=item, target_position=start))
        taken = 0
        skip_button_text = big_font.render("Skip", True, (0, 0, 0))
        skip_button = skip_button_text.get_rect()
        skip_button.topleft = (opening_inventory.position[0] + (opening_inventory.width - skip_button.width) / 2,
                               opening_inventory.position[1] + 200)
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
            n = 0
            if skip_button.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    return "skip"
                n = 3
            pygame.draw.rect(opening_surface, (0, 255, 100), skip_button.inflate(20 + n, 10 + n), border_radius=5)
            opening_surface.blit(skip_button_text, skip_button)

            self.game_instance.screen.blit(opening_surface, (0, 0))
            pygame.display.flip()
            clock.tick(self.config.fps)
        return "continue"

    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.config = game_instance.config
        self.mode = 'round'
        self.position = self.config.ui_pos
        self.play_button = None
        self.field_button = None
        self.finish_button = None
        self.reroll_button = None
        self.context = ContextWindow()

    def change_mode(self, mode):
        assert mode in ['shop', 'round', 'round_finishable', 'field_modification', 'results']
        self.mode = mode

    def draw(self, surface):
        # Display UI
        font = pygame.font.Font(self.config.fontfile, 24)
        big_font = pygame.font.Font(self.config.fontfile, 36)
        ui_surface = pygame.Surface((self.config.ui_width, self.config.screen_height))
        ui_surface.fill((20, 10, 60))

        if self.mode in ['round', 'round_finishable', 'results']:
            if self.mode == 'round_finishable':
                finish_button_text = big_font.render("Finish", True, (0, 0, 0))
                self.finish_button = finish_button_text.get_rect()
                self.finish_button.topleft = self.config.ui_continue_pos
                self.finish_button.width = self.config.ui_butt_width_1
                n = 0
                if self.finish_button.inflate(20, 10).move(self.position).collidepoint(pygame.mouse.get_pos()):
                    n = 3
                pygame.draw.rect(ui_surface, (255, 255, 0),
                                 self.finish_button.inflate(20 + n, 10 + n), border_radius=5)
                ui_surface.blit(finish_button_text, self.finish_button)
            score = self.game_instance.round_instance.score
            min_score_text = font.render(f"Required score: {self.game_instance.score_needed}", True, (255, 255, 255))
            score_text = font.render(f"Score: {int(score) if score == int(score) else score}",
                                     True, (255, 255, 255))
            balls_text = font.render(f"Balls Left: {self.game_instance.round_instance.balls_left}",
                                     True, (255, 255, 255))
            ui_surface.blit(balls_text, self.config.ui_balls_pos)
            ui_surface.blit(score_text, self.config.ui_score_pos)
            ui_surface.blit(min_score_text, self.config.ui_min_score_pos)

        elif self.mode in ['shop', 'field_modification']:
            if self.mode == 'shop':
                play_button_text = big_font.render("Play", True, (0, 0, 0))
                field_button_text = big_font.render("Field", True, (0, 0, 0))
                reroll_button_text = big_font.render("Reroll", True, (0, 0, 0))
            else:
                play_button_text = big_font.render("Play", True, (0, 0, 0))
                field_button_text = big_font.render("Back", True, (0, 0, 0))
            self.play_button = play_button_text.get_rect()
            self.play_button.topleft = self.config.ui_continue_pos
            self.play_button.width = self.config.ui_butt_width_1
            self.field_button = field_button_text.get_rect()
            self.field_button.topleft = self.config.ui_field_config_pos
            self.field_button.width = self.config.ui_butt_width_2
            n = 0
            if self.play_button.inflate(20, 10).move(self.position).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(ui_surface, (255, 255, 0), self.play_button.inflate(20 + n, 10 + n), border_radius=5)
            ui_surface.blit(play_button_text, self.play_button)
            n = 0
            if self.field_button.inflate(20, 10).move(self.position).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(ui_surface, (255, 0, 100), self.field_button.inflate(20 + n, 10 + n), border_radius=5)
            ui_surface.blit(field_button_text, self.field_button)
            if self.mode == 'shop':
                self.reroll_button = reroll_button_text.get_rect()
                self.reroll_button.topleft = self.config.ui_reroll_pos
                self.reroll_button.width = self.config.ui_butt_width_2
                n = 0
                if self.reroll_button.inflate(20, 10).move(self.position).collidepoint(pygame.mouse.get_pos()):
                    n = 3
                if self.game_instance.money >= self.game_instance.reroll_cost:
                    color = (0, 255, 100)
                else:
                    color = (100, 150, 120)
                pygame.draw.rect(ui_surface, color, self.reroll_button.inflate(20 + n, 10 + n), border_radius=5)
                ui_surface.blit(reroll_button_text, self.reroll_button)
            score_text = font.render(f"Next score: {self.game_instance.score_needed}", True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_min_score_pos)

        money_text = font.render(f"$ {self.game_instance.money}", True, (255, 255, 255))
        ui_surface.blit(money_text, self.config.ui_money_pos)
        surface.blit(ui_surface, self.position)
        self.context.draw(surface)

    def update(self, dt):
        mpos = pygame.mouse.get_pos()
        if self.mode in ['shop', 'field_modification'] and \
                self.play_button.inflate(20, 10).move(self.position).collidepoint(mpos):
            self.context.update(mpos, self.config.play_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and \
                self.field_button.inflate(20, 10).move(self.position).collidepoint(mpos):
            self.context.update(mpos, self.config.field_description)
            self.context.set_visibility(True)
        elif self.mode == 'field_modification' and \
                self.field_button.inflate(20, 10).move(self.position).collidepoint(mpos):
            self.context.update(mpos, self.config.back_description)
            self.context.set_visibility(True)
        elif self.mode == 'shop' and \
                self.reroll_button.inflate(20, 10).move(self.position).collidepoint(mpos):
            self.context.update(mpos, self.config.reroll_description.format(self.game_instance.reroll_cost))
            self.context.set_visibility(True)
        elif self.mode == 'round_finishable' and \
                self.finish_button.inflate(20, 10).move(self.position).collidepoint(mpos):
            self.context.update(mpos, self.config.finish_description)
            self.context.set_visibility(True)
        else:
            self.context.set_visibility(False)

    def handle_event(self, event):
        mpos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.mode in ['shop', 'field_modification'] and\
                    self.play_button.inflate(20, 10).move(self.position).collidepoint(mpos):
                return "continue"
            if self.mode in ['shop', 'field_modification'] and\
                    self.field_button.inflate(20, 10).move(self.position).collidepoint(mpos):
                return "field_setup"
            if self.mode == 'shop' and\
                    self.reroll_button.inflate(20, 10).move(self.position).collidepoint(mpos):
                return "reroll"
            if self.mode == 'round_finishable' and\
                    self.finish_button.inflate(20, 10).move(self.position).collidepoint(mpos):
                return "round_over"
