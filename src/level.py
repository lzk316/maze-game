from src.ball import Ball
from src.map import Map
from src.controller import Controller
from src.modes.gravity_mode import GravityMode
from src.modes.non_gravity_mode import NonGravityMode


class Level:
    def __init__(self, level_number, mode, difficulty):
        self.level_number = level_number
        self.difficulty = difficulty
        self.attempts = 0
        self.is_completed = False
        self.mode = mode

        # 初始化游戏对象
        self.ball = Ball()
        self.map = Map(level_number)
        self.controller = Controller()
        self.tool = Tool() if difficulty == "easy" else None

        # 设置游戏模式
        if mode == "gravity":
            self.game_mode = GravityMode(self.ball, self.map)
        else:
            self.game_mode = NonGravityMode(self.ball)

    def start_level(self):
        self.ball.reset_position()
        self.map.generate_map()
        self.attempts = 0
        self.is_completed = False

    def reset_level(self):
        self.ball.reset_position()
        self.attempts += 1

    def switch_mode(self, new_mode):
        self.mode = new_mode
        if new_mode == "gravity":
            self.game_mode = GravityMode(self.ball, self.map)
        else:
            self.game_mode = NonGravityMode(self.ball)

    def update(self):
        self.game_mode.update()
        if self.map.check_collision(self.ball):
            self.reset_level()

    def draw(self, screen):
        self.map.draw(screen)
        self.ball.draw(screen)
        # 绘制UI元素...