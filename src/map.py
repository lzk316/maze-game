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
            self.image_array = pygame.surfarray.array3d(self.image).swapaxes(0, 1)
        except FileNotFoundError:
            raise FileNotFoundError(f"地图图片未找到: {full_path}")
        except pygame.error:
            raise ValueError(f"无法加载图片: {full_path}")

        self.scale = scale
        self.raw_width = self.image.get_width()  # 原始图片宽度(像素)
        self.raw_height = self.image.get_height()  # 原始图片高度(像素)
        self.game_width = self.raw_width * scale  # 游戏逻辑宽度
        self.game_height = self.raw_height * scale  # 游戏逻辑高度

        # 游戏元素
        self.walls = []
        self.traps = []
        self.start_position = None
        self.end_position = None
        self.obstacle_radius = 15

        # UI显示相关
        self.screen_width = 0
        self.screen_height = 0
        self.offset_x = 0
        self.offset_y = 0

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
        return self.start_position  # 已经是游戏坐标，不需要加offset

    def check_collision(self, ball):
        """检查碰撞并返回碰撞类型"""
        ball_pos = np.array([ball.position[0], ball.position[1]])

        # 1. 检查终点
        if self.end_position:
            end_pos = np.array(self.end_position)
            distance = np.linalg.norm(ball_pos - end_pos)
            if distance < (ball.radius + self.end_radius):
                return "goal"

        # 2. 检查陷阱
        for trap in self.traps:
            trap_pos = np.array(trap.position)
            distance = np.linalg.norm(ball_pos - trap_pos)
            if distance < (ball.radius + trap.radius):
                trap.activate()
                return "trap"

        # 3. 检查墙壁
        ball_rect = pygame.Rect(
            ball.position[0] - ball.radius,
            ball.position[1] - ball.radius,
            ball.radius * 2,
            ball.radius * 2
        )

        for wall in self.walls:
            wall_rect = pygame.Rect(wall)
            if wall_rect.colliderect(ball_rect):
                # 计算从哪边碰撞
                if abs(ball_rect.left - wall_rect.right) < 5:
                    return "wall_right"
                elif abs(ball_rect.right - wall_rect.left) < 5:
                    return "wall_left"
                elif abs(ball_rect.top - wall_rect.bottom) < 5:
                    return "wall_bottom"
                elif abs(ball_rect.bottom - wall_rect.top) < 5:
                    return "wall_top"
                return "wall"

        # 4. 检查地图边界
        if (ball.position[0] < ball.radius or
                ball.position[0] > self.game_width - ball.radius or
                ball.position[1] < ball.radius or
                ball.position[1] > self.game_height - ball.radius):
            return "boundary"

        return None

    def calculate_offset(self, screen_width, screen_height):
        """计算地图居中所需的偏移量"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x = (screen_width - self.game_width) // 2
        self.offset_y = (screen_height - self.game_height) // 2

    def draw(self, screen):
        """绘制地图"""
        self.calculate_offset(screen.get_width(), screen.get_height())

        # 绘制背景（可选）
        screen.fill((240, 240, 240))  # 浅灰色背景


        # 绘制墙壁
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 0), (
                wall[0] + self.offset_x,
                wall[1] + self.offset_y,
                wall[2], wall[3]
            ))

        # 绘制陷阱
        for trap in self.traps:
            pygame.draw.circle(screen, trap.color,
                               (int(trap.position[0] + self.offset_x),
                                int(trap.position[1] + self.offset_y)),
                               trap.radius)

        # 绘制终点
        if self.end_position:
            pygame.draw.circle(screen, (0, 0, 255),
                               (int(self.end_position[0] + self.offset_x),
                                int(self.end_position[1] + self.offset_y)),
                               self.end_radius)