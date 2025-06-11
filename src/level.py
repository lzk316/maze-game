import numpy as np
import pygame
from ball import Ball
from map import Map
from tool import Tool
from controller import Controller
from gravity_mode import GravityMode
from non_gravity_mode import NonGravityMode
from physics import PhysicsWorld

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
        self.gravity_mode = GravityMode()
        self.non_gravity_mode = NonGravityMode()
        self.world = None
        self.rotation_angle = 0

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

        # 初始化物理世界
        if self.mode == 'gravity':
            self.world = PhysicsWorld(gravity=(0, 9.8), pixels_per_meter=100)
        else:
            self.world = PhysicsWorld(gravity=(0, 0), pixels_per_meter=100)

        # 创建小球的物理实体
        self.ball.box2d_body = self.world.create_ball(
            position=start_pos,
            radius=self.ball.radius,
            density=1.0,
            friction=0.1,
            restitution=0.3
        )

        # 创建墙壁的物理实体
        for wall in self.game_map.walls:
            x, y, w, h = wall
            self.world.create_static_box(
                position=(x + w/2, y + h/2),
                size=(w, h)
            )

        # 创建陷阱的物理实体
        for trap in self.game_map.traps:
            self.world.create_static_circle(
                position=trap.position,
                radius=trap.radius
            )

        # 创建终点的物理实体
        if self.game_map.end_position:
            self.world.create_static_circle(
                position=self.game_map.end_position,
                radius=self.game_map.end_radius
            )


        return True

    def reset_level(self):
        """重置关卡"""
        if self.game_map and self.ball:
            start_pos = self.game_map.get_start_position()
            if start_pos:
                self.ball.reset_position(start_pos)
                if self.ball.box2d_body:
                    self.ball.box2d_body.position = (start_pos[0]/self.world.PPM, start_pos[1]/self.world.PPM)
                    self.ball.box2d_body.linearVelocity = (0, 0)
                return True
        return False

    def update(self):
        if not self.is_completed and self.ball and self.game_map:
            # 更新物理世界
            if self.world:
                self.world.step()

            # 更新小球的渲染位置
            if self.ball.box2d_body:
                self.ball.update_from_box2d(self.ball.box2d_body)

            # 应用用户输入控制
            if self.mode == 'non-gravity':
                direction = self.controller.get_direction()
                if direction:
                    force = np.array(direction) * 50000 # 调整力的大小
                    self.world.apply_force_to_ball(self.ball.box2d_body, force)
            else:
                rotation = self.controller.get_rotation()
                if rotation:
                    angle = self.gravity_mode.rotate_map(rotation)
                    self.rotation_angle += angle
                    self.world.rotate_world(angle)

            # 检查是否达到终点
            if self.game_map.end_position:
                end_pos = np.array(self.game_map.end_position)
                ball_pos = self.ball.position
                distance = np.linalg.norm(ball_pos - end_pos)
                if distance < (self.ball.radius + self.game_map.end_radius):
                    self.is_completed = True
                    self.show_victory = True
                    self.victory_time = pygame.time.get_ticks()

            # 检查是否触碰陷阱
            for trap in self.game_map.traps:
                trap_pos = np.array(trap.position)
                ball_pos = self.ball.position
                distance = np.linalg.norm(ball_pos - trap_pos)
                if distance < (self.ball.radius + trap.radius + 20):
                    trap.activate()
                    self.reset_level()
                    break

    def draw(self, screen):
        """绘制关卡"""
        if not self.game_map:
            return

        # 绘制地图
        self.game_map.draw(screen, self.rotation_angle)

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