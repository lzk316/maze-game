import pygame
import numpy as np


class Ball:
    def __init__(self, position):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.radius = 15  # 直径30像素
        self.direction = np.array([0, 0], dtype=float)
        self.color = (0, 255, 0)  # 绿色
        self.speed = 5  # 移动速度

    def apply_gravity(self, gravity=(0, -0.5)):
        """应用重力"""
        self.velocity += np.array(gravity)

    def update_position(self):
        """更新位置"""
        self.position += self.velocity
        # 简单的速度衰减
        self.velocity *= 0.95

    def reset_position(self, new_position):
        """重置位置"""
        self.position = np.array(new_position, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.direction = np.array([0, 0], dtype=float)

    def draw(self, screen):
        """绘制小球"""
        pygame.draw.circle(screen, self.color,
                           (int(self.position[0]), int(self.position[1])),
                           self.radius)