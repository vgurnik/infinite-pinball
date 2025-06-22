import sys
import json
import pygame

from utils.misc import load_textures, choose_items
from utils.textures import mouse_scale, display_screen
from utils.text import format_text, loc
from config import Config, asset_path, fontfile
from field import Field
from ui import Ui
from round import PinballRound
from sound_engine import SoundEngine
import screens
from inventory import Inventory, PlayerInventory, InventoryItem
from game_effects import DisappearingItem
from game_objects import GameObject
import effects
import save_system


class PinballGame:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.screen_size = self.config.base_resolution
        self.debug_mode = self.config.debug_mode
        save_system.load_pref(self)
        self.display = pygame.display.set_mode((self.config.screen_width, self.config.screen_height),
                                               (pygame.FULLSCREEN if self.config.fullscreen else 0))
        self.screen = pygame.Surface(self.config.base_resolution, pygame.SRCALPHA)

        with open(asset_path.joinpath('config/sprites.json')) as file:
            sprite_conf = json.load(file)
        self.textures = load_textures(sprite_conf)
        pygame.display.set_caption("Infinite Pinball")
        icon = pygame.image.load(asset_path.joinpath('textures/ball.ico'))
        pygame.display.set_icon(icon)

        self.flags = self.config.start_flags
        self.reroll_cost = self.flags['reroll_start_cost']
        self.money = 0
        self.round = 0
        self.score_needed = self.config.min_score[self.round]
        self.immediate = {}
        self.real_fps = 0
        self.cont = False
        self.ui = None
        self.inventory = None
        self.field = None
        self.round_instance = None
        self.sound = SoundEngine()

    def callback(self, event, arbiters=None):
        for card in self.inventory.items:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "passive":
                    effects.call(effect, arbiters=arbiters, card=card)
        for card in self.round_instance.applied_cards.items[:]:
            for effect in card.effects:
                if effect["trigger"] == event and effect["usage"] == "active" and effect["duration"] != 0:
                    effects.call(effect, arbiters=arbiters, card=card)
        if arbiters is None:
            return
        for arb in arbiters:
            if issubclass(arb.__class__, GameObject):
                if arb.cooldown == 0:
                    for effect in arb.effects:
                        if effect["trigger"] == event:
                            effects.call(effect, arbiters)
                            arb.cooldown = max(arb.cooldown, effect["cooldown"])
                if arb.cooldown > 0:
                    arb.cooldown_timer = arb.cooldown

    def shop_screen(self, _shop=None):
        clock = pygame.time.Clock()
        dt = 1.0 / (self.real_fps if self.real_fps > 1 else self.config.fps)
        self.ui.change_mode("shop")
        shop_size = self.config.shop_size
        if _shop is None:
            shop = Inventory()
            items = choose_items(shop_size[1], self.config.shop_items["card"], self.config.rarities["card"],
                                 exclude_pool=self.inventory.collect_names())
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_cards[0] + (
                                                    2 * i - shop_size[1]) * 65, self.config.shop_pos_cards[1])))
            items = choose_items(shop_size[0], self.config.shop_items["buildable"], self.config.rarities["buildable"])
            for i, item in enumerate(items):
                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get("buildable_pack"),
                                            target_position=(self.config.shop_pos_objects[0] + (
                                                    2 * i - shop_size[0]) * 65, self.config.shop_pos_objects[1]),
                              for_buildable=self.textures.get(obj_def["texture"])))
            items = choose_items(shop_size[2], self.config.shop_items["immediate"], self.config.rarities["immediate"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_effects[0] + (
                                                    2 * i - shop_size[2]) * 65, self.config.shop_pos_effects[1])))
            items = choose_items(shop_size[3], self.config.shop_items["pack"], self.config.rarities["pack"])
            for i, item in enumerate(items):
                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(item.get("sprite")),
                                            target_position=(self.config.shop_pos_packs[0] + (
                                                    2 * i - shop_size[3]) * 65, self.config.shop_pos_packs[1]),
                                            card_size=(123, 163)))
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
                                self.reroll_cost += self.flags["reroll_start_cost"]
                            for item in shop.items[:]:
                                if item.properties["type"] in ["card", "buildable"]:
                                    shop.remove_item(item)
                            items = choose_items(shop_size[1], self.config.shop_items["card"],
                                                 self.config.rarities["card"],
                                                 exclude_pool=self.inventory.collect_names())
                            for i, item in enumerate(items):
                                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get(
                                    item.get("sprite")), target_position=(self.config.shop_pos_cards[0] + (
                                                    2 * i - shop_size[1]) * 65, self.config.shop_pos_cards[1])))
                            items = choose_items(shop_size[0], self.config.shop_items["buildable"],
                                                 self.config.rarities["buildable"])
                            for i, item in enumerate(items):
                                obj_def = self.config.objects_settings[item["object_type"]][item["class"]]
                                shop.add_item(InventoryItem(properties=item, sprite=self.textures.get("buildable_pack"),
                                                            target_position=(self.config.shop_pos_objects[0] +
                                                                             (2 * i - shop_size[0]) * 65,
                                                                             self.config.shop_pos_objects[1]),
                                                            for_buildable=self.textures.get(obj_def["texture"])))
                            self.callback("reroll", arbiters=[shop])
                    else:
                        save_system.save()
                        return ui_return, shop
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = screens.overlay_menu(self.screen, "ui.text.pause",
                                                      ["ui.button.resume", "ui.button.settings", "ui.button.main"])
                        if choice == "ui.button.main":
                            save_system.save()
                            return 'menu', shop
                        if choice == "ui.button.settings":
                            screens.settings_menu()
                        _ = clock.tick(self.config.fps)
                    elif event.key == pygame.K_RETURN:
                        save_system.save()
                        return "continue", shop
                item = shop.handle_event(event)
                if item is not None:
                    success = True
                    if self.money >= item.properties["buy_price"]:
                        if item.properties["type"] in ["card", "buildable"]:
                            if self.inventory.add_item(item):
                                self.money -= item.properties["buy_price"]
                                shop.remove_item(item)
                                message = format_text("ui.message.purchased", item.name, item.properties['buy_price'])
                            else:
                                message = loc("ui.message.not_enough_space")
                                success = False
                        elif item.properties["type"] == "immediate":
                            if item.use():
                                visual_effects.append(DisappearingItem(item, 0.3))
                                shop.remove_item(item)
                                self.money -= item.properties["buy_price"]
                                message = format_text("ui.message.purchased", item.name, item.properties['buy_price'])
                            else:
                                message = format_text("ui.message.not_purchased", item.name)
                                success = False
                        elif item.properties["type"] == "pack":
                            self.money -= item.properties["buy_price"]
                            shop.remove_item(item)
                            if item.properties["kind"] == "oneof":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                items = choose_items(item.properties["amount"][1], pool,
                                                     self.config.rarities[item.properties["item_type"]],
                                                     exclude_pool=self.inventory.collect_names() + shop.collect_names())
                            elif item.properties["kind"] == "all":
                                pool = self.config.shop_items[item.properties["item_type"]]
                                positive = choose_items(item.properties["amount"][1], pool,
                                                        {"epic": {"value": 1}},
                                                        exclude_pool=self.inventory.collect_names() +
                                                        shop.collect_names())
                                negative = choose_items(item.properties["amount"][2], pool,
                                                        {"negative": {"value": 1}},
                                                        exclude_pool=self.inventory.collect_names() +
                                                        shop.collect_names())
                                items = positive + negative
                            else:
                                items = []
                            screens.open_pack(items, item.pos, item.properties["kind"], item.properties["amount"][0],
                                              self.textures.get(item.properties["sprite"]+"_opening"))
                            _ = clock.tick(self.config.fps)
                    else:
                        message = format_text("ui.message.not_enough_money", item.name)
                        success = False
                    if success:
                        self.sound.play("coins-")
                    else:
                        self.sound.play("buzz_low")
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        visual_effects.append(DisappearingItem(ret["try_selling"], 0.1))
                        self.money += ret["try_selling"].properties["price"]
                        message = format_text("ui.message.sold", ret['try_selling'].name,
                                              ret['try_selling'].properties['price'])
                        self.sound.play("coins+")
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        allow = False
                        lasting = False
                        for effect in item.effects:
                            if effect["usage"] == "active":
                                allow = True
                            if effect["duration"] != 0:
                                lasting = True
                        if allow and not lasting and item.use():
                            self.inventory.remove_item(item)
                            visual_effects.append(DisappearingItem(item, 0.1))

            self.screen.fill((20, 20, 70))

            big_font = pygame.font.Font(fontfile, 36)
            header = big_font.render(loc("ui.text.shop"), True, (255, 255, 255))
            self.screen.blit(header, (self.config.shop_pos[0] + 50, self.config.shop_pos[1]))

            if message:
                font = pygame.font.Font(fontfile, 24)
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

            display_screen(self.screen)
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
                    save_system.save()
                    return {"continue": "continue", "field_setup": "back"}[ui_return]
                match event.type:
                    case pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    case pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            choice = screens.overlay_menu(self.screen, "ui.text.pause", [
                                "ui.button.resume", "ui.button.settings", "ui.button.main"])
                            if choice == "ui.button.main":
                                save_system.save()
                                return 'menu'
                            if choice == "ui.button.settings":
                                screens.settings_menu()
                            _ = clock.tick(self.config.fps)
                        elif event.key == pygame.K_RETURN:
                            waiting = False
                ret = self.inventory.handle_event(event)
                if ret:
                    if "try_selling" in ret and self.inventory.remove_item(ret["try_selling"]):
                        self.money += ret["try_selling"].properties["price"] // 2
                        self.sound.play("coins+")
                    elif "try_using" in ret:
                        item = ret["try_using"]
                        if item.properties["type"] == "buildable" and self.field.place(item):
                            self.inventory.remove_item(item)    # TODO: if placing is not allowed, remove object
                        elif item.properties["type"] == "card":
                            for effect in item.effects:
                                if effect["name"] == "delete_object" and\
                                        self.field.delete(mouse_scale(pygame.mouse.get_pos())):
                                    item.use()              # TODO: if usage is not allowed, place object back
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
            display_screen(self.screen)
            dt = clock.tick(self.config.fps) / 1000
            self.real_fps = clock.get_fps()
        return 'back'

    def run(self):
        self.field = Field()
        self.ui = Ui()
        self.inventory = PlayerInventory()
        self.round_instance = PinballRound()
        while True:
            self.cont = save_system.load()
            continue_from = None
            if self.cont:
                continue_from = self.ui.mode
            choices = ["ui.button.start", "ui.button.settings", "ui.button.exit"]
            if self.cont:
                choices.insert(0, "ui.button.continue")
            if self.debug_mode:
                choices.append("Debug_Shop")

            choice = screens.overlay_menu(self.screen, "ui.text.main", choices)
            if choice == "ui.button.exit":
                break
            if choice == "ui.button.settings":
                screens.settings_menu()
                continue
            if choice == "Debug_Shop":
                self.reroll_cost = 0
                self.money = 10000
                self.field = Field()
                result = 'win'
                while result in ['win', 'back']:
                    result, shop = self.shop_screen()
                    if result == 'field_setup':
                        result = self.field_modification_screen()
                self.money = 0
                continue
            if choice in ["ui.button.start", "ui.button.continue"]:
                self.config = Config(self.config)
                if choice == "ui.button.start":
                    continue_from = None
                    self.inventory = PlayerInventory()
                    self.field = Field()
                    self.flags = self.config.start_flags
                    self.money = 0
                    self.round = 0
                self.score_needed = self.config.min_score[self.round]
                while True:
                    if continue_from is None or continue_from in ['round', 'round_finishable']:
                        continue_from = None
                        self.round_instance = PinballRound()
                        result, round_score = self.round_instance.run()
                        if result != "round_over":
                            self.cont = True
                            break
                        result = screens.round_results_overlay(round_score, self.score_needed)
                        if result == 'lose':
                            save_system.save(delete=True)
                            self.cont = False
                            break
                        self.sound.play('coins+')
                    else:
                        result = 'win'
                    if continue_from is None or continue_from == 'results':
                        self.round += 1
                    continue_from = None
                    if self.round < len(self.config.min_score):
                        self.score_needed = self.config.min_score[self.round]
                    else:
                        self.score_needed = self.config.min_score[-1] * (10 + 2 * (self.round - len(
                            self.config.min_score))) ** (self.round - len(self.config.min_score) + 1)
                    shop = None
                    self.reroll_cost = self.flags['reroll_start_cost']
                    while result in ['win', 'back']:
                        result, shop = self.shop_screen(shop)
                        if result == 'field_setup':
                            result = self.field_modification_screen()
                    if result == 'menu':
                        self.cont = True
                        break
                if result == "exit":
                    self.cont = True
                    break
        pygame.quit()
