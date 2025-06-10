import numpy as np
import pygame


class GravityMode:
    def __init__(self):
        self.name = "Gravity Mode"
        self.gravity = np.array([0, 9.8])  # 物理标准重力加速度(m/s^2)
        self.rotation_speed = 1.5  # 旋转速度(弧度/秒)
        self.current_angle = 0  # 当前旋转角度(弧度)
        self.pixels_per_meter = 50  # 像素/米比例
        self.time_step = 1 / 60.0  # 假设60FPS
        self.rotation_center = None  # 旋转中心点

        # 物理参数
        self.elasticity = 0.05  # 弹性系数
        self.max_bounce_velocity = 15  # 最大反弹速度

    def set_rotation_center(self, center):
        """设置旋转中心点(通常为屏幕中心)"""
        self.rotation_center = np.array(center)

    def rotate_map(self, direction):
        """处理地图旋转逻辑"""
        if direction == 'left':
            self.current_angle += self.rotation_speed * self.time_step
        elif direction == 'right':
            self.current_angle -= self.rotation_speed * self.time_step

    def apply_gravity_to_ball(self, ball):
        """保持重力垂直向下，更新小球运动（坐标不旋转）"""

        # 转换为物理单位 (像素 -> 米)
        position_m = ball.position / self.pixels_per_meter
        velocity_m = ball.velocity / self.pixels_per_meter

        # 恒定垂直向下的重力
        gravity = np.array([0.0, 9.8])

        # 速度更新
        velocity_m += gravity * self.time_step

        # 位置更新
        position_m += velocity_m * self.time_step

        # 转换回游戏单位
        ball.velocity = velocity_m * self.pixels_per_meter
        ball.position = position_m * self.pixels_per_meter

    def get_transform_matrix(self):
        """获取当前旋转的变换矩阵"""
        if self.rotation_center is None:
            return None

        center_x, center_y = self.rotation_center  # 使用地图的中心作为旋转中心

        # 创建旋转矩阵
        cos_val = np.cos(self.current_angle)
        sin_val = np.sin(self.current_angle)

        # 变换矩阵: 平移至原点 → 旋转 → 平移回原位置
        transform = np.array([
            [cos_val, -sin_val, center_x * (1 - cos_val) + center_y * sin_val],
            [sin_val, cos_val, center_y * (1 - cos_val) - center_x * sin_val],
            [0, 0, 1]
        ])
        return transform

    def transform_point(self, point):
        """应用当前旋转变换到指定点"""
        if self.rotation_center is None:
            return point

        # 转换为齐次坐标
        homogenous = np.array([point[0], point[1], 1])

        # 应用变换
        transformed = np.dot(self.get_transform_matrix(), homogenous)

        return transformed[:2]

    def handle_collision(self, ball, collision_type):
        """处理小球与墙壁/边界的碰撞反弹"""
        if collision_type == "wall_left" or collision_type == "wall_right":
            # 水平方向反弹 (x轴速度取反)
            ball.velocity[0] = -ball.velocity[0] * self.elasticity
            # 限制最大反弹速度
            if abs(ball.velocity[0]) > self.max_bounce_velocity:
                ball.velocity[0] = self.max_bounce_velocity * (1 if ball.velocity[0] > 0 else -1)

        elif collision_type == "wall_top" or collision_type == "wall_bottom":
            # 垂直方向反弹 (y轴速度取反)
            ball.velocity[1] = -ball.velocity[1] * self.elasticity
            # 限制最大反弹速度
            if abs(ball.velocity[1]) > self.max_bounce_velocity:
                ball.velocity[1] = self.max_bounce_velocity * (1 if ball.velocity[1] > 0 else -1)

        elif collision_type == "wall" or collision_type == "boundary":
            # 通用反弹 (两个方向速度都取反)
            ball.velocity = -ball.velocity * self.elasticity
            # 限制速度大小
            speed = np.linalg.norm(ball.velocity)
            if speed > self.max_bounce_velocity:
                ball.velocity = ball.velocity / speed * self.max_bounce_velocity