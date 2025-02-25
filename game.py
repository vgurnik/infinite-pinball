import pygame
import sys
from config import Config
from round import PinballRound


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height))
        pygame.display.set_caption("Infinite Pinball")
        self.money_total = 0
        self.textures = self.load_textures()

    @staticmethod
    def load_textures():
        # Load textures
        textures = {"ball": pygame.image.load("assets/ball.bmp").convert_alpha(),
                    "flipper_left": pygame.image.load("assets/flipper_left.bmp").convert_alpha(),
                    "bumper": pygame.image.load("assets/bumper_big.bmp").convert_alpha(),
                    "bumper_bumped": pygame.image.load("assets/bumper_big_bumped.bmp").convert_alpha()}
        textures["flipper_right"] = pygame.transform.flip(textures["flipper_left"], flip_x=True, flip_y=False)
        return textures

    def main_menu(self):
        choice = PinballRound.overlay_menu(self.screen, "Main Menu", ["Start Game", "Preferences", "Exit"])
        return choice

    def preferences_menu(self):
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 28)
        pref_running = True
        while pref_running:
            self.screen.fill((20, 20, 70))
            pref_text = font.render("Preferences", True, (255, 255, 255))
            balls_text = font.render(f"Number of Balls: {self.config.balls} (Left/Right to change)",
                                     True, (255, 255, 255))
            back_text = font.render("Press ESC to go back", True, (255, 255, 255))
            self.screen.blit(pref_text, (self.config.screen_width // 2 - pref_text.get_width() // 2, 100))
            self.screen.blit(balls_text, (self.config.screen_width // 2 - balls_text.get_width() // 2, 200))
            self.screen.blit(back_text, (self.config.screen_width // 2 - back_text.get_width() // 2, 300))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.config.balls > 1:
                            self.config.balls -= 1
                    elif event.key == pygame.K_RIGHT:
                        self.config.balls += 1
                    elif event.key == pygame.K_ESCAPE:
                        pref_running = False
            pygame.display.flip()
            clock.tick(30)


    def shop_screen(self, money):
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 24)
        big_font = pygame.font.SysFont("Arial", 36)
        grid_cols, grid_rows = self.config.shop_grid
        shop_rect = pygame.Rect(*self.config.shop_rect)
        cell_width = shop_rect.width // grid_cols
        cell_height = shop_rect.height // grid_rows

        message = ""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return money
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if shop_rect.collidepoint(pos):
                        rel_x = pos[0] - shop_rect.x
                        rel_y = pos[1] - shop_rect.y
                        col = rel_x // cell_width
                        row = rel_y // cell_height
                        idx = row * grid_cols + col
                        if idx < len(self.config.shop_items):
                            item = self.config.shop_items[idx]
                            if money >= item["price"]:
                                money -= item["price"]
                                message = f"Purchased {item['name']} for {item['price']}!"
                            else:
                                message = f"Not enough money for {item['name']}."
            self.screen.fill((20, 20, 70))
            header = big_font.render("In-Game Shop", True, (255, 255, 255))
            self.screen.blit(header, (shop_rect.x, shop_rect.y - 40))
            for row in range(grid_rows):
                for col in range(grid_cols):
                    idx = row * grid_cols + col
                    cell_rect = pygame.Rect(shop_rect.x + col * cell_width,
                                            shop_rect.y + row * cell_height, cell_width, cell_height)
                    pygame.draw.rect(self.screen, (200, 200, 200), cell_rect, 2)
                    if idx < len(self.config.shop_items):
                        item = self.config.shop_items[idx]
                        item_text = font.render(item["name"], True, (255, 255, 255))
                        price_text = font.render(f"${item['price']}", True, (255, 255, 0))
                        self.screen.blit(item_text, item_text.get_rect(center=(cell_rect.centerx,
                                                                               cell_rect.centery - 10)))
                        self.screen.blit(price_text, price_text.get_rect(center=(cell_rect.centerx,
                                                                                 cell_rect.centery + 20)))
            button_text = big_font.render("Start Next Round", True, (0, 0, 0))
            button_rect = button_text.get_rect()
            button_rect.topleft = (shop_rect.x, shop_rect.bottom + 60)
            n = 0
            if button_rect.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(self.screen, (255, 255, 0), button_rect.inflate(20+n, 10+n), border_top_left_radius=5,
                             border_top_right_radius=5, border_bottom_left_radius=5, border_bottom_right_radius=5)
            self.screen.blit(button_text, button_rect)
            if pygame.mouse.get_pressed()[0]:
                mpos = pygame.mouse.get_pos()
                if button_rect.inflate(20, 10).collidepoint(mpos):
                    pygame.time.delay(200)
                    return money
            if message:
                msg_text = font.render(message, True, (0, 255, 0))
                self.screen.blit(msg_text, (shop_rect.x, shop_rect.bottom + 20))
            score_text = font.render(f"Next score: {self.config.min_score}", True, (255, 255, 255))
            money_text = font.render(f"$ {money}", True, (255, 255, 255))
            self.screen.blit(score_text, self.config.ui_min_score_pos)
            self.screen.blit(money_text, self.config.ui_money_pos)
            pygame.display.flip()
            clock.tick(30)

    def field_modification_screen(self):
        # Here you could let the player add or remove objects, rearrange bumpers, etc.
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 36)
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(180)
        overlay.fill((50, 50, 50))
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        waiting = False
            self.screen.blit(overlay, (0, 0))
            text = font.render("Field Modification Mode - Press ESC or ENTER to exit", True, (255, 255, 255))
            self.screen.blit(text, (self.config.screen_width//2 - text.get_width()//2, self.config.screen_height//2))
            pygame.display.flip()
            clock.tick(30)

    def round_results_overlay(self, score, money, min_score):
        money_gain = score // 10
        new_total = money + money_gain
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 36)
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(100)
        overlay.fill((20, 20, 20))
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
            self.screen.blit(overlay, (0, 0))
            texts = [
                "Round Over!",
                f"Score: {score}",
                f"Money earned: {money_gain}",
                f"Total Money: {new_total}",
                f"Required Minimum Score: {min_score}",
                "Press ENTER to continue..."
            ]
            for i, line in enumerate(texts):
                txt = font.render(line, True, (255, 255, 255))
                self.screen.blit(txt, (self.config.screen_width // 2 - txt.get_width() // 2, 150 + i * 45))
            pygame.display.flip()
            clock.tick(30)
        return new_total

    def run(self):
        while True:
            choice = self.main_menu()
            if choice == "Exit":
                break
            elif choice == "Preferences":
                self.preferences_menu()
                continue
            elif choice == "Start Game":
                while True:
                    round_instance = PinballRound(self.screen, self.config, self.money_total, self.textures)
                    result, round_score, self.money_total = round_instance.run()
                    if result == "round_over":
                        self.money_total = self.round_results_overlay(
                            round_score, self.money_total, self.config.min_score)
                        self.money_total = self.shop_screen(self.money_total)
                    else:
                        break
                    if result == "exit":
                        break
                if result == "exit":
                    break
        pygame.quit()
