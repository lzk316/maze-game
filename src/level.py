import numpy as np
import pygame
from ball import Ball
from map import Map
from tool import Tool
from controller import Controller
from non_gravity_mode import NonGravityMode
from gravity_mode import GravityMode


class Level:
    def __init__(self, level_number, difficulty, mode):
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



        map_center = (
            self.game_map.game_width // 2,
            self.game_map.game_height // 2
            )
        self.mode_handler.set_rotation_center(map_center)

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
            # 增加子步数以提高精度
            sub_steps = 8  # 增加到8个子步

            for _ in range(sub_steps):
                prev_pos = np.copy(self.ball.position)
                prev_vel = np.copy(self.ball.velocity)

                # 应用控制
                if self.mode == 'non-gravity':
                    direction = self.controller.get_direction()
                    self.mode_handler.control_ball(self.ball, direction)
                else:
                    rotation = self.controller.get_rotation()
                    self.mode_handler.rotate_map(rotation)
                    self.mode_handler.apply_gravity_to_ball(self.ball)

                self.ball.update_position()
                # 精确碰撞检测
                collision_info = self.game_map.check_collision(self.ball, self.mode_handler)

                if collision_info:
                    if collision_info["type"] == "trap":
                        if not self.reset_level():
                            print("重置失败：找不到起始位置！")
                        break

                    elif collision_info["type"] == "goal":
                        self.is_completed = True
                        self.show_victory = True
                        self.victory_time = pygame.time.get_ticks()
                        break

                    else:  # 墙壁或边界碰撞

                        # 打印碰撞信息
                        print("happen")
                        # 回退到碰撞前状态
                        self.ball.position = prev_pos
                        self.ball.velocity = prev_vel

                        # 处理碰撞响应
                        response = self.mode_handler.handle_collision(
                            self.ball,
                            collision_info["type"],
                            collision_info["point"]
                        )

                        # 应用碰撞后的物理
                        if self.mode == 'gravity':
                            self.mode_handler.apply_gravity_to_ball(self.ball, response)

    def draw(self, screen):
        """绘制关卡"""
        if not self.game_map:
            return

        # 绘制地图
        if self.mode == 'gravity':
            self.game_map.draw(screen, self.mode_handler)
        else:
            self.game_map.draw(screen)

        # 绘制小球
        if self.ball:
            self.ball.draw(screen, self.game_map.offset_x, self.game_map.offset_y, self.game_map.ui_scale)
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

