"""
HappyCG
"""
import threading
import time
import importlib
import importlib.util
import sys
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
from happy.util import b62


class Cg(Service):
    """_summary_"""

    __opened_cg_processes = []

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

    @staticmethod
    def open():
        """open cg process and add process to __opened_cg_processes[]
        Returns:
            _type_: HappyCG
        """
        processes = happy.mem.CgMem.list_cg_processes()
        for process in processes:
            if process not in Cg.__opened_cg_processes:
                mem = happy.mem.CgMem(process)
                new_cg = Cg(mem)
                Cg.__opened_cg_processes.append(process)
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
        Cg.__opened_cg_processes.remove(self.mem.process_id)
        self.is_closed = True

    def update(self):
        """update all children and trigger events"""

        self.battle.update()
        self.player.update()
        self.pets.update()
        self.items.update()

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
                else:
                    script.on_not_battle(self)

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
        if self.player.mp_max - self.player.mp >= lose_mp:
            first_food = next(
                (food for food in self.items.foods if food.name not in excepts), None
            )
            if first_food is not None:
                self._decode_send(
                    f"iVfo {self.map.x_62} {self.map.y_62} {first_food.index_62} 0"
                )
            else:
                print("nothing to eat")

    def use_item(self, item: Item):
        """_summary_

        Args:
            item (Item): _description_
        """
        self._decode_send(f"Ak {self.map.x_62} {self.map.y_62} {item.index_62} 0")

    def right_click(self, direction: Literal["A", "B", "C", "D", "E", "F", "G", "H"]):
        """鼠标右键点击交互

        Args:
            direction: A-H,顺时针表示左上,上,右上,右,右下,下,左下,左
        """
        self._decode_send(f"zA {self.map.x_62} {self.map.y_62} {direction} 0")

    def tp(self):
        """登出"""
        self._decode_send("mU")

    @property
    def is_moving(self) -> bool:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x0054DCB0) != 65535

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
                self._decode_send(f"xD {x62} {y62} 5m {npc_id_62} 4")
            if npc_type == 364:
                if self.player.mp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5T {npc_id_62} 4")
                if self.player.hp_per < 100:
                    self._decode_send(f"xD {x62} {y62} 5V {npc_id_62} 4")
                self._decode_send(f"xD {x62} {y62} 5W {npc_id_62} 4")
