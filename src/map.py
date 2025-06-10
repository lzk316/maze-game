import pygame
import numpy as np
from obstacle import Obstacle
from trap import Trap
import os
from pathlib import Path


class Map:
    def __init__(self, image_path, scale=100):
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
        self.game_width = self.raw_width * scale  # 游戏逻辑宽度（扩大100倍）
        self.game_height = self.raw_height * scale  # 游戏逻辑高度（扩大100倍）

        # 添加UI显示比例
        self.ui_scale = 0.1  # UI显示缩小10倍
        self.ui_width = int(self.game_width * self.ui_scale)
        self.ui_height = int(self.game_height * self.ui_scale)

        # 游戏元素
        self.walls = []
        self.traps = []
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
                # 蓝色是终点 (0, 0, 255)
                elif (pixel == [0, 0, 255]).all():
                    self.end_position = (x * self.scale + self.scale // 2,
                                         y * self.scale + self.scale // 2)
                    self.end_radius = self.obstacle_radius

    def get_start_position(self):
        """获取起始位置"""
        return self.start_position

    def get_transformed_walls(self, gravity_mode):
        """返回旋转变换后的墙体位置（用于碰撞检测）"""
        if not gravity_mode:
            return self.walls

        transformed_walls = []
        for wall in self.walls:
            x, y, w, h = wall
            corners = [
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h)
            ]
            rotated = [gravity_mode.transform_point(corner) for corner in corners]

            # 得到外接矩形
            xs = [p[0] for p in rotated]
            ys = [p[1] for p in rotated]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max_x - min_x
            height = max_y - min_y
            transformed_walls.append((min_x, min_y, width, height))

        return transformed_walls

    def check_collision(self, ball, gravity_mode=None):
        if gravity_mode:
            ball_pos = gravity_mode.transform_point(ball.position)
        else:
            ball_pos = ball.position

        # 使用圆形碰撞检测而不是矩形
        ball_circle = (ball_pos[0], ball_pos[1], ball.radius)

        # 1. 检查终点
        if self.end_position:
            end_pos = np.array(self.end_position)
            if gravity_mode:
                end_pos = gravity_mode.transform_point(end_pos)

            distance = np.linalg.norm(ball_pos - end_pos)
            if distance < (ball.radius + self.end_radius):
                return {"type": "goal", "point": end_pos}

        # 2. 检查陷阱
        for trap in self.traps:
            trap_pos = np.array(trap.position)
            if gravity_mode:
                trap_pos = gravity_mode.transform_point(trap_pos)

            distance = np.linalg.norm(ball_pos - trap_pos)
            if distance < (ball.radius + trap.radius):
                trap.activate()
                return {"type": "trap", "point": trap_pos}

        # 3. 精确的墙壁碰撞检测
        walls = self.get_transformed_walls(gravity_mode)
        for wall in walls:
            wall_rect = pygame.Rect(wall)

            # 计算球心到矩形的最短距离
            closest_x = max(wall_rect.left, min(ball_pos[0], wall_rect.right))
            closest_y = max(wall_rect.top, min(ball_pos[1], wall_rect.bottom))

            distance_x = ball_pos[0] - closest_x
            distance_y = ball_pos[1] - closest_y
            distance = np.sqrt(distance_x ** 2 + distance_y ** 2)

            if distance < ball.radius:
                # 计算碰撞法向量
                if distance == 0:  # 球心在矩形内
                    # 找出最短的逃脱方向
                    dist_left = abs(ball_pos[0] - wall_rect.left)
                    dist_right = abs(ball_pos[0] - wall_rect.right)
                    dist_top = abs(ball_pos[1] - wall_rect.top)
                    dist_bottom = abs(ball_pos[1] - wall_rect.bottom)

                    min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

                    if min_dist == dist_left:
                        normal = np.array([-1, 0])
                    elif min_dist == dist_right:
                        normal = np.array([1, 0])
                    elif min_dist == dist_top:
                        normal = np.array([0, -1])
                    else:
                        normal = np.array([0, 1])
                else:
                    normal = np.array([distance_x, distance_y]) / distance

                collision_point = np.array([closest_x, closest_y])

                # 确定碰撞类型
                if abs(ball_pos[0] - wall_rect.left) < ball.radius:
                    return {"type": "wall_left", "point": collision_point, "normal": normal}
                elif abs(ball_pos[0] - wall_rect.right) < ball.radius:
                    return {"type": "wall_right", "point": collision_point, "normal": normal}
                elif abs(ball_pos[1] - wall_rect.top) < ball.radius:
                    return {"type": "wall_top", "point": collision_point, "normal": normal}
                elif abs(ball_pos[1] - wall_rect.bottom) < ball.radius:
                    return {"type": "wall_bottom", "point": collision_point, "normal": normal}
                else:
                    return {"type": "wall", "point": collision_point, "normal": normal}

        # 4. 检查地图边界
        boundary_collision = False
        normal = np.array([0, 0])

        if ball_pos[0] < ball.radius:
            boundary_collision = True
            normal += np.array([1, 0])
        if ball_pos[0] > self.game_width - ball.radius:
            boundary_collision = True
            normal += np.array([-1, 0])
        if ball_pos[1] < ball.radius:
            boundary_collision = True
            normal += np.array([0, 1])
        if ball_pos[1] > self.game_height - ball.radius:
            boundary_collision = True
            normal += np.array([0, -1])

        if boundary_collision:
            if np.linalg.norm(normal) > 0:
                normal = normal / np.linalg.norm(normal)
            collision_point = np.array([
                max(ball.radius, min(ball_pos[0], self.game_width - ball.radius)),
                max(ball.radius, min(ball_pos[1], self.game_height - ball.radius))
            ])
            return {"type": "boundary", "point": collision_point, "normal": normal}

        return None

    def calculate_offset(self, screen_width, screen_height):
        """计算地图居中所需的偏移量"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x = (screen_width - self.ui_width) // 2
        self.offset_y = (screen_height - self.ui_height) // 2

    def draw(self, screen, gravity_mode=None):
        """绘制地图（基于逻辑坐标旋转，再缩放并偏移到UI）"""
        self.calculate_offset(screen.get_width(), screen.get_height())

        # 绘制背景（可选）
        screen.fill((240, 240, 240))  # 浅灰色背景

        # 获取变换函数（如果有）
        transform_func = gravity_mode.transform_point if gravity_mode else lambda p: p

        # 绘制墙壁
        for wall in self.walls:
            x, y, w, h = wall
            # 定义墙体的四个角（逻辑坐标）
            corners = [
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h)
            ]
            # 旋转逻辑坐标（如果有重力模式）
            rotated_corners = [transform_func(corner) for corner in corners]
            # 缩小到UI坐标并加上偏移量
            screen_corners = [
                (
                    int(corner[0] * self.ui_scale + self.offset_x),
                    int(corner[1] * self.ui_scale + self.offset_y)
                )
                for corner in rotated_corners
            ]
            pygame.draw.polygon(screen, (0, 0, 0), screen_corners)

        # 绘制陷阱
        for trap in self.traps:
            # 获取陷阱的逻辑坐标
            trap_pos = trap.position
            # 旋转逻辑坐标（如果有重力模式）
            if gravity_mode:
                trap_pos = transform_func(trap_pos)
            # 缩小到UI坐标并加上偏移量
            screen_pos = (
                int(trap_pos[0] * self.ui_scale + self.offset_x),
                int(trap_pos[1] * self.ui_scale + self.offset_y)
            )
            # 绘制陷阱（半径也缩小10倍）
            pygame.draw.circle(
                screen,
                trap.color,
                screen_pos,
                int(trap.radius * self.ui_scale)
            )

        # 绘制终点
        if self.end_position:
            # 获取终点的逻辑坐标
            end_pos = self.end_position
            # 旋转逻辑坐标（如果有重力模式）
            if gravity_mode:
                end_pos = transform_func(end_pos)
            # 缩小到UI坐标并加上偏移量
            screen_pos = (
                int(end_pos[0] * self.ui_scale + self.offset_x),
                int(end_pos[1] * self.ui_scale + self.offset_y)
            )
            # 绘制终点（半径也缩小10倍）
            pygame.draw.circle(
                screen,
                (0, 0, 255),  # 蓝色
                screen_pos,
                int(self.end_radius * self.ui_scale)
            )
