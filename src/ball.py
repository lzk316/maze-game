import numpy as np
import pygame


class Ball:
    def __init__(self, position, radius=150, density=1.0, friction=0.1, restitution=0.1):
        self.position = np.array(position, dtype=float)
        self.radius = radius
        self.color = (0, 255, 0)
        self.rotation_angle = 0  # 当前旋转角度（弧度）
        self.box2d_body = None  # Box2D物理实体
        self.initial_position = position[:]

    def reset_position(self, position):
        """重置小球的位置"""
        self.position = np.array(position, dtype=float)
        self.rotation_angle = 0  # 重置旋转角度

    def update_from_box2d(self, body):
        """从Box2D物理实体更新位置和旋转"""
        self.position = np.array((body.position.x * 100, body.position.y * 100))
        self.rotation_angle = body.angle

    def draw(self, screen, offset_x=0, offset_y=0, ui_scale=0.1):
        """绘制带旋转效果的小球（缩小10倍显示）"""
        # 计算UI显示位置和大小
        ui_radius = int(self.radius * ui_scale)
        ui_pos = (int(self.position[0] * ui_scale + offset_x),
                  int(self.position[1] * ui_scale + offset_y))

        # 绘制基本圆形
        pygame.draw.circle(screen, self.color, ui_pos, ui_radius)

        # 绘制旋转标记线
        start_pos = ui_pos
        end_pos = (
            int(ui_pos[0] + np.cos(self.rotation_angle) * ui_radius),
            int(ui_pos[1] + np.sin(self.rotation_angle) * ui_radius)
        )
        pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 2)