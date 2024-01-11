"""player class"""
import time
import happy.service
import happy.unit
import happy.skill


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
        s = self.mem.read_string(0x00CB27EC)
        return int(s[:4])

    @property
    def hp_max(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        s = self.mem.read_string(0x00CB27EC)
        return int(s[5:])

    @property
    def mp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        s = self.mem.read_string(0x00CB7900)
        return int(s[:4])

    @property
    def mp_max(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        s = self.mem.read_string(0x00CB7900)
        return int(s[5:])

    @property
    def position(self):
        """_summary_

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
        return self.mem.read_string(0x00F4C3F8)

    @property
    def position_hex(self):
        """_summary_

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
        print(player_battle_order)
        time.sleep(0.1)
        # 还原
        self.mem.write_string(addr_player_buffer, "G\0")
        self.mem.write_bytes(addr_player_flag, bytes.fromhex("74 5E"), 2)

    def cast(self, skill: happy.skill.PlayerSkill, unit: happy.unit.Unit, use_level=11):
        """_summary_

        Args:
            index (_type_): _description_
            lv (_type_): _description_
            pos (_type_): _description_
        """
        cast_level = use_level if skill.level > use_level else skill.level
        position = unit.position
        if "強力" in skill.name:
            position = position + 0x14
        if "超強" in skill.name:
            position = 0x29 if unit.is_enemy else 0x28
        self._execute_player_command(f"S|{skill.index:X}|{cast_level-1:X}|{position:X}")

    def use_item(self):
        """not implement"""

    def attack(self, unit: happy.unit.Unit):
        """_summary_

        Args:
            pos (_type_): _description_
        """

        self._execute_player_command(f"H|{unit.position_hex}")

    def guard(self):
        """_summary_

        Args:
            pos (_type_): _description_
        """
        self._execute_player_command()
