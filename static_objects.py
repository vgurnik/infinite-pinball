import math
import pymunk


class StaticObjects:
    @staticmethod
    def create_boundaries(space, config):
        lwx = config.left_wall_x
        rwx = config.right_wall_x
        topy = config.top_wall_y
        boty = config.bottom_wall_y
        scr_height = config.screen_height
        launch_opening_top = config.launch_opening_top
        bopt = config.bottom_opening_top
        ramp_wall = config.launch_ramp_wall_x

        static_lines = [
            pymunk.Segment(space.static_body, (lwx, scr_height), (lwx, topy), 5),
            pymunk.Segment(space.static_body, (rwx, scr_height), (rwx, config.bottom_opening_bottom), 5),
            pymunk.Segment(space.static_body, (rwx, bopt), (rwx, launch_opening_top), 5),
            pymunk.Segment(space.static_body, (lwx, topy), (ramp_wall, topy), 5),
            pymunk.Segment(space.static_body, (config.divider_x, config.divider_y1),
                           (config.divider_x, config.divider_y2), 5),
            pymunk.Segment(space.static_body, config.recline_left_start, config.recline_left_end, 5),
            pymunk.Segment(space.static_body, config.recline_right_start, config.recline_right_end, 5),
            pymunk.Segment(space.static_body, (ramp_wall, boty), (ramp_wall, topy), 5)
        ]
        for line in static_lines:
            line.elasticity = 0.5
            line.friction = 0

        # Add additional curved segments.
        cr_center = config.curve_center_right
        cl_center = config.curve_center_left
        cr = config.curve_radius
        for i in range(10):
            ang1 = i / 10 * math.pi / 2
            ang2 = (i + 1) / 10 * math.pi / 2
            curve1 = pymunk.Segment(space.static_body,
                                    (cr_center[0] + cr * math.cos(ang1), cr_center[1] - cr * math.sin(ang1)),
                                    (cr_center[0] + cr * math.cos(ang2), cr_center[1] - cr * math.sin(ang2)), 5)
            curve1.elasticity = 0
            curve1.friction = 0
            curve2 = pymunk.Segment(space.static_body,
                                    (cl_center[0] - cr * math.cos(ang1), cl_center[1] - cr * math.sin(ang1)),
                                    (cl_center[0] - cr * math.cos(ang2), cl_center[1] - cr * math.sin(ang2)), 5)
            curve2.elasticity = 0
            curve2.friction = 0
            static_lines.append(curve1)
            static_lines.append(curve2)
        ramp_bot_wall = pymunk.Segment(space.static_body, (ramp_wall, boty), (rwx, boty), 5)
        ramp_bot_wall.elasticity = 0.1
        ramp_bot_wall.friction = 1
        static_lines.append(ramp_bot_wall)

        space.add(*static_lines)

    @staticmethod
    def create_ramp_gates(space, config):
        gate_shape = pymunk.Segment(space.static_body, config.ramp_gate_start, config.ramp_recline_start, 5)
        gate_shape.elasticity = 0.5
        gate_shape.friction = 0
        gate_shape.sensor = True
        space.add(gate_shape)
        recline_shape = pymunk.Segment(space.static_body, config.ramp_recline_start, config.ramp_recline_end, 5)
        recline_shape.elasticity = 0.5
        recline_shape.friction = 0
        recline_shape.sensor = True
        space.add(recline_shape)
        return gate_shape, recline_shape

    @staticmethod
    def create_shield(space, config):
        shield = pymunk.Segment(space.static_body, (config.left_flipper_pos[0], config.left_flipper_pos[1] + 50),
                                (config.right_flipper_pos[0], config.right_flipper_pos[1] + 50), 5)
        shield.elasticity = 1.5
        shield.friction = 0
        shield.sensor = True
        space.add(shield)
        return shield
