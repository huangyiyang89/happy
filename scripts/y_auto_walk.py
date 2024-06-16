"script"
import random
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "自动遇敌"
        self.range = 2
        self.start_x = 0
        self.start_y = 0

    def on_not_moving(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """

        if cg.map.x == 134 and cg.map.y == 174:
            cg.go_to(135, 175)
            return
        if cg.map.x == 135 and cg.map.y == 175:
            cg.go_to(134, 174)
            return

        if self.start_x == 0 and self.start_y == 0:
            self.start_x = cg.map.x
            self.start_y = cg.map.y

        if cg.map.x == self.start_x and cg.map.y == self.start_y:
            # 生成随机数 x
            x = random.choice([2, -2, 0, 0])
            # 根据 x 的值确定 y 的值
            if x in [-2, 2]:
                y = 0
            else:
                y = random.choice([2, -2])
            cg.go_to(
                self.start_x + x,
                self.start_y + y,
            )
        else:
            cg.go_to(self.start_x, self.start_y)

    def on_start(self, cg):
        self.start_x = 0
        self.start_y = 0
