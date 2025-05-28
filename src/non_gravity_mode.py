import numpy as np


class NonGravityMode:
    def __init__(self):
        self.name = "Non-Gravity Mode"
        self.movement_speed = 5.0

    def control_ball(self, ball, direction):
        """直接控制小球移动"""
        if direction is not None:
            # 标准化方向向量
            dir_array = np.array(direction, dtype=float)
            norm = np.linalg.norm(dir_array)
            if norm > 0:
                dir_array = dir_array / norm

            # 应用速度
            ball.velocity = dir_array * self.movement_speed
        else:
            ball.velocity = np.array([0.0, 0.0])

        ball.update_position()