import pygame
from thorn import Thorn
from trap import Trap
from guard import Guard
from pathlib import Path

class Map:
    def __init__(self, image_path, scale=100, difficulty="hard"):

        self.difficulty = difficulty
        base_dir = Path(__file__).parent.parent
        full_path = base_dir / "assets" / "images" / image_path

        try:
            self.image = pygame.image.load(str(full_path))
            self.image_array = pygame.surfarray.array3d(self.image).swapaxes(0, 1)
        except FileNotFoundError:
            raise FileNotFoundError(f"{full_path}")
        except pygame.error:
            raise ValueError(f" {full_path}")

        self.scale = scale
        self.raw_width = self.image.get_width()
        self.raw_height = self.image.get_height()
        self.game_width = self.raw_width * scale
        self.game_height = self.raw_height * scale


        self.ui_scale = 0.1
        self.ui_width = int(self.game_width * self.ui_scale)
        self.ui_height = int(self.game_height * self.ui_scale)


        self.walls = []
        self.traps = []
        self.thorns = []
        self.start_position = None
        self.end_position = None
        self.obstacle_radius = 150


        self.screen_width = 0
        self.screen_height = 0
        self.offset_x = 0
        self.offset_y = 0
        self.guards = []
        self.parse_map()

    def parse_map(self):

        height, width, _ = self.image_array.shape

        for y in range(height):
            for x in range(width):
                pixel = self.image_array[y, x]

                if (pixel == [0, 0, 0]).all():
                    self.walls.append((x * self.scale, y * self.scale,
                                       self.scale, self.scale))

                elif (pixel == [0, 255, 0]).all():
                    self.start_position = (x * self.scale + self.scale // 2,
                                           y * self.scale + self.scale // 2)

                elif (pixel == [255, 0, 0]).all():
                    trap_pos = (x * self.scale + self.scale // 2,
                                y * self.scale + self.scale // 2)
                    self.traps.append(Trap(trap_pos, self.obstacle_radius))

                elif (pixel == [255, 0, 255]).all():
                    if self.difficulty == "hard":
                        thorn_pos = (x * self.scale + self.scale // 2,
                                 y * self.scale + self.scale // 2)
                        self.thorns.append(Thorn(thorn_pos, size=300))

                elif (pixel == [255, 255, 0]).all():
                    if self.difficulty == "hard":
                        guard_pos = (x * self.scale + self.scale // 2,
                                     y * self.scale + self.scale // 2)
                        self.guards.append(Guard(guard_pos))

                elif (pixel == [0, 0, 255]).all():
                    self.end_position = (x * self.scale + self.scale // 2,
                                         y * self.scale + self.scale // 2)
                    self.end_radius = self.obstacle_radius

    def get_start_position(self):

        return self.start_position

    def calculate_offset(self, screen_width, screen_height):

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x = (screen_width - self.ui_width) // 2
        self.offset_y = (screen_height - self.ui_height) // 2

    def draw(self, screen, rotation_angle=0):

        self.calculate_offset(screen.get_width(), screen.get_height())


        screen.fill((240, 240, 240))


        for wall in self.walls:
            x, y, w, h = wall

            screen_rect = pygame.Rect(
                x * self.ui_scale + self.offset_x,
                y * self.ui_scale + self.offset_y,
                w * self.ui_scale,
                h * self.ui_scale
            )
            pygame.draw.rect(screen, (0, 0, 0), screen_rect)


        for trap in self.traps:

            screen_pos = (
                trap.position[0] * self.ui_scale + self.offset_x,
                trap.position[1] * self.ui_scale + self.offset_y
            )

            pygame.draw.circle(
                screen,
                trap.color,
                (int(screen_pos[0]), int(screen_pos[1])),
                int(trap.radius * self.ui_scale)
            )

        for thorn in self.thorns:
            if thorn.is_visible:

                screen_pos = (
                    thorn.position[0] * self.ui_scale + self.offset_x,
                    thorn.position[1] * self.ui_scale + self.offset_y
                )

                pygame.draw.rect(
                    screen,
                    thorn.color,
                    (screen_pos[0] - thorn.size // 2 * self.ui_scale,
                     screen_pos[1] - thorn.size // 2 * self.ui_scale,
                     thorn.size * self.ui_scale,
                     thorn.size * self.ui_scale)
                )


        if self.end_position:

            screen_pos = (
                self.end_position[0] * self.ui_scale + self.offset_x,
                self.end_position[1] * self.ui_scale + self.offset_y
            )

            pygame.draw.circle(
                screen,
                (0, 0, 255),
                (int(screen_pos[0]), int(screen_pos[1])),
                int(self.end_radius * self.ui_scale)
            )