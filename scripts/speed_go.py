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
        self.name = "高速移动"
        self.speed = 135


    def on_not_battle(self, cg):
        cg.mem.write_int(0x00F4C460,self.speed)
