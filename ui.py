import pygame
from game_effects import ContextWindow
from utils.textures import mouse_scale
from utils.text import format_text, loc
import game_context


class Button:
    def __init__(self, text, pos, size, color, font_size=36, offset=(0, 0)):
        font = pygame.font.Font(game_context.game.config.fontfile, font_size)
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

    def __init__(self):
        self.config = game_context.game.config
        self.mode = 'round'
        self.position = self.config.ui_pos
        self.play_button = Button(loc("ui.button.play", self.config.lang), self.config.ui_continue_pos,
                                  (self.config.ui_butt_width_1, 40), (255, 255, 0), 36, offset=self.position)
        self.field_button = Button(loc("ui.button.field", self.config.lang), self.config.ui_field_config_pos,
                                   (self.config.ui_butt_width_2, 40), (255, 0, 100), 36, offset=self.position)
        self.reroll_button = Button(loc("ui.button.reroll", self.config.lang), self.config.ui_reroll_pos,
                                    (self.config.ui_butt_width_2, 40), (0, 255, 100), 36, offset=self.position)
        self.context = ContextWindow()

    def change_mode(self, mode):
        assert mode in ['shop', 'round', 'round_finishable', 'field_modification', 'results']
        self.mode = mode
        self.context.set_visibility(False)
        if self.mode == 'round_finishable':
            self.play_button = Button(loc("ui.button.finish", self.config.lang), self.config.ui_continue_pos,
                                      (self.config.ui_butt_width_1, 40), (255, 255, 0), offset=self.position)
        elif self.mode in ['shop', 'field_modification']:
            self.play_button = Button(loc("ui.button.play", self.config.lang), self.config.ui_continue_pos,
                                      (self.config.ui_butt_width_1, 40), (255, 255, 0), offset=self.position)
            if self.mode == 'shop':
                self.field_button = Button(loc("ui.button.field", self.config.lang), self.config.ui_field_config_pos,
                                           (self.config.ui_butt_width_2, 40), (255, 0, 100), offset=self.position)
            else:
                self.field_button = Button(loc("ui.button.back", self.config.lang), self.config.ui_field_config_pos,
                                           (self.config.ui_butt_width_2, 40), (255, 0, 100), offset=self.position)

    def draw(self, surface):
        game = game_context.game
        font = pygame.font.Font(self.config.fontfile, 24)
        ui_surface = pygame.Surface((self.config.ui_width, self.config.screen_height))
        ui_surface.fill((20, 10, 60))
        req = int(game.score_needed) if (game.score_needed == int(game.score_needed)) else game.score_needed
        if self.mode in ['round', 'round_finishable', 'results']:
            if self.mode == 'round_finishable':
                self.play_button.draw(ui_surface)
            score = game.round_instance.score
            min_score_text = font.render(format_text("ui.text.req_score", self.config.lang, req), True, (255, 255, 255))
            score_text = font.render(format_text("ui.text.score", self.config.lang, score), True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_score_pos)
            ui_surface.blit(min_score_text, self.config.ui_min_score_pos)

        elif self.mode in ['shop', 'field_modification']:
            self.play_button.draw(ui_surface)
            self.field_button.draw(ui_surface)
            if self.mode == 'shop':
                self.reroll_button.draw(ui_surface, game.money < game.reroll_cost)
            score_text = font.render(format_text("ui.text.next_score", self.config.lang, req), True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_min_score_pos)

        round_text = font.render(format_text("ui.text.round", self.config.lang, game.round + 1),
                                 True, (255, 100, 200))
        ui_surface.blit(round_text, self.config.ui_round_pos)
        money_text = font.render(
            f"$ {round(game.money) if game.money == round(game.money) else game.money}",
            True, (255, 255, 0))
        ui_surface.blit(money_text, self.config.ui_money_pos)
        surface.blit(ui_surface, self.position)
        self.context.draw(surface)

    def update(self, _dt):
        mpos = mouse_scale(pygame.mouse.get_pos())
        if self.mode in ['shop', 'field_modification'] and self.play_button.is_hovered():
            self.context.update(mpos, 'text', loc("ui.message.play_description", self.config.lang))
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.field_button.is_hovered():
            self.context.update(mpos, 'text', loc("ui.message.field_description", self.config.lang))
            self.context.set_visibility(True)
        elif self.mode == 'field_modification' and self.field_button.is_hovered():
            self.context.update(mpos, 'text', loc("ui.message.back_description", self.config.lang))
            self.context.set_visibility(True)
        elif self.mode == 'shop' and self.reroll_button.is_hovered():
            self.context.update(mpos, 'text', loc("ui.message.reroll_description", self.config.lang
                                                  ).format(game_context.game.reroll_cost))
            self.context.set_visibility(True)
        elif self.mode == 'round_finishable' and self.play_button.is_hovered():
            self.context.update(mpos, 'text', loc("ui.message.finish_description", self.config.lang))
            self.context.set_visibility(True)
        else:
            self.context.set_visibility(False)

    def handle_event(self, event):
        game = game_context.game
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
            if event.key == pygame.K_r and game.debug_mode:
                game.textures = game.load_textures()
                game.field.textures = game.textures
                print('textures reloaded')
            if event.key == pygame.K_EQUALS and game.debug_mode:
                game.money += 1000
                print('+$1000')
            if event.key == pygame.K_MINUS and game.debug_mode:
                game.round_instance.score += 1000
                print('+1000 score')
        return None
