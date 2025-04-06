import sys
import math
import random
from pathlib import Path
import pygame
from config import Config
from field import Field
from ui import Ui
from round import PinballRound
from inventory import Inventory, PlayerInventory, InventoryItem
from game_effects import DisappearingItem


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height),
                                              pygame.SCALED | pygame.RESIZABLE)
        self.textures = self.load_textures()
        self.field = Field(self)
        self.ui = Ui(self)
        pygame.display.set_caption("Infinite Pinball")

        self.reroll_cost = 10
        self.money = 0
        self.round = 0
        self.score_needed = self.config.min_score[self.round]
        self.inventory = PlayerInventory(self)
        self.round_instance = None
        self.real_fps = 0

    @staticmethod
    def load_textures():
        asset_folder = Path(__file__).resolve().with_name("assets")
        # Load textures
        textures = {"ball": pygame.image.load(asset_folder.joinpath("ball.bmp")).convert_alpha(),
                    "flipper_left": pygame.image.load(asset_folder.joinpath("flipper_left.bmp")).convert_alpha(),
                    "longboi": pygame.image.load(asset_folder.joinpath("longboi.bmp")).convert_alpha(),
                    "pro_flipper": pygame.image.load(asset_folder.joinpath("pro_flipper.bmp")).convert_alpha(),
                    "bumper": pygame.image.load(asset_folder.joinpath("bumper_big.bmp")).convert_alpha(),
                    "bumper_bumped": pygame.image.load(asset_folder.joinpath("bumper_big_bumped.bmp")).convert_alpha(),
                    "bumper_small": pygame.image.load(asset_folder.joinpath("bumper_small.bmp")).convert_alpha(),
                    "bumper_small_bumped": pygame.image.load(asset_folder.joinpath("bumper_small_bumped.bmp")
                                                             ).convert_alpha()}
        return textures

    def main_menu(self):
        choice = self.ui.overlay_menu(self.screen, "Main Menu",
                                      ["Start Game", "Preferences", "Exit", "Debug_Shop"])
        return choice

    def preferences_menu(self):
        clock = pygame.time.Clock()
        font = pygame.font.Font(self.config.fontfile, 28)
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

    def shop_screen(self, _shop=None):
        clock = pygame.time.Clock()
        dt = 1.0 / (self.real_fps if self.real_fps > 50 else self.config.fps)
        self.ui.change_mode("shop")
        if _shop is None:
            shop = Inventory()
            for i in range(3):
                item = random.randint(0, len(self.config.shop_items["card"]) - 1)
                item = self.config.shop_items["card"][item]
                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                    self.config.shop_pos_cards[0] + i * 130, self.config.shop_pos_cards[1])))
            for i in range(2):
                item = random.randint(0, len(self.config.shop_items["buildable"]) - 1)
                item = self.config.shop_items["buildable"][item]
                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                    self.config.shop_pos_objects[0] + i * 130, self.config.shop_pos_objects[1])))
            for i in range(1):
                item = random.randint(0, len(self.config.shop_items["immediate"]) - 1)
                item = self.config.shop_items["immediate"][item]
                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                    self.config.shop_pos_effects[0] + i * 130, self.config.shop_pos_effects[1])))
            for i in range(2):
                item = random.randint(0, len(self.config.shop_items["pack"]) - 1)
                item = self.config.shop_items["pack"][item]
                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                    self.config.shop_pos_packs[0] + i * 130, self.config.shop_pos_packs[1])))
        else:
            shop = _shop

        message = ""
        effects = []
        while True:
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return is not None:
                    if ui_return == 'reroll':
                        if self.money >= self.reroll_cost:
                            self.money -= self.reroll_cost
                            self.reroll_cost *= 2
                            for item in shop.items:
                                if item.properties["type"] in ["card", "buildable"]:
                                    shop.remove_item(item)
                            for i in range(3):
                                item = random.randint(0, len(self.config.shop_items["card"]) - 1)
                                item = self.config.shop_items["card"][item]
                                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                                    self.config.shop_pos_cards[0] + i * 130, self.config.shop_pos_cards[1])))
                            for i in range(2):
                                item = random.randint(0, len(self.config.shop_items["buildable"]) - 1)
                                item = self.config.shop_items["buildable"][item]
                                shop.add_item(InventoryItem(item["name"], properties=item, target_position=(
                                    self.config.shop_pos_objects[0] + i * 130, self.config.shop_pos_objects[1])))
                    else:
                        return ui_return, shop
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "continue", shop
                item = shop.handle_event(event)
                if item is not None:
                    if self.money >= item.properties["price"]:
                        if item.properties["type"] in ["card", "buildable"]:
                            if item.effect["effect"] is not None and item.effect["trigger"] == "passive":
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
                                if item.effect["trigger"] == "passive" and execution \
                                        and item.effect["negative_effect"]:
                                    # Theoretically impossible to have this return False, but just in case be mindful.<-
                                    item.effect["negative_effect"](self, *item.effect["params"])
                        elif item.properties["type"] == "immediate":
                            if item.effect["effect"](self, *item.effect["params"]):
                                effects.append(DisappearingItem(item, 0.1))
                                shop.remove_item(item)
                                self.money -= item.properties["price"]
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                message = f"Effect of {item.name} cannot be applied!"
                        elif item.properties["type"] == "pack":
                            self.money -= item.properties["price"]
                            shop.remove_item(item)
                            if item.properties["kind"] == "oneof":
                                items = []
                                collection = self.config.shop_items[item.properties["item_type"]]
                                for i in range(item.properties["amount"][1]):
                                    pack_item = collection[random.randint(0, len(collection) - 1)]
                                    items.append(pack_item)
                            else:
                                items = []
                            self.ui.open_pack(items, item.pos, item.properties["kind"], item.properties["amount"][0])
                    else:
                        message = f"Not enough money for {item.name}."
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret:
                        item = ret["try_selling"]
                        if item.effect["negative_effect"] is None \
                                or item.effect["negative_effect"](self, *item.effect["params"]):
                            self.money += item.properties["price"] // 2
                            self.inventory.remove_item(item)
                            message = f"Sold {item.name} for {item.properties['price'] // 2}!"

            self.screen.fill((20, 20, 70))

            big_font = pygame.font.Font(self.config.fontfile, 36)
            header = big_font.render("In-Game Shop", True, (255, 255, 255))
            self.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))
            shop.update(dt)
            shop.draw(self.screen)

            self.ui.draw(self.screen)
            self.ui.update(dt)

            if message:
                font = pygame.font.Font(self.config.fontfile, 24)
                msg_text = font.render(message, True, (0, 255, 0))
                self.screen.blit(msg_text, (self.config.shop_pos_effects[0], self.config.shop_pos_effects[1] + 200))

            self.inventory.update(dt)
            self.inventory.draw(self.screen)
            for effect in effects[:]:
                effect.update(dt)
                effect.draw(self.screen)
                if effect.is_dead():
                    effects.remove(effect)
            pygame.display.flip()
            clock.tick(self.real_fps if self.real_fps > 50 else self.config.fps)
            self.real_fps = clock.get_fps()

    def field_modification_screen(self):
        clock = pygame.time.Clock()
        dt = 1.0 / self.config.fps
        self.ui.change_mode("field_modification")

        waiting = True
        while waiting:
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return is not None:
                    return {"continue": "back", "field_setup": "win"}[ui_return]
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = self.ui.overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
                        if choice == "Exit to Main Menu":
                            return 'menu'
                    elif event.key == pygame.K_RETURN:
                        waiting = False
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret:
                        item = ret["try_selling"]
                        if item.effect["negative_effect"] is None \
                                or item.effect["negative_effect"](self, *item.effect["params"]):
                            self.money += item.properties["price"] // 2
                            self.inventory.remove_item(item)
                        else:
                            pass
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        if item.properties["type"] == "buildable":
                            if self.field.place(item):
                                self.inventory.remove_item(item)
                        elif item.properties["type"] == "card":
                            if item.effect["effect"].__module__ == "card_functions.delete_object":
                                if self.field.delete(pygame.mouse.get_pos()):
                                    item.effect["effect"](self, *item.effect["params"])
                                    self.inventory.remove_item(item)
                    if "hovering" in ret:
                        item = ret["hovering"]
                        self.field.hovered_item = item
                    else:
                        self.field.hovered_item = None
                else:
                    self.field.hovered_item = None
            self.screen.fill((20, 20, 70))
            self.ui.draw(self.screen)
            self.ui.update(dt)
            self.field.draw(self.screen)
            self.inventory.update(dt)
            self.inventory.draw(self.screen)
            pygame.display.flip()
            clock.tick(self.config.fps)
        return 'back'

    def round_results_overlay(self, score, min_score):
        extra_orders = int(math.log10(score / min_score)) if score >= min_score else 0
        award = self.config.base_award + extra_orders * self.config.extra_award_per_order \
                                       + self.round_instance.balls_left * self.config.extra_award_per_ball
        if score >= min_score:
            self.money += award

        self.ui.change_mode('results')
        self.ui.draw(self.screen)
        self.ui.update(0)

        font = pygame.font.Font(self.config.fontfile, 36)
        overlay = pygame.Surface((self.config.screen_width - self.config.ui_width, self.config.screen_height))
        overlay.fill((20, 20, 20))
        overlay.set_alpha(200)
        self.screen.blit(overlay, self.config.field_pos)
        if score < min_score:
            result = 'lose'
            texts = [
                "Game Over!",
                f"Score: {int(score) if score == int(score) else score}",
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
                f"Score: {int(score) if score == int(score) else score}",
                f"Required Minimum Score: {min_score}",
                f"Award: {self.config.base_award}",
                f"Total Money: {self.money}",
                "Press ENTER to continue..."
            ]
            if extra_orders * self.config.extra_award_per_order > 0:
                texts.insert(4, f"Award for extra score: {extra_orders * self.config.extra_award_per_order}")
            if self.round_instance.balls_left > 0:
                texts.insert(4, f"Award for balls left: {self.round_instance.balls_left * self.config.extra_award_per_ball}")
            for i, line in enumerate(texts):
                if i == 0:
                    txt = font.render(line, True, (0, 255, 0))
                else:
                    txt = font.render(line, True, (255, 255, 255))
                self.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + self.config.ui_width,
                                       150 + i * 45))
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
            pygame.display.flip()
        return result

    def run(self):
        while True:
            choice = self.main_menu()
            if choice == "Exit":
                break
            if choice == "Preferences":
                self.preferences_menu()
                continue
            if choice == "Debug_Shop":
                self.reroll_cost = self.config.reroll_cost
                self.money = 10000
                self.field = Field(self)
                result = 'win'
                while result in ['win', 'back']:
                    result, shop = self.shop_screen()
                    if result == 'field_setup':
                        result = self.field_modification_screen()
                self.money = 0
                continue
            if choice == "Start Game":
                self.config = Config()
                self.inventory.clear()
                self.field = Field(self)
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
                        self.score_needed = 10 ** (self.round - 2)
                    shop = None
                    self.reroll_cost = self.config.reroll_cost
                    while result in ['win', 'back']:
                        result, shop = self.shop_screen(shop)
                        if result == 'field_setup':
                            result = self.field_modification_screen()
                    if result == 'menu':
                        break
                if result == "exit":
                    break
        pygame.quit()
