"script"
import random
import happy.script
import happy.core



class Script(happy.script.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "自动遇敌"
        self.range = 3
        self.start_x = 0
        self.start_y = 0

    def on_not_battle(self, cg: happy.core.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """

        if self.start_x == 0 and self.start_y == 0:
            self.start_x = cg.map.x
            self.start_y = cg.map.y

        cg.go_to(
            self.start_x + random.randrange(-self.range, self.range+1),
            self.start_y + random.randrange(-self.range, self.range+1),
        )

    def on_enable(self, enable):
        self.start_x = 0
        self.start_y = 0
