"script"
import happy
import time
import random
from happy.util import b62


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "里洞战神"

    def on_not_battle(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        

        if cg.player.hp_per < 30 or cg.player.mp < 30 or cg.pets.battle_pet.hp_per < 30:
            self.on_low_health(cg)
            return

        # 亚诺曼医院
        if cg.map.id == 30105:
            cg.tp()

        # 亚诺曼
        if cg.map.id == 30010:
            cg.go_astar(21, 126)

        # 德威特岛
        if cg.map.id == 30001:
            cg.go_astar(129, 295)

        # 里洞（外）
        if cg.map.id == 32511:
            if len(cg.map.exits) > 0:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            else:
                cg.map.read_data()
                cg.go_astar(25, 15)

        if "地下" in cg.map.name:
            if len(cg.map.exits) < 2:
                e1 = random.randint(0, cg.map.width_east)
                e2 = random.randint(0, cg.map.width_east)
                s1 = random.randint(0, cg.map.height_south)
                s2 = random.randint(0, cg.map.height_south)
                cg._decode_send(
                    f"UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}"
                )
            for exit in cg.map.exits:
                if exit[2] == 17955:
                    cg.go_astar(exit[0], exit[1])

    def on_low_health(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.id == 30105:
            if (cg.map.x, cg.map.y) == (13, 22):
                cg.right_click("C")
            else:
                cg.go_to(13, 22)
            return

        if cg.map.id not in (30010, 30105):
            print("low hp and map id wrong")
            cg.tp()
            return

        if (cg.map.x, cg.map.y) == (68, 100) or (cg.map.x, cg.map.y) == (194, 93):
            cg.right_click("A")
            time.sleep(0.5)
        else:
            cg.go_astar(116, 134)

    def on_bag_is_full(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        pass

    def on_enable(self, enable):
        pass
