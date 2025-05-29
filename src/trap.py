import pygame
from obstacle import Obstacle

class Trap(Obstacle):
    def __init__(self, position, radius=15):
        super().__init__(position, radius)
        self.color = (255, 0, 0)  # 红色

    def activate(self):
        """激活陷阱"""
        super().activate()
        return True  # 返回True表示需要重置关卡

    def draw(self, screen):
        """绘制陷阱"""
        pygame.draw.circle(screen, self.color,
                           (int(self.position[0]), int(self.position[1])),
                           self.radius)