import pygame
import numpy as np


class Obstacle:
    def __init__(self, position, radius=150):
        self.position = np.array(position)
        self.radius = radius
        self.is_active = True

    def check_collision(self, ball):
        """检查与球的碰撞"""
        if not self.is_active:
            return False

        distance = np.linalg.norm(ball.position - self.position)
        return distance < (ball.radius + self.radius)

    def activate(self):
        """激活障碍物效果"""
        self.is_active = True
        return True

    def draw(self, screen):
        """绘制障碍物"""
        pass  # 由子类实现