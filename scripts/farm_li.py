"script"
import time
import random
import happy
from happy.util import b62


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "里洞战神"

    def on_not_moving(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        if cg.items.blanks_count == 0:
            self.on_bag_is_full(cg)
            return

        if cg.player.hp_per < 30 or cg.player.mp < 30 or cg.pets.battle_pet.hp_per < 30:
            self.on_low_health(cg)
            return

        # 亚诺曼医院
        if cg.map.id == 30105:
            cg.tp()

        # 亚诺曼
        if cg.map.id == 30010:
            if cg.map.x > 100:
                cg.tp()
            else:
                cg.go_astar(21, 126)

        # 德威特岛
        if cg.map.id == 30001:
            cg.go_if(211,344,156,339,156,343)
            cg.go_if(156,343,153,315)
            cg.go_if(153,315,122,306)
            cg.go_if(122,306,129,295)

        # 里洞（外）
        if cg.map.id == 32511:
            if len(cg.map.exits) > 0:
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            else:
                cg.go_astar(25, 15)

        if "地下" in cg.map.name:
            cg.map.read_data()
            if len(cg.map.exits) < 2:
                e1 = random.randint(0, cg.map.width_east)
                e2 = random.randint(0, cg.map.width_east)
                s1 = random.randint(0, cg.map.height_south)
                s2 = random.randint(0, cg.map.height_south)
                cg._decode_send(
                    f"UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}"
                )
                # cg._decode_send(
                #         f"UUN 1 {b62(cg.map.id)} {cg.map.x} {cg.map.y} {b62(cg.map.width_east)} {b62(cg.map.height_south)}"
                # )
                cg.go_astar(cg.map.x+random.randint(-5,5),cg.map.y+random.randint(-5,5))
            else:
                if cg.map.exits[-1][2] == 17955:
                    cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])
                else:
                    # 到达最后一层
                    cg.go_astar(cg.map.x+random.randint(-5,5),cg.map.y+random.randint(-5,5))

        if "底層" in cg.map.name:
            cg.go_if(13, 6, 6, 10)
            cg.go_if(
                6, 10, 12, 22, 9 + random.randint(-2, 2), 16 + random.randint(-2, 2)
            )

    def on_low_health(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.id not in (30010, 30105):
            print("low hp and map id wrong")
            cg.tp()
            return

        if cg.map.id == 30105:
            if (cg.map.x, cg.map.y) == (13, 23):
                cg.right_click("B")
            else:
                cg.go_to(13, 23)

        if cg.map.id == 30010:
            if (cg.map.x, cg.map.y) == (68, 100) or (cg.map.x, cg.map.y) == (194, 93):
                cg.right_click("A")
                time.sleep(0.5)
            else:
                cg.go_to(116, 134)

    def on_bag_is_full(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.id not in [30105, 30010]:
            cg.tp()

        # 亚诺曼医院
        if cg.map.id == 30105:
            cg.go_to(8, 29)
            return

        # 亚诺曼
        if cg.map.id == 30010:
            cg.go_if(116, 130, 136, 142, 133, 133)

            if (cg.map.x, cg.map.y) == (68, 100) or (cg.map.x, cg.map.y) == (194, 93):
                cg.right_click("A")
                time.sleep(0.5)

            if (cg.map.x, cg.map.y) == (133, 133):
                cg.right_click("A")
                cg.sell()
            return

    def on_enable(self, enable):
        pass
