import numpy as np
import pygame


class GravityMode:
    def __init__(self):
        self.name = "Gravity Mode"
        self.gravity = np.array([0, 9.8])  # 物理标准重力加速度(m/s^2)
        self.rotation_speed = 1  # 旋转速度(弧度/秒)
        self.current_angle = 0  # 当前旋转角度(弧度)
        self.pixels_per_meter = 100  # 像素/米比例
        self.time_step = 1 / 60.0  # 假设60FPS
        self.rotation_center = None  # 旋转中心点

        # 物理参数
        self.elasticity = 0.01  # 弹性系数
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

    def apply_gravity_to_ball(self, ball, collision_info=None):
        """应用重力（不考虑摩擦力）"""
        # 转换为物理单位 (像素 -> 米)
        position_m = ball.position / self.pixels_per_meter
        velocity_m = ball.velocity / self.pixels_per_meter

        # 恒定垂直向下的重力
        gravity = np.array([0.0, 9.8])

        if collision_info and "normal" in collision_info:
            # 有碰撞时，仅保留重力沿斜面的分量
            normal = collision_info["normal"]
            gravity_tangent = gravity - np.dot(gravity, normal) * normal
            acceleration = gravity_tangent
        else:
            # 无碰撞时，直接应用重力
            acceleration = gravity

        # 速度更新
        velocity_m += acceleration * self.time_step

        # 位置更新
        position_m += velocity_m * self.time_step

        # 转换回游戏单位
        ball.velocity = velocity_m * self.pixels_per_meter
        ball.position = position_m * self.pixels_per_meter

        # 更新球的旋转（仅基于水平速度）
        if np.linalg.norm(ball.velocity) > 0.1:
            horizontal_velocity = np.array([ball.velocity[0], 0])
            if np.linalg.norm(horizontal_velocity) > 0.1:
                ball.angular_velocity = np.linalg.norm(horizontal_velocity) / ball.radius
                direction = 1 if ball.velocity[0] > 0 else -1
                ball.rotation_angle += ball.angular_velocity * direction * self.time_step

    def handle_collision(self, ball, collision_type, collision_point=None):
        """处理碰撞并返回碰撞法向量（完全阻止穿透）"""
        if collision_type == "wall_left":
            normal = np.array([1, 0])  # 从右侧碰撞
        elif collision_type == "wall_right":
            normal = np.array([-1, 0])  # 从左侧碰撞
        elif collision_type == "wall_top":
            normal = np.array([0, 1])  # 从下方碰撞
        elif collision_type == "wall_bottom":
            normal = np.array([0, -1])  # 从上方碰撞
        else:
            # 通用碰撞，计算近似法向量
            if collision_point is not None:
                normal = (ball.position - collision_point)
                normal = normal / np.linalg.norm(normal)
            else:
                normal = -ball.velocity / np.linalg.norm(ball.velocity)

        # 完全消除垂直于墙壁的速度分量
        velocity_along_normal = np.dot(ball.velocity, normal)
        ball.velocity -= velocity_along_normal * normal

        # 确保小球不会嵌入墙体
        if collision_point is not None:
            penetration_depth = ball.radius - np.linalg.norm(ball.position - collision_point)
            if penetration_depth > 0:
                ball.position += normal * penetration_depth * 1.01  # 稍微推开一点

        print(f"碰撞类型: {collision_type}, 碰撞点: {collision_point}, 碰撞法向量: {normal}, 小球速度: {ball.velocity}")
        return {"normal": normal}

    def transform_point(self, point):
        """应用当前旋转变换到指定点"""
        if self.rotation_center is None:
            return point

        # 转换为齐次坐标
        homogenous = np.array([point[0], point[1], 1])

        # 获取变换矩阵
        transform = self.get_transform_matrix()

        # 应用变换
        transformed = np.dot(transform, homogenous)

        return transformed[:2]

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
