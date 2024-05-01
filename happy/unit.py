"""
Unit
"""

import random
from typing import Iterator
from happy.mem import CgMem
from happy.service import Service


class Unit:
    """name,level,hp,maxhp,mp,maxmp"""

    def __init__(self, data_list: list = None) -> None:
        if isinstance(data_list, list) and len(data_list) == 12:
            self.position_hex = data_list[0]
            self.name = data_list[1]
            self.level = int(data_list[4], 16)
            self.hp = int(data_list[5], 16)
            self.hp_max = int(data_list[6], 16)
            self.mp = int(data_list[7], 16)
            self.mp_max = int(data_list[8], 16)
        else:
            self.position_hex = "0"
            self.name = ""
            self.level = 0
            self.hp = 0
            self.hp_max = 1
            self.mp = 0
            self.mp_max = 1

    @property
    def exist(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return len(self.name) > 0

    @property
    def hp_per(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.hp / self.hp_max * 100

    @property
    def hp_lost(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.hp_max - self.hp

    @property
    def mp_per(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mp / self.mp_max * 100

    @property
    def mp_lost(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mp_max - self.mp

    @property
    def position(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return int(self.position_hex, 16)

    @property
    def is_enemy(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.position > 9

    @property
    def formatted_info(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.exist:
            return (
                self.name
                + " LV:"
                + str(self.level)
                + "\r\n"
                + str(self.hp)
                + "/"
                + str(self.hp_max)
                + "\r\n"
                + str(self.mp)
                + "/"
                + str(self.mp_max)
            )
        else:
            return "空"


class UnitCollection(Service):
    """_summary_

    Args:
        Service (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.update()

    def update(self):
        self._units = [Unit() for _ in range(20)]
        battle_units_buffer = self.mem.read_string(0x00590758, 1000)
        if len(battle_units_buffer) < 12:
            return self
        data_array = battle_units_buffer[4:].split("|")
        for i in range(0, len(data_array) - 12, 12):
            _unit = Unit(data_array[i : i + 12])
            self._units[_unit.position] = _unit
        return self
    
    @property
    def player(self):
        """_summary_
        """
        pos = self.mem.read_int(0x005989DC)
        return self.get_unit(pos)
    
    @property
    def pet(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        player_pos = self.mem.read_int(0x005989DC)
        pet_pos = player_pos+5
        if player_pos>=5:
            pet_pos = 10-player_pos
        return self.get_unit(pet_pos)

    @property
    def friends(self):
        """只返回存在的单位

        Returns:
            _type_: _description_
        """
        return [unit for unit in self._units[:10] if unit.exist]

    @property
    def enemies(self):
        """只返回存在的单位

        Returns:
            _type_: _description_
        """
        return [unit for unit in self._units[10:] if unit.exist]

    def get_lowest_hp_per_friend(self):
        """_summary_"""
        if len(self.friends) == 0:
            return None
        return min(self.friends, key=lambda unit: unit.hp_per)

    def get_cross_heal_unit(self, hp_lower_than_per=75):
        """_summary_

        Args:
            hp_lower_than_per (int, optional): _description_. Defaults to 75.
        """

        # 强力位二进制表示
        crosses = [
            0b1110010000,
            0b1101001000,
            0b1010100100,
            0b0101000010,
            0b0010100001,
            0b1000011100,
            0b0100011010,
            0b0010010101,
            0b0001001010,
            0b0000100101,
        ]

        # 场上存在符合条件的友方单位二进制表示是否存在
        units_bit = 0
        for unit in self.friends:
            if unit.hp_per <= hp_lower_than_per:
                # 单位如果血量符合条件则移位存入units_bit
                units_bit += 1 << (9 - unit.position)

        ret_unit = None
        for friend in self.friends:
            count = UnitCollection.count_set_bits(units_bit & crosses[friend.position])
            if count == 4:
                return friend
            if count == 3:
                ret_unit = friend
        return ret_unit

    def get_cross_enemy(self):
        """_summary_"""
        # 强力位二进制表示
        crosses = [
            0b1110010000,
            0b1101001000,
            0b1010100100,
            0b0101000010,
            0b0010100001,
            0b1000011100,
            0b0100011010,
            0b0010010101,
            0b0001001010,
            0b0000100101,
        ]

        # 场上存在符合条件的友方单位二进制表示是否存在
        units_bit = 0
        for unit in self.enemies:
            # 单位如果血量符合条件则移位存入units_bit
            units_bit += 1 << (9 - unit.position + 10)

        # 检查友方10个位置，返回单位存在且强力位符合条件的目标数大于3的位置，没有返回-1
        ret_enemy = None
        # 随机寻找目标
        shuffled_list = self.enemies.copy()  # 首先複製原始列表
        random.shuffle(shuffled_list)  # 然後打亂新列表
        for enemy in shuffled_list:
            count = UnitCollection.count_set_bits(
                units_bit & crosses[enemy.position - 10]
            )
            if count == 4:
                return enemy
            if count == 3:
                ret_enemy = enemy
        return ret_enemy

    def get_line_unit(self):
        """回力攻击位置

        Returns:
            _type_: _description_
        """
        front = 0
        back = 0
        back_target = None
        front_target = None

        for enemy in self.enemies:
            if enemy.position > 14:
                front += 1
                front_target = enemy
            else:
                back += 1
                back_target = enemy
        return back_target if back >= front else front_target

    def __getitem__(self, index):
        return self._units[index]

    def __iter__(self) -> Iterator[Unit]:
        return iter(self._units)

    def get_random_enemy(self):
        """注意当进入战斗过早,units数据未返回时,该函数可能返回None

        Returns:
            _type_: _description_
        """
        if self.enemies:
            return random.choice(self.enemies)
        else:
            # 处理空列表的情况，可以返回 None 或其他默认值
            return None

    @staticmethod
    def count_set_bits(n):
        """计算二进制数中有多少个1

        Args:
            n (_type_): _description_

        Returns:
            _type_: _description_
        """
        count = 0
        while n:
            count += n & 1
            n >>= 1
        return count

    def print_all_units(self):
        """_summary_"""
        for unit in self._units:
            print(unit.formatted_info)

    #根据位置查找单位
    def get_unit(self,position):
        """_summary_

        Args:
            position (_type_): _description_

        Returns:
            _type_: _description_
        """
        for unit in self._units:
            if unit.position == position and unit.exist:
                return unit
        return None