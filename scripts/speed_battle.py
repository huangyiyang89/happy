"script"
import happy.script
import happy


class Script(happy.script.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "高速战斗"
        self.speed = 300


    def on_battle(self, cg: happy.Cg):
        t0 = cg.mem.read_double(0x0072B9D8)
        cg.mem.write_double(0x0072B9D8, t0 - self.speed)

    def on_update(self, cg: happy.Cg):
        if cg.state in (9,10) and cg.state2 in (5,1,2,4,8,11):
            t0 = cg.mem.read_double(0x0072B9D8)
            cg.mem.write_double(0x0072B9D8, t0 - self.speed)