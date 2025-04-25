import sys
import math
from pathlib import Path
import pygame

import misc
from config import Config
from field import Field
from ui import Ui
from round import PinballRound
from inventory import Inventory, PlayerInventory, InventoryItem
from game_effects import DisappearingItem
import effects
from misc import mouse_scale, display_screen
import sprites


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
        self.immediate = {}
        self.flags = {"charge_bonus": False}
        self.real_fps = 0

    @staticmethod
    def load_textures():
        # Load textures
        simple_sprites = ["field", "ramps"]
        textures = {sprite: sprites.Sprite(sprite+'.bmp') for sprite in simple_sprites}
        # Load animated textures
        textures["bumper"] = sprites.AnimatedSprite("bumper_big.bmp", uvs=[(0, 0), (32, 0)], wh=(32, 32))
        textures["bumper_small"] = sprites.AnimatedSprite("bumper_small.bmp", uvs=[(0, 0), (16, 0)], wh=(16, 16))
        textures["bumper_money"] = sprites.AnimatedSprite("bumper_money.bmp", uvs=[(0, 0), (16, 0)], wh=(16, 16))
        textures["flipper"] = sprites.AnimatedSprite("flipper.bmp", uvs=[(0, 0), (0, 10)], wh=(40, 10))
        textures["longboi"] = sprites.AnimatedSprite("longboi.bmp", uvs=[(0, 0), (0, 10)], wh=(45, 10))
        textures["pro_flipper"] = sprites.AnimatedSprite("pro_flipper.bmp", uvs=[(0, 0), (0, 10)], wh=(30, 10))

        textures["charge_indicator"] = sprites.AnimatedSprite("charge_indicator.bmp",
                                                              uvs=[(0, 0), (0, 10)], wh=(30, 10))
        textures["shield"] = sprites.AnimatedSprite("shield.bmp", uvs=[(0, 0), (0, 30), (0, 60)], wh=(200, 30), ft=0.1)
        textures["spring"] = sprites.AnimatedSprite("spring.bmp", uvs=[(0, 0), (40, 0), (80, 0), (120, 0),
                                                                       (160, 0), (200, 0), (240, 0)], wh=(40, 60))
        cards_spritesheet = sprites.Sprite("cards.bmp")
        textures["buildable_pack"] = sprites.Sprite(cards_spritesheet, (0, 0), (60, 80))
        textures["slowmo"] = sprites.Sprite(cards_spritesheet, (60, 0), (60, 80))
        textures["doublescore"] = sprites.Sprite(cards_spritesheet, (120, 0), (60, 80))
        textures["quintupler"] = sprites.Sprite(cards_spritesheet, (180, 0), (60, 80))
        textures["overload"] = sprites.Sprite(cards_spritesheet, (240, 0), (60, 80))
        textures["ticket"] = sprites.Sprite(cards_spritesheet, (300, 0), (60, 80))
        textures["wrench"] = sprites.Sprite(cards_spritesheet, (360, 0), (60, 80))
        textures["cardholder"] = sprites.Sprite(cards_spritesheet, (420, 0), (60, 80))
        textures["shield_card"] = sprites.Sprite(cards_spritesheet, (480, 0), (60, 80))

        textures["+ball"] = sprites.Sprite(cards_spritesheet, (0, 80), (60, 80))
        textures["backpack"] = sprites.Sprite(cards_spritesheet, (60, 80), (60, 80))
        textures["launcher"] = sprites.Sprite(cards_spritesheet, (60, 160), (60, 80))

        textures["slimeball_card"] = sprites.Sprite(cards_spritesheet, (120, 80), (60, 80))
        textures["agile_card"] = sprites.Sprite(cards_spritesheet, (180, 80), (60, 80))
        textures["bumperball_card"] = sprites.Sprite(cards_spritesheet, (240, 80), (60, 80))
        textures["goldball_card"] = sprites.Sprite(cards_spritesheet, (300, 80), (60, 80))
        textures["sellball"] = sprites.Sprite(cards_spritesheet, (360, 80), (60, 80))
        textures["multiball"] = sprites.Sprite(cards_spritesheet, (420, 80), (60, 80))
        textures["bonus_ball"] = sprites.Sprite(cards_spritesheet, (480, 80), (60, 80))

        textures["5xscore"] = sprites.Sprite(cards_spritesheet, (120, 160), (60, 80))
        textures["platinum"] = sprites.Sprite(cards_spritesheet, (180, 160), (60, 80))
        textures["luckyball_card"] = sprites.Sprite(cards_spritesheet, (240, 160), (60, 80))

        ball_spritesheet = sprites.Sprite("balls.bmp")
        textures["ball"] = sprites.Sprite(ball_spritesheet, (0, 0), (16, 16))
        textures["goldball"] = sprites.Sprite(ball_spritesheet, (16, 0), (16, 16))
        textures["slimeball"] = sprites.Sprite(ball_spritesheet, (0, 16), (16, 16))
        textures["luckyball"] = sprites.Sprite(ball_spritesheet, (16, 16), (16, 16))
        return textures

    def callback(self, event, arbiter=None, arbiter_cooldown=0):
        for card in self.inventory.items:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "passive":
                    if arbiter is not None:
                        effects.call(effect, self, arbiter)
                    else:
                        effects.call(effect, self)
        for card in self.round_instance.applied_cards.items[:]:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "active" and effect["duration"] != 0:
                    if arbiter is not None:
                        effects.call(effect, self, arbiter)
                    else:
                        effects.call(effect, self)
        if arbiter is not None and arbiter_cooldown == 0:
            for effect in arbiter.effects:
                if effect["trigger"] == event:
                    effects.call(effect, self, arbiter)

    def main_menu(self):
        if self.debug_mode:
            choice = self.ui.overlay_menu(self.screen, "Main Menu", ["Start Game", "Settings", "Exit", "Debug_Shop"])
        else:
            choice = self.ui.overlay_menu(self.screen, "Main Menu", ["Start Game", "Settings", "Exit"])
        return choice

    def shop_screen(self, _shop=None):
        clock = pygame.time.Clock()
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)
        self.ui.change_mode("shop")
        if _shop is None:
            shop = Inventory(self.config)
            items = misc.choose_items(self, 3, self.config.shop_items["card"], self.config.rarities["card"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get(item.get("sprite")), properties=item,
                                            target_position=(self.config.shop_pos_cards[0] + i * 130,
                                                             self.config.shop_pos_cards[1])))
            items = misc.choose_items(self, 2, self.config.shop_items["buildable"], self.config.rarities["buildable"])
            for i, item in enumerate(items):
                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get("buildable_pack"), properties=item,
                                            target_position=(self.config.shop_pos_objects[0] + i * 130,
                                                             self.config.shop_pos_objects[1]),
                              for_buildable=self.textures.get(obj_def["texture"])))
            items = misc.choose_items(self, 1, self.config.shop_items["immediate"], self.config.rarities["immediate"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get(item.get("sprite")), properties=item,
                                            target_position=(self.config.shop_pos_effects[0] + i * 130,
                                                             self.config.shop_pos_effects[1])))
            items = misc.choose_items(self, 2, self.config.shop_items["pack"], self.config.rarities["pack"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get(item.get("sprite")), properties=item,
                                            target_position=(self.config.shop_pos_packs[0] + i * 130,
                                                             self.config.shop_pos_packs[1])))
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
                            for item in shop.items[:]:
                                if item.properties["type"] in ["card", "buildable"]:
                                    shop.remove_item(item)
                            items = misc.choose_items(self, 3, self.config.shop_items["card"], self.config.rarities["card"])
                            for i, item in enumerate(items):
                                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get(item.get("sprite")),
                                                            properties=item, target_position=(
                                        self.config.shop_pos_cards[0] + i * 130, self.config.shop_pos_cards[1])))
                            items = misc.choose_items(self, 2, self.config.shop_items["buildable"],
                                                      self.config.rarities["buildable"])
                            for i, item in enumerate(items):
                                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                                shop.add_item(InventoryItem(item["name"], sprite=self.textures.get("buildable_pack"),
                                                            properties=item, target_position=(
                                        self.config.shop_pos_objects[0] + i * 130, self.config.shop_pos_objects[1]),
                                                            for_buildable=self.textures.get(obj_def["texture"])))
                    else:
                        return ui_return, shop
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = self.ui.overlay_menu(self.screen, "Paused", [
                            "Resume", "Settings", "Exit to Main Menu"])
                        if choice == "Exit to Main Menu":
                            return 'menu', shop
                        if choice == "Settings":
                            self.ui.settings_menu()
                        _ = clock.tick(self.config.fps)
                    elif event.key == pygame.K_RETURN:
                        return "continue", shop
                item = shop.handle_event(event)
                if item is not None:
                    if self.money >= item.properties["buy_price"]:
                        if item.properties["type"] in ["card", "buildable"]:
                            if self.inventory.add_item(item):
                                self.money -= item.properties["buy_price"]
                                shop.remove_item(item)
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                message = "Not enough inventory space!"
                        elif item.properties["type"] == "immediate":
                            if item.use(self):
                                visual_effects.append(DisappearingItem(item, 0.3))
                                shop.remove_item(item)
                                self.money -= item.properties["buy_price"]
                                message = f"Purchased {item.name} for {item.properties['price']}!"
                            else:
                                message = f"{item.name} cannot be applied!"
                        elif item.properties["type"] == "pack":
                            self.money -= item.properties["buy_price"]
                            shop.remove_item(item)
                            if item.properties["kind"] == "oneof":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                items = misc.choose_items(self, item.properties["amount"][1], pool,
                                                          self.config.rarities[item.properties["item_type"]])
                            elif item.properties["kind"] == "all":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                positive = misc.choose_items(self, item.properties["amount"][1], pool,
                                                             {"epic": {"value": 1}})
                                negative = misc.choose_items(self, item.properties["amount"][2], pool,
                                                             {"negative": {"value": 1}})
                                items = positive + negative
                            else:
                                items = []
                            self.ui.open_pack(items, item.pos, item.properties["kind"], item.properties["amount"][0])
                            _ = clock.tick(self.config.fps)
                    else:
                        message = f"Not enough money for {item.name}."
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        visual_effects.append(DisappearingItem(ret["try_selling"], 0.1))
                        self.money += ret["try_selling"].properties["price"]
                        message = f"Sold {ret['try_selling'].name} for {ret['try_selling'].properties['price']}!"
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        allow = False
                        lasting = False
                        for effect in item.effects:
                            if effect["usage"] == "active":
                                allow = True
                            if effect["duration"] != 0:
                                lasting = True
                        if allow and not lasting and item.use(self):
                            self.inventory.remove_item(item)
                            visual_effects.append(DisappearingItem(item, 0.1))

            self.screen.fill((20, 20, 70))

            big_font = pygame.font.Font(self.config.fontfile, 36)
            header = big_font.render("Game Shop", True, (255, 255, 255))
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

            display_screen(self.display, self.screen, self.screen_size)
            pygame.display.flip()
            dt = clock.tick(self.config.fps) / 1000
            self.real_fps = clock.get_fps()

    def field_modification_screen(self):
        clock = pygame.time.Clock()
        self.ui.change_mode("field_modification")
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                ui_return = self.ui.handle_event(event)
                if ui_return is not None:
                    return {"continue": "continue", "field_setup": "back"}[ui_return]
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = self.ui.overlay_menu(self.screen, "Paused", [
                                "Resume", "Settings", "Exit to Main Menu"])
                            if choice == "Exit to Main Menu":
                                return 'menu'
                            if choice == "Settings":
                                self.ui.settings_menu()
                            _ = clock.tick(self.config.fps)
                        elif event.key == pygame.K_RETURN:
                            waiting = False
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        self.money += ret["try_selling"].properties["price"] // 2
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        if item.properties["type"] == "buildable" and self.field.place(item):
                            self.inventory.remove_item(item)    # TODO: if placing is not allowed, remove object
                        elif item.properties["type"] == "card":
                            for effect in item.effects:
                                if effect["effect_name"] == "delete_object" and\
                                        self.field.delete(mouse_scale(pygame.mouse.get_pos())):
                                    item.use(self)              # TODO: if usage is not allowed, place object back
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
            self.screen.blit(self.field.draw(), self.field.position)
            self.inventory.update(dt)
            self.inventory.draw(self.screen)
            display_screen(self.display, self.screen, self.screen_size)
            dt = clock.tick(self.config.fps) / 1000
            self.real_fps = clock.get_fps()
        return 'back'

    def round_results_overlay(self, score, min_score):
        self.immediate['interest'] = 0
        self.immediate['interest_cap'] = 0
        self.immediate['$per_order'] = 0
        self.immediate['$per_ball'] = 0
        self.callback("round_win")
        extra_orders = int(math.log2(score / min_score)) if score >= min_score else 0
        order_reward = extra_orders * (self.config.extra_award_per_order + self.immediate['$per_order'])
        charged_ball = 0
        if len(self.round_instance.active_balls) > 0 and not self.round_instance.ball_launched:
            charged_ball += 1
        ball_reward = (len(self.round_instance.ball_queue) + charged_ball) * (
                self.config.extra_award_per_ball + self.immediate['$per_ball'])
        interest_reward = min(int((self.config.interest_rate + self.immediate['interest']) * self.money), (
                self.config.interest_cap + self.immediate['interest_cap']))
        if score >= min_score:
            self.money += self.config.base_award + order_reward + ball_reward + interest_reward

        self.screen.fill((20, 20, 70))
        self.ui.change_mode('results')
        self.ui.draw(self.screen)
        self.ui.update(0)
        self.screen.blit(self.field.draw(), self.field.position)

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
                "Press ENTER or click to return to main menu"
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
                "Press ENTER or click to continue..."
            ]
            if interest_reward > 0:
                texts.insert(4, f"{round(self.config.interest_rate * 100)}% interest: {interest_reward} (max {self.config.interest_cap})")
            if order_reward > 0:
                texts.insert(4, f"Award for extra score: {order_reward}")
            if ball_reward > 0:
                texts.insert(4, f"Award for balls left: {ball_reward}")
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
            display_screen(self.display, self.screen, self.screen_size)
        return result

    def run(self):
        while True:
            choice = self.main_menu()
            if choice == "Exit":
                break
            if choice == "Settings":
                self.ui.settings_menu()
                continue
            if choice == "Debug_Shop":
                self.reroll_cost = 0
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
                self.inventory = PlayerInventory(self)
                self.field = Field(self)
                self.flags = {"charge_bonus": False}
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
                    if self.round < len(self.config.min_score):
                        self.score_needed = self.config.min_score[self.round]
                    else:
                        self.score_needed = self.config.min_score[-1] * 10 ** (self.round -
                                                                               len(self.config.min_score) + 1)
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
