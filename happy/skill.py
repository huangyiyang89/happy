"""Skill"""
from typing import Iterator
from happy.mem import CgMem
from happy.service import Service


class Skill:
    """name,index"""

    def __init__(self, index, name) -> None:
        self.index = index
        self.name = name


class PlayerSkill(Skill):
    """_summary_

    Args:
        index: 隐藏的技能顺序
        Skill (_type_): _description_
    """

    def __init__(self, index, name, level, max_level_cost) -> None:
        super().__init__(index, name)
        self.level = level
        self.max_level_cost = max_level_cost

    def get_efficient_level(self, enemies_count):
        """_summary_

        Args:
            enemies_count (_type_): _description_

        Returns:
            _type_: _description_
        """
        if enemies_count > 6:
            return self.level
        if self.name in ["氣功彈", "亂射"]:
            return enemies_count + 2
        return self.level


class PlayerSkillCollection(Service):
    """_summary_

    Args:
        Service (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.update()

    def update(self):
        self._skills = [None] * 15
        for i in range(0, 14):
            name = self.mem.read_string(0x00E8D6EC + 0x4C4C * i)
            level = self.mem.read_int(0x00E8D708 + 0x4C4C * i)
            customized_position = self.mem.read_int(0x00E8D724 + 0x4C4C * i)
            if len(name) > 0:
                max_level_cost = self.mem.read_int(
                    0x00E8D6EC + 0x4C4C * i + 0xB8 + 0x94 * (level - 1)
                )
                skill = PlayerSkill(i, name, level, max_level_cost)
                self._skills[customized_position] = skill

        self._skills = [skill for skill in self._skills if skill is not None]

    def __getitem__(self, index) -> PlayerSkill:
        return self._skills[index]

    def __iter__(self) -> Iterator[PlayerSkill]:
        return iter(self._skills)

    def get_skill(self, name) -> PlayerSkill | None:
        """_summary_

        Args:
            name (_type_): _description_

        Returns:
            _type_: _description_
        """
        for skill in self._skills:
            if skill.name == name:
                return skill
        return None

    def get_aoe_skill(self) -> PlayerSkill | None:
        """_summary_

        Returns:
            _type_: _description_
        """
        for skill in self._skills:
            if skill.name in [
                "亂射",
                "氣功彈",
                "刀刃亂舞",
                "因果報應",
                "追月",
                "超強隕石魔法",
                "超強冰凍魔法",
                "超強火焰魔法",
                "超強風刃魔法",
            ]:
                return skill
        return None


class PetSkill(Skill):
    """_summary_

    Args:
        Skill (_type_): _description_
    """

    def __init__(self, index, name, cost) -> None:
        super().__init__(index, name)
        self.cost = cost
