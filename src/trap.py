import pygame
from obstacle import Obstacle

class Trap(Obstacle):
    def __init__(self, position, radius=150):
        super().__init__(position, radius)
        self.color = (255, 0, 0)

    def activate(self):

        super().activate()
        print(f"3{self.position}")
        return True

    def draw(self, screen):

        pygame.draw.circle(screen, self.color,
                           (int(self.position[0]), int(self.position[1])),
                           self.radius)