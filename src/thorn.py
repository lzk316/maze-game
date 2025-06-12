import pygame
import math
from src.obstacle import Obstacle


class Thorn(Obstacle):
    def __init__(self, position, size=300):
        super().__init__(position)
        self.size = size
        self.color = (255, 0, 255)
        self.is_activated = False
        self.is_visible = False

    def check_collision(self, ball):

        ball_x, ball_y = ball.position
        ball_radius = ball.radius
        center_x, center_y = self.position


        half_size = self.size // 2
        left = center_x - half_size - 10
        right = center_x + half_size + 10
        top = center_y - half_size - 10
        bottom = center_y + half_size + 10


        if left <= ball_x <= right and top <= ball_y <= bottom:

            if (ball_x - left) < ball_radius or (right - ball_x) < ball_radius or \
               (ball_y - top) < ball_radius or (bottom - ball_y) < ball_radius:
                return True

        return False

    def activate(self):
        self.is_activated = True
        self.is_visible = True
        return True

    def draw(self, screen):

        if self.is_activated:

            pygame.draw.rect(screen, self.color,
                             (self.position[0] - self.size // 2,
                              self.position[1] - self.size // 2,
                              self.size, self.size))