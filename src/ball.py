import pygame
import pymunk


class Ball:
    def __init__(self):
        self.radius = 15
        self.color = (255, 0, 0)  # 红色小球
        self.position = [100, 100]  # 初始位置
        self.velocity = [0, 0]
        self.physical_body = None  # 用于重力模式的物理实体

    def move(self, direction):
        # 非重力模式下的移动
        speed = 5
        if direction == "up":
            self.position[1] -= speed
        elif direction == "down":
            self.position[1] += speed
        elif direction == "left":
            self.position[0] -= speed
        elif direction == "right":
            self.position[0] += speed

    def reset_position(self):
        self.position = [100, 100]
        self.velocity = [0, 0]
        if self.physical_body:
            self.physical_body.position = pymunk.Vec2d(100, 100)
            self.physical_body.velocity = (0, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.position[0]), int(self.position[1])),
                           self.radius)