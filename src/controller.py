import pygame


class Controller:
    def __init__(self, input_type='keyboard'):
        self.input_type = input_type
        self.current_direction = None
        self.current_rotation = None

    def handle_event(self, event):
        """处理键盘事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                self.current_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.current_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.current_direction = (1, 0)
        elif event.type == pygame.KEYUP:
            self.current_direction = None

    def control_ball(self, direction):
        """控制小球方向"""
        self.current_direction = direction

    def rotate_map(self, direction):
        """控制地图旋转"""
        self.current_rotation = direction

    def get_direction(self):
        """获取当前方向控制"""
        # 这里应该处理实际输入，简化处理直接返回存储的方向
        return self.current_direction

    def get_rotation(self):
        """获取当前旋转控制"""
        return self.current_rotation