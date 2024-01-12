"script"
import happy.script
import happy.core


class Script(happy.script.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "高速战斗"
        self.speed = 100


    def on_battle(self, cg: happy.core.Cg):
        t0 = cg.mem.read_double(0x0072B9D8)
        cg.mem.write_double(0x0072B9D8, t0 - self.speed)
