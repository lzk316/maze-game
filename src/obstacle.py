
import numpy as np


class Obstacle:
    def __init__(self, position, radius=150):
        self.position = np.array(position)
        self.radius = radius
        self.is_active = True

    def check_collision(self, ball):
        dx = self.position[0] - ball.position[0]
        dy = self.position[1] - ball.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5


        if distance < self.radius + ball.radius:
            print(f"[DEBUG] {self.position},  {ball.position}")
            ball.reset_position()
            return True
        return False

    def activate(self):

        self.is_active = True
        return True

    def draw(self, screen):

        pass