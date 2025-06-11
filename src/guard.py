# guard.py
import numpy as np
import pygame
from queue import PriorityQueue
import math
import time


class Guard:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float64)
        self.radius = 100  # 与小球的半径相同
        self.speed = 300.0 # 像素/秒
        self.state = "patrol"  # 初始状态：巡逻
        self.patrol_range = 1500  # 巡逻范围
        self.patrol_points = []  # 巡逻点
        self.patrol_target = 0  # 当前巡逻目标点索引
        self.path = []  # 寻路路径
        self.last_move_time = 0  # 上次移动时间
        self.grid_size = 100  # 网格大小（像素）
        self.grid_width = 65  # 网格宽度
        self.grid_height = 65  # 网格高度
        self.pathfinding_cooldown = 0  # 寻路冷却时间
        self.pathfinding_interval = 1  # 寻路最小间隔(秒)

        # 初始化巡逻点 (垂直巡逻)
        self.patrol_points.append(np.array(position))
        self.patrol_points.append(np.array([position[0], position[1] - self.patrol_range]))

    def update(self, game_map, ball_position, current_time):
        """更新守卫状态"""
        if current_time - self.last_move_time < 0.5:
            return

        self.last_move_time = current_time
        distance_to_ball = np.linalg.norm(self.position - ball_position)

        # 状态转换逻辑
        if self.state == "patrol":
            if distance_to_ball <= self.patrol_range * 1.2:
                self.state = "chase"
                self.path = []
        elif self.state == "chase":
            if distance_to_ball > self.patrol_range * 1.2:
                self.state = "return"
                self._find_nearest_patrol_point()
                self.path = []
        elif self.state == "return":
            # 检查是否应该切换回追逐状态
            if distance_to_ball <= self.patrol_range * 1.2:
                self.state = "chase"
                self.path = []
            # 检查是否到达巡逻点
            elif np.linalg.norm(self.position - self.patrol_points[self.patrol_target]) < 50:
                self.state = "patrol"
                self.patrol_target = 0

        # 行为执行逻辑
        if self.state == "patrol":
            self._patrol()
        elif self.state == "chase":
            self._chase(game_map, ball_position)
        elif self.state == "return":
            self._return_to_patrol(game_map)  # 确保调用返回行为

    def _patrol(self):
        """巡逻行为"""
        target = self.patrol_points[self.patrol_target]
        direction = target - self.position
        distance = np.linalg.norm(direction)

        if distance < 50:  # 到达目标点
            # 切换巡逻目标点
            self.patrol_target = 1 if self.patrol_target == 0 else 0
            target = self.patrol_points[self.patrol_target]
            direction = target - self.position
            distance = np.linalg.norm(direction)

        if distance > 0:
            # 垂直移动
            direction = direction / distance
            self.position = (self.position + direction * min(float(distance), self.speed)).astype(np.float64)
    def _chase(self, game_map, ball_position):
        """追逐行为"""
        current_time = time.time()
        # 如果没有路径或路径无效，重新寻路
        if (not self.path or
                current_time - self.pathfinding_cooldown > self.pathfinding_interval):
            self._find_path(game_map, ball_position)
            self.pathfinding_cooldown = current_time

        # 如果有路径，沿着路径移动
        if self.path:
            next_pos = self.path[0]
            direction = next_pos - self.position
            distance = np.linalg.norm(direction)

            if distance < 50:  # 到达路径点
                self.path.pop(0)  # 移除已到达的点
                if self.path:
                    next_pos = self.path[0]
                    direction = next_pos - self.position
                    distance = np.linalg.norm(direction)

            if distance > 0:
                direction = direction / distance
                self.position = (self.position + direction * min(float(distance), self.speed)).astype(np.float64)

    def _return_to_patrol(self, game_map):
        """返回巡逻点行为"""
        # 如果没有路径或路径无效，重新寻路
        if not self.path:
            target = self.patrol_points[self.patrol_target]
            self._find_path(game_map, target)

        # 如果有路径，沿着路径移动
        if self.path:
            next_pos = self.path[0]
            direction = next_pos - self.position
            distance = np.linalg.norm(direction)

            if distance < 50:  # 到达路径点
                self.path.pop(0)  # 移除已到达的点
                if not self.path:  # 如果这是路径的最后一个点
                    # 到达巡逻点，切换回巡逻状态
                    self.state = "patrol"
                    # 重置巡逻目标为最近的巡逻点
                    self._find_nearest_patrol_point()
                    return
                else:
                    next_pos = self.path[0]
                    direction = next_pos - self.position
                    distance = np.linalg.norm(direction)

            if distance > 0:
                direction = direction / distance
                self.position = (self.position + direction * min(float(distance), self.speed)).astype(np.float64)

    def _find_nearest_patrol_point(self):
        """找到最近的巡逻点"""
        min_distance = float('inf')
        nearest_index = 0

        for i, point in enumerate(self.patrol_points):
            distance = np.linalg.norm(self.position - point)
            if distance < min_distance:
                min_distance = distance
                nearest_index = i

        self.patrol_target = nearest_index

    def _position_to_grid(self, position):
        """将位置转换为网格坐标"""
        grid_x = max(0, min(self.grid_width - 1, int(position[0] / self.grid_size)))
        grid_y = max(0, min(self.grid_height - 1, int(position[1] / self.grid_size)))
        return (grid_x, grid_y)

    def _grid_to_position(self, grid):
        """将网格坐标转换为位置"""
        x = grid[0] * self.grid_size + self.grid_size / 2 -50
        y = grid[1] * self.grid_size + self.grid_size / 2 -50
        return np.array([x, y])

    def _find_path(self, game_map, target):
        """A*寻路算法 - 使用65x65网格地图"""
        # 创建网格地图 (65x65)
        grid = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]

        # 标记墙壁为障碍物
        for wall in game_map.walls:
            # 计算墙壁在网格中的位置
            x, y, w, h = wall
            grid_x1 = max(0, min(self.grid_width - 1, int(x / self.grid_size)))
            grid_y1 = max(0, min(self.grid_height - 1, int(y / self.grid_size)))
            grid_x2 = max(0, min(self.grid_width - 1, int((x + w) / self.grid_size)))
            grid_y2 = max(0, min(self.grid_height - 1, int((y + h) / self.grid_size)))

            # 标记墙壁覆盖的网格为障碍物
            for i in range(grid_x1, grid_x2 + 1):
                for j in range(grid_y1, grid_y2 + 1):
                    grid[i][j] = 1

        # 起点和终点（网格坐标）
        start = self._position_to_grid(self.position)
        end = self._position_to_grid(target)

        # A*算法实现
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}

        while not open_set.empty():
            current = open_set.get()[1]

            if current == end:
                # 重建路径（网格坐标 -> 实际位置）
                self.path = []
                while current in came_from:
                    self.path.insert(0, self._grid_to_position(current))
                    current = came_from[current]
                return

            # 四个方向：上、下、左、右
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)

                # 检查边界
                if (neighbor[0] < 0 or neighbor[0] >= self.grid_width or
                        neighbor[1] < 0 or neighbor[1] >= self.grid_height):
                    continue

                # 检查障碍物
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue

                # 计算新的G分数
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, end)
                    open_set.put((f_score[neighbor], neighbor))

        # 如果找不到路径，直接向目标移动
        self.path = [target]

    def _heuristic(self, a, b):
        """启发式函数（曼哈顿距离）"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def check_collision(self, ball):
        """检查与小球碰撞"""
        distance = np.linalg.norm(self.position - ball.position)
        return distance < (self.radius + ball.radius)

    def draw(self, screen, offset_x, offset_y, ui_scale):
        """绘制守卫"""
        ui_radius = int(self.radius * ui_scale)
        ui_pos = (int(self.position[0] * ui_scale + offset_x),
                  int(self.position[1] * ui_scale + offset_y))

        # 绘制黄色圆形
        pygame.draw.circle(screen, (255, 255, 0), ui_pos, ui_radius)

        # 绘制状态指示器
        if self.state == "patrol":
            color = (0, 255, 0)  # 绿色
        elif self.state == "chase":
            color = (255, 0, 0)  # 红色
        else:  # return
            color = (255, 165, 0)  # 橙色

        pygame.draw.circle(screen, color, ui_pos, 5)  # 中心点状态指示

        # 绘制路径（调试用）
        for i, point in enumerate(self.path):
            ui_point = (int(point[0] * ui_scale + offset_x),
                        int(point[1] * ui_scale + offset_y))
            pygame.draw.circle(screen, (0, 0, 255), ui_point, 3)
            if i > 0:
                prev_point = (int(self.path[i - 1][0] * ui_scale + offset_x),
                              int(self.path[i - 1][1] * ui_scale + offset_y))
                pygame.draw.line(screen, (0, 0, 255), prev_point, ui_point, 1)