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
        self.victory_time = None
        self.show_victory = None
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
        if start_pos is None:
            print("错误：地图中没有起始位置！")
            return False

        self.ball = Ball(start_pos)

        # 根据难度初始化工具
        if self.difficulty == 'easy':
            self.tool.increase_count(3)  # 简单模式给3个工具

        return True

    def reset_level(self):
        """重置关卡"""
        if self.game_map:
            start_pos = self.game_map.get_start_position()
            if start_pos:
                self.ball.reset_position(start_pos)
                return True
        return False

    def update(self):
        if not self.is_completed and self.ball and self.game_map:
            # 保存上一帧位置用于碰撞回退
            prev_pos = np.copy(self.ball.position)

            # 更新球的位置
            if self.mode == 'non-gravity':
                direction = self.controller.get_direction()
                self.mode_handler.control_ball(self.ball, direction)
            else:
                rotation = self.controller.get_rotation()
                self.mode_handler.rotate_map(self.game_map, rotation)
                self.mode_handler.apply_gravity_to_ball(self.ball)

            # 检测碰撞
            collision = self.game_map.check_collision(self.ball)

            if collision == "trap":
                # 陷阱碰撞 - 重置到起点
                if not self.reset_level():
                    print("重置失败：找不到起始位置！")

            elif collision and ("wall" in collision or collision == "boundary"):
                # 墙壁或边界碰撞 - 根据方向反弹
                if "left" in collision or "right" in collision:
                    self.ball.velocity[0] *= -0.7  # x方向反弹
                if "top" in collision or "bottom" in collision:
                    self.ball.velocity[1] *= -0.7  # y方向反弹

                # 回退到碰撞前位置
                self.ball.position = prev_pos

            elif collision == "goal":
                # 到达终点
                self.is_completed = True
                self.show_victory = True
                self.victory_time = pygame.time.get_ticks()

    def draw(self, screen):
        """绘制关卡"""
        if not self.game_map:
            return

        # 绘制地图
        self.game_map.draw(screen)

        # 绘制小球
        if self.ball:
            pygame.draw.circle(screen, self.ball.color,
                               (int(self.ball.position[0] + self.game_map.offset_x),
                                int(self.ball.position[1] + self.game_map.offset_y)),
                               self.ball.radius)

        # 绘制UI：关卡数、难度、工具数量等
        font = pygame.font.SysFont(None, 36)
        level_text = font.render(f"Level: {self.level_number}", True, (0, 0, 0))
        screen.blit(level_text, (20, 20))

        diff_text = font.render(f"Difficulty: {self.difficulty}", True, (0, 0, 0))
        screen.blit(diff_text, (20, 60))

        tool_text = font.render(f"Tools: {self.tool.count}", True, (0, 0, 0))
        screen.blit(tool_text, (20, 100))

        # 通关显示
        if self.is_completed and self.show_victory:
            victory_font = pygame.font.SysFont(None, 72)
            victory_text = victory_font.render("关卡完成!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(victory_text, text_rect)

            # 3秒后显示下一关提示
            if pygame.time.get_ticks() - self.victory_time > 3000:
                next_font = pygame.font.SysFont(None, 48)
                next_text = next_font.render("按N键进入下一关", True, (0, 0, 255))
                next_rect = next_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
                screen.blit(next_text, next_rect)

    def draw_debug(self, screen):
        """绘制调试信息"""
        if not self.game_map or not self.ball:
            return

        # 绘制球的实际碰撞框
        ball_rect = pygame.Rect(
            self.ball.position[0] + self.game_map.offset_x - self.ball.radius,
            self.ball.position[1] + self.game_map.offset_y - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2
        )
        pygame.draw.rect(screen, (255, 0, 0), ball_rect, 1)

        # 绘制所有墙壁框
        for wall in self.game_map.walls:
            wall_rect = pygame.Rect(
                wall[0] + self.game_map.offset_x,
                wall[1] + self.game_map.offset_y,
                wall[2],
                wall[3]
            )
            pygame.draw.rect(screen, (0, 255, 0), wall_rect, 1)