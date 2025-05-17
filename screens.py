import sys
import math
import pygame
from game_effects import AnimatedEffect
from inventory import InventoryItem, PackInventory
from utils.textures import mouse_scale, display_screen
from utils.text import format_text, loc
from ui import Button
from field import Field
from ui import Ui
import game_context


def overlay_menu(screen, title, options):
    game = game_context.game
    selected = 0
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    option_rects = []

    while True:
        mouse_pos = mouse_scale(pygame.mouse.get_pos())
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
        font = pygame.font.Font(game.config.fontfile, 36)
        title_text = font.render(loc(title, game.config.lang), True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title_text, title_rect)
        option_rects = []
        for idx, option in enumerate(options):
            if idx == selected:
                opt_font = pygame.font.Font(game.config.fontfile, 42)
                color = (255, 255, 0)
            else:
                opt_font = pygame.font.Font(game.config.fontfile, 36)
                color = (255, 255, 255)
            text = opt_font.render(loc(option, game.config.lang), True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, 250 + idx * 50))
            screen.blit(text, rect)
            option_rects.append(rect)
        display_screen(game.display, screen, game.screen_size)


def open_pack(items, start, kind, amount, opening_sprite):
    game = game_context.game
    clock = pygame.time.Clock()
    dt = 1.0 / (game.real_fps if game.real_fps > 1 else game.config.fps)
    big_font = pygame.font.Font(game.config.fontfile, 36)
    opening_inventory = PackInventory(len(items) * 150)
    for item in items:
        if item["type"] == "buildable":
            obj_def = game.config.objects_settings[item["object_type"]][item["class"]]
            opening_inventory.add_item(InventoryItem(properties=item,
                                                     sprite=game.textures.get("buildable_pack"),
                                                     target_position=start, for_buildable=
                                                     game.textures.get(obj_def["texture"])))
        else:
            opening_inventory.add_item(InventoryItem(properties=item, sprite=game.textures.get(
                item.get("sprite")), target_position=start))
    taken = 0
    skip_button = Button(loc("ui.button.skip", game.config.lang),
                         (opening_inventory.position[0] + opening_inventory.width / 2,
                          opening_inventory.position[1] + 200), "auto", (0, 255, 100))
    opening_effect = AnimatedEffect(game.display, game.screen_size)
    game.screen.fill((20, 20, 70))

    header = big_font.render(loc("ui.text.shop", game.config.lang), True, (255, 255, 255))
    game.screen.blit(header, (game.config.shop_pos[0] + 50, game.config.shop_pos[1]))
    game.ui.draw(game.screen)
    game.ui.update(dt)
    game.inventory.update(dt)
    game.inventory.draw(game.screen)
    opening_inventory.draw(game.screen)
    opening_effect.start(game.screen, opening_sprite, (start.x - 3, start.y - 23),
                         (126, 188))
    clock.tick(game.config.fps)
    dt = 0
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
                    if game.inventory.add_item(item):
                        opening_inventory.remove_item(item)
                        taken += 1
                elif kind == 'all':
                    to_remove = []
                    for item in opening_inventory.items:
                        if game.inventory.add_item(item):
                            to_remove.append(item)
                        else:
                            for i in to_remove:
                                game.inventory.remove_item(i)
                            break
                    else:
                        taken = amount

        game.screen.fill((20, 20, 70))

        header = big_font.render(loc("ui.text.shop", game.config.lang), True, (255, 255, 255))
        game.screen.blit(header, (game.config.shop_pos[0] + 50, game.config.shop_pos[1]))
        game.ui.draw(game.screen)
        game.ui.update(dt)
        game.inventory.update(dt)
        game.inventory.draw(game.screen)

        opening_surface = pygame.Surface((game.config.screen_width, game.config.screen_height), pygame.SRCALPHA)
        opening_surface.fill((20, 20, 20, 150))
        skip_button.draw(opening_surface)
        if skip_button.is_pressed():
            return "skip"

        opening_inventory.update(dt)
        opening_inventory.draw(opening_surface)
        if kind == 'oneof':
            pack_header = big_font.render(loc("ui.text.take", game.config.lang).format(taken, amount),
                                          True, (255, 255, 255))
        else:
            pack_header = big_font.render(loc("ui.text.take_all", game.config.lang), True, (255, 255, 255))
        opening_surface.blit(pack_header, (opening_inventory.position[0] + (opening_inventory.width -
                                                                            pack_header.get_width()) / 2,
                                           opening_inventory.position[1] - 50))

        game.screen.blit(opening_surface, (0, 0))
        display_screen(game.display, game.screen, game.screen_size)
        dt = clock.tick(game.config.fps) / 1000
        game.real_fps = clock.get_fps()
    return "continue"


def settings_menu():
    game = game_context.game
    font = pygame.font.Font(game.config.fontfile, 28)
    bigger_font = pygame.font.Font(game.config.fontfile, 30)
    pref_running = True
    resolution_index = game.config.resolutions.index(game.screen_size)
    options = ["resolution", "fullscreen", "language", "debug_mode", "back"]
    selected_option = 0

    while pref_running:
        screen_reload = False
        lang_reload = False
        game.screen.fill((20, 20, 70))
        pref_text = font.render(loc("ui.text.settings", game.config.lang), True, (255, 255, 255))
        resolution_text = font.render(loc("ui.settings.resolution", game.config.lang).format(
            game.config.resolutions[resolution_index]), True, (255, 255, 255))
        fullscreen_text = font.render(loc("ui.settings.fullscreen", game.config.lang).format(
            loc("ui.settings." + ('on' if game.config.fullscreen else 'off'), game.config.lang)),
            True, (255, 255, 255))
        lang_text = font.render(loc("ui.settings.language", game.config.lang).format(
            loc("lang_name", game.config.lang)), True, (255, 255, 255))
        debug_text = font.render(loc("ui.settings.debug", game.config.lang).format(
            loc("ui.settings." + ('on' if game.debug_mode else 'off'), game.config.lang)),
            True, (255, 255, 255))
        back_text = font.render(loc("ui.settings.back", game.config.lang), True, (255, 255, 255))
        match options[selected_option]:
            case "resolution":
                resolution_text = bigger_font.render(loc("ui.settings.resolution", game.config.lang).format(
                    game.config.resolutions[resolution_index]), True, (255, 255, 0))
            case "fullscreen":
                fullscreen_text = bigger_font.render(loc("ui.settings.fullscreen", game.config.lang).format(
                    loc("ui.settings." + ('on' if game.config.fullscreen else 'off'), game.config.lang)),
                    True, (255, 255, 0))
            case "language":
                lang_text = bigger_font.render(loc("ui.settings.language", game.config.lang).format(
                    loc("lang_name", game.config.lang)), True, (255, 255, 0))
            case "debug_mode":
                debug_text = bigger_font.render(loc("ui.settings.debug", game.config.lang).format(
                    loc("ui.settings." + ('on' if game.debug_mode else 'off'), game.config.lang)), True,
                    (255, 255, 0))
            case "back":
                back_text = bigger_font.render(loc("ui.settings.back", game.config.lang), True, (255, 255, 0))

        game.screen.blit(pref_text, (game.config.screen_width // 2 - pref_text.get_width() // 2, 100))
        game.screen.blit(resolution_text, (game.config.screen_width // 2 - resolution_text.get_width() // 2, 200))
        game.screen.blit(fullscreen_text, (game.config.screen_width // 2 - fullscreen_text.get_width() // 2, 250))
        game.screen.blit(lang_text, (game.config.screen_width // 2 - lang_text.get_width() // 2, 300))
        game.screen.blit(debug_text, (game.config.screen_width // 2 - debug_text.get_width() // 2, 350))
        game.screen.blit(back_text, (game.config.screen_width // 2 - back_text.get_width() // 2, 400))

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP:
                            selected_option = (selected_option - 1) % len(options)
                        case pygame.K_DOWN:
                            selected_option = (selected_option + 1) % len(options)
                        case pygame.K_RETURN:
                            match options[selected_option]:
                                case "resolution":
                                    resolution_index = (resolution_index + 1) % len(game.config.resolutions)
                                    game.screen_size = game.config.resolutions[resolution_index]
                                    screen_reload = True
                                case "fullscreen":
                                    game.config.fullscreen = not game.config.fullscreen
                                    screen_reload = True
                                case "language":
                                    lang = (game.config.langs.index(game.config.lang) + 1) % len(game.config.langs)
                                    game.config.lang = game.config.langs[lang]
                                    lang_reload = True
                                case "debug_mode":
                                    game.debug_mode = not game.debug_mode
                                case "back":
                                    pref_running = False
                        case pygame.K_ESCAPE:
                            pref_running = False
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        match options[selected_option]:
                            case "resolution":
                                resolution_index = (resolution_index + (2 * (event.key == pygame.K_LEFT) - 1)) \
                                                   % len(game.config.resolutions)
                                game.screen_size = game.config.resolutions[resolution_index]
                                screen_reload = True
                            case "fullscreen":
                                game.config.fullscreen = not game.config.fullscreen
                                screen_reload = True
                            case "language":
                                lang = (game.config.langs.index(game.config.lang) +
                                        (2 * (event.key == pygame.K_LEFT) - 1)) % len(game.config.langs)
                                game.config.lang = game.config.langs[lang]
                                lang_reload = True
                            case "debug_mode":
                                game.debug_mode = not game.debug_mode
                            case "back":
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
                    elif 400 <= mouse_y <= 430:
                        selected_option = 4
                    match options[selected_option]:
                        case "resolution":
                            resolution_index = (resolution_index + 1) % len(game.config.resolutions)
                            game.screen_size = game.config.resolutions[resolution_index]
                            screen_reload = True
                        case "fullscreen":
                            game.config.fullscreen = not game.config.fullscreen
                            screen_reload = True
                        case "language":
                            lang = (game.config.langs.index(game.config.lang) + 1) % len(game.config.langs)
                            game.config.lang = game.config.langs[lang]
                            lang_reload = True
                        case "debug_mode":
                            game.debug_mode = not game.debug_mode
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
                    elif 400 <= mouse_y <= 430:
                        selected_option = 4
        if lang_reload:
            game.field = Field()
            game.ui = Ui()
            game.inventory = PlayerInventory()
        if screen_reload:
            game.display = pygame.display.set_mode(game.screen_size, (pygame.FULLSCREEN
                                                                      if game.config.fullscreen else 0))
        display_screen(game.display, game.screen, game.screen_size)


def round_results_overlay(score, min_score):
    game = game_context.game
    game.immediate['interest'] = 0
    game.immediate['interest_cap'] = 0
    game.immediate['$per_order'] = 0
    game.immediate['$per_ball'] = 0
    game.callback("round_win")
    extra_orders = int(math.log2(score / min_score)) if score >= min_score else 0
    order_reward = extra_orders * (game.config.extra_award_per_order + game.immediate['$per_order'])
    charged_ball = 0
    if len(game.round_instance.active_balls) > 0 and not game.round_instance.ball_launched:
        charged_ball += 1
    ball_reward = (len(game.round_instance.ball_queue) + charged_ball) * (
            game.config.extra_award_per_ball + game.immediate['$per_ball'])
    interest_reward = min(int((game.config.interest_rate + game.immediate['interest']) * game.money), (
            game.config.interest_cap + game.immediate['interest_cap']))
    if score >= min_score:
        game.money += game.config.base_award + order_reward + ball_reward + interest_reward

    game.screen.fill((20, 20, 70))
    game.ui.change_mode('results')
    game.ui.draw(game.screen)
    game.ui.update(0)
    game.screen.blit(game.field.draw(), game.field.position)

    font = pygame.font.Font(game.config.fontfile, 36)
    overlay = pygame.Surface((game.config.screen_width - game.config.ui_width, game.config.screen_height))
    overlay.fill((20, 20, 20))
    overlay.set_alpha(200)
    game.screen.blit(overlay, game.config.field_pos)
    if score < min_score:
        result = 'lose'
        texts = [
            loc("ui.message.lose", game.config.lang),
            format_text("ui.message.score", game.config.lang, score, min_score),
            format_text("ui.message.money", game.config.lang, game.money),
            loc("ui.message.return_lose", game.config.lang)
        ]
        for i, line in enumerate(texts):
            txt = font.render(line, True, (255, 100, 100))
            game.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + game.config.ui_width,
                                   150 + i * 45))
    else:
        result = 'win'
        texts = [
            loc("ui.message.complete", game.config.lang),
            format_text("ui.message.score", game.config.lang, score, min_score),
            format_text("ui.message.reward", game.config.lang, game.config.base_award),
            format_text("ui.message.money", game.config.lang, game.money),
            loc("ui.message.go_next", game.config.lang)
        ]
        if interest_reward > 0:
            texts.insert(3, format_text("ui.message.interest", game.config.lang,
                                        round(game.config.interest_rate * 100), interest_reward,
                                        game.config.interest_cap))
        if order_reward > 0:
            texts.insert(3, format_text("ui.message.score_reward", game.config.lang, order_reward))
        if ball_reward > 0:
            texts.insert(3, format_text("ui.message.ball_reward", game.config.lang, ball_reward))
        for i, line in enumerate(texts):
            if i == 0:
                txt = font.render(line, True, (0, 255, 0))
            else:
                txt = font.render(line, True, (255, 255, 255))
            game.screen.blit(txt, (overlay.get_width() // 2 - txt.get_width() // 2 + game.config.ui_width,
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
        display_screen(game.display, game.screen, game.screen_size)
    return result
