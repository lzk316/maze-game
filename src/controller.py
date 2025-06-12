
import pygame


class Controller:
    def __init__(self, input_type='keyboard'):
        self.input_type = input_type
        self.level = None
        self.current_direction = None
        self.rotation_direction = None  # 'left', 'right' or None
        self.key_states = {
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_states[event.key] = True
            self._update_control_states()
        elif event.type == pygame.KEYUP:
            self.key_states[event.key] = False
            self._update_control_states()

    def _update_control_states(self):
        if self.key_states[pygame.K_UP]:
            self.current_direction = (0, -1)
        elif self.key_states[pygame.K_DOWN]:
            self.current_direction = (0, 1)
        elif self.key_states[pygame.K_LEFT]:
            self.current_direction = (-1, 0)
        elif self.key_states[pygame.K_RIGHT]:
            self.current_direction = (1, 0)
        else:
            self.current_direction = None

        if self.key_states[pygame.K_LEFT] and not self.key_states[pygame.K_RIGHT]:
            self.rotation_direction = 'left'
        elif self.key_states[pygame.K_RIGHT] and not self.key_states[pygame.K_LEFT]:
            self.rotation_direction = 'right'
        else:
            self.rotation_direction = None

    def get_direction(self):

        return self.current_direction

    def get_rotation(self):

        return self.rotation_direction

