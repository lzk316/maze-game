import numpy as np
import pygame

class GravityMode:
    def __init__(self):
        self.last_rotation_direction = None
        self.name = "Gravity Mode"
        self.rotation_speed = 1
        self.current_angle = 0
        self.time_step = 1 / 60.0

    def rotate_map(self, direction):
        self.last_rotation_direction = direction
        if direction == 'left':
            self.current_angle += self.rotation_speed * self.time_step
        elif direction == 'right':
            self.current_angle -= self.rotation_speed * self.time_step
        return self.current_angle

    def apply_gravity(self, world):
        pass
    def handle_collision(self, world):
        pass

    def update_physics(self, world):
        world.step()