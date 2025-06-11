import numpy as np

class NonGravityMode:
    def __init__(self):
        self.name = "Non-Gravity Mode"
        self.movement_speed = 10

    def control_ball(self, world, ball_body, direction):
        """直接控制小球移动"""
        if direction is not None:
            # 标准化方向向量
            dir_array = np.array(direction, dtype=float)
            norm = np.linalg.norm(dir_array)
            if norm > 0:
                dir_array = dir_array / norm

            # 应用速度
            velocity = dir_array * self.movement_speed / world.PPM
            ball_body.linearVelocity = velocity

    def handle_collision(self):
        """处理碰撞"""
        pass  # 碰撞由Box2D自动处理

    def update(self):
        """更新逻辑"""
        pass  # 更新由物理引擎自动处理