"""
HappyCG
"""
import threading
import time
import importlib
import importlib.util
import sys
import requests
import random
from typing import Literal
import happy.unit
import happy.player
import happy.pet
import happy.script
import happy.map
from happy.mem import CgMem
from happy.battle import Battle
from happy.service import Service
from happy.item import Item, ItemCollection
from happy.util import b62, merge_path
import happy.pywinhandle


class Cg(Service):
    """_summary_"""

    opened_cg_processes = []

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._is_running = False
        self._thread = None
        self.battle = Battle(mem)
        self.player = happy.player.Player(mem)
        self.pets = happy.pet.PetCollection(mem)
        self.map = happy.map.Map(mem)
        self.items = ItemCollection(mem)
        self._scripts = []
        self.is_closed = False
        self._last_captcha_code = ""

    @staticmethod
    def open(name=""):
        """open cg process and add process to __opened_cg_processes[]
        Returns:
            _type_: HappyCG
        """
        processes = CgMem.list_cg_processes()
        for process in processes:
            if process not in Cg.opened_cg_processes:
                mem = CgMem(process)
                new_cg = Cg(mem)
                if name not in new_cg.player.name:
                    continue
                Cg.opened_cg_processes.append(process)
                new_cg.update()
                return new_cg
        return None

    def _main_loop(self):
        """not used yet"""
        try:
            while self._is_running:
                time.sleep(0.1)
                self.update()
        except Exception as e:  # pylint: disable=broad-except
            print(e)
            self.close()

    def start_loop(self):
        """start main loop not used yet"""
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target=self._main_loop)
            self._thread.start()

    def close(self):
        """close not used yet"""
        if self._is_running:
            self._is_running = False
        Cg.opened_cg_processes.remove(self.mem.process_id)
        self.is_closed = True

    def update(self):
        """update all children and trigger events"""

        self.battle.update()
        self.player.update()
        self.pets.update()
        self.items.update()
        self.map.update()

        for script in self._scripts:
            if script.enable:
                script.on_update(self)
                if self.battle.is_fighting:
                    script.on_battle(self)
                    if self.battle.is_player_turn:
                        script.on_player_turn(self)
                    elif self.battle.is_player_second_turn:
                        script.on_player_second_turn(self)
                    elif self.battle.is_pet_turn:
                        script.on_pet_turn(self)
                    elif self.battle.is_pet_second_turn:
                        script.on_pet_second_turn(self)
                else:
                    script.on_not_battle(self)
                    if not self.is_moving:
                        script.on_not_moving(self)

    def go_to(self, x, y):
        """_summary_

        Args:
            x (_type_): _description_
            y (_type_): _description_
        """
        # 走路
        # 0046845D  原A3 C8 C2 C0 00 改90 90 90 90 90
        # 00468476  原89 0D C4 C2 C0 00 改90 90 90 90 90 90
        # 00C0C2C4 X 00C0C2C8 Y 00C0C2DC 置1
        print(self.player.name + f"start going to {x} {y}")
        self.mem.write_bytes(0x0046845D, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_bytes(0x00468476, bytes.fromhex("90 90 90 90 90 90"), 6)
        self.mem.write_int(0x00C0C2C4, x)
        self.mem.write_int(0x00C0C2C8, y)
        self.mem.write_int(0x00C0C2DC, 1)
        time.sleep(0.1)

        # 还原
        self.mem.write_int(0x00C0C2DC, 0)
        self.mem.write_bytes(0x0046845D, bytes.fromhex("A3 C8 C2 C0 00"), 5)
        self.mem.write_bytes(0x00468476, bytes.fromhex("89 0D C4 C2 C0 00"), 6)

    def go_if(self, x1, y1, x2, y2, x3=None, y3=None, map_id=None):
        """_summary_

        Args:
            x1 (_type_): _description_
            y1 (_type_): _description_
            x2 (_type_): _description_
            y2 (_type_): _description_
            x3 (_type_, optional): _description_. Defaults to None.
            y3 (_type_, optional): _description_. Defaults to None.
            map_id (_type_, optional): _description_. Defaults to None.
        """
        if map_id is not None:
            if self.map.id != map_id:
                return
        if (x1 <= self.map.x <= x2 or x2 <= self.map.x <= x1) and (
            y1 <= self.map.y <= y2 or y2 <= self.map.y <= y1
        ):
            if x3 is not None and y3 is not None:
                if not (self.map.x == x3 and self.map.y == y3):
                    self.go_to(x3, y3)

            if x3 is None and y3 is None:
                if self.map.x == x2 and self.map.y == y2:
                    return
                self.go_to(x2, y2)

    def go_astar(self, x, y):
        """_summary_

        Args:
            x (_type_): _description_
            y (_type_): _description_
        """
        self.map.read_data()
        path = self.map.astar(x, y)
        if path and len(path) > 1:
            path = merge_path(path)
            self.go_to(*path[1])
        else:
            print("未找到路径")
            self.go_to(x + random.randint(-2, 2), y + random.randint(-2, 2))
            self.map.read_data()

    def load_script(self, file_path, module_name, class_name, enable=False):
        """_summary_

        Args:
            module_name (_type_): _description_
            class_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, file_path + module_name + ".py"
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            script_class = getattr(module, class_name)
            instance = script_class()
            if isinstance(instance, happy.script.Script):
                instance.enable = enable
                self._scripts.append(instance)

            print(f"'{class_name}' from module '{module_name}' loaded successfully.")
            return instance
        except (ImportError, AttributeError) as e:
            print(
                f"Failed to load class '{class_name}' from module '{module_name}': {e}"
            )
            return None

    def eat_food(self, lose_mp=600, excepts="魅惑的哈密瓜麵包"):
        """对玩家使用物品栏中第一个类型为料理的物品"""

        first_food = next(
            (food for food in self.items.foods if food.name not in excepts), None
        )
        if first_food is not None:
            if self.player.mp_max - self.player.mp >= lose_mp:
                self.use_item(first_food)
                self.select_target()
                self._decode_send(
                    f"iVfo {self.map.x_62} {self.map.y_62} {first_food.index_62} 0"
                )
            if (
                self.pets.battle_pet.mp_max - self.pets.battle_pet.mp >= lose_mp
                and self.pets.battle_pet.mp < 200
                and self.pets.battle_pet.has_power_magic_skill()
            ):
                self.use_item(first_food)
                self.select_target()
                self._decode_send(
                    f"iVfo {self.map.x_62} {self.map.y_62} {first_food.index_62} {self.pets.battle_pet.index+1}"
                )
        else:
            print("nothing to eat")

    def eat_drug(self, lose_hp=400, excepts=""):
        """对玩家使用物品栏中第一个类型为药的物品"""
        if self.player.hp_max - self.player.hp >= lose_hp:
            first_drug = next(
                (drug for drug in self.items.drugs if drug.name not in excepts), None
            )
            if first_drug is not None:
                self.use_item(first_drug)
                self.select_target()
                self._decode_send(
                    f"iVfo {self.map.x_62} {self.map.y_62} {first_drug.index_62} 0"
                )
            else:
                print("nothing to eat")

    def use_item(self, item: Item):
        """_summary_

        Args:
            item (Item): _description_
        """
        self._decode_send(f"Ak {self.map.x_62} {self.map.y_62} {item.index_62} 0")

    def select_target(self):
        """_summary_"""
        self._decode_send("mjCv 0")

    def right_click(self, direction: Literal["A", "B", "C", "D", "E", "F", "G", "H"]):
        """鼠标右键点击交互

        Args:
            direction: A-H,顺时针表示左上,上,右上,右,右下,下,左下,左
        """
        self._decode_send(f"zA {self.map.x_62} {self.map.y_62} {direction} 0")

    def tp(self):
        """登出"""
        self._decode_send("lO")

    @property
    def is_moving(self) -> bool:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x0054DCB0) != 65535

    @property
    def account(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(0x00D15644)

    @property
    def is_opening_dialog(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_dialog_type() != 4294967295

    def get_dialog_type(self):
        """没有对话窗口为FFFFFFFF=4294967295
        医生窗口为2
        卖东西为7
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x005709B8)

    def get_npc_type(self):
        """最近一次交互过的NPC类型
        328普通护士 364资深护士 336医师
        对话结束值不变，不能判断是正否在对话
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00C43900)

    def get_npc_id(self):
        """最近一次交互过的NPC id
        对话结束值不变，不能判断是正否在对话
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00C32AB0)

    def call_nurse(self):
        """打开对话窗口后三补"""
        # 对话id 医生编号
        # yJ 9 w 5W 2Me 4 西医资深补宠
        # yJ 8 x 5W 2Mf 4 东医资深
        # yJ 8 v 5m 2LV 4 东医普通
        # yJ 9 u 5m 2LW 4 西医普通

        # yJ 9 w 5T 2Me 4 西医资深补蓝
        # yJ 9 u 5j 2LW 4 西医普通补蓝

        # yJ 9 w 5V 2Me 4 西医资深补血
        # yJ 9 u 5l 2LW 4 西医普通补血
        dialog_type = self.get_dialog_type()
        if dialog_type == 2:
            npc_type = self.get_npc_type()
            npc_id = self.get_npc_id()
            x62 = self.map.x_62
            y62 = self.map.y_62
            npc_id_62 = b62(npc_id)

            if npc_type == 328:
                if self.player.mp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5j {npc_id_62} 4")
                if self.player.hp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5l {npc_id_62} 4")
                if (
                    self.pets.battle_pet is not None
                    and (self.pets.battle_pet.hp_per + self.pets.battle_pet.mp_per)
                    < 200
                ):
                    self._decode_send(f"xD {x62} {y62} 5m {npc_id_62} 4")
            if npc_type == 364:
                if self.player.mp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5T {npc_id_62} 4")
                if self.player.hp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5V {npc_id_62} 4")
                if (
                    self.pets.battle_pet is not None
                    and (self.pets.battle_pet.hp_per + self.pets.battle_pet.mp_per)
                    < 200
                ):
                    self._decode_send(f"xD {x62} {y62} 5W {npc_id_62} 4")

    def sell(self):
        """_summary_"""
        # xD 29 29 5o 54L 0 11\\z3\\z12\\z3\\z13\\z3\\z14\\z3\\z15\\z3\\z16\\z3\\z18\\z3\\z19\\z3\\z21\\z3\\z23\\z3\\z24\\z3\\z25\\z1\\z26\\z2\\z27\\z1
        unk = self.mem.read_int(0x00CAF1F4)
        dialog_type = self.get_dialog_type()
        if dialog_type == 5:
            # npc_type = self.get_npc_type()
            npc_id_62 = b62(self.get_npc_id())
            x62 = self.map.x_62
            y62 = self.map.y_62
            items_str = ""
            for item in self.items.bags_valids:
                if "魔石" in item.name or "卡片" in item.name:
                    items_str += str(item.index) + r"\\z" + str(item.count) + r"\\z"
            content = f"xD {x62} {y62} 5o {b62(unk)} 0 " + items_str[:-3]
            self._decode_send(content)

    def _stop_random_key(self):
        self.mem.write_bytes(0x00530CA3, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_bytes(0x00530CB9, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_int(0x0057E998, 2)

    def produce(self, craft_id=0, craft_name=""):
        """根据生产的物品名称或id生产

        Args:
            craft_id (int, optional): 寿喜锅 912. Defaults to 0.
            craft_name (str, optional): _description_. Defaults to "".
        """
        self._stop_random_key()

        craft: PlayerSkillCraft = self.player.skills.find_craft(craft_id, craft_name)
        if craft is None:
            print("未找到要生产的技能")
            return False
        if craft.cost > self.player.mp:
            print("mp不足")
            return False

        items_str = ""
        for ingredient in craft.ingredients:
            item = self.items.find(ingredient.itemid, ingredient.name, ingredient.count)
            if item is None:
                box = self.items.find_box(ingredient.name)
                if box:
                    self.use_item(box)
                    return True
                print("材料用尽。")
                return False
            items_str = "|" + str(item.index) + items_str

        send_content = f"sM {craft.skill.index} 0 -1 {craft.id}" + items_str
        self._decode_send("Ivfo q")
        time.sleep(14)
        self._decode_send(send_content)
        return True

    def get_captcha(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        code = self.mem.read_string(0x00C32D4E, 10)
        if code != "" and self._last_captcha_code != code:
            self._last_captcha_code = code
            return code
        return None

    @staticmethod
    def close_handles():
        """_summary_"""
        process_ids = list(CgMem.list_cg_processes())
        handles = happy.pywinhandle.find_handles(process_ids, ["汢敵"])
        happy.pywinhandle.close_handles(handles)

    def send_wechat_notification(self):
        """_summary_

        Args:
            content (_type_): _description_
        """
        code = self.get_captcha()
        if code is not None:
            url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e0ce689b-5a47-4ae2-ab5e-0539268956d7"
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"### 账号: {self.account}\n### 验证链接:\n[https://www.bluecg.net/plugin.php?id=gift:v3&ac={self.account}&time={code}](https://www.bluecg.net/plugin.php?id=gift:v3&ac={self.account}&time={code})"
                }
            }
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload, headers=headers, timeout=1000)

            if response.status_code == 200:
                print("Markdown message sent successfully.")
            else:
                print(
                    "Failed to send Markdown message. Status code:",
                    response.status_code,
                )
