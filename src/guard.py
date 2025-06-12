
import numpy as np
import pygame
from queue import PriorityQueue

import time


class Guard:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float64)
        self.radius = 100
        self.speed = 300.0
        self.state = "patrol"
        self.patrol_range = 1500
        self.patrol_points = []
        self.patrol_target = 0
        self.path = []
        self.last_move_time = 0
        self.grid_size = 100
        self.grid_width = 65
        self.grid_height = 65
        self.pathfinding_cooldown = 0
        self.pathfinding_interval = 1


        self.patrol_points.append(np.array(position))
        self.patrol_points.append(np.array([position[0], position[1] - self.patrol_range]))

    def update(self, game_map, ball_position, current_time):

        if current_time - self.last_move_time < 0.5:
            return

        self.last_move_time = current_time
        distance_to_ball = np.linalg.norm(self.position - ball_position)


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

            if distance_to_ball <= self.patrol_range * 1.2:
                self.state = "chase"
                self.path = []

            elif np.linalg.norm(self.position - self.patrol_points[self.patrol_target]) < 50:
                self.state = "patrol"
                self.patrol_target = 0


        if self.state == "patrol":
            self._patrol()
        elif self.state == "chase":
            self._chase(game_map, ball_position)
        elif self.state == "return":
            self._return_to_patrol(game_map)

    def _patrol(self):

        target = self.patrol_points[self.patrol_target]
        direction = target - self.position
        distance = np.linalg.norm(direction)

        if distance < 50:

            self.patrol_target = 1 if self.patrol_target == 0 else 0
            target = self.patrol_points[self.patrol_target]
            direction = target - self.position
            distance = np.linalg.norm(direction)

        if distance > 0:

            direction = direction / distance
            self.position = (self.position + direction * min(float(distance), self.speed)).astype(np.float64)

    def _chase(self, game_map, ball_position):

        current_time = time.time()

        if (not self.path or
                current_time - self.pathfinding_cooldown > self.pathfinding_interval):
            self._find_path(game_map, ball_position)
            self.pathfinding_cooldown = current_time

        if self.path:
            next_pos = self.path[0]
            direction = next_pos - self.position
            distance = np.linalg.norm(direction)

            if distance < 50:
                self.path.pop(0)
                if self.path:
                    next_pos = self.path[0]
                    direction = next_pos - self.position
                    distance = np.linalg.norm(direction)

            if distance > 0:
                direction = direction / distance
                self.position = (self.position + direction * min(float(distance), self.speed)).astype(np.float64)

    def _return_to_patrol(self, game_map):

        if not self.path:
            target = self.patrol_points[self.patrol_target]
            self._find_path(game_map, target)


        if self.path:
            next_pos = self.path[0]
            direction = next_pos - self.position
            distance = np.linalg.norm(direction)

            if distance < 50:
                self.path.pop(0)
                if not self.path:

                    self.state = "patrol"

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

        min_distance = float('inf')
        nearest_index = 0

        for i, point in enumerate(self.patrol_points):
            distance = np.linalg.norm(self.position - point)
            if distance < min_distance:
                min_distance = distance
                nearest_index = i

        self.patrol_target = nearest_index

    def _position_to_grid(self, position):

        grid_x = max(0, min(self.grid_width - 1, int(position[0] / self.grid_size)))
        grid_y = max(0, min(self.grid_height - 1, int(position[1] / self.grid_size)))
        return (grid_x, grid_y)

    def _grid_to_position(self, grid):

        x = grid[0] * self.grid_size + self.grid_size / 2 -50
        y = grid[1] * self.grid_size + self.grid_size / 2 -50
        return np.array([x, y])

    def _find_path(self, game_map, target):

        grid = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]


        for wall in game_map.walls:

            x, y, w, h = wall
            grid_x1 = max(0, min(self.grid_width - 1, int(x / self.grid_size)))
            grid_y1 = max(0, min(self.grid_height - 1, int(y / self.grid_size)))
            grid_x2 = max(0, min(self.grid_width - 1, int((x + w) / self.grid_size)))
            grid_y2 = max(0, min(self.grid_height - 1, int((y + h) / self.grid_size)))


            for i in range(grid_x1, grid_x2 + 1):
                for j in range(grid_y1, grid_y2 + 1):
                    grid[i][j] = 1


        start = self._position_to_grid(self.position)
        end = self._position_to_grid(target)


        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}

        while not open_set.empty():
            current = open_set.get()[1]

            if current == end:

                self.path = []
                while current in came_from:
                    self.path.insert(0, self._grid_to_position(current))
                    current = came_from[current]
                return


            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)


                if (neighbor[0] < 0 or neighbor[0] >= self.grid_width or
                        neighbor[1] < 0 or neighbor[1] >= self.grid_height):
                    continue


                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue


                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, end)
                    open_set.put((f_score[neighbor], neighbor))


        self.path = [target]

    def _heuristic(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def check_collision(self, ball):

        distance = np.linalg.norm(self.position - ball.position)
        return distance < (self.radius + ball.radius)

    def draw(self, screen, offset_x, offset_y, ui_scale):

        ui_radius = int(self.radius * ui_scale)
        ui_pos = (int(self.position[0] * ui_scale + offset_x),
                  int(self.position[1] * ui_scale + offset_y))


        pygame.draw.circle(screen, (255, 255, 0), ui_pos, ui_radius)


        if self.state == "patrol":
            color = (0, 255, 0)
        elif self.state == "chase":
            color = (255, 0, 0)
        else:
            color = (255, 165, 0)

        pygame.draw.circle(screen, color, ui_pos, 5)


        for i, point in enumerate(self.path):
            ui_point = (int(point[0] * ui_scale + offset_x),
                        int(point[1] * ui_scale + offset_y))
            pygame.draw.circle(screen, (0, 0, 255), ui_point, 3)
            if i > 0:
                prev_point = (int(self.path[i - 1][0] * ui_scale + offset_x),
                              int(self.path[i - 1][1] * ui_scale + offset_y))
                pygame.draw.line(screen, (0, 0, 255), prev_point, ui_point, 1)