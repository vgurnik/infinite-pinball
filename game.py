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
import effects
from misc import scale, mouse_scale


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen_size = self.config.base_resolution
        self.debug_mode = self.config.debug_mode
        self.display = pygame.display.set_mode((self.config.screen_width, self.config.screen_height),
                                               (pygame.FULLSCREEN if self.config.fullscreen else 0))
        self.screen = pygame.Surface(self.config.base_resolution, pygame.SRCALPHA)
        self.textures = self.load_textures()
        self.field = Field(self)
        self.ui = Ui(self)
        pygame.display.set_caption("Infinite Pinball")
        icon = pygame.image.load(Path(__file__).resolve().with_name("assets").joinpath('ball.ico'))
        pygame.display.set_icon(icon)

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
        textures = {"field": pygame.image.load(asset_folder.joinpath("field.bmp")).convert_alpha(),
                    "ramps": pygame.image.load(asset_folder.joinpath("ramps.bmp")).convert_alpha(),
                    "ball": pygame.image.load(asset_folder.joinpath("ball.bmp")).convert_alpha(),
                    "flipper_left": pygame.image.load(asset_folder.joinpath("flipper_left.bmp")).convert_alpha(),
                    "longboi": pygame.image.load(asset_folder.joinpath("longboi.bmp")).convert_alpha(),
                    "pro_flipper": pygame.image.load(asset_folder.joinpath("pro_flipper.bmp")).convert_alpha(),
                    "bumper": pygame.image.load(asset_folder.joinpath("bumper_big.bmp")).convert_alpha(),
                    "bumper_bumped": pygame.image.load(asset_folder.joinpath("bumper_big_bumped.bmp")).convert_alpha(),
                    "bumper_small": pygame.image.load(asset_folder.joinpath("bumper_small.bmp")).convert_alpha(),
                    "bumper_small_bumped": pygame.image.load(asset_folder.joinpath("bumper_small_bumped.bmp")
                                                             ).convert_alpha()}
        return textures

    def callback(self, event, arbiter=None):
        for card in self.inventory.items:
            for effect in card.effects:
                if effect["trigger"] == event:
                    effects.call(effect, self, arbiter)
        for card in self.round_instance.applied_cards.items[:]:
            for effect in card.effects:
                if effect["trigger"] == event and effect["duration"] > 0:
                    effects.call(effect, self, arbiter)

    def main_menu(self):
        if self.debug_mode:
            choice = self.ui.overlay_menu(self.screen, "Main Menu",
                                      ["Start Game", "Preferences", "Exit", "Debug_Shop"])
        else:
            choice = self.ui.overlay_menu(self.screen, "Main Menu",
                                      ["Start Game", "Preferences", "Exit"])
        return choice

    def preferences_menu(self):
        clock = pygame.time.Clock()
        font = pygame.font.Font(self.config.fontfile, 28)
        bigger_font = pygame.font.Font(self.config.fontfile, 30)
        pref_running = True
        resolution_index = self.config.resolutions.index(self.screen_size)
        options = ["resolution", "fullscreen", "debug_mode", "back"]
        selected_option = 0

        while pref_running:
            reload = False
            self.screen.fill((20, 20, 70))
            pref_text = font.render("Preferences", True, (255, 255, 255))
            resolution_text = font.render(f"Resolution: {self.config.resolutions[resolution_index]}", True,
                                          (255, 255, 255))
            fullscreen_text = font.render(f"Fullscreen: {'On' if self.config.fullscreen else 'Off'}", True,
                                          (255, 255, 255))
            debug_text = font.render(f"Debug Mode: {'On' if self.debug_mode else 'Off'}", True, (255, 255, 255))
            back_text = font.render("Go back", True, (255, 255, 255))
            match selected_option:
                case 0:
                    resolution_text = bigger_font.render(f"Resolution: {self.config.resolutions[resolution_index]}",
                                                         True, (255, 255, 0))
                case 1:
                    fullscreen_text = bigger_font.render(f"Fullscreen: {'On' if self.config.fullscreen else 'Off'}",
                                                         True, (255, 255, 0))
                case 2:
                    debug_text = bigger_font.render(f"Debug Mode: {'On' if self.debug_mode else 'Off'}", True,
                                                    (255, 255, 0))
                case 3:
                    back_text = bigger_font.render("Go back", True, (255, 255, 0))

            self.screen.blit(pref_text, (self.config.screen_width // 2 - pref_text.get_width() // 2, 100))
            self.screen.blit(resolution_text, (self.config.screen_width // 2 - resolution_text.get_width() // 2, 200))
            self.screen.blit(fullscreen_text, (self.config.screen_width // 2 - fullscreen_text.get_width() // 2, 250))
            self.screen.blit(debug_text, (self.config.screen_width // 2 - debug_text.get_width() // 2, 300))
            self.screen.blit(back_text, (self.config.screen_width // 2 - back_text.get_width() // 2, 350))

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_option = (selected_option - 1) % len(options)
                        elif event.key == pygame.K_DOWN:
                            selected_option = (selected_option + 1) % len(options)
                        elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                            match options[selected_option]:
                                case "resolution":
                                    resolution_index = (resolution_index + (2 * (event.key == pygame.K_LEFT) - 1)) %\
                                                       len(self.config.resolutions)
                                    self.screen_size = self.config.resolutions[resolution_index]
                                    reload = True
                                case "fullscreen":
                                    self.config.fullscreen = not self.config.fullscreen
                                    reload = True
                                case "debug_mode":
                                    self.debug_mode = not self.debug_mode
                                case "back":
                                    pref_running = False
                        elif event.key == pygame.K_ESCAPE or (event.key == pygame.K_RETURN and
                                                              options[selected_option] == "back"):
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
                                self.screen_size = self.config.resolutions[resolution_index]
                                reload = True
                            case "fullscreen":
                                self.config.fullscreen = not self.config.fullscreen
                                reload = True
                            case "debug_mode":
                                self.debug_mode = not self.debug_mode
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
                self.display = pygame.display.set_mode(self.screen_size, (
                    pygame.FULLSCREEN if self.config.fullscreen else 0))
            self.display.blit(scale(self.screen, self.screen_size), (0, 0))
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
        visual_effects = []
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
                            execution = item.add(self)
                            addition = self.inventory.add_item(item)
                            if execution and addition:
                                self.money -= item.properties["price"]
                                shop.remove_item(item)
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                if not addition:
                                    message = "Not enough inventory space!"
                                else:
                                    message = f"{item.name} cannot be applied!"
                                if execution and not item.sell(self):
                                    raise RuntimeError("Item could not be added, but effects could not be recalled")
                        elif item.properties["type"] == "immediate":
                            if item.use(self):
                                visual_effects.append(DisappearingItem(item, 0.1))
                                shop.remove_item(item)
                                self.money -= item.properties["price"]
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                message = f"{item.name} cannot be applied!"
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
                                items = []      # TODO: other kinds of pack
                            self.ui.open_pack(items, item.pos, item.properties["kind"], item.properties["amount"][0])
                    else:
                        message = f"Not enough money for {item.name}."
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and ret["try_selling"].sell(self):
                        self.money += ret["try_selling"].properties["price"] // 2
                        self.inventory.remove_item(ret["try_selling"])
                        message = f"Sold {ret['try_selling'].name} for {ret['try_selling'].properties['price'] // 2}!"

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

            for effect in visual_effects[:]:
                effect.update(dt)
                effect.draw(self.screen)
                if effect.is_dead():
                    visual_effects.remove(effect)

            self.display.blit(scale(self.screen, self.screen_size), (0, 0))
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
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = self.ui.overlay_menu(self.screen, "Paused", ["Resume", "Exit to Main Menu"])
                            if choice == "Exit to Main Menu":
                                return 'menu'
                        elif event.key == pygame.K_RETURN:
                            waiting = False
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and ret["try_selling"].sell(self):
                        self.money += ret["try_selling"].properties["price"] // 2
                        self.inventory.remove_item(ret["try_selling"])
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        if item.properties["type"] == "buildable" and self.field.place(item):
                            self.inventory.remove_item(item)
                        elif item.properties["type"] == "card":
                            for effect in item.effects:
                                if effect["effect_name"] == "delete_object" and\
                                        self.field.delete(mouse_scale(pygame.mouse.get_pos())):
                                    item.use(self)      # TODO: if usage is not allowed, place object back
                                    self.inventory.remove_item(item)
                                    break
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
            self.display.blit(scale(self.screen, self.screen_size), (0, 0))
            pygame.display.flip()
            clock.tick(self.config.fps)
        return 'back'

    def round_results_overlay(self, score, min_score):
        extra_orders = int(math.log2(score / min_score)) if score >= min_score else 0
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
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.MOUSEBUTTONDOWN:
                        waiting = False
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting = False
            self.display.blit(scale(self.screen, self.screen_size), (0, 0))
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
