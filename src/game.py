import pygame
from level import Level
from physics import PhysicsWorld
from player import Player
import sys
import numpy as np

class Game:
    def __init__(self, screen_width=1600, screen_height=1000):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.current_level = None
        self.game_mode = None  # 'gravity' or 'non-gravity'
        self.physics_world = None

    def start_level(self, level_number, difficulty, mode):
        """开始指定关卡"""
        self.current_level = Level(level_number, difficulty, mode)
        self.game_mode = mode

        # 初始化物理世界
        if mode == 'gravity':
            self.physics_world = PhysicsWorld(gravity=(0, 9.8), pixels_per_meter=100)
        else:
            self.physics_world = PhysicsWorld(gravity=(0, 0), pixels_per_meter=100)

        # 构建地图文件名
        map_file = f"maze{level_number}.png"
        try:
            return self.current_level.start_level(map_file)
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return False

    def restart_level(self):
        """重新开始当前关卡"""
        if self.current_level:
            return self.current_level.reset_level()
        return False

    def switch_mode(self, new_mode):
        """切换游戏模式"""
        if self.current_level and new_mode in ['gravity', 'non-gravity']:
            self.game_mode = new_mode
            # 这里需要重新初始化关卡以适应新模式
            level_number = self.current_level.level_number
            difficulty = self.current_level.difficulty
            self.start_level(level_number, difficulty, new_mode)
            return True
        return False

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.current_level:
                    self.current_level.controller.handle_event(event)

            # 更新游戏状态
            if self.current_level:
                self.current_level.update()

            # 渲染
            self.screen.fill((255, 255, 255))  # 白色背景
            if self.current_level:
                self.current_level.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()