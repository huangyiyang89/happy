"script"
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "迷宫寻路"

    def on_not_moving(self, cg: happy.Cg):

        if len(cg.map.exits) > 1:
            if "佈滿青苔的洞窟" in cg.map.name:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            elif "黃金迷宮一階段地下49層" in cg.map.name:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            elif "黃金迷宮二階段地下49層" in cg.map.name:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            elif "龍之住處" in cg.map.name:
                cg.go_astar(91, 8)
            elif "'貝茲雷姆的迷宮" in cg.map.name:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            else:
                cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])

    def on_update(self, cg: happy.Cg):
        cg.map.request_map_data()
        cg.map.read_data()

    def on_battle(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
        if len(cg.battle.units.enemies)>0:
            if cg.battle.units.enemies[0].name in ["修伯特"]:
                print(cg.battle.units.enemies[0].formatted_info)
