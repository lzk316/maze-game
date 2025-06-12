import pygame
from level import Level
from physics import PhysicsWorld
from player import Player
import sys

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

        self.current_level = Level(level_number, difficulty, mode)
        self.game_mode = mode

        if mode == 'gravity':
            self.physics_world = PhysicsWorld(gravity=(0, 9.8), pixels_per_meter=100)
        else:
            self.physics_world = PhysicsWorld(gravity=(0, 0), pixels_per_meter=100)

        map_file = f"maze{level_number}.png"
        try:
            return self.current_level.start_level(map_file)
        except FileNotFoundError as e:
            print(f"error: {e}")
            return False


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.current_level:
                    self.current_level.controller.handle_event(event)
                    self.current_level.handle_event(event)

            if self.current_level:
                self.current_level.update()

            self.screen.fill((255, 255, 255))
            if self.current_level:
                self.current_level.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()
        sys.exit()