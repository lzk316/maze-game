import numpy as np
import pygame


class Ball:
    def __init__(self, position, radius=150, density=1.0, friction=0.1, restitution=0.1):
        self.position = np.array(position, dtype=float)
        self.radius = radius
        self.color = (0, 255, 0)
        self.rotation_angle = 0
        self.box2d_body = None
        self.initial_position = position[:]

    def reset_position(self, position):

        self.position = np.array(position, dtype=float)
        self.rotation_angle = 0

    def update_from_box2d(self, body):

        self.position = np.array((body.position.x * 100, body.position.y * 100))
        self.rotation_angle = body.angle

    def draw(self, screen, offset_x=0, offset_y=0, ui_scale=0.1):

        ui_radius = int(self.radius * ui_scale)
        ui_pos = (int(self.position[0] * ui_scale + offset_x),
                  int(self.position[1] * ui_scale + offset_y))

        pygame.draw.circle(screen, self.color, ui_pos, ui_radius)

        start_pos = ui_pos
        end_pos = (
            int(ui_pos[0] + np.cos(self.rotation_angle) * ui_radius),
            int(ui_pos[1] + np.sin(self.rotation_angle) * ui_radius)
        )
        pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 2)