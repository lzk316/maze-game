import pygame

class Controller:
    def __init__(self, input_type='keyboard'):
        self.input_type = input_type
        # 非重力模式控制
        self.current_direction = None
        # 重力模式控制
        self.rotation_direction = None  # 'left', 'right' 或 None
        # 按键状态缓存
        self.key_states = {
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False
        }

    def handle_event(self, event):
        """处理键盘事件"""
        if event.type == pygame.KEYDOWN:
            self.key_states[event.key] = True
            self._update_control_states()
        elif event.type == pygame.KEYUP:
            self.key_states[event.key] = False
            self._update_control_states()

    def _update_control_states(self):
        """根据按键状态更新控制方向"""
        # 非重力模式方向控制 (优先)
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

        # 重力模式旋转控制 (独立)
        if self.key_states[pygame.K_LEFT] and not self.key_states[pygame.K_RIGHT]:
            self.rotation_direction = 'left'
        elif self.key_states[pygame.K_RIGHT] and not self.key_states[pygame.K_LEFT]:
            self.rotation_direction = 'right'
        else:
            self.rotation_direction = None

    def get_direction(self):
        """获取非重力模式方向控制"""
        return self.current_direction

    def get_rotation(self):
        """获取重力模式旋转控制"""
        return self.rotation_direction

    def clear_controls(self):
        """清除所有控制状态"""
        self.current_direction = None
        self.rotation_direction = None
        for key in self.key_states:
            self.key_states[key] = False