"script"
import time
import random
import logging
import happy
from happy.util import send_wechat_notification


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "里洞魔石"
        self.start_time = time.time
        self.sell_record = []
        self.move_record = []
        self._last_update_time = 0

    def on_start(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.sell_record = []
        self.move_record = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        cg.set_auto_ret_blackscreen()
        cg.set_auto_login()
        cg.set_auto_select_charater()

    def on_stop(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
        cg.set_auto_ret_blackscreen(False)
        cg.set_auto_login(False)
        cg.set_auto_select_charater(False)

    def on_not_moving(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        if cg.items.blanks_count == 0:
            self.go_to_sell(cg)
            return

        if cg.player.mp_per != 100 and cg.map.name in ("亞諾曼城", "中央醫院"):
            self.go_to_heal(cg)
            return

        # 武器损坏装备背包内武器
        if not cg.items[2].valid:
            bow = cg.items.find(item_name="弓")
            if bow:
                cg.use_item(bow)
            else:
                self.go_to_buy_bow(cg)
            return

        # 水晶損壞
        if not cg.items[7].valid:
            crystal = cg.items.find(item_name="地水的水晶")
            if crystal:
                cg.use_item(crystal)
            else:
                self.go_to_buy_crystal(cg)
            return

        if cg.player.hp_per < 40 or cg.player.mp < 60 or cg.pets.battle_pet.hp_per < 30:
            self.go_to_heal(cg)
            return

        if cg.player.injury or (cg.pets.battle_pet and cg.pets.battle_pet.injury):
            self.go_to_cure(cg)
            return

        if cg.map.name in "亞諾曼城" and cg.items.blanks_count < 10:
            self.go_to_sell(cg)
            return

        # 亞諾曼
        if cg.map.name in "亞諾曼城":
            if (cg.map.x, cg.map.y) == (120, 139):
                cg.right_click("A")
                time.sleep(0.5)
            if cg.map.x >= 21 and cg.map.x <= 73 and cg.map.y >= 97 and cg.map.y <= 127:
                cg.go_if(73, 97, 60, 105)
                cg.go_if(61, 105, 57, 125)
                cg.go_if(58, 127, 21, 125)
                return
            cg.tp()
        # 德威特岛
        if cg.map.id == 30001:
            cg.go_astar(129, 295)

            # 处理卡死
            cg.go_if(129, 295, 128, 295)

            return

        # 里洞（外）
        if cg.map.id == 32511:
            if len(cg.map.exits) != 0:
                if cg.map.x == cg.map.exits[0][0] and cg.map.y == cg.map.exits[0][1]:
                    cg.go_astar(
                        cg.map.x + random.randint(-1, 1),
                        cg.map.y + random.randint(-1, 1),
                    )
                cg.go_astar(cg.map.exits[0][0], cg.map.exits[0][1])
            else:
                cg.go_astar(24, 19)
            return

        if "地下" in cg.map.name:
            if len(cg.map.exits) < 2:
                cg.go_astar(
                    cg.map.x + random.randint(-5, 5), cg.map.y + random.randint(-5, 5)
                )
            else:
                if cg.map.exits[-1][2] == 17955:
                    if (
                        cg.map.x == cg.map.exits[-1][0]
                        and cg.map.y == cg.map.exits[-1][1]
                    ):
                        cg.go_astar(
                            cg.map.x + random.randint(-1, 1),
                            cg.map.y + random.randint(-1, 1),
                        )
                    cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])
                else:
                    # 到达最后一层
                    cg.go_astar(
                        cg.map.x + random.randint(-5, 5),
                        cg.map.y + random.randint(-5, 5),
                    )
            return

        if "底層" in cg.map.name:
            if cg.map.x == 13:
                cg.go_to(12, 6)

            else:
                cg.go_to(13, 6)
            return

        cg.tp()
        time.sleep(1)

    def go_to_hospital(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        print(cg.player.name + ":" + self.efficiency)
        if cg.map.name in "亞諾曼城":
            if cg.map.x == 116 and cg.map.y == 134:
                cg.go_to(116, 135)
                return
            if cg.map.x < 122 and cg.map.x > 114 and cg.map.y < 141 and cg.map.y > 133:
                cg.go_to(116, 134)
                return
            cg.tp()
            return
        if cg.map.name in "中央醫院":
            return

        cg.tp()

    def go_to_heal(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.name not in "中央醫院":
            self.go_to_hospital(cg)
            return
        if cg.map.y > 23:
            cg.go_to(13, 23)
            return
        if (cg.map.x, cg.map.y) == (13, 23):
            cg.right_click("B")
            return
        cg.tp()

    def go_to_sell(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.name not in "亞諾曼城":
            cg.tp()
        # 亚诺曼
        if cg.map.id == 30010:
            cg.go_if(116, 130, 136, 142, 133, 133)

            if (cg.map.x, cg.map.y) == (68, 100) or (cg.map.x, cg.map.y) == (194, 93):
                cg.right_click("A")
                time.sleep(0.5)

            if (cg.map.x, cg.map.y) == (133, 133):
                cg.right_click("A")
                time.sleep(0.5)
                cg.sell()
            return

    def go_to_cure(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.name not in "中央醫院":
            self.go_to_hospital(cg)
            return
        if cg.map.y > 23:
            cg.go_to(7, 23)
            return
        cg.go_if(13, 23, 7, 17)
        cg.go_if(7, 23, 7, 9)
        cg.go_if(7, 9, 9, 7)
        if (cg.map.x, cg.map.y) == (9, 7):
            cg.right_click("B")
            cg.cure()

    def go_to_buy_bow(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.name in "亞諾曼城":
            cg.go_if(120, 139, 93, 138)
            cg.go_if(93, 138, 93, 123)
            cg.go_if(93, 123, 100, 114)
            return
        if cg.map.name in "銳健武器店":
            if (cg.map.x, cg.map.y) == (18, 13):
                cg.right_click("C")
                cg.buy_bow()
                time.sleep(1)
            else:
                cg.go_to(18, 13)
            return
        cg.tp()

    def go_to_buy_crystal(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.Cg): _description_
        """
        if cg.map.name in "亞諾曼城":
            cg.go_if(120, 139, 93, 138)
            cg.go_if(93, 138, 93, 128)
            cg.go_if(93, 128, 97, 128)
            return
        if cg.map.name in "命運小屋":
            if (cg.map.x, cg.map.y) == (15, 22):
                cg.right_click("C")
                cg.buy_crystal()
                time.sleep(1)
            else:
                cg.go_to(15, 22)
            return
        cg.tp()

    def on_update(self, cg: happy.Cg):

        cg.retry_if_login_failed()
        # 迷宫内或者洞外
        if "地下" in cg.map.name or cg.map.id == 32511:
            if time.time() - self._last_update_time > 2:
                cg.map.read_data()
                self._last_update_time = time.time()
            if len(cg.map.exits) < 2:
                cg.map.request_map_data()



        # 记录效率
        if len(self.sell_record) == 0:
            self.sell_record.append((cg.items.gold, time.time()))
        else:
            if cg.items.gold > self.sell_record[-1][0]:
                self.sell_record.append((cg.items.gold, time.time()))
                logging.info("%s 出售魔石,当前魔币:%s", cg.account, cg.items.gold)

        if time.time() - self.move_record[2][2] >= 100:
            self.move_record.append((cg.map.x, cg.map.y, time.time()))
            self.move_record.pop(0)
        if (
            self.move_record[0][:2]
            == self.move_record[1][:2]
            == self.move_record[2][:2]
        ):
            if cg.is_disconnected:
                logging.warning("%s 已掉线,尝试重连.", cg.account)
                send_wechat_notification(
                    f"{cg.account} {cg.player.name} 已掉线,尝试重连."
                )
                self.move_record = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
            else:
                cg.tp()
                logging.warning("%s 角色疑似卡死,TP.", cg.account)
                send_wechat_notification(
                    f"{cg.account} {cg.player.name} 角色疑似卡死,{cg.map.name} {cg.map.x},{cg.map.y} TP."
                )
                self.move_record = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]

    def on_not_battle(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
        # 仍东西
        # cg.drop_item("卡片", "魔石(18G)")
        if cg.map.id == 30001:
            cg.map.read_data()

    @property
    def efficiency(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if len(self.sell_record) > 2:
            return (
                str(
                    int(
                        (self.sell_record[-1][0] - self.sell_record[1][0])
                        / (self.sell_record[-1][1] - self.sell_record[1][1])
                        * 3600
                    )
                )
                + "/h 当前:"
                + str(self.sell_record[-1][0])
            )
        return "N/A"
