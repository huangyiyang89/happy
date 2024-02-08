"script"
import happy

class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "迷宫寻路"

    def on_not_moving(self, cg: happy.Cg):
        cg.map.read_data()
        if len(cg.map.exits) < 2:
            cg.map.request_map_data()
        else:
            cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])

