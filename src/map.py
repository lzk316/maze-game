import pygame
import numpy as np
from obstacle import Obstacle
from trap import Trap
import os
from pathlib import Path


class Map:
    def __init__(self, image_path, scale=10):
        # 构建正确的图片路径
        base_dir = Path(__file__).parent.parent  # 获取上级目录
        full_path = base_dir / "assets" / "images" / image_path

        try:
            self.image = pygame.image.load(str(full_path))
            self.image_array = pygame.surfarray.array3d(self.image).swapaxes(0,1)
        except FileNotFoundError:
            raise FileNotFoundError(f"地图图片未找到: {full_path}")
        except pygame.error:
            raise ValueError(f"无法加载图片: {full_path}")
        self.scale = scale
        self.width = self.image.get_width() * scale
        self.height = self.image.get_height() * scale
        self.walls = []
        self.traps = []
        self.start_position = None
        self.end_position = None
        self.obstacle_radius = 15
        self.offset_x = 0  # 水平偏移量
        self.offset_y = 0  # 垂直偏移量

        self.parse_map()

    def parse_map(self):
        """解析地图图像，识别元素"""
        height, width, _ = self.image_array.shape

        for y in range(height):
            for x in range(width):
                pixel = self.image_array[y, x]
                # 黑色是墙壁 (0, 0, 0)
                if (pixel == [0, 0, 0]).all():
                    self.walls.append((x * self.scale, y * self.scale,
                                       self.scale, self.scale))
                # 绿色是起点 (0, 255, 0)
                elif (pixel == [0, 255, 0]).all():
                    self.start_position = (x * self.scale + self.scale // 2,
                                           y * self.scale + self.scale // 2)
                # 红色是陷阱 (255, 0, 0)
                elif (pixel == [255, 0, 0]).all():
                    trap_pos = (x * self.scale + self.scale // 2,
                                y * self.scale + self.scale // 2)
                    self.traps.append(Trap(trap_pos, self.obstacle_radius))
                # 蓝色是终点 (0, 0, 255)
                elif (pixel == [0, 0, 255]).all():
                    self.end_position = (x * self.scale + self.scale // 2,
                                         y * self.scale + self.scale // 2)
                    self.end_radius = self.obstacle_radius

    def get_start_position(self):
        """获取起始位置"""
        if self.start_position:
            return (self.start_position[0] + self.offset_x,
                    self.start_position[1] + self.offset_y)
        return None

    def check_collision(self, ball):
        """检查碰撞：墙壁矩形碰撞，陷阱圆形碰撞"""
        # 调整球的位置以考虑地图偏移
        adjusted_ball_pos = (ball.position[0] - self.offset_x,
                             ball.position[1] - self.offset_y)

        # 墙壁碰撞（矩形）
        ball_rect = pygame.Rect(
            adjusted_ball_pos[0] - ball.radius,
            adjusted_ball_pos[1] - ball.radius,
            ball.radius * 2,
            ball.radius * 2
        )

        for wall in self.walls:
            wall_rect = pygame.Rect(wall)
            if wall_rect.colliderect(ball_rect):
                return True

        # 陷阱碰撞（圆形）
        for trap in self.traps:
            if trap.check_collision(ball):
                trap.activate()
                return True

        return False

    def check_win_condition(self, ball):
        """检查是否到达终点（圆形碰撞）"""
        if not self.end_position:
            return False

        # 调整球的位置以考虑地图偏移
        adjusted_ball_pos = np.array([ball.position[0] - self.offset_x,
                                      ball.position[1] - self.offset_y])
        adjusted_end_pos = np.array([self.end_position[0],
                                     self.end_position[1]])

        distance = np.linalg.norm(adjusted_ball_pos - adjusted_end_pos)
        return distance < (ball.radius + self.end_radius)

    def calculate_offset(self, screen_width, screen_height):
        """计算地图居中所需的偏移量"""
        self.offset_x = (screen_width - self.width) // 2
        self.offset_y = (screen_height - self.height) // 2

    def draw(self, screen):
        """绘制地图"""
        screen_width, screen_height = screen.get_size()
        self.calculate_offset(screen_width, screen_height)

        # 绘制墙壁
        for wall in self.walls:
            adjusted_wall = (
                wall[0] + self.offset_x,
                wall[1] + self.offset_y,
                wall[2],
                wall[3]
            )
            pygame.draw.rect(screen, (0, 0, 0), adjusted_wall)

        # 绘制陷阱
        for trap in self.traps:
            adjusted_pos = (
                trap.position[0] + self.offset_x,
                trap.position[1] + self.offset_y
            )
            pygame.draw.circle(screen, trap.color,
                               (int(adjusted_pos[0]), int(adjusted_pos[1])),
                               trap.radius)

        # 绘制终点
        if self.end_position:
            adjusted_end_pos = (
                self.end_position[0] + self.offset_x,
                self.end_position[1] + self.offset_y
            )
            pygame.draw.circle(screen, (0, 0, 255),
                               (int(adjusted_end_pos[0]), int(adjusted_end_pos[1])),
                               self.end_radius)