import pygame
from src.level import Level
from src.player import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.current_level = None
        self.running = True

    def start_level(self, level_num, mode="non-gravity", difficulty="easy"):
        self.current_level = Level(level_num, mode, difficulty)
        self.current_level.start_level()

    def restart_level(self):
        if self.current_level:
            self.current_level.reset_level()

    def switch_mode(self, new_mode):
        if self.current_level:
            self.current_level.switch_mode(new_mode)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 更新游戏状态
            if self.current_level:
                self.current_level.update()
                self.current_level.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()