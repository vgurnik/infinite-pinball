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
        self.ball_radius = 15
        self.ball_mass = 1

        # Launch parameters.
        self.launch_charge_rate = 2000
        self.launch_max_impulse = 5000
        self.launch_indicator_size = (20, 40)

        # Flipper parameters.
        self.flipper_length = 80
        self.flipper_width = 20
        self.flipper_stiffness = 70000000
        self.flipper_damping = 3000000
        self.left_flipper_pos = (220, 750)
        self.right_flipper_pos = (380, 750)
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

        # Shop settings.
        self.shop_items = {
            "cards": [
                {"name": "Shield", "price": 60, "effect": "card"},
                {"name": "SlowMo", "price": 90, "effect": "card"},
                {"name": "Mega Bump", "price": 120, "effect": "card"},
                {"name": "Bonus", "price": 150, "effect": "card"}
            ],
            "effects": [
                {"name": "+Ball", "price": 50, "effect": "immediate"},
                {"name": "Multiplier", "price": 100, "effect": "immediate"}
            ],
            "objects": [
                {"name": "Bumper Up", "price": 75, "effect": "buildable"},
                {"name": "Flipper Up", "price": 80, "effect": "buildable"}
            ],
            "packs": [
                {"name": "Card Pack", "price": 200, "item_type": "cards", "effect": "pack"},
                {"name": "Object Pack", "price": 100, "item_type": "objects", "effect": "pack"},
            ]
        }

        # Custom bumpers.
        self.bumpers = [
            {"pos": (200, 300), "radius": 30, "force": 1.3, "score": 100, "money": 10},
            {"pos": (400, 300), "radius": 30, "force": 1.3, "score": 100, "money": 10},
            {"pos": (300, 500), "radius": 30, "force": 1.3, "score": 100, "money": 10},
            {"pos": (300, 720), "radius": 10, "force": 1.0, "score": 5, "money": 0},
            {"pos": (300, 100), "radius": 10, "force": 1.1, "score": 50, "money": 0},
            {"pos": (100, 400), "radius": 10, "force": 1.1, "score": 50, "money": 0},
            {"pos": (500, 400), "radius": 10, "force": 1.1, "score": 50, "money": 0},
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
                           self.bottom_wall_y - self.ball_radius - 15)
