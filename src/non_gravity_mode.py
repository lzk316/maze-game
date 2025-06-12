import numpy as np

class NonGravityMode:
    def __init__(self):
        self.name = "Non-Gravity Mode"
        self.movement_speed = 10

    def control_ball(self, world, ball_body, direction):

        if direction is not None:

            dir_array = np.array(direction, dtype=float)
            norm = np.linalg.norm(dir_array)
            if norm > 0:
                dir_array = dir_array / norm


            velocity = dir_array * self.movement_speed / world.PPM
            ball_body.linearVelocity = velocity

    def handle_collision(self):
        pass

    def update(self):
        pass