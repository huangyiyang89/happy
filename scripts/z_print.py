"script"
import time
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "指令输出"
        self.last = ""
    

    def on_update(self, cg: happy.Cg):
        addr = 0x00580CE1
        new = cg.mem.read_string(addr)
        new = new.split("\n")[0]
        if new != self.last:
            print(new)
            self.last = new

