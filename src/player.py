import json
import os


class Player:
    def __init__(self, username=None):
        self.username = username
        self.password = None
        self.total_attempts = 0
        self.completed_levels = 0
        self.current_level = 1
        self.scores = {}  # 格式: {level_num: {"attempts": int, "completed": bool}}
        self.logged_in = False
        self.save_file = "player_data.json"

        if username:
            self.load_data()

    def login(self, username, password):
        """玩家登录"""
        self.username = username
        self.password = password  # 实际应用中应该加密存储

        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                if username in data:
                    player_data = data[username]
                    self.total_attempts = player_data.get("total_attempts", 0)
                    self.completed_levels = player_data.get("completed_levels", 0)
                    self.current_level = player_data.get("current_level", 1)
                    self.scores = player_data.get("scores", {})

        self.logged_in = True
        return True

    def logout(self):
        """玩家登出"""
        self.save_data()
        self.logged_in = False

    def save_data(self):
        """保存玩家数据"""
        data = {}
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)

        data[self.username] = {
            "total_attempts": self.total_attempts,
            "completed_levels": self.completed_levels,
            "current_level": self.current_level,
            "scores": self.scores
        }

        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        """加载玩家数据"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                if self.username in data:
                    player_data = data[self.username]
                    self.total_attempts = player_data.get("total_attempts", 0)
                    self.completed_levels = player_data.get("completed_levels", 0)
                    self.current_level = player_data.get("current_level", 1)
                    self.scores = player_data.get("scores", {})

    def update_stats(self, level_num, attempts, completed):
        """更新玩家统计数据"""
        self.total_attempts += attempts

        if level_num not in self.scores:
            self.scores[level_num] = {"attempts": 0, "completed": False}

        self.scores[level_num]["attempts"] += attempts

        if completed and not self.scores[level_num]["completed"]:
            self.scores[level_num]["completed"] = True
            self.completed_levels += 1
            if level_num >= self.current_level:
                self.current_level = level_num + 1

    def get_level_stats(self, level_num):
        """获取指定关卡的统计数据"""
        return self.scores.get(level_num, {"attempts": 0, "completed": False})

    def reset_progress(self):
        """重置玩家进度"""
        self.total_attempts = 0
        self.completed_levels = 0
        self.current_level = 1
        self.scores = {}