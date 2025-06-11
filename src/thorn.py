import pygame
import math
from src.obstacle import Obstacle


class Thorn(Obstacle):
    def __init__(self, position, size=300):
        super().__init__(position)
        self.size = size
        self.color = (255, 0, 255)  # 紫色
        self.is_activated = False  # 是否被激活（触碰后显示）
        self.is_visible = False  # 是否可见

    def check_collision(self, ball):
        # 简单的圆形与正方形碰撞检测
        ball_x, ball_y = ball.position
        ball_radius = ball.radius
        center_x, center_y = self.position

        # 计算正方形的边界
        half_size = self.size // 2
        left = center_x - half_size - 10  # 向左扩展10像素
        right = center_x + half_size + 10  # 向右扩展10像素
        top = center_y - half_size - 10  # 向上扩展10像素
        bottom = center_y + half_size + 10  # 向下扩展10像素

        # 检查是否在正方形范围内
        if left <= ball_x <= right and top <= ball_y <= bottom:
            # 检查是否在正方形的边界内
            if (ball_x - left) < ball_radius or (right - ball_x) < ball_radius or \
               (ball_y - top) < ball_radius or (bottom - ball_y) < ball_radius:
                return True

        return False

    def activate(self):
        self.is_activated = True
        self.is_visible = True  # 触碰后变为可见
        return True  # 返回True表示需要重置小球

    def draw(self, screen):
        """绘制荆棘"""
        if self.is_activated:
            # 绘制正方形
            pygame.draw.rect(screen, self.color,
                             (self.position[0] - self.size // 2,
                              self.position[1] - self.size // 2,
                              self.size, self.size))