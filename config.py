from pathlib import Path


class Config:
    def __init__(self):
        self.fontfile = Path(__file__).resolve().with_name("assets").joinpath('terminal-grotesque.ttf')

        # Screen and simulation settings.
        self.screen_width = 1280
        self.screen_height = 720
        self.fps = 180
        self.gravity = (0, 900)

        # UI panel settings.
        self.ui_pos = (50, 0)
        self.ui_width = 250
        self.ui_min_score_pos = (10, 10)
        self.ui_score_pos = (10, 40)
        self.ui_money_pos = (10, 70)
        self.ui_balls_pos = (10, 100)
        self.ui_butt_width = 160
        self.ui_continue_pos = (20, 150)
        self.ui_field_config_pos = (20, 220)
        self.ui_inventory_pos = (60, 300)
        self.ui_inventory_height = 200

        # Table boundaries.
        self.field_pos = (350, 0)
        self.left_wall_x = 10
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
        self.launch_charge_rate = 2000
        self.launch_max_impulse = 5000
        self.launch_indicator_size = (20, 40)

        # Flipper parameters.
        self.flipper_length = 80
        self.flipper_width = 20
        self.flipper_stiffness = 80000000
        self.flipper_damping = 3500000
        self.left_flipper_default_angle = 30
        self.left_flipper_active_angle = -30
        self.right_flipper_default_angle = -30
        self.right_flipper_active_angle = 30

        # Game play.
        self.balls = 3
        self.min_score = [1000,
                          2000,
                          5000,
                          10000,
                          30000,
                          75000,
                          150000,
                          500000,
                          2000000,
                          10000000]
        self.base_award = 50
        self.extra_award_per_order = 100
        self.extra_award_per_ball = 100
        self.score_multiplier = 1

        # Shop settings.
        self.shop_items = {
            "cards": [
                {"name": "Shield", "price": 60, "type": "card", "effect": "shield", "duration": 10, "trigger": "once",
                 "description": "Allow the ball to bounce\nfrom the bottom for 10 s"},
                {"name": "SlowMo", "price": 90, "type": "card", "effect": "time_warp", "params": [0.5],
                 "trigger": "once", "duration": 10, "description": "Slow down time\nfor 10 s"},
                {"name": "Mega Bump", "price": 120, "type": "card", "effect": "bumper_empower", "trigger": "once",
                 "params": [2], "duration": 10, "description": "Increase the strength of all bumpers\nx2 for 10 s"},
                {"name": "Bonus", "price": 150, "type": "card", "effect": "change_score_multiplier", "trigger": "once",
                 "params": [5, 'm'], "duration": 5, "description": "Increase points scored\nx5 for 5 s"},
                {"name": "Bonus Ball", "price": 150, "type": "card", "effect": "change_ball_amount",
                 "params": [1], "description": "Get an additional ball\nwhile this card is in your inventory"},
                {"name": "Doubler", "price": 150, "type": "card", "effect": "change_score_multiplier",
                 "params": [2, 'm'], "description": "Earn double score\nwhile this card is in your inventory"},
                {"name": "Extra slot", "price": 150, "type": "card", "effect": "inventory_size",
                 "params": [2], "description": "Get 2 extra inventory slots\nwhile this card is in your inventory"},
            ],
            "vouchers": [
                {"name": "+Inventory slot", "price": 300, "type": "immediate", "effect": "inventory_size",
                 "params": [1], "description": "Additional inventory slot"},
                {"name": "+Ball", "price": 150, "type": "immediate", "effect": "change_ball_amount", "params": [1],
                 "description": "Additional ball"},
                {"name": "Multiplier", "price": 100, "type": "immediate", "effect": "change_score_multiplier",
                 "params": [0.5, 's'], "description": "Score 50% more points"}
            ],
            "objects": [
                {"name": "Bumper", "price": 75, "type": "buildable", "object_type": "bumper", "class": "bumper_big",
                 "description": "Additional big bumper"},
                {"name": "Small Bumper", "price": 50, "type": "buildable", "object_type": "bumper",
                 "class": "bumper_small", "description": "Additional small bumper"},
                {"name": "Flipper", "price": 100, "type": "buildable", "object_type": "flipper",
                 "class": "flipper_standard", "description": "Replaceable flipper\nThis can only replace a flipper"}
            ],
            "packs": [
                {"name": "Card Pack", "price": 200, "item_type": "cards", "type": "pack",
                 "description": "Choose 1 of 4 cards"},
                {"name": "Big Card Pack", "price": 400, "item_type": "cards", "type": "pack",
                 "description": "Choose 1 of 6 cards"},
                {"name": "Object Pack", "price": 100, "item_type": "objects", "type": "pack",
                 "description": "Choose 1 of 4 objects"},
                {"name": "Big Object Pack", "price": 200, "item_type": "objects", "type": "pack",
                 "description": "Choose 1 of 6 objects"},
            ]
        }

        self.objects_settings = {
            "ball": {"ball_standard": {"texture": "ball", "size": 15, "mass": 1, "effect": None}},
            "bumper": {"bumper_big": {"texture": "bumper", "size": 30, "force": 1.3, "effect": "bump",
                                      "params": [100, 10]},
                       "bumper_small": {"texture": "bumper_small", "size": 15, "force": 1.1, "effect": "bump",
                                        "params": [50, 0]}},
            "flipper": {"flipper_standard": {"texture": "flipper_left", "size": 80, "force": 0.6, "effect": None}}
        }

        self.left_flipper_pos = (230, 650)
        self.right_flipper_pos = (370, 650)

        self.board_objects = [
            {"pos": (200, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (400, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 470), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 100), "type": "bumper", "class": "bumper_small"},
            {"pos": (100, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": (500, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": self.left_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": True},
            {"pos": self.right_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": False},
        ]

        # Derived values.
        self.shop_pos = (self.ui_pos[0] + self.ui_width + 10, self.ui_pos[1] + 50)
        self.shop_pos_objects = (self.shop_pos[0] + 30, 150)
        self.shop_pos_cards = (self.shop_pos_objects[0] + 300, 150)
        self.shop_pos_effects = (self.shop_pos[0] + 100, 350)
        self.shop_pos_packs = (self.shop_pos_effects[0] + 300, 350)
        self.right_wall_x = self.left_wall_x + self.field_width
        self.bottom_wall_y = self.top_wall_y + self.field_height
        self.launch_opening_top = self.top_wall_y + self.launch_opening_height
        self.bottom_opening_bottom = self.bottom_wall_y - self.bottom_opening_distance
        self.bottom_opening_top = self.bottom_opening_bottom - self.bottom_opening_height
        self.launch_ramp_wall_x = self.right_wall_x + self.launch_ramp_width
        self.recline_left_start = (self.left_wall_x, self.bottom_wall_y - 50)
        self.recline_left_end = (self.left_flipper_pos[0] - self.flipper_length / 2 - 10,
                                 self.left_flipper_pos[1] - self.flipper_width / 2)
        self.recline_right_start = (self.right_wall_x, self.bottom_wall_y - 50)
        self.recline_right_end = (self.right_flipper_pos[0] + self.flipper_length / 2 + 10,
                                  self.right_flipper_pos[1] - self.flipper_width / 2)
        self.curve_center_right = (self.launch_ramp_wall_x - self.curve_radius,
                                   self.top_wall_y + self.curve_radius)
        self.curve_center_left = (self.left_wall_x + self.curve_radius,
                                  self.top_wall_y + self.curve_radius)
        self.ramp_gate_start = (self.right_wall_x, self.top_wall_y)
        self.ramp_gate_end = (self.right_wall_x, self.launch_opening_top)
        self.ramp_recline_start = (self.right_wall_x, self.bottom_opening_bottom)
        self.ramp_recline_end = (self.launch_ramp_wall_x, self.bottom_opening_bottom - 30)
        self.launch_indicator_pos = (self.screen_width - self.launch_indicator_size[0] - 20,
                                     self.screen_height - self.launch_indicator_size[1] - 20)
        self.ball_start = ((self.right_wall_x + self.launch_ramp_wall_x) / 2,
                           self.bottom_wall_y - 30)
