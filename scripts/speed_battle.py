"script"
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg: happy.Cg) -> None:
        super().__init__(cg)
        self.name = "高速战斗"
        self.speed = 7.0

    def _write_speed(self, cg: happy.Cg):
        value = cg.mem.read_double(0x00548F10)
        if value != self.speed:
            cg.mem.write_double(0x00548F10, self.speed)

    def _write_original(self, cg: happy.Cg):
        value = cg.mem.read_double(0x00548F10)
        if value != 16.6666666666666667:
            cg.mem.write_double(0x00548F10, 16.6666666666666667)

    def on_battle(self, cg: happy.Cg):
        self._write_speed(cg)

    def on_not_battle(self, cg: happy.Cg):
        self._write_original(cg)

    def on_update(self, cg: happy.Cg):
        if cg.state in (9, 10) and cg.state2 in (5, 1, 2, 4, 8, 11):
            self._write_speed(cg)

    def on_stop(self, cg: happy.Cg):
        self._write_original(cg)
