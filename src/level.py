import glob
import random

import numpy as np
import pygame
from ball import Ball
from map import Map
from controller import Controller
from gravity_mode import GravityMode
from non_gravity_mode import NonGravityMode
from physics import PhysicsWorld
import time

class Level:
    def __init__(self, level_number, difficulty, mode):
        self.game = None
        self.victory_time = None
        self.show_victory = None
        self.level_number = level_number
        self.difficulty = difficulty
        self.mode = mode
        self.attempts = 0
        self.is_completed = False
        self.ball = None
        self.game_map = None
        self.controller = Controller()
        self.gravity_mode = GravityMode()
        self.non_gravity_mode = NonGravityMode()
        self.world = None
        self.rotation_angle = 0

        self.start_x = 50
        self.start_y = 200
        self.button_width = 250
        self.button_height = 100
        self.spacing = 150
        self.level_button_rect = pygame.Rect(
            self.start_x, self.start_y,
            self.button_width, self.button_height
        )
        self.difficulty_button_rect = pygame.Rect(
            self.start_x, self.start_y + self.button_height + self.spacing,
            self.button_width, self.button_height
        )
        self.mode_button_rect = pygame.Rect(
            self.start_x, self.start_y + 2 * (self.button_height + self.spacing),
            self.button_width, self.button_height
        )
        screen_width = 1600
        right_start_x = screen_width - self.start_x - self.button_width
        self.reset_button_rect = pygame.Rect(
            right_start_x, self.start_y,
            self.button_width, self.button_height
        )
        self.tool_button_rect = pygame.Rect(
            right_start_x, self.start_y + self.button_height + self.spacing,
            self.button_width, self.button_height
        )
        self.help_button_rect = pygame.Rect(
            right_start_x, self.start_y + 2 * (self.button_height + self.spacing),
            self.button_width, self.button_height
        )

        self.total_levels = len(glob.glob("assets/images/maze*.png"))
        self.show_level_list = False
        self.is_selecting_level = False

        self.guards = []

        self.reset_count = 0
        self.show_help = False
        self.tool_used = False

    def start_level(self, map_file=None):

        self.attempts += 1
        self.is_completed = False
        self.guards = []
        self.tool_used = False

        try:
            self.game_map = Map(map_file, difficulty=self.difficulty)
        except Exception as e:
            print(f" 2{e}")
            return False


        start_pos = self.game_map.get_start_position()
        if start_pos is None:
            print("123")
            return False

        self.ball = Ball(start_pos)


        if self.mode == 'gravity':
            self.world = PhysicsWorld(gravity=(0, 9.8), pixels_per_meter=100)
        else:
            self.world = PhysicsWorld(gravity=(0, 0), pixels_per_meter=100)


        self.ball.box2d_body = self.world.create_ball(
            position=start_pos,
            radius=self.ball.radius,
            density=1.0,
            friction=0.1,
            restitution=0.3
        )


        for wall in self.game_map.walls:
            x, y, w, h = wall
            self.world.create_static_box(
                position=(x + w/2, y + h/2),
                size=(w, h)
            )


        for trap in self.game_map.traps:
            self.world.create_static_circle(
                position=trap.position,
                radius=trap.radius
            )


        if self.game_map.end_position:
            self.world.create_static_circle(
                position=self.game_map.end_position,
                radius=self.game_map.end_radius
            )

        if self.difficulty == 'hard' and self.game_map.guards:
            for guard in self.game_map.guards:
                guard.box2d_body = self.world.create_guard(
                    position=guard.position,
                    radius=guard.radius
                )
                self.guards.append(guard)


        self.rotation_angle = 0
        self.reset_count = 0
        return True

    def reset_level(self):

        self.reset_count += 1
        if self.game_map and self.ball:
            start_pos = self.game_map.get_start_position()
            if start_pos:
                self.ball.reset_position(start_pos)
                if self.ball.box2d_body:
                    self.ball.box2d_body.position = (start_pos[0]/self.world.PPM, start_pos[1]/self.world.PPM)
                    self.ball.box2d_body.linearVelocity = (0, 0)

                for guard in self.guards:
                    guard.position = np.array(guard.patrol_points[0])
                    if guard.box2d_body:
                        guard.box2d_body.position = (
                        guard.position[0] / self.world.PPM, guard.position[1] / self.world.PPM)
                    guard.state = "patrol"
                    guard.patrol_target = 0
                    guard.path = []

                self.is_completed = False
                self.show_victory = False
                self.rotation_angle = 0
                return True
        return False

    def update(self):
        if not self.is_completed and self.ball and self.game_map:

            if self.world:
                self.world.step()


            if self.ball.box2d_body:
                self.ball.update_from_box2d(self.ball.box2d_body)


            if self.mode == 'non-gravity':
                direction = self.controller.get_direction()
                if direction:
                    force = np.array(direction) * 10000
                    self.world.apply_force_to_ball(self.ball.box2d_body, force)
            else:
                rotation = self.controller.get_rotation()
                if rotation:

                    if rotation == 'left':
                        self.rotation_angle += self.gravity_mode.rotation_speed * self.gravity_mode.time_step

                        gravity_angle = -self.rotation_angle
                    elif rotation == 'right':
                        self.rotation_angle -= self.gravity_mode.rotation_speed * self.gravity_mode.time_step

                        gravity_angle = -self.rotation_angle


                    gravity_x = 9.8 * np.sin(gravity_angle)
                    gravity_y = 9.8 * np.cos(gravity_angle)
                    self.world.set_gravity((gravity_x, gravity_y))


            if self.game_map.end_position:
                end_pos = np.array(self.game_map.end_position)
                ball_pos = self.ball.position
                distance = np.linalg.norm(ball_pos - end_pos)
                if distance < (self.ball.radius + self.game_map.end_radius):
                    self.is_completed = True
                    self.show_victory = True



            for trap in self.game_map.traps:
                trap_pos = np.array(trap.position)
                ball_pos = self.ball.position
                distance = np.linalg.norm(ball_pos - trap_pos)
                if distance < (self.ball.radius + trap.radius + 20):
                    trap.activate()
                    self.reset_level()
                    break


            for thorn in self.game_map.thorns:
                if thorn.check_collision(self.ball):
                    if thorn.activate():
                        self.reset_level()
                        break

            current_time = time.time()
            for guard in self.guards:
                guard.update(self.game_map, self.ball.position, current_time)


                if guard.box2d_body:
                    guard.box2d_body.position = (guard.position[0] / self.world.PPM,
                                                 guard.position[1] / self.world.PPM)


            for guard in self.guards:
                if guard.check_collision(self.ball):
                    self.reset_level()
                    break

    def use_tool(self):

        self.tool_used = True

        if self.difficulty == 'easy':

            if self.game_map.traps:
                trap_to_remove = random.choice(self.game_map.traps)
                self.game_map.traps.remove(trap_to_remove)
        elif self.difficulty == 'hard':

            for thorn in self.game_map.thorns:
                thorn.is_visible = True


    def draw(self, screen):

        if not self.game_map:
            return


        map_center_x = self.game_map.ui_width // 2 + self.game_map.offset_x
        map_center_y = self.game_map.ui_height // 2 + self.game_map.offset_y


        screen.fill((240, 240, 240))

        rotated_screen = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        self.game_map.draw(rotated_screen)
        if self.ball:
            self.ball.draw(rotated_screen, self.game_map.offset_x, self.game_map.offset_y, self.game_map.ui_scale)

        for guard in self.guards:
            guard.draw(rotated_screen, self.game_map.offset_x, self.game_map.offset_y, self.game_map.ui_scale)


        if self.rotation_angle != 0:
            rotated_image = pygame.transform.rotate(rotated_screen, np.degrees(self.rotation_angle))
            rotated_rect = rotated_image.get_rect(center=(map_center_x, map_center_y))
            screen.blit(rotated_image, rotated_rect)
        else:
            screen.blit(rotated_screen, (0, 0))


        button_width = 250
        button_height = 100
        spacing = 150
        start_x = 50
        start_y = 200


        mouse_pos = pygame.mouse.get_pos()


        button_color1 = (220, 220, 220)
        if not self.is_selecting_level and self.level_button_rect.collidepoint(mouse_pos):
            button_color1 = (180, 180, 255)
        pygame.draw.rect(screen, button_color1, self.level_button_rect)
        button_color2 = (220, 220, 220)
        if not self.is_selecting_level and self.difficulty_button_rect.collidepoint(mouse_pos):
            button_color2 = (180, 180, 255)
        pygame.draw.rect(screen, button_color2, self.difficulty_button_rect)
        button_color3 = (220, 220, 220)
        if not self.is_selecting_level and self.mode_button_rect.collidepoint(mouse_pos):
            button_color3 = (180, 180, 255)
        pygame.draw.rect(screen, button_color3, self.mode_button_rect)

        font = pygame.font.SysFont(None, 36)


        level_text = font.render(f"Level: {self.level_number}", True, (0, 0, 0))
        screen.blit(level_text, (self.level_button_rect.centerx - level_text.get_width() // 2,
                                 self.level_button_rect.centery - level_text.get_height() // 2))


        diff_text = font.render(f"Difficulty: {self.difficulty}", True, (0, 0, 0))
        screen.blit(diff_text, (self.difficulty_button_rect.centerx - diff_text.get_width() // 2,
                                self.difficulty_button_rect.centery - diff_text.get_height() // 2))

        mode_text = font.render(f"Mode: {self.mode}", True, (0, 0, 0))
        screen.blit(mode_text, (self.mode_button_rect.centerx - mode_text.get_width() // 2,
                                self.mode_button_rect.centery - mode_text.get_height() // 2))

        reset_color = (220, 220, 220)
        if self.reset_button_rect.collidepoint(mouse_pos):
            reset_color = (180, 180, 255)
        pygame.draw.rect(screen, reset_color, self.reset_button_rect)
        reset_text = font.render(f"Reset: {self.reset_count}", True, (0, 0, 0))
        screen.blit(reset_text, (self.reset_button_rect.centerx - reset_text.get_width() // 2,
                                 self.reset_button_rect.centery - reset_text.get_height() // 2))


        if self.reset_count >= 10 and not self.tool_used:
            tool_color = (220, 220, 220)
            if self.tool_button_rect.collidepoint(mouse_pos):
                tool_color = (180, 180, 255)
        else:
            tool_color = (150, 150, 150)
        pygame.draw.rect(screen, tool_color, self.tool_button_rect)
        tool_text = font.render("Tool", True, (0, 0, 0))
        screen.blit(tool_text, (self.tool_button_rect.centerx - tool_text.get_width() // 2,
                                self.tool_button_rect.centery - tool_text.get_height() // 2))


        help_color = (220, 220, 220)
        if self.help_button_rect.collidepoint(mouse_pos):
            help_color = (180, 180, 255)
        pygame.draw.rect(screen, help_color, self.help_button_rect)
        help_text = font.render("Help", True, (0, 0, 0))
        screen.blit(help_text, (self.help_button_rect.centerx - help_text.get_width() // 2,
                                self.help_button_rect.centery - help_text.get_height() // 2))


        if self.show_help:
            help_box = pygame.Rect(
                self.tool_button_rect.left,
                self.tool_button_rect.top,
                300,
                200
            )
            pygame.draw.rect(screen, (255, 255, 230), help_box)
            pygame.draw.rect(screen, (100, 100, 100), help_box, 2)

            help_title = font.render("Tool Usage", True, (0, 0, 0))
            screen.blit(help_title, (help_box.left + 20, help_box.top + 15))


            help_font = pygame.font.SysFont(None, 20)
            help_desc1 = help_font.render("Easy Mode: Remove one random trap", True, (0, 0, 0))
            help_desc2 = help_font.render("Hard Mode: Reveal all thorns", True, (0, 0, 0))

            help_condition = help_font.render("Available after 10 resets", True, (0, 0, 0))

            screen.blit(help_desc1, (help_box.left + 20, help_box.top + 60))
            screen.blit(help_desc2, (help_box.left + 20, help_box.top + 100))
            screen.blit(help_condition, (help_box.left + 20, help_box.top + 140))
            help_once = help_font.render("Can be used once per level", True, (0, 0, 0))
            screen.blit(help_once, (help_box.left + 20, help_box.top + 180))

        if self.show_level_list:
            list_start_y = self.level_button_rect.bottom + 50

            level_list_text = font.render("choose:", True, (0, 0, 0))
            screen.blit(level_list_text, (start_x, list_start_y))


            list_background = pygame.Rect(
                start_x - 10,
                list_start_y - 10,
                button_width + 20,
                (self.total_levels + 1) * 50 + 20
            )
            pygame.draw.rect(screen, (230, 230, 230), list_background)
            pygame.draw.rect(screen, (100, 100, 100), list_background, 2)  # 边框

            for i, level_num in enumerate(range(1, self.total_levels + 1)):
                level_rect = pygame.Rect(
                    start_x,
                    list_start_y + (i + 1) * 50,
                    button_width,
                    40
                )


                if level_num == self.level_number:
                    pygame.draw.rect(screen, (180, 230, 255), level_rect)

                level_text = font.render(f"maze{level_num}.png", True, (0, 0, 0))
                screen.blit(level_text, (level_rect.x + 10, level_rect.centery - level_text.get_height() // 2))


        if self.is_completed and self.show_victory:
            victory_font = pygame.font.SysFont(None, 72)
            victory_text = victory_font.render("Success!", True, (255, 0, 0))
            text_rect = victory_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(victory_text, text_rect)

    def switch_mode(self, new_mode):

        if new_mode in ['gravity', 'non-gravity']:
            self.mode = new_mode

            map_file = f"maze{self.level_number}.png"
            self.start_level(map_file)
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos


            if self.level_button_rect.collidepoint(mouse_pos):
                self.show_level_list = not self.show_level_list
                self.is_selecting_level = self.show_level_list


            if self.show_level_list:

                list_start_y = self.level_button_rect.bottom + 50

                for i, level_num in enumerate(range(1, self.total_levels + 1)):
                    level_rect = pygame.Rect(
                        self.start_x,
                        list_start_y + (i + 1) * 50,
                        self.button_width,
                        40
                    )

                    if level_rect.collidepoint(mouse_pos):

                        self.level_number = level_num
                        map_file = f"maze{self.level_number}.png"
                        self.start_level(map_file)
                        self.show_level_list = False
                        break
            else:             self.is_selecting_level = False

            if not self.is_selecting_level:
                if self.difficulty_button_rect.collidepoint(mouse_pos):

                    if self.difficulty == "easy":
                        self.difficulty = "hard"
                    else:
                        self.difficulty = "easy"

                    map_file = f"maze{self.level_number}.png"
                    self.start_level(map_file)

                if self.mode_button_rect.collidepoint(mouse_pos):

                    new_mode = 'non-gravity' if self.mode == 'gravity' else 'gravity'
                    self.switch_mode(new_mode)

                if self.reset_button_rect.collidepoint(mouse_pos):
                    self.reset_level()

                if (self.tool_button_rect.collidepoint(mouse_pos) and
                        self.reset_count >= 10 and
                        not self.tool_used):
                    self.use_tool()

                if self.help_button_rect.collidepoint(mouse_pos):
                    self.show_help = not self.show_help