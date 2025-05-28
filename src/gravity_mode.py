import numpy as np


class GravityMode:
    def __init__(self):
        self.name = "Gravity Mode"
        self.gravity = np.array([0, -0.5])  # 默认向下重力
        self.rotation_speed = 90  # 旋转速度(度/秒)
        self.current_angle = 0  # 当前旋转角度

    def rotate_map(self, game_map, direction):
        """旋转地图并调整重力方向"""
        if direction is None:
            return

        # 根据输入方向计算角度变化
        if direction == 'left':
            self.current_angle += self.rotation_speed
        elif direction == 'right':
            self.current_angle -= self.rotation_speed

        # 标准化角度到0-360范围
        self.current_angle %= 360

        # 根据角度计算重力方向
        radians = np.radians(self.current_angle)
        self.gravity = np.array([
            np.sin(radians),  # x分量
            -np.cos(radians)  # y分量 (负号因为屏幕y轴向下)
        ]) * 0.5  # 重力大小保持0.5

    def apply_gravity_to_ball(self, ball):
        """对小球应用重力并更新位置"""
        ball.velocity += self.gravity
        ball.update_position()

        # 可选：添加速度限制
        max_speed = 10
        speed = np.linalg.norm(ball.velocity)
        if speed > max_speed:
            ball.velocity = ball.velocity / speed * max_speed

    def control_ball(self, ball, direction):
        pass