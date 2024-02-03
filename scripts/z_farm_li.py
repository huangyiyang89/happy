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
        self.name = "里洞魔石"
        self.sell_record = []

    def on_not_moving(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        if cg.items.blanks_count == 0:
            self.go_to_sell(cg)
            return

        if cg.player.hp_per < 30 or cg.player.mp < 30 or cg.pets.battle_pet.hp_per < 30:
            self.go_to_heal(cg)
            return

        # 亚诺曼
        if cg.map.id == 30010:
            if cg.items.blanks_count < 10:
                self.go_to_sell(cg)
                return
            if cg.map.x > 100:
                cg.tp()
            else:
                cg.go_astar(21, 126)

        # 亚诺曼医院
        if cg.map.id == 30105:
            cg.tp()

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
            # cg.map.read_data()
            if len(cg.map.exits) < 2:
            #     e1 = random.randint(0, cg.map.width_east)
            #     e2 = random.randint(0, cg.map.width_east)
            #     s1 = random.randint(0, cg.map.height_south)
            #     s2 = random.randint(0, cg.map.height_south)
            #     cg._decode_send(
            #         f"UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}"
            #     )
                # cg._decode_send(
                #         f"UUN 1 {b62(cg.map.id)} {cg.map.x} {cg.map.y} {b62(cg.map.width_east)} {b62(cg.map.height_south)}"
                # )
                cg.go_astar(cg.map.x+random.randint(-5,5),cg.map.y+random.randint(-5,5))
            else:
                if cg.map.exits[-1][2] == 17955:
                    #cg.map.map_flag_data[cg.map.exits[0][1]][cg.map.exits[0][0]]= 0 #上一層樓梯設置不可到達防止來回上下樓
                    cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])
                else:
                    # 到达最后一层
                    cg.go_astar(cg.map.x+random.randint(-5,5),cg.map.y+random.randint(-5,5))

        if "底層" in cg.map.name:
            if cg.map.x == 13:
                cg.go_to(12,6)
            else:
                cg.go_to(13,6)

    def go_to_heal(self, cg: happy.Cg):
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

    def go_to_sell(self, cg: happy.Cg):
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
                self.sell_record.append((cg.items.gold,time.gmtime()))
            return

    def on_enable(self, enable):
        self.sell_record = []

    def on_update(self, cg: happy.Cg):
        cg.send_wechat_notification()
        if "地下" in cg.map.name:
            cg.map.read_data()
            if len(cg.map.exits) < 2:
                    e1 = random.randint(0, cg.map.width_east)
                    e2 = random.randint(0, cg.map.width_east)
                    s1 = random.randint(0, cg.map.height_south)
                    s2 = random.randint(0, cg.map.height_south)
                    cg._decode_send(
                        f"UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}")