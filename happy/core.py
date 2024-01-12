"""
HappyCG
"""
import threading
import time
import importlib
import importlib.util
import sys
import happy.mem
import happy.service
import happy.unit
import happy.player
import happy.pet
import happy.script
import happy.map
import happy.battle
import happy.item


class Cg(happy.service.Service):
    """_summary_"""

    __opened_cg_processes = []

    def __init__(self, mem: happy.mem.CgMem) -> None:
        super().__init__(mem)
        self._is_running = False
        self._thread = None
        self.battle = happy.battle.Battle(mem)
        self.player = happy.player.Player(mem)
        self.pets = happy.pet.PetCollection(mem)
        self.map = happy.map.Map(mem)
        self.items = happy.item.ItemCollection(mem)
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

    @property
    def is_fighting(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        return self.mem.read_short(0x0072B9D0) == 3

    @property
    def is_player_turn(self):
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return self.mem.read_int(0x00598974) == 1

    @property
    def is_pet_turn(self):
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return self.mem.read_int(0x00598974) == 4

    @property
    def is_player_second_turn(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00598974) == 1 and self.mem.read_int(0x0059892C) == 1

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

    def _decode_send(self, content):
        """发明文包"""
        # 0057A718 缓存指针
        # 00581000 空内存
        # 使用空内存写入字符串
        self.mem.write_string(0x00581000, content + "\0")
        # 改写缓存地址
        self.mem.write_bytes(0x005064BC, bytes.fromhex("B9 00 10 58 00 90"), 6)
        # 鼠标右击发包
        self.mem.write_short(0x00CDA984, 2)
        time.sleep(0.1)
        # 改回原地址
        self.mem.write_bytes(0x005064BC, bytes.fromhex("8B 0D 18 A7 57 00"), 6)

    def eat_food(self):
        """_summary_"""
        next_food = next(self.items.foods, None)
        if next_food is not None:
            self._decode_send(
                f"jBdn {self.base62_encode(self.map.x)} {self.base62_encode(self.map.y)} {self.base62_encode(next_food.index)} 0 OO c"
            )
        else:
            print("nothing to eat")


class CgException(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code}: {self.message}"
