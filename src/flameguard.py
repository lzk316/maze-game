class FlameGuard:
    def __init__(self, position, patrol_range):
        self.position = position
        self.patrol_range = patrol_range
        self.state = "patrol"  # patrol, chase, return
        self.patrol_path = []
        self.current_target = 0

    def update(self, ball_position):
        if self._ball_in_range(ball_position):
            self.state = "chase"
            self._chase_ball(ball_position)
        else:
            if self.state == "chase":
                self.state = "return"
            self._patrol()

    def _ball_in_range(self, ball_position):
        distance = ((ball_position[0] - self.position[0]) ** 2 +
                    (ball_position[1] - self.position[1]) ** 2) ** 0.5
        return distance < self.patrol_range

    def _chase_ball(self, ball_position):
        # 简单追踪逻辑
        dx = ball_position[0] - self.position[0]
        dy = ball_position[1] - self.position[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            self.position[0] += dx / dist * 2
            self.position[1] += dy / dist * 2

    def _patrol(self):
        # 巡逻逻辑
        if not self.patrol_path:
            return

        target = self.patrol_path[self.current_target]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist < 5:  # 到达目标点
            self.current_target = (self.current_target + 1) % len(self.patrol_path)
        else:
            self.position[0] += dx / dist * 1.5
            self.position[1] += dy / dist * 1.5