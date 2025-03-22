import pygame
import sys
import math
import random
from config import Config
from round import PinballRound
from inventory import Inventory, PlayerInventory, InventoryItem
from game_effects import overlay_menu, DisappearingItem


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height))
        pygame.display.set_caption("Infinite Pinball")
        self.money = 0
        self.round = 0
        self.score_needed = self.config.min_score[self.round]
        self.textures = self.load_textures()
        self.inventory = PlayerInventory(position=self.config.ui_inventory_pos,
                                         width=self.config.ui_width, height=self.config.ui_inventory_height)
        self.round_instance = None

    @staticmethod
    def load_textures():
        # Load textures
        textures = {"ball": pygame.image.load("assets/ball.bmp").convert_alpha(),
                    "flipper_left": pygame.image.load("assets/flipper_left.bmp").convert_alpha(),
                    "bumper": pygame.image.load("assets/bumper_big.bmp").convert_alpha(),
                    "bumper_bumped": pygame.image.load("assets/bumper_big_bumped.bmp").convert_alpha(),
                    "bumper_small": pygame.image.load("assets/bumper_small.bmp").convert_alpha(),
                    "bumper_small_bumped": pygame.image.load("assets/bumper_small_bumped.bmp").convert_alpha()}
        return textures

    def main_menu(self):
        choice = overlay_menu(self.screen, "Main Menu",
                              ["Start Game", "Preferences", "Exit", "Debug_Shop"])
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
            clock.tick(self.config.fps)

    def shop_screen(self):
        clock = pygame.time.Clock()
        dt = 1.0 / self.config.fps
        font = pygame.font.SysFont("Arial", 24)
        big_font = pygame.font.SysFont("Arial", 36)
        shop = Inventory()
        for i in range(2):
            item = random.randint(0, len(self.config.shop_items["cards"])-1)
            item = self.config.shop_items["cards"][item]
            shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                self.config.shop_pos_cards[0] + i * 130, self.config.shop_pos_cards[1])))
        for i in range(3):
            item = random.randint(0, len(self.config.shop_items["objects"])-1)
            item = self.config.shop_items["objects"][item]
            shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                self.config.shop_pos_objects[0] + i * 130, self.config.shop_pos_objects[1])))
        for i in range(1):
            item = random.randint(0, len(self.config.shop_items["vouchers"])-1)
            item = self.config.shop_items["vouchers"][item]
            shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                self.config.shop_pos_effects[0] + 100 + i * 130, self.config.shop_pos_effects[1])))
        for i in range(2):
            item = random.randint(0, len(self.config.shop_items["packs"])-1)
            item = self.config.shop_items["packs"][item]
            shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                self.config.shop_pos_packs[0] + i * 130, self.config.shop_pos_packs[1])))

        play_button_text = big_font.render("Play", True, (0, 0, 0))
        play_button_rect = play_button_text.get_rect()
        play_button_rect.topleft = self.config.ui_continue_pos
        play_button_rect.width = self.config.ui_butt_width
        field_button_text = big_font.render("Field", True, (0, 0, 0))
        field_button_rect = field_button_text.get_rect()
        field_button_rect.topleft = self.config.ui_field_config_pos
        field_button_rect.width = self.config.ui_butt_width

        message = ""
        effects = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "continue"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mpos = pygame.mouse.get_pos()
                    if play_button_rect.inflate(20, 10).collidepoint(mpos):
                        pygame.time.delay(200)
                        return "continue"
                    if field_button_rect.inflate(20, 10).collidepoint(mpos):
                        pygame.time.delay(200)
                        return "field_setup"
                item = shop.handle_event(event)
                if item is not None:
                    if self.money >= item.properties["price"]:
                        if item.properties["type"] in ["active_card", "passive_card", "buildable"]:
                            if item.properties["type"] == "passive_card":
                                execution = item.effect["effect"](self, *item.effect["params"])
                            else:
                                execution = True
                            addition = self.inventory.add_item(item)
                            if execution and addition:
                                self.money -= item.properties["price"]
                                shop.remove_item(item)
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                if not addition:
                                    message = "Not enough inventory space!"
                                elif not execution:
                                    message = f"Effect of {item.name} cannot be applied!"
                                if item.properties["type"] == "passive_card" and execution \
                                        and item.effect["negative_effect"]:
                                    # Theoretically impossible to have this return False, but just in case be mindful.<-
                                    item.effect["negative_effect"](self, *item.effect["params"])
                        elif item.properties["type"] == "immediate":
                            if item.effect["effect"](self, *item.effect["params"]):
                                effects.append(DisappearingItem(item, 0.5))
                                shop.remove_item(item)
                                self.money -= item.properties["price"]
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                message = f"Effect of {item.name} cannot be applied!"
                    else:
                        message = f"Not enough money for {item.name}."
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret:
                        item = ret["try_selling"]
                        if item.effect["negative_effect"] is None\
                                or item.effect["negative_effect"](self, *item.effect["params"]):
                            self.money += item.properties["price"] // 2
                            self.inventory.remove_item(item)
                            message = f"Sold {item.name} for {item.properties['price'] // 2}!"
            self.screen.fill((20, 20, 70))
            n = 0
            if play_button_rect.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(self.screen, (255, 255, 0), play_button_rect.inflate(20 + n, 10 + n), border_radius=5)
            self.screen.blit(play_button_text, play_button_rect)
            n = 0
            if field_button_rect.inflate(20, 10).collidepoint(pygame.mouse.get_pos()):
                n = 3
            pygame.draw.rect(self.screen, (255, 0, 100), field_button_rect.inflate(20 + n, 10 + n), border_radius=5)
            self.screen.blit(field_button_text, field_button_rect)
            header = big_font.render("In-Game Shop", True, (255, 255, 255))
            self.screen.blit(header, self.config.shop_pos)
            if message:
                msg_text = font.render(message, True, (0, 255, 0))
                self.screen.blit(msg_text, (self.config.shop_pos_effects[0], self.config.shop_pos_effects[1] + 200))
            score_text = font.render(f"Next score: {self.score_needed}", True, (255, 255, 255))
            money_text = font.render(f"$ {self.money}", True, (255, 255, 255))
            self.screen.blit(score_text, self.config.ui_min_score_pos)
            self.screen.blit(money_text, self.config.ui_money_pos)

            shop.update(dt)
            shop.draw(self.screen)
            self.inventory.update(dt)
            self.inventory.draw(self.screen)
            for effect in effects[:]:
                effect.update(dt)
                effect.draw(self.screen)
                if effect.is_dead():
                    effects.remove(effect)
            pygame.display.flip()
            clock.tick(self.config.fps)

    def field_modification_screen(self):
        # Here you could let the player add or remove objects, rearrange bumpers, etc.
        clock = pygame.time.Clock()
        dt = 1.0 / self.config.fps
        font = pygame.font.SysFont("Arial", 36)
        overlay = pygame.Surface((self.config.screen_width, self.config.screen_height))
        overlay.set_alpha(80)
        overlay.fill((50, 50, 50))
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
                        if choice == "Exit to Main Menu":
                            return 'menu'
                    elif event.key == pygame.K_RETURN:
                        waiting = False
                self.inventory.handle_event(event)
            self.screen.blit(overlay, (0, 0))
            text = font.render("Field Modification Mode - Press ESC or ENTER to exit", True, (255, 255, 255))
            self.screen.blit(text, (self.config.screen_width//2 - text.get_width()//2, self.config.screen_height//2))
            self.inventory.update(dt)
            self.inventory.draw(self.screen)
            pygame.display.flip()
            clock.tick(self.config.fps)
        return 'back'

    def round_results_overlay(self, score, min_score):
        extra_orders = int(math.log10(score / min_score)) if score >= min_score else 0
        award = self.config.base_award + extra_orders * self.config.extra_award_per_order
        if score >= min_score:
            self.money += award
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 36)
        overlay = pygame.Surface((self.config.screen_width - self.config.ui_width, self.config.screen_height))
        overlay.fill((20, 20, 20, 80))
        waiting = True
        result = 'lose'
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
            self.screen.blit(overlay, (self.config.ui_width, 0))
            if score < min_score:
                result = 'lose'
                texts = [
                    "Game Over!",
                    f"Score: {score}",
                    f"Required Minimum Score: {min_score}",
                    f"Total Money: {self.money}",
                    "Press ENTER to return to main menu"
                ]
                for i, line in enumerate(texts):
                    txt = font.render(line, True, (255, 100, 100))
                    self.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + self.config.ui_width,
                                           150 + i * 45))
            else:
                result = 'win'
                texts = [
                    "Round Complete!",
                    f"Score: {score}",
                    f"Required Minimum Score: {min_score}",
                    f"Award: {self.config.base_award}",
                    f"Award for extra score: {award - self.config.base_award}",
                    f"Total Money: {self.money}",
                    "Press ENTER to continue..."
                ]
                for i, line in enumerate(texts):
                    if i == 0:
                        txt = font.render(line, True, (0, 255, 0))
                    else:
                        txt = font.render(line, True, (255, 255, 255))
                    self.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + self.config.ui_width,
                                           150 + i * 45))
            pygame.display.flip()
            clock.tick(self.config.fps)
        return result

    def run(self):
        while True:
            choice = self.main_menu()
            if choice == "Exit":
                break
            elif choice == "Preferences":
                self.preferences_menu()
                continue
            elif choice == "Debug_Shop":
                self.money = 10000
                self.shop_screen()
                self.money = 0
                continue
            elif choice == "Start Game":
                self.config = Config()
                self.money = 0
                self.round = 0
                self.score_needed = self.config.min_score[0]
                while True:
                    self.round_instance = PinballRound(self)
                    result, round_score = self.round_instance.run()
                    if result != "round_over":
                        break
                    result = self.round_results_overlay(round_score, self.score_needed)
                    if result == 'lose':
                        break
                    self.round += 1
                    if self.round < 10:
                        self.score_needed = self.config.min_score[self.round]
                    else:
                        self.score_needed = 10**(self.round - 2)
                    while result in ['win', 'back']:
                        result = self.shop_screen()
                        if result == 'field_setup':
                            result = self.field_modification_screen()
                    if result == 'menu':
                        break
                if result == "exit":
                    break
        pygame.quit()
