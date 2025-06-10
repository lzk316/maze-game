import numpy as np

class NonGravityMode:
    def __init__(self):
        self.name = "Non-Gravity Mode"
        self.movement_speed = 10
        self.rotation_center = None  # 旋转中心点
        self.current_angle = 0.0  # 当前旋转角度（弧度）
        self.elasticity = 0.05  # 弹性系数
        self.max_bounce_velocity = 15  # 最大反弹速度

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

        # 直接更新位置
        ball.position += ball.velocity

    def set_rotation_center(self, center):
        """设置旋转中心点"""
        self.rotation_center = np.array(center)

    def rotate_map(self, direction):
        """处理地图旋转逻辑"""
        if direction == 'left':
            self.current_angle += 0.05  # 旋转速度（弧度/帧）
        elif direction == 'right':
            self.current_angle -= 0.05  # 旋转速度（弧度/帧）

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

    def handle_collision(self, ball, collision_type, collision_point=None):
        """处理碰撞并返回碰撞法向量"""
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

        # 完全消除垂直墙壁的速度分量（无反弹）
        velocity_along_normal = np.dot(ball.velocity, normal)
        ball.velocity -= velocity_along_normal * normal

        # 限制最大速度
        speed = np.linalg.norm(ball.velocity)
        if speed > self.max_bounce_velocity:
            ball.velocity = ball.velocity / speed * self.max_bounce_velocity

        return {"normal": normal}