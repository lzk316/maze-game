class Player:
    def __init__(self):
        self.username = None
        self.password = None
        self.total_attempts = 0
        self.completed_levels = 0
        self.is_logged_in = False

    def login(self, username, password):
        self.username = username
        self.password = password
        self.is_logged_in = True
        return True

    def logout(self):
        self.is_logged_in = False
        return True

    def update_stats(self, level_completed=False):
        self.total_attempts += 1
        if level_completed:
            self.completed_levels += 1