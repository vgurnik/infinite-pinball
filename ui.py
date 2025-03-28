import pygame
import sys


class Ui:
    @staticmethod
    def overlay_menu(screen, title, options):
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
            font = pygame.font.Font("assets/terminal-grotesque.ttf", 36)
            title_text = font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
            screen.blit(title_text, title_rect)
            option_rects = []
            for idx, option in enumerate(options):
                if idx == selected:
                    opt_font = pygame.font.Font("assets/terminal-grotesque.ttf", 42)
                    color = (255, 255, 0)
                else:
                    opt_font = pygame.font.Font("assets/terminal-grotesque.ttf", 36)
                    color = (255, 255, 255)
                text = opt_font.render(option, True, color)
                rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
                screen.blit(text, rect)
                option_rects.append(rect)
            pygame.display.flip()

    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.config = game_instance.config
        self.mode = 'round'
        self.play_button = None
        self.field_button = None
        self.finish_button = None

    def change_mode(self, mode):
        assert mode in ['shop', 'round', 'round_finishable', 'field_modification', 'results']
        self.mode = mode

    def draw(self, surface):
        # Display UI
        font = pygame.font.Font("assets/terminal-grotesque.ttf", 24)
        big_font = pygame.font.Font("assets/terminal-grotesque.ttf", 36)
        ui_surface = pygame.Surface((self.config.ui_width, self.config.screen_height))
        ui_surface.fill((20, 10, 60))

        if self.mode in ['round', 'round_finishable', 'results']:
            if self.mode == 'round_finishable':
                finish_button_text = big_font.render("Finish", True, (0, 0, 0))
                self.finish_button = finish_button_text.get_rect()
                self.finish_button.topleft = self.config.ui_continue_pos
                self.finish_button.width = self.config.ui_butt_width
                n = 0
                if self.finish_button.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
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

        elif self.mode == 'shop':
            play_button_text = big_font.render("Play", True, (0, 0, 0))
            self.play_button = play_button_text.get_rect()
            self.play_button.topleft = self.config.ui_continue_pos
            self.play_button.width = self.config.ui_butt_width
            field_button_text = big_font.render("Field", True, (0, 0, 0))
            self.field_button = field_button_text.get_rect()
            self.field_button.topleft = self.config.ui_field_config_pos
            self.field_button.width = self.config.ui_butt_width
            n = 0
            if self.play_button.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(ui_surface, (255, 255, 0), self.play_button.inflate(20 + n, 10 + n), border_radius=5)
            ui_surface.blit(play_button_text, self.play_button)
            n = 0
            if self.field_button.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(ui_surface, (255, 0, 100), self.field_button.inflate(20 + n, 10 + n), border_radius=5)
            ui_surface.blit(field_button_text, self.field_button)
            score_text = font.render(f"Next score: {self.game_instance.score_needed}", True, (255, 255, 255))
            ui_surface.blit(score_text, self.config.ui_min_score_pos)

        money_text = font.render(f"$ {self.game_instance.money}", True, (255, 255, 255))
        ui_surface.blit(money_text, self.config.ui_money_pos)
        surface.blit(ui_surface, (0, 0))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mpos = pygame.mouse.get_pos()
            if self.mode == 'shop' and self.play_button.inflate(20, 10).collidepoint(mpos):
                return "continue"
            if self.mode == 'shop' and self.field_button.inflate(20, 10).collidepoint(mpos):
                return "field_setup"
            if self.mode == 'round_finishable' and self.finish_button.inflate(20, 10).collidepoint(mpos):
                return "round_over"
