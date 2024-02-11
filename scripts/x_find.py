"script"
import happy
import time
class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "迷宫寻路"

    def on_not_moving(self, cg: happy.Cg):
        if "黃金迷宮一階段地下49層" in cg.map.name:
            cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])

        if len(cg.map.exits) > 1:
            cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])

    def on_update(self, cg: happy.Cg):
        cg.send_wechat_notification()
        if len(cg.map.exits) < 2:
            cg.map.request_map_data()
