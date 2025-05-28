class Obstacle:
    def __init__(self, position):
        self.position = position
        self.active = True

    def check_collision(self, ball):
        # 检测与球的碰撞
        pass

    def activate(self):
        # 激活障碍物效果
        pass

    def draw(self, screen):
        # 绘制障碍物
        pass