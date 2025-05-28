from src.obstacle import Obstacle
import pygame


class Trap(Obstacle):
    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius
        self.color = (255, 255, 0)  # 黄色陷阱

    def check_collision(self, ball):
        # 简单距离检测
        distance = ((ball.position[0] - self.position[0]) ** 2 +
                    (ball.position[1] - self.position[1]) ** 2) ** 0.5
        return distance < (ball.radius + self.radius)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.position[0]), int(self.position[1])),
                           self.radius)