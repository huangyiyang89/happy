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
        self.name = "自动拉霸"

    def on_not_moving(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """

        if cg.map.x == 27 and cg.map.y == 19:
            item = cg.items.find("籌碼")
            if item:
                cg.laba()
                cg.items.tidyup()
                time.sleep(0.1)

    def on_battle(self, cg: happy.Cg):
        if cg.battle.is_pet_turn:
            for enemy in cg.battle.units.enemies:
                print(enemy.formatted_info)

