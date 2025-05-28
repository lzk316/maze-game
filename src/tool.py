
class Tool:
    def __init__(self):
        self.tools = {
            "trap_remover": 0,
            "thorn_remover": 0,
            "enemy_freezer": 0
        }

    def use_tool(self, tool_type):
        if self.tools.get(tool_type, 0) > 0:
            self.tools[tool_type] -= 1
            return True
        return False

    def increase_count(self, tool_type, amount=1):
        if tool_type in self.tools:
            self.tools[tool_type] += amount