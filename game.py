import sys
import math
from pathlib import Path
from json import load

import pygame

from utils.misc import load_textures, choose_items
from utils.textures import mouse_scale, display_screen
from utils.text import format_text, loc
from config import Config
from field import Field
from ui import Ui
from round import PinballRound
from inventory import Inventory, PlayerInventory, InventoryItem
from game_effects import DisappearingItem
from game_objects import GameObject
import effects


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen_size = self.config.base_resolution
        self.debug_mode = self.config.debug_mode
        self.display = pygame.display.set_mode((self.config.screen_width, self.config.screen_height),
                                               (pygame.FULLSCREEN if self.config.fullscreen else 0))
        self.screen = pygame.Surface(self.config.base_resolution, pygame.SRCALPHA)
        with open(Path(__file__).resolve().with_name("assets").joinpath('config/sprites.json')) as file:
            sprite_config = load(file)
        self.textures = load_textures(sprite_config)
        self.field = Field(self)
        self.ui = Ui(self)
        pygame.display.set_caption("Infinite Pinball")
        icon = pygame.image.load(Path(__file__).resolve().with_name("assets").joinpath('textures/ball.ico'))
        pygame.display.set_icon(icon)

        self.reroll_cost = self.config.reroll_start_cost
        self.money = 0
        self.round = 0
        self.score_needed = self.config.min_score[self.round]
        self.inventory = PlayerInventory(self)
        self.round_instance = PinballRound(self)
        self.immediate = {}
        self.flags = self.config.start_flags
        self.real_fps = 0

    def callback(self, event, arbiters=None):
        for card in self.inventory.items:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "passive":
                    if arbiters is not None:
                        effects.call(effect, self, arbiters)
                    else:
                        effects.call(effect, self)
        for card in self.round_instance.applied_cards.items[:]:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "active" and effect["duration"] != 0:
                    if arbiters is not None:
                        effects.call(effect, self, arbiters)
                    else:
                        effects.call(effect, self)
        if arbiters is not None:
            for arb in arbiters:
                if issubclass(arb.__class__, GameObject):
                    if arb.cooldown == 0:
                        for effect in arb.effects:
                            if effect["trigger"] == event:
                                effects.call(effect, self, arbiters)
                                arb.cooldown = max(arb.cooldown, effect["cooldown"])
                    if arb.shape.type != 'ball' and arb.cooldown > 0:
                        arb.cooldown_timer = arb.cooldown

    def shop_screen(self, _shop=None):
        clock = pygame.time.Clock()
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)
        self.ui.change_mode("shop")
        if _shop is None:
            shop = Inventory(self.config)
            items = choose_items(self, 3, self.config.shop_items["card"], self.config.rarities["card"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_cards[0] + i * 130,
                                                             self.config.shop_pos_cards[1])))
            items = choose_items(self, 2, self.config.shop_items["buildable"], self.config.rarities["buildable"])
            for i, item in enumerate(items):
                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get("buildable_pack"),
                                            target_position=(self.config.shop_pos_objects[0] + i * 130,
                                                             self.config.shop_pos_objects[1]),
                              for_buildable=self.textures.get(obj_def["texture"])))
            items = choose_items(self, 1, self.config.shop_items["immediate"], self.config.rarities["immediate"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_effects[0] + i * 130,
                                                             self.config.shop_pos_effects[1])))
            items = choose_items(self, 2, self.config.shop_items["pack"], self.config.rarities["pack"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_packs[0] + i * 130,
                                                             self.config.shop_pos_packs[1]), card_size=(123, 163)))
            self.callback("shop_create", arbiters=[shop])
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
                            if self.flags['reroll_mode'] == 'm':
                                self.reroll_cost *= self.config.reroll_next
                            else:
                                self.reroll_cost += self.config.reroll_start_cost
                            for item in shop.items[:]:
                                if item.properties["type"] in ["card", "buildable"]:
                                    shop.remove_item(item)
                            items = choose_items(self, 3, self.config.shop_items["card"], self.config.rarities["card"])
                            for i, item in enumerate(items):
                                shop.add_item(InventoryItem(properties=item,
                                                            sprite=self.textures.get(item.get("sprite")),
                                                            target_position=(self.config.shop_pos_cards[0] + i * 130,
                                                                             self.config.shop_pos_cards[1])))
                            items = choose_items(self, 2, self.config.shop_items["buildable"],
                                                 self.config.rarities["buildable"])
                            for i, item in enumerate(items):
                                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get("buildable_pack"),
                                                            target_position=(self.config.shop_pos_objects[0] + i * 130,
                                                                             self.config.shop_pos_objects[1]),
                                                            for_buildable=self.textures.get(obj_def["texture"])))
                    else:
                        return ui_return, shop
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = self.ui.overlay_menu(self.screen, "ui.text.pause",
                                                      ["ui.button.resume", "ui.button.settings", "ui.button.main"])
                        if choice == "ui.button.main":
                            return 'menu', shop
                        if choice == "ui.button.settings":
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
                                message = format_text("ui.message.purchased", self.config.lang, item.name,
                                                      item.properties['buy_price'])
                            else:
                                message = loc("ui.message.not_enough_space", self.config.lang)
                        elif item.properties["type"] == "immediate":
                            if item.use(self):
                                visual_effects.append(DisappearingItem(item, 0.3))
                                shop.remove_item(item)
                                self.money -= item.properties["buy_price"]
                                message = format_text("ui.message.purchased", self.config.lang, item.name,
                                                      item.properties['buy_price'])
                            else:
                                message = format_text("ui.message.not_purchased", self.config.lang, item.name)
                        elif item.properties["type"] == "pack":
                            self.money -= item.properties["buy_price"]
                            shop.remove_item(item)
                            if item.properties["kind"] == "oneof":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                items = choose_items(self, item.properties["amount"][1], pool,
                                                     self.config.rarities[item.properties["item_type"]])
                            elif item.properties["kind"] == "all":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                positive = choose_items(self, item.properties["amount"][1], pool,
                                                        {"epic": {"value": 1}})
                                negative = choose_items(self, item.properties["amount"][2], pool,
                                                        {"negative": {"value": 1}})
                                items = positive + negative
                            else:
                                items = []
                            self.ui.open_pack(items, item.pos, item.properties["kind"], item.properties["amount"][0],
                                              self.textures.get(item.properties["sprite"]+"_opening"))
                            _ = clock.tick(self.config.fps)
                    else:
                        message = format_text("ui.message.not_enough_money", self.config.lang, item.name)
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        visual_effects.append(DisappearingItem(ret["try_selling"], 0.1))
                        self.money += ret["try_selling"].properties["price"]
                        message = format_text("ui.message.sold", self.config.lang, ret['try_selling'].name,
                                              ret['try_selling'].properties['price'])
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
            header = big_font.render(loc("ui.text.shop", self.config.lang), True, (255, 255, 255))
            self.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))

            if message:
                font = pygame.font.Font(self.config.fontfile, 24)
                msg_text = font.render(message, True, (0, 255, 0))
                self.screen.blit(msg_text, (self.config.shop_pos_effects[0], self.config.shop_pos_effects[1] + 200))

            shop.update(dt)
            shop.draw(self.screen)

            self.ui.draw(self.screen)
            self.ui.update(dt)

            self.inventory.update(dt)
            self.inventory.draw(self.screen)

            for effect in visual_effects[:]:
                effect.update(dt)
                effect.draw(self.screen)
                if effect.is_dead():
                    visual_effects.remove(effect)

            display_screen(self.display, self.screen, self.screen_size)
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
                            choice = self.ui.overlay_menu(self.screen, "ui.text.pause", [
                                "ui.button.resume", "ui.button.settings", "ui.button.main"])
                            if choice == "ui.button.main":
                                return 'menu'
                            if choice == "ui.button.settings":
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
                                if effect["name"] == "delete_object" and\
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
                loc("ui.message.lose", self.config.lang),
                format_text("ui.message.score", self.config.lang, score, min_score),
                format_text("ui.message.money", self.config.lang, self.money),
                loc("ui.message.return_lose", self.config.lang)
            ]
            for i, line in enumerate(texts):
                txt = font.render(line, True, (255, 100, 100))
                self.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + self.config.ui_width,
                                       150 + i * 45))
        else:
            result = 'win'
            texts = [
                loc("ui.message.complete", self.config.lang),
                format_text("ui.message.score", self.config.lang, score, min_score),
                format_text("ui.message.reward", self.config.lang, self.config.base_award),
                format_text("ui.message.money", self.config.lang, self.money),
                loc("ui.message.go_next", self.config.lang)
            ]
            if interest_reward > 0:
                texts.insert(3, format_text("ui.message.interest", self.config.lang,
                                            round(self.config.interest_rate * 100), interest_reward,
                                            self.config.interest_cap))
            if order_reward > 0:
                texts.insert(3, format_text("ui.message.score_reward", self.config.lang, order_reward))
            if ball_reward > 0:
                texts.insert(3, format_text("ui.message.ball_reward", self.config.lang, ball_reward))
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
            if self.debug_mode:
                choice = self.ui.overlay_menu(self.screen, "ui.text.main",
                                              ["ui.button.start", "ui.button.settings", "ui.button.exit", "Debug_Shop"])
            else:
                choice = self.ui.overlay_menu(self.screen, "ui.text.main",
                                              ["ui.button.start", "ui.button.settings", "ui.button.exit"])
            if choice == "ui.button.exit":
                break
            if choice == "ui.button.settings":
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
            if choice == "ui.button.start":
                self.config = Config()
                self.inventory = PlayerInventory(self)
                self.field = Field(self)
                self.flags = self.config.start_flags
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
                    self.reroll_cost = self.config.reroll_start_cost
                    while result in ['win', 'back']:
                        result, shop = self.shop_screen(shop)
                        if result == 'field_setup':
                            result = self.field_modification_screen()
                    if result == 'menu':
                        break
                if result == "exit":
                    break
        pygame.quit()
