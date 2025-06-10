import pygame
import numpy as np


class Ball:
    def __init__(self, position):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)
        self.angular_velocity = 0  # 角速度（弧度/帧）
        self.radius = 150
        self.mass = 1.0
        self.color = (0, 255, 0)
        self.speed = 5
        self.rotation_angle = 0  # 当前旋转角度（弧度）


    def update_position(self):
        """更新球的位置"""
        self.position += self.velocity
        # 打印小球的当前坐标
        print(f"小球当前坐标: {self.position}")

    def reset_position(self, position):
        """重置小球的位置"""
        self.position = np.array(position, dtype=float)
        self.velocity = np.array([0, 0], dtype=float)  # 重置速度
        self.angular_velocity = 0  # 重置角速度
        self.rotation_angle = 0  # 重置旋转角度

    def update_rotation(self):
        """根据速度更新旋转角度"""
        if np.linalg.norm(self.velocity) > 0.1:  # 有显著移动时才旋转
            # 计算角速度（速度/半径）
            self.angular_velocity = np.linalg.norm(self.velocity) / self.radius
            # 根据运动方向确定旋转方向
            direction = 1 if self.velocity[0] > 0 else -1
            self.rotation_angle += self.angular_velocity * direction

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