"""
HappyCG
"""

import os, glob
import threading
import time
import logging
import importlib
import importlib.util
import sys
from typing import Literal, Callable
import psutil
import happy.unit
import happy.player
import happy.pet
import happy.map
from happy.mem import CgMem
from happy.battle import Battle
from happy.service import Service
from happy.item import Item, ItemCollection
from happy.util import b62, merge_path, solve_captcha, solve_captcha_v2
import happy.pywinhandle
from pymem.exception import MemoryReadError


class Cg(Service):
    """_summary_"""

    opened_cg_processes = []
    opened_cg_list: list["Cg"] = []

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._is_running = False
        self._thread = None
        self.battle = Battle(mem)
        self.player = happy.player.Player(mem)
        self.pets = happy.pet.PetCollection(mem)
        self.map = happy.map.Map(mem)
        self.items = ItemCollection(mem)
        self._scripts: list[Script] = []
        self.is_closed = False
        self._last_update_time = 0
        self._eat_food_flag = 0
        self.on_close: Callable = None

    @property
    def _tick_count(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C304)

    @staticmethod
    def open(account=None, name=None):
        """open cg process and add to opened_cg_list
        Returns:
            _type_: HappyCG
        """
        Cg.opened_cg_list.sort(key=lambda x: x.account)
        processes = CgMem.list_cg_processes()
        process_ids = [cg.mem.process_id for cg in Cg.opened_cg_list]
        for process in processes:
            if process not in process_ids:
                mem = CgMem(process)
                new_cg = Cg(mem)
                if (
                    (account and new_cg.account == account)
                    or (name and new_cg.player.name and name in new_cg.player.name)
                    or (not account and not name)
                ):
                    Cg.opened_cg_list.append(new_cg)
                    new_cg.load_scripts()
                    new_cg.start_loop()
                    return new_cg
        return None

    def process_is_closed(self):
        """判断游戏进程是否已关闭

        Returns:
            _type_: _description_
        """
        return not self.mem.process_id in (p.pid for p in psutil.process_iter())

    def _main_loop(self):
        """not used yet"""

        while self._is_running:
            try:
                self.update()
                time.sleep(0.1)
            except MemoryReadError as e:
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
        if not self.is_closed:
            self.is_closed = True
            Cg.opened_cg_list.remove(self)
        if self.on_close is not None:
            self.on_close()

    @property
    def is_exist(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return not self.is_closed

    def update(self):
        """update all children and trigger events"""
        self._last_update_time = time.time()
        self.map.update()
        self.battle.update()
        self.player.update()
        self.pets.update()
        self.items.update()

        for script in self._scripts:
            if script.enable:
                if script.state == 1:
                    script.on_start(self)
                    script.state = 2
                    return
                if script.state == 3:
                    script.on_stop(self)
                    script.state = 0
                    return
                script.on_update(self)
                if self.state == 9 and self.state2 == 3:
                    script.on_not_battle(self)
                    if not self.is_moving:
                        script.on_not_moving(self)
                if self.battle.is_fighting:
                    self._eat_food_flag = 0
                    script.on_battle(self)
                    if self.battle.is_player_turn:
                        script.on_player_turn(self)
                    elif self.battle.is_player_second_turn:
                        script.on_player_second_turn(self)
                    elif self.battle.is_pet_turn:
                        script.on_pet_turn(self)
                    elif self.battle.is_pet_second_turn:
                        script.on_pet_second_turn(self)

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
        # print(self.player.name + f"start going to {x} {y}")
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

    # TODO：改进这个函数
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
                return False
        if (x1 <= self.map.x <= x2 or x2 <= self.map.x <= x1) and (
            y1 <= self.map.y <= y2 or y2 <= self.map.y <= y1
        ):
            if x3 is not None and y3 is not None:
                if not (self.map.x == x3 and self.map.y == y3):
                    self.go_to(x3, y3)
                    return True

            if x3 is None and y3 is None:
                if self.map.x == x2 and self.map.y == y2:
                    return False
                self.go_to(x2, y2)
                return True
        return False

    def go_astar(self, x, y):
        """_summary_

        Args:
            x (_type_): _description_
            y (_type_): _description_
        """
        path = self.map.astar(x, y)
        if path and len(path) > 1:
            path = merge_path(path)
            self.go_to(*path[1])

    def go_send_call(
        self,
        direction=Literal[
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "aa",
            "bb",
            "cc",
            "dd",
            "ee",
            "ff",
            "gg",
            "hh",
        ],
    ):
        """发走路包

        Args:
            direction (_type_, optional): _description_. Defaults to \
                Literal["a", "b", "c", "d", "e", "f", "g", "h","aa", \
                    "bb", "cc", "dd", "ee", "ff", "gg", "hh"].
        """
        self._decode_send(f"zA {self.map.x_62} {self.map.y_62} {direction} 0")

    def load_scripts(self):
        scripts_directory = os.path.join(os.path.dirname(sys.argv[0]), "scripts\\")
        py_files = glob.glob(os.path.join(scripts_directory, "*.py"))
        script_file_names = [
            os.path.splitext(os.path.basename(file))[0] for file in py_files
        ]
        for script_file_name in script_file_names:
            self.load_script(scripts_directory, script_file_name, "Script")

    def load_script(self, file_path, module_name, class_name):
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
            instance = script_class(self)
            if isinstance(instance, Script):
                self._scripts.append(instance)

            print(f"'{class_name}' from module '{module_name}' loaded successfully.")
            return instance
        except (ImportError, AttributeError) as e:
            print(
                f"Failed to load class '{class_name}' from module '{module_name}': {e}"
            )
            return None

    def eat_food(self):
        """对玩家使用物品栏中第一个类型为料理的物品"""

        if self.battle.is_fighting:
            self._eat_food_flag = 0
            return

        first_food = self.items.first_food
        if first_food is None:
            box = self.items.first_food_box
            if box:
                self.use_item(box)
                time.sleep(0.5)
            return

        re_mp = 0
        if first_food.name == "魚翅湯":
            re_mp = 1000
        if first_food.name == "壽喜鍋":
            re_mp = 600
        if first_food.name == "漢堡":
            re_mp = 450
        if first_food.name == "麵包":
            re_mp = 100

        if (
            self._eat_food_flag in (0, 1)
            and self.player.mp_max - self.player.mp >= re_mp
        ):
            self.use_item(first_food)
            self.select_target()
            self._decode_send(
                f"iVfo {self.map.x_62} {self.map.y_62} {first_food.index_62} 0"
            )
            self._eat_food_flag += 2
            return

        if (
            self._eat_food_flag in (0, 2)
            and self.pets.battle_pet
            and self.pets.battle_pet.mp_max - self.pets.battle_pet.mp >= re_mp
            and self.pets.battle_pet.mp < 300
            and (
                self.pets.battle_pet.has_power_magic_skill()
                or (
                    self.pets.battle_pet.hp_per < 50
                    and self.pets.battle_pet.mp_per < 10
                )
            )
        ):
            self.use_item(first_food)
            self.select_target()
            self._decode_send(
                f"iVfo {self.map.x_62} {self.map.y_62} {first_food.index_62} {self.pets.battle_pet.index+1}"
            )
            self._eat_food_flag += 1

    def eat_drug(self):
        """对玩家使用物品栏中第一个类型为药的物品"""
        if self.player.hp_max > 500:
            return
        first_drug = self.items.first_drug
        if first_drug is None:
            return
        recovery = first_drug.is_drug
        if self.player.hp_lost >= recovery:
            self.use_item(first_drug)
            self.select_target()
            self._decode_send(
                f"iVfo {self.map.x_62} {self.map.y_62} {first_drug.index_62} 0"
            )
            time.sleep(0.5)

        if self.pets.battle_pet and self.pets.battle_pet.hp_lost >= recovery:
            self.use_item(first_drug)
            self.select_target()
            self._decode_send(
                f"iVfo {self.map.x_62} {self.map.y_62} {first_drug.index_62} {self.pets.battle_pet.index+1}"
            )
            time.sleep(0.5)

    def use_item(self, item: Item | str):
        """_summary_

        Args:
            item (Item): _description_
        """
        
        if isinstance(item,str):
            item_to_use = self.items.find(item)
        if isinstance(item,Item):
            item_to_use = item
        if item_to_use:
            self._decode_send(f"Ak {self.map.x_62} {self.map.y_62} {item_to_use.index_62} 0")
        else:
            pass

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
        self.mem.write_int(0x00F62954, 7)
        self.mem.write_int(0x00F62954, 3)

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
    def customize_title(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(0x00F4C409)

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
        东门药剂师5
        卖东西为7
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x005709B8)

    def get_npc_type(self):
        """最近一次交互过的NPC类型
        333东门药剂师 328普通护士 364资深护士 336医师
        对话结束值不变，不能判断是正否在对话
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00C43900)

    def get_npc_id(self):
        """最近一次交互过的NPC id
        9616东门药剂师
        对话结束值不变，不能判断是正否在对话
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00CAF1F4)

    def get_team_count(self):
        """队伍人数,0为未组队
        Returns:
            _type_: _description_
        """
        party1 = self.mem.read_int(0x00FFD000)
        party2 = self.mem.read_int(0x00FFD030)
        party3 = self.mem.read_int(0x00FFD060)
        party4 = self.mem.read_int(0x00FFD090)
        party5 = self.mem.read_int(0x00FFD0C0)
        return party1 + party2 + party3 + party4 + party5

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
        npc_id = self.get_npc_id()
        if dialog_type == 2 and npc_id > 0:
            npc_type = self.get_npc_type()
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

    def join_team(self):
        """join team"""
        self._decode_send(f"zn {self.map.x_62} {self.map.y_62} 1")

    def sell(self):
        """_summary_"""
        npc_id = self.get_npc_id()
        dialog_type = self.get_dialog_type()
        if dialog_type == 5:
            x62 = self.map.x_62
            y62 = self.map.y_62
            items_str = ""
            for item in self.items.bags_valids:
                if (
                    "魔石" in item.name
                    or "卡片" in item.name
                    or ("寵物鈴鐺" in item.name and item.count >= 40)
                    or ("紙人娃娃" in item.name and item.count >= 40)
                ):
                    count = 1 if "寵物鈴鐺" in item.name else item.count
                    count = 1 if "紙人娃娃" in item.name else count
                    items_str += str(item.index) + r"\\z" + str(count) + r"\\z"
            if items_str != "":
                content = f"xD {x62} {y62} 5o {b62(npc_id)} 0 " + items_str[:-3]
                self._decode_send(content)

    def engage_npc(
        self, npc_x: int, npc_y: int, dialog_type: int, action: int, send_data: str
    ):
        """
        与 NPC 交互的函数
        f"xD {self.map.x_62} {self.map.y_62} {b62(action)} {b62(now_npc_id)} " + send_data
        参数：
            npc_x (int)：NPC 的 x 坐标
            npc_y (int)：NPC 的 y 坐标
            dialog_type (int)：对话类型
            action (int)：交互动作（326=5g 对话 334=5o 表示卖，335=5p 表示买）
            send_data (str)：要发送给 NPC 的数据

        返回：
            None
        """
        now_dialog_type = self.get_dialog_type()
        if (
            now_dialog_type == dialog_type
            and abs(self.map.x - npc_x) <= 2
            and abs(self.map.y - npc_y) <= 2
        ):
            now_npc_id = self.get_npc_id()
            content = (
                f"xD {self.map.x_62} {self.map.y_62} {b62(action)} {b62(now_npc_id)} "
                + send_data
            )
            print("engage_npc:", content)
            self._decode_send(content)
            time.sleep(1)

    def _stop_random_key(self):
        self.mem.write_bytes(0x00530CA3, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_bytes(0x00530CB9, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_int(0x0057E998, 2)

    @staticmethod
    def close_handles():
        """_summary_"""
        process_ids = list(CgMem.list_cg_processes())
        handles = happy.pywinhandle.find_handles(process_ids, ["汢敵"])
        happy.pywinhandle.close_handles(handles)

    def solve_if_captch(self):
        """_summary_"""
        version = self.mem.read_string(0x00C32CAC, 20)
        isv2 = "v2" in version
        code = self.mem.read_string(0x00C32D4E, 10)
        context = self.mem.read_string(0x00C32D40, 50)
        if code != "" and code.isdigit() and len(code) == 10:
            if isv2:
                success = solve_captcha_v2(self.account, code)
            else:
                success = solve_captcha(self.account, code)
            if success:
                self.mem.write_string(0x00C32D4E, "\0\0\0\0\0\0\0\0\0\0")
            else:
                logging.info(
                    "验证失败,账号:"
                    + self.account
                    + ",code:"
                    + code
                    + ",context:"
                    + context
                )

    def drop_item(self, *args):
        """仍物品，*args可为Item示例或物品名string

        Args:
            item: item_name or Item instance
        """
        for item in args:
            if isinstance(item, Item):
                self._decode_send(
                    f"QpfE {self.map.x_62} {self.map.y_62} 0 {item.index_62}"
                )
            if isinstance(item, str):
                item_to_find = self.items.find(item_name=item)
                if item_to_find:
                    self._decode_send(
                        f"QpfE {self.map.x_62} {self.map.y_62} 0 {item_to_find.index_62}"
                    )

    def get_script(self, name):
        """_summary_

        Args:
            name (_type_): _description_

        Returns:
            _type_: _description_
        """
        for script in self._scripts:
            if script.name == name:
                return script
        return None

    @property
    def is_disconnected(self) -> bool:
        """是否掉线

        Returns:
            bool: _description_
        """
        # 0x00D10EB0 0x00D10EB1 0x00D10EB2
        # value = self.mem.read_bytes(0x00D10EB2, 1)
        # flag = int.from_bytes(value, byteorder="little")

        return not self.state in (9, 10)

    def disable_shell(self, enable=True):
        """禁止游戏弹出网页"""
        pointer = self.mem.read_int(0x0053E220)
        if enable:
            self.mem.write_bytes(pointer, bytes.fromhex("C2 04 00"), 3)
        else:
            self.mem.write_bytes(pointer, bytes.fromhex("8B FF 55"), 3)

    def set_auto_login(self, enable=True):
        """_summary_

        Args:
            line (int, optional): 几线. Defaults to 0.
            enable (bool, optional): _description_. Defaults to True.
        """
        # 00458C40 函数开头
        # 写入几线
        # 00458E1A  E8 80 F0 FF FF 改 B8 D3 00 00 00 BE 03 00 00 00 90 过跳转

        # 处理重连失败弹窗
        # 00458CB9 39 35 54 29 F6 00 0F 85 69 02 00 00 改C7 05 54 29 F6 00 01 00 00 00 90 90

        if enable:
            line = self.mem.read_int(0x00927644)
            line_str = str(line).zfill(2)
            self.mem.write_bytes(
                0x00458E1A,
                bytes.fromhex(f"B8 D3 00 00 00 BE {line_str} 00 00 00 90"),
                11,
            )
        else:
            self.mem.write_bytes(
                0x00458E1A, bytes.fromhex("55 E8 80 F0 FF FF 83 C4 04 A8 40"), 11
            )

    def retry_if_login_failed(self):
        """_summary_"""
        # 1没有小窗 3正在连接
        if self.state == 2:
            state = self.mem.read_int(0x00F62954)
            if not state in (1, 3):
                logging.warning("%s 正在重连", self.account)
                self.mem.write_int(0x00F62954, 1)
                time.sleep(3)

    def set_auto_select_charater(self, enable=True):
        """_summary_

        Args:
            enable (bool, optional): _description_. Defaults to True.
        """
        # call start at 0045A285
        #                                                              0/1左侧右侧角色
        # 0045A2A0 原83 F8 06 0F 87 0D 04 00 00 改 B8 01 00 00 00 66 BB 01 00
        character = self.mem.read_int(0x00F627F8)
        if enable:
            if character == 0:
                self.mem.write_bytes(
                    0x0045A2A0, bytes.fromhex("B8 01 00 00 00 66 BB 00 00"), 9
                )
            else:
                self.mem.write_bytes(
                    0x0045A2A0, bytes.fromhex("B8 01 00 00 00 66 BB 01 00"), 9
                )
        else:
            self.mem.write_bytes(
                0x0045A2A0, bytes.fromhex("83 F8 06 0F 87 0D 04 00 00"), 9
            )

    def set_auto_ret_blackscreen(self, enable=True):
        """_summary_

        Args:
            enable (bool, optional): _description_. Defaults to True.
        """
        # 005122DB  黑屏跳出 0F 84 4D FF FF FF 改90 90 90 90 90 90
        if enable:
            self.mem.write_bytes(0x005122DB, bytes.fromhex("90 90 90 90 90 90"), 6)
        else:
            self.mem.write_bytes(0x005122DB, bytes.fromhex("0F 84 4D FF FF FF"), 6)

    @property
    def state(self):
        """输入账号界面=1 服务器选择=2 角色选择=3 角色创建=4 登陆中=6 游戏中=9 战斗中=10 掉线黑屏=11

        Returns:
            _type_: int
        """
        # 00F62930
        return self.mem.read_int(0x00F62930)

    @property
    def state2(self):
        """输入账号界面= 服务器选择=1 角色选择=11 游戏中=3 战斗输入指令中=4 等待战斗动画中=6   遇敌 5-1-2-3-4  退出战斗2-8-11-2-3

        Returns:
            _type_: int
        """
        return self.mem.read_int(0x00F62954)

    @property
    def move_speed(self):
        """_summary_"""
        self.mem.read_int(0x00F4C460)

    @move_speed.setter
    def move_speed(self, value):
        self.mem.write_int(0x00F4C460, value)

    def cure(self):
        """亞諾曼治療"""
        npc_id = self.get_npc_id()
        if npc_id>0:
            self._decode_send(f"xD 9 7 5q {b62(npc_id)} 0 7")
            logging.warning("%s 正在治疗", self.account)

    def buy_crystal(self):
        """亞諾曼買水晶"""
        npc_id = self.get_npc_id()
        if npc_id>0:
            self._decode_send(f"xD f m 5p {b62(npc_id)} 0 9" + r"\\z1")
            logging.warning("%s 购买水晶", self.account)

    def buy_bow(self):
        """亞諾曼買弓"""
        npc_id = self.get_npc_id()
        if npc_id>0:
            self._decode_send(f"xD i d 5p {b62(npc_id)} 0 3" + r"\\z1")
            logging.warning("%s 购买弓", self.account)

    def laba(self):
        """_summary_"""
        # xJ r j 5g 5Qm 1
        npc_id = self.get_npc_id()
        self._decode_send(f"xD r j 5g {b62(npc_id)} 1")

    def add_point(self, index):
        """加点 0 体力 1 力量 2 防御 3 敏捷 4 魔法

        Args:
            state_index (_type_): _description_
        """
        self._decode_send(f"IHw {index}")


class Script:
    """Script interface"""

    def __init__(self, cg: Cg) -> None:
        self._state = 0
        self.name = "no name script"
        self.cg = cg

    @property
    def state(self):
        """0停止 1等待开始 2正在运行 3等待结束

        Returns:
            _type_: _description_
        """
        return self._state

    @state.setter
    def state(self, value):
        """0停止 1等待开始 2正在运行 3等待结束

        Returns:
            _type_: _description_
        """
        self._state = value

    @property
    def enable(self):
        """state > 0

        Returns:
            _type_: _description_
        """
        return self.state > 0

    @enable.setter
    def enable(self, value):
        if value:
            self.start()
        else:
            self.stop()

    def start(self):
        """设置state = 1 等待开始"""
        if self.state in (0, 3):
            self.state = 1

    def stop(self):
        """设置state = 3 等待结束"""
        if self.state in (1, 2):
            self.state = 3

    def on_start(self, cg):
        """_summary_"""

    def on_stop(self, cg):
        """_summary_"""

    def on_update(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_battle(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_player_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_player_second_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_pet_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_pet_second_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_battle(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_moving(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
