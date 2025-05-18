from pathlib import Path
from json import load
import pygame


class Config:
    def __init__(self):
        self.fontfile = Path(__file__).resolve().with_name("assets").joinpath('lang/TDATextCondensed.ttf')
        self.debug_mode = False
        self.fullscreen = False
        self.resolutions = pygame.display.list_modes()
        self.langs = ["en", "ru"]
        self.lang = self.langs[1]
        self.base_resolution = (1280, 720)

        # Screen and simulation settings.
        self.screen_width = 1280
        self.screen_height = 720
        self.fps = 180
        self.max_dt = 1 / self.fps
        self.gravity = (0, 900)

        # UI panel settings.
        self.ui_pos = (50, 0)
        self.ui_width = 280
        self.ui_round_pos = (10, 10)
        self.ui_min_score_pos = (10, 40)
        self.ui_score_pos = (10, 70)
        self.ui_money_pos = (10, 100)
        self.ui_butt_width_1 = 230
        self.ui_butt_width_2 = 100
        self.ui_continue_pos = (20, 150)
        self.ui_field_config_pos = (20, 220)
        self.ui_reroll_pos = (150, 220)
        self.ui_inventory_pos = (60, 300)
        self.ui_inventory_height = 300
        self.ui_deletion_size = (200, 150)

        # Table boundaries.
        self.field_pos = (350, 0)
        self.left_wall_x = 15
        self.top_wall_y = 10
        self.field_width = 600
        self.field_height = 600
        self.launch_opening_height = 100
        self.bottom_opening_distance = 200
        self.bottom_opening_height = 60
        self.launch_ramp_width = 50
        self.curve_radius = 100

        self.divider_x = 300
        self.divider_y1 = 150
        self.divider_y2 = 300

        # Launch parameters.
        self.launch_charge_rate = 1500
        self.launch_max_impulse = 2000
        self.launch_indicator_size = (40, 60)

        # Flipper parameters.
        self.flipper_stiffness = 90000000
        self.flipper_damping = 3500000
        self.left_flipper_default_angle = 30
        self.left_flipper_active_angle = -30
        self.right_flipper_default_angle = -30
        self.right_flipper_active_angle = 30

        # Game play.
        self.balls = 3
        self.min_score = [500,
                          1000,
                          2000,
                          3000,
                          4000,
                          5000,
                          10000,
                          30000,
                          75000,
                          150000,
                          500000,
                          2000000,
                          10000000]
        self.base_award = 50
        self.extra_award_per_order = 50
        self.extra_award_per_ball = 100
        self.charge_bonus = 2
        self.interest_rate = 0.1
        self.interest_cap = 50
        self.score_multiplier = 1
        self.reroll_start_cost = 10
        self.reroll_next = 2
        self.inventory_size = 5
        self.start_flags = {"charge_bonus": False, "reroll_mode": 'm', "shop_upgrade": 0}

        self.shop_size = [2, 3, 1, 2]

        with open(Path(__file__).resolve().with_name("assets").joinpath('config/cards.json')) as file:
            self.shop_items = load(file)
        with open(Path(__file__).resolve().with_name("assets").joinpath('config/objects.json')) as file:
            self.objects_settings = load(file)
        self.rarities = self.shop_items.pop("rarities")

        self.left_flipper_pos = (190, 630)
        self.right_flipper_pos = (410, 630)

        self.board_objects = [
            {"pos": (200, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (400, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 470), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 100), "type": "pin", "class": "pin"},
            {"pos": (100, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": (500, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": self.left_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": True},
            {"pos": self.right_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": False},
        ]

        # Derived values.
        self.shop_pos = (self.ui_pos[0] + self.ui_width + 10, self.ui_pos[1] + 50)
        self.pack_opening_pos = (self.shop_pos[0] + 30, self.shop_pos[1] + 200)
        self.shop_pos_objects = (self.shop_pos[0] + 200, 150)
        self.shop_pos_cards = (self.shop_pos[0] + 670, 150)
        self.shop_pos_effects = (self.shop_pos[0] + 200, 350)
        self.shop_pos_packs = (self.shop_pos[0] + 670, 350)
        self.right_wall_x = self.left_wall_x + self.field_width
        self.bottom_wall_y = self.top_wall_y + self.field_height
        self.launch_opening_top = self.top_wall_y + self.launch_opening_height
        self.bottom_opening_bottom = self.bottom_wall_y - self.bottom_opening_distance
        self.bottom_opening_top = self.bottom_opening_bottom - self.bottom_opening_height
        self.launch_ramp_wall_x = self.right_wall_x + self.launch_ramp_width
        self.recline_left_start = (self.left_wall_x, self.bottom_wall_y - 50)
        self.recline_left_end = (self.left_flipper_pos[0] - 10,
                                 self.left_flipper_pos[1])
        self.recline_right_start = (self.right_wall_x, self.bottom_wall_y - 50)
        self.recline_right_end = (self.right_flipper_pos[0] + 10,
                                  self.right_flipper_pos[1])
        self.curve_center_right = (self.launch_ramp_wall_x - self.curve_radius,
                                   self.top_wall_y + self.curve_radius)
        self.curve_center_left = (self.left_wall_x + self.curve_radius,
                                  self.top_wall_y + self.curve_radius)
        self.ramp_gate_start = (self.right_wall_x, self.top_wall_y)
        self.ramp_gate_end = (self.right_wall_x, self.launch_opening_top)
        self.ramp_recline_start = (self.right_wall_x, self.bottom_opening_bottom)
        self.ramp_recline_end = (self.launch_ramp_wall_x, self.bottom_opening_bottom - 30)
        self.field_size = (self.launch_ramp_wall_x + 15, self.bottom_wall_y + 110)
        self.launch_indicator_pos = (self.right_wall_x + 7, self.bottom_wall_y - 5)
        self.ball_start = (self.right_wall_x + self.launch_ramp_width / 2,
                           self.bottom_wall_y - 30)
        self.ball_queue_x = self.field_size[0] + 20
        self.ball_queue_lower_y = self.bottom_wall_y - 40

        self.applied_effects_settings = {
            "pos": (self.field_pos[0] + self.field_size[0] + 50, 50),
            "width": 200,
            "height": 400,
            "max_size": 1e10
        }
        self.ui_deletion_pos = (self.field_pos[0] + self.field_size[0] + 20,
                                self.screen_height - self.ui_deletion_size[1] - 10)
