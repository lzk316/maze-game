class Tool:
    def __init__(self, tool_type='obstacle_remover', count=0):
        self.type = tool_type
        self.count = count

    def use_tool(self):
        """使用工具"""
        if self.count > 0:
            self.count -= 1
            return True
        return False

    def increase_count(self, amount=1):
        """增加工具数量"""
        self.count += amount
        return self.count

