import pygame
import math
from src.obstacle import Obstacle


class Thorn(Obstacle):
    def __init__(self, position, size):
        """
        初始化荆棘障碍物

        参数:
            position: (x, y) 荆棘的中心位置
            size: 荆棘的大小(边长)
        """
        super().__init__(position)
        self.size = size
        self.color = (0, 255, 0)  # 绿色荆棘
        self.damage = True  # 是否造成伤害
        self.spikes = 5  # 尖刺数量
        self.spike_length = size // 2

        # 预计算尖刺顶点坐标(优化性能)
        self.spike_points = []
        self._calculate_spike_points()

    def _calculate_spike_points(self):
        """计算尖刺的顶点坐标"""
        center_x, center_y = self.position
        angle_step = 2 * math.pi / self.spikes

        self.spike_points = []
        for i in range(self.spikes):
            # 内点(靠近中心)
            inner_angle = i * angle_step
            inner_radius = self.size // 4
            inner_x = center_x + inner_radius * math.cos(inner_angle)
            inner_y = center_y + inner_radius * math.sin(inner_angle)

            # 外点(尖刺尖端)
            outer_angle = inner_angle
            outer_x = center_x + self.spike_length * math.cos(outer_angle)
            outer_y = center_y + self.spike_length * math.sin(outer_angle)

            # 下一个内点(形成三角形)
            next_inner_angle = (i + 1) * angle_step
            next_inner_x = center_x + inner_radius * math.cos(next_inner_angle)
            next_inner_y = center_y + inner_radius * math.sin(next_inner_angle)

            self.spike_points.append(((inner_x, inner_y), (outer_x, outer_y), (next_inner_x, next_inner_y)))

    def check_collision(self, ball):
        """
        检查小球与荆棘的碰撞

        参数:
            ball: Ball对象

        返回:
            bool: 是否发生碰撞
        """
        # 简单的圆形与多边形碰撞检测
        ball_x, ball_y = ball.position
        ball_radius = ball.radius
        center_x, center_y = self.position

        # 首先检查与包围圆的碰撞(优化性能)
        distance_sq = (ball_x - center_x) ** 2 + (ball_y - center_y) ** 2
        if distance_sq > (self.spike_length + ball_radius) ** 2:
            return False

        # 然后检查与每个尖刺的碰撞
        for spike in self.spike_points:
            inner, outer, next_inner = spike

            # 三角形边1: inner -> outer
            if self._line_circle_collision(inner, outer, (ball_x, ball_y), ball_radius):
                return True

            # 三角形边2: outer -> next_inner
            if self._line_circle_collision(outer, next_inner, (ball_x, ball_y), ball_radius):
                return True

            # 三角形边3: next_inner -> inner (通常不需要检查，因为在内圈)

        return False

    def _line_circle_collision(self, line_start, line_end, circle_center, circle_radius):
        """
        检查线段与圆的碰撞

        参数:
            line_start: (x, y) 线段起点
            line_end: (x, y) 线段终点
            circle_center: (x, y) 圆心
            circle_radius: 圆半径

        返回:
            bool: 是否发生碰撞
        """
        # 将线段表示为向量
        line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
        line_len_sq = line_vec[0] ** 2 + line_vec[1] ** 2

        # 如果线段长度为0，退化为点与圆的碰撞
        if line_len_sq == 0:
            return (line_start[0] - circle_center[0]) ** 2 + (
                        line_start[1] - circle_center[1]) ** 2 <= circle_radius ** 2

        # 计算投影点
        to_start_vec = (circle_center[0] - line_start[0], circle_center[1] - line_start[1])
        t = max(0, min(1, (to_start_vec[0] * line_vec[0] + to_start_vec[1] * line_vec[1]) / line_len_sq))
        projection = (line_start[0] + t * line_vec[0], line_start[1] + t * line_vec[1])

        # 检查距离
        dist_sq = (circle_center[0] - projection[0]) ** 2 + (circle_center[1] - projection[1]) ** 2
        return dist_sq <= circle_radius ** 2

    def activate(self):
        """激活荆棘效果"""
        # 当小球碰到荆棘时调用
        print("荆棘激活! 小球将重置位置")
        return True  # 返回True表示需要重置小球

    def draw(self, screen):
        """绘制荆棘"""
        # 绘制中心圆
        pygame.draw.circle(screen, (100, 200, 100),
                           (int(self.position[0]), int(self.position[1])),
                           self.size // 4)

        # 绘制尖刺
        for spike in self.spike_points:
            inner, outer, next_inner = spike
            pygame.draw.polygon(screen, self.color, [inner, outer, next_inner])

        # 绘制尖刺边框(可选)
        for spike in self.spike_points:
            inner, outer, next_inner = spike
            pygame.draw.line(screen, (0, 100, 0), inner, outer, 2)
            pygame.draw.line(screen, (0, 100, 0), outer, next_inner, 2)