"""player class"""

import math
import time
import happy.service
import happy.unit
import happy.skill
from happy.item import Item


class Player(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
        happy (_type_): _description_
    """

    def __init__(self, mem) -> None:
        happy.service.Service.__init__(self, mem)
        self.skills = happy.skill.PlayerSkillCollection(mem)

    def update(self):
        self.skills.update()

    @property
    def hp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        hp_str = self.mem.read_string(0x00CB27EC, 4)
        return int(hp_str)

    @property
    def hp_max(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        hp_max_str = self.mem.read_string(0x00CB27F1, 4)
        return int(hp_max_str)

    @property
    def hp_lost(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.hp_max - self.hp

    @property
    def hp_per(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.hp_max:
            return int(self.hp / self.hp_max * 100)
        return 0

    @property
    def mp_per(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.mp_max:
            return int(self.mp / self.mp_max * 100)
        return 0

    @property
    def mp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        mp_str = self.mem.read_string(0x00CB7900, 4)
        return int(mp_str)

    @property
    def mp_lost(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mp_max - self.mp

    @property
    def mp_max(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        mp_max_str = self.mem.read_string(0x00CB7905, 4)
        return int(mp_max_str)

    @property
    def level(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C2F4)

    @property
    def value_recovery(self):
        """回复

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C398)

    @property
    def injury(self):
        """受伤程度 25/50/75/100

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C3E4)

    @property
    def position(self):
        """战斗中的位置

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x005989DC)

    @property
    def is_enemy(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return False

    @property
    def job_name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(0x00E8D6D0)

    @property
    def name(self):
        """kk"""
        return self.mem.read_string(0x00F4C3F8, encoding="big5hkscs")

    @property
    def position_hex(self):
        """战斗中的位置 16进制

        Returns:
            _type_: _description_
        """
        return hex(self.mem.read_int(0x005989DC))[2:]

    def _execute_player_command(self, player_battle_order="G\0"):
        addr_player_buffer = 0x00543F84
        addr_player_flag = 0x0048F9F7

        # hook
        self.mem.write_string(addr_player_buffer, player_battle_order + "\0")
        self.mem.write_bytes(addr_player_flag, bytes.fromhex("90 90"), 2)
        # print(player_battle_order)
        time.sleep(0.1)
        # 还原
        self.mem.write_string(addr_player_buffer, "G\0")
        self.mem.write_bytes(addr_player_flag, bytes.fromhex("74 5E"), 2)

    def cast(
        self, skill: happy.skill.PlayerSkill, unit: happy.unit.Unit = None, use_level=11
    ):
        """_summary_

        Args:
            index (_type_): _description_
            lv (_type_): _description_
            pos (_type_): _description_
        """
        max_level = math.floor(self.level / 10) + 1
        cast_level = min(skill.level, use_level, max_level)
        position = unit.position if unit is not None else 0
        if "強力" in skill.name:
            position = position + 0x14
        if "超強" in skill.name:
            position = 0x29 if unit.is_enemy else 0x28

        self._execute_player_command(f"S|{skill.index:X}|{cast_level-1:X}|{position:X}")

    def use_battle_item(self, item: Item, unit: happy.unit.Unit = None):
        """使用物品"""
        order = "I|" + hex(item.index)
        if unit is not None:
            order += "|" + unit.position_hex
        self._execute_player_command(order)

    def attack(self, unit: happy.unit.Unit):
        """攻击

        Args:
            pos (_type_): _description_
        """

        self._execute_player_command(f"H|{unit.position_hex}")

    def guard(self):
        """防御

        Args:
            pos (_type_): _description_
        """
        self._execute_player_command()

    @property
    def remain_points(self):
        """剩余点数

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00CB0AF4)
