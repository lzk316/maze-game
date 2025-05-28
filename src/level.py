import numpy as np
import pygame
from ball import Ball
from map import Map
from tool import Tool
from controller import Controller
from non_gravity_mode import NonGravityMode
from gravity_mode import GravityMode


class Level:
    def __init__(self, level_number, difficulty='easy', mode='non-gravity'):
        self.level_number = level_number
        self.difficulty = difficulty
        self.mode = mode
        self.attempts = 0
        self.is_completed = False
        self.ball = None
        self.game_map = None
        self.tool = Tool()
        self.controller = Controller()

        # 根据模式初始化
        if mode == 'non-gravity':
            self.mode_handler = NonGravityMode()
        else:
            self.mode_handler = GravityMode()

    def start_level(self, map_file=None):
        """开始关卡"""
        self.attempts += 1
        self.is_completed = False

        try:
            self.game_map = Map(map_file)
        except Exception as e:
            print(f"加载地图失败: {e}")
            return False

        # 初始化小球
        start_pos = self.game_map.get_start_position()
        self.ball = Ball(start_pos)

        # 根据难度初始化工具
        if self.difficulty == 'easy':
            self.tool.increase_count(3)  # 简单模式给3个工具

        return True

    def reset_level(self):
        """重置关卡"""
        return self.start_level()

    def update(self):
        """更新关卡状态"""
        if not self.is_completed:
            # 处理控制输入
            if self.mode == 'non-gravity':
                direction = self.controller.get_direction()
                self.mode_handler.control_ball(self.ball, direction)
            else:
                rotation = self.controller.get_rotation()
                self.mode_handler.rotate_map(self.game_map, rotation)
                self.mode_handler.apply_gravity_to_ball(self.ball)

            # 检查碰撞
            if self.game_map.check_collision(self.ball):
                self.reset_level()

            # 检查是否到达终点
            if self.game_map.check_win_condition(self.ball):
                self.is_completed = True

    def draw(self, screen):
        """绘制关卡"""
        # 先绘制地图
        self.game_map.draw(screen)

        # 绘制小球（需要考虑地图偏移）
        adjusted_ball_pos = (
            self.ball.position[0] + self.game_map.offset_x,
            self.ball.position[1] + self.game_map.offset_y
        )
        self.ball.position = np.array(adjusted_ball_pos)
        self.ball.draw(screen)
        # 绘制后恢复球的位置
        self.ball.position = np.array([
            adjusted_ball_pos[0] - self.game_map.offset_x,
            adjusted_ball_pos[1] - self.game_map.offset_y
        ])

        # 绘制UI：关卡数、难度、工具数量等
        font = pygame.font.SysFont(None, 36)
        level_text = font.render(f"Level: {self.level_number}", True, (0,0,0))
        screen.blit(level_text, (20, 20))

        diff_text = font.render(f"Difficulty: {self.difficulty}", True, (0,0,0))
        screen.blit(diff_text, (20, 60))

        tool_text = font.render(f"Tools: {self.tool.count}", True, (0,0,0))
        screen.blit(tool_text, (20, 100))