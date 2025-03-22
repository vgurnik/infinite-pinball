class Config:
    def __init__(self):
        # Screen and simulation settings.
        self.screen_width = 900
        self.screen_height = 850
        self.fps = 180
        self.gravity = (0, 900)

        # UI panel settings.
        self.ui_width = 200
        self.ui_min_score_pos = (10, 10)
        self.ui_score_pos = (10, 40)
        self.ui_money_pos = (10, 70)
        self.ui_balls_pos = (10, 100)
        self.ui_butt_width = 160
        self.ui_continue_pos = (20, 150)
        self.ui_field_config_pos = (20, 220)
        self.ui_inventory_pos = (10, 300)
        self.ui_inventory_height = 300

        # Table boundaries.
        self.left_wall_x = 50
        self.top_wall_y = 50
        self.field_width = 500
        self.field_height = 700
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
        self.flipper_stiffness = 70000000
        self.flipper_damping = 3000000
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
        self.base_award = 10
        self.extra_award_per_order = 5
        self.score_multiplier = 1

        # Shop settings.
        self.shop_items = {
            "cards": [
                {"name": "Shield", "price": 60, "type": "card", "effect": "change_ball_amount",
                 "description": "Allow the ball to bounce\nfrom the bottom for 5 s"},
                {"name": "SlowMo", "price": 90, "type": "card", "effect": "change_ball_amount",
                 "description": "Slow down time\nfor 5 s"},
                {"name": "Mega Bump", "price": 120, "type": "card", "effect": "change_ball_amount",
                 "description": "Increase the strength of all bumpers\nx2 for 5 s"},
                {"name": "Bonus", "price": 150, "type": "card", "effect": "change_ball_amount",
                 "description": "Increase scoring points\nx5 for 5 s"}
            ],
            "effects": [
                {"name": "+Ball", "price": 50, "type": "immediate", "effect": "change_ball_amount", "params": [1],
                 "description": "Additional ball"},
                {"name": "Multiplier", "price": 100, "type": "immediate", "effect": "change_score_multiplier",
                 "params": [0.5], "description": "Score 50% more points"}
            ],
            "objects": [
                {"name": "Bumper", "price": 75, "type": "buildable", "object_type": "bumper", "class": "bumper_big",
                 "description": "Additional big bumper"},
                {"name": "Bumper", "price": 50, "type": "buildable", "object_type": "bumper", "class": "bumper_small",
                 "description": "Additional small bumper"},
                {"name": "Flipper", "price": 100, "type": "buildable",
                 "description": "Additional flipper\nlol what\nthis will be a replaceable flipper"}
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
            "flipper": {"flipper_standard": {"texture": "flipper_left", "force": 0.6, "effect": None}}
        }

        self.left_flipper_pos = (220, 750)
        self.right_flipper_pos = (380, 750)

        self.board_objects = [
            {"pos": (200, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (400, 300), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 500), "type": "bumper", "class": "bumper_big"},
            {"pos": (300, 100), "type": "bumper", "class": "bumper_small"},
            {"pos": (150, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": (450, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": (150, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": (450, 400), "type": "bumper", "class": "bumper_small"},
            {"pos": self.left_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": True},
            {"pos": self.right_flipper_pos, "type": "flipper", "class": "flipper_standard", "is_left": False},
        ]

        # Derived values.
        self.shop_pos = (self.ui_width + 200, 50)
        self.shop_pos_objects = (self.ui_width + 30, 150)
        self.shop_pos_cards = (self.shop_pos_objects[0] + 400, 150)
        self.shop_pos_effects = (self.ui_width + 30, 350)
        self.shop_pos_packs = (self.shop_pos_effects[0] + 400, 350)
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
