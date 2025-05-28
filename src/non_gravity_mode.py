class NonGravityMode:
    def __init__(self, ball):
        self.ball = ball

    def update(self):
        # 非重力模式下，小球只在控制时移动
        pass

    def control_ball(self, direction):
        self.ball.move(direction)