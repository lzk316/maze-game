import pygame
import numpy as np


class Obstacle:
    def __init__(self, position, radius=150):
        self.position = np.array(position)
        self.radius = radius
        self.is_active = True

    def check_collision(self, ball):
        # 计算两点间距离
        dx = self.position[0] - ball.position[0]
        dy = self.position[1] - ball.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # 判断是否碰撞
        if distance < self.radius + ball.radius:
            print(f"[DEBUG] 陷阱碰撞发生！位置: {self.position}, 小球位置: {ball.position}")
            ball.reset_position()
            return True
        return False

    def activate(self):
        """激活障碍物效果"""
        self.is_active = True
        return True

    def draw(self, screen):
        """绘制障碍物"""
        pass  # 由子类实现