import pygame
from src.obstacle import Obstacle
from src.trap import Trap
from src.thorn import Thorn
from src.flameguard import FlameGuard


class Map:
    def __init__(self, level_number, cell_size=30):
        self.level_number = level_number
        self.cell_size = cell_size
        self.width = 750  # 地图宽度(像素)
        self.height = 750  # 地图高度(像素)
        self.rows = self.height // cell_size
        self.cols = self.width // cell_size
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.walls = []
        self.traps = []
        self.thorns = []
        self.flame_guards = []
        self.start_pos = (1, 1)  # 起始位置(格子坐标)
        self.end_pos = (self.cols - 2, self.rows - 2)  # 结束位置(格子坐标)

        # 初始化地图边界
        self._init_borders()

    def _init_borders(self):
        """初始化地图边界墙"""
        for i in range(self.rows):
            self._set_cell(i, 0, "wall")
            self._set_cell(i, self.cols - 1, "wall")
        for j in range(self.cols):
            self._set_cell(0, j, "wall")
            self._set_cell(self.rows - 1, j, "wall")

    def generate_map(self):
        """根据关卡号生成地图"""
        # 这里可以根据level_number生成不同的地图
        # 示例：简单的迷宫
        self._set_cell(5, 5, "trap")
        self._set_cell(10, 10, "thorn")
        self._set_cell(15, 15, "flame_guard")

        # 添加一些墙
        for i in range(5, 15):
            self._set_cell(i, 8, "wall")
        for j in range(5, 15):
            self._set_cell(12, j, "wall")

    def _set_cell(self, row, col, cell_type):
        """设置格子类型"""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False

        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2

        # 清除原有内容
        if self.grid[row][col]:
            if isinstance(self.grid[row][col], Trap) and self.grid[row][col] in self.traps:
                self.traps.remove(self.grid[row][col])
            elif isinstance(self.grid[row][col], Thorn) and self.grid[row][col] in self.thorns:
                self.thorns.remove(self.grid[row][col])
            elif isinstance(self.grid[row][col], FlameGuard) and self.grid[row][col] in self.flame_guards:
                self.flame_guards.remove(self.grid[row][col])
            elif self.grid[row][col] == "wall" and (row, col) in self.walls:
                self.walls.remove((row, col))

        # 设置新内容
        if cell_type == "wall":
            self.grid[row][col] = "wall"
            self.walls.append((row, col))
        elif cell_type == "trap":
            trap = Trap((x, y), self.cell_size // 2 - 2)
            self.grid[row][col] = trap
            self.traps.append(trap)
        elif cell_type == "thorn":
            thorn = Thorn((x, y), self.cell_size)
            self.grid[row][col] = thorn
            self.thorns.append(thorn)
        elif cell_type == "flame_guard":
            flame_guard = FlameGuard((x, y), 150)  # 150是巡逻范围
            self.grid[row][col] = flame_guard
            self.flame_guards.append(flame_guard)
        elif cell_type == "empty":
            self.grid[row][col] = None
        elif cell_type == "start":
            self.start_pos = (row, col)
            self.grid[row][col] = "start"
        elif cell_type == "end":
            self.end_pos = (row, col)
            self.grid[row][col] = "end"

        return True

    def get_cell_type(self, row, col):
        """获取格子类型"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return type(self.grid[row][col]).__name__ if self.grid[row][col] and not isinstance(self.grid[row][col],
                                                                                                str) else \
            self.grid[row][col]
        return None

    def check_collision(self, ball):
        """检查小球与障碍物的碰撞"""
        # 检查墙壁碰撞
        ball_row = int(ball.position[1] / self.cell_size)
        ball_col = int(ball.position[0] / self.cell_size)

        # 检查当前格子及周围格子
        for r in range(max(0, ball_row - 1), min(self.rows, ball_row + 2)):
            for c in range(max(0, ball_col - 1), min(self.cols, ball_col + 2)):
                if self.grid[r][c] == "wall":
                    # 简单矩形碰撞检测
                    wall_x = c * self.cell_size
                    wall_y = r * self.cell_size
                    if (wall_x < ball.position[0] < wall_x + self.cell_size and
                            wall_y < ball.position[1] < wall_y + self.cell_size):
                        return True

                elif isinstance(self.grid[r][c], Obstacle):
                    if self.grid[r][c].check_collision(ball):
                        self.grid[r][c].activate()
                        return True

        return False

    def update(self):
        """更新地图上的动态元素(如火焰守卫)"""
        for flame_guard in self.flame_guards:
            flame_guard.update(self.ball.position if hasattr(self, 'ball') else (0, 0))

    def draw(self, screen):
        """绘制地图"""
        # 绘制背景格子
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        # 绘制墙壁
        for row, col in self.walls:
            pygame.draw.rect(screen, (100, 100, 100),
                             (col * self.cell_size, row * self.cell_size,
                              self.cell_size, self.cell_size))

        # 绘制陷阱
        for trap in self.traps:
            trap.draw(screen)

        # 绘制荆棘
        for thorn in self.thorns:
            thorn.draw(screen)

        # 绘制火焰守卫
        for flame_guard in self.flame_guards:
            flame_guard.draw(screen)

        # 绘制起点和终点
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        pygame.draw.rect(screen, (0, 255, 0),
                         (start_col * self.cell_size, start_row * self.cell_size,
                          self.cell_size, self.cell_size), 3)

        pygame.draw.rect(screen, (255, 0, 0),
                         (end_col * self.cell_size, end_row * self.cell_size,
                          self.cell_size, self.cell_size), 3)

    def get_pixel_position(self, row, col):
        """获取格子的中心像素坐标"""
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        return (x, y)

    def get_grid_position(self, x, y):
        """获取像素坐标对应的格子坐标"""
        row = y // self.cell_size
        col = x // self.cell_size
        return (row, col)