import pygame
import numpy as np
from obstacle import Obstacle
from thorn import Thorn
from trap import Trap
import os
from pathlib import Path

class Map:
    def __init__(self, image_path, scale=100, difficulty="hard"):
        # 构建正确的图片路径
        self.difficulty = difficulty
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
        self.game_width = self.raw_width * scale  # 游戏逻辑宽度（扩大100倍）
        self.game_height = self.raw_height * scale  # 游戏逻辑高度（扩大100倍）

        # 添加UI显示比例
        self.ui_scale = 0.1  # UI显示缩小10倍
        self.ui_width = int(self.game_width * self.ui_scale)
        self.ui_height = int(self.game_height * self.ui_scale)

        # 游戏元素
        self.walls = []
        self.traps = []
        self.thorns = []
        self.start_position = None
        self.end_position = None
        self.obstacle_radius = 150

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
                # 紫色是荆棘 (255, 0, 255)
                elif (pixel == [255, 0, 255]).all():
                    if self.difficulty == "hard":
                        thorn_pos = (x * self.scale + self.scale // 2,
                                 y * self.scale + self.scale // 2)
                        self.thorns.append(Thorn(thorn_pos, size=300))
                # 蓝色是终点 (0, 0, 255)
                elif (pixel == [0, 0, 255]).all():
                    self.end_position = (x * self.scale + self.scale // 2,
                                         y * self.scale + self.scale // 2)
                    self.end_radius = self.obstacle_radius

    def get_start_position(self):
        """获取起始位置"""
        return self.start_position

    def calculate_offset(self, screen_width, screen_height):
        """计算地图居中所需的偏移量"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x = (screen_width - self.ui_width) // 2
        self.offset_y = (screen_height - self.ui_height) // 2

    def draw(self, screen, rotation_angle=0):
        """绘制地图"""
        self.calculate_offset(screen.get_width(), screen.get_height())

        # 绘制背景（可选）
        screen.fill((240, 240, 240))  # 浅灰色背景

        # 绘制墙壁
        for wall in self.walls:
            x, y, w, h = wall
            # 缩小到UI坐标并加上偏移量
            screen_rect = pygame.Rect(
                x * self.ui_scale + self.offset_x,
                y * self.ui_scale + self.offset_y,
                w * self.ui_scale,
                h * self.ui_scale
            )
            pygame.draw.rect(screen, (0, 0, 0), screen_rect)

        # 绘制陷阱
        for trap in self.traps:
            # 缩小到UI坐标并加上偏移量
            screen_pos = (
                trap.position[0] * self.ui_scale + self.offset_x,
                trap.position[1] * self.ui_scale + self.offset_y
            )
            # 绘制陷阱（半径也缩小10倍）
            pygame.draw.circle(
                screen,
                trap.color,
                (int(screen_pos[0]), int(screen_pos[1])),
                int(trap.radius * self.ui_scale)
            )

        for thorn in self.thorns:
            if thorn.is_visible:
                # 缩小到UI坐标并加上偏移量
                screen_pos = (
                    thorn.position[0] * self.ui_scale + self.offset_x,
                    thorn.position[1] * self.ui_scale + self.offset_y
                )
                # 绘制荆棘（边长也缩小10倍）
                pygame.draw.rect(
                    screen,
                    thorn.color,
                    (screen_pos[0] - thorn.size // 2 * self.ui_scale,
                     screen_pos[1] - thorn.size // 2 * self.ui_scale,
                     thorn.size * self.ui_scale,
                     thorn.size * self.ui_scale)
                )

        # 绘制终点
        if self.end_position:
            # 缩小到UI坐标并加上偏移量
            screen_pos = (
                self.end_position[0] * self.ui_scale + self.offset_x,
                self.end_position[1] * self.ui_scale + self.offset_y
            )
            # 绘制终点（半径也缩小10倍）
            pygame.draw.circle(
                screen,
                (0, 0, 255),  # 蓝色
                (int(screen_pos[0]), int(screen_pos[1])),
                int(self.end_radius * self.ui_scale)
            )