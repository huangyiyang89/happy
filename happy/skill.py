"""Skill"""

from typing import Iterator
from happy.mem import CgMem
from happy.service import Service


class PlayerSkill(Service):
    """_summary_

    Args:
        index: 隐藏的技能顺序
        Skill (_type_): _description_
    """

    offset = 0x00E8D6EC
    size = 0x4C4C

    def __init__(self, index, max_level_cost, mem: CgMem) -> None:
        Service.__init__(self, mem)
        self.index = index
        self.max_level_cost = max_level_cost

        self.address = PlayerSkill.offset + index * PlayerSkill.size

        self._crafts = []
        for i in range(50):
            craft = PlayerSkillCraft(self, i)
            if craft.name != "":
                self.crafts.append(craft)
            else:
                break

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

    def find_craft(self, craft_id=0, craft_name=""):
        """_summary_

        Args:
            id (int, optional): _description_. Defaults to 0.
            name (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        for craft in self.crafts:
            if craft.id == craft_id or craft.name == craft_name:
                return craft
        return None

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(self.address)

    @property
    def slot_size(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_bytes(self.address + 25, 1)

    @property
    def padding(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_bytes(self.address + 26, 2)

    @property
    def level(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 28)

    @property
    def max_level(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 32)

    @property
    def exp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 36)

    @property
    def max_exp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 40)

    @property
    def type(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 44)

    @property
    def id(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 48)

    @property
    def unknown(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 52)

    @property
    def pos(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 56)

    @property
    def crafts(self) -> list["PlayerSkillCraft"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._crafts


# typedef struct skill_sub_s
# {
# 	char name[25];//0
# 	char info[99];//25
# 	int cost;//124
# 	int unk1;//128
# 	int flags;//132
# 	int unk3;//136
# 	int available;//140
# 	int level;//144
# }skill_sub_t;
class PlayerSubSkill(Service):
    """_summary_

    Args:
        Service (_type_): _description_
    """
    offset = 0x3C  # 60
    size = 0x94  # 148


class PlayerSkillCraft(Service):
    """_summary_

    Args:
        Service (_type_): _description_

    Returns:
        _type_: _description_
    """
    offset = 0x8E8
    size = 0x134

    def __init__(self, skill: PlayerSkill, index: int) -> None:
        super().__init__(skill.mem)
        self._skill = skill
        self._index = index
        self.address = (
            skill.address + PlayerSkillCraft.offset + index * PlayerSkillCraft.size
        )
        self._ingredients = []
        for i in range(5):
            ingredient = CraftIngredients(self, i)
            if ingredient.itemid != -1:
                self._ingredients.append(ingredient)
            else:
                break

    @property
    def skill(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._skill

    @property
    def index(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._index

    @property
    def id(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address)

    @property
    def cost(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 4)

    @property
    def level(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 8)

    @property
    def available(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 12)

    @property
    def itemid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 16)

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(self.address + 20)

    @property
    def info(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(self.address + 49)

    @property
    def ingredients(self) -> list["CraftIngredients"]:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._ingredients


class CraftIngredients(Service):
    """制作所需材料

    Args:
        Service (_type_): _description_

    Returns:
        _type_: _description_
    """

    offset = 108
    size = 40

    def __init__(self, craft: PlayerSkillCraft, index) -> None:
        super().__init__(craft.mem)
        self.index = index
        self.address = (
            craft.address + CraftIngredients.offset + index * CraftIngredients.size
        )

    @property
    def itemid(self):
        """=-1 if none

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address)

    @property
    def count(self):
        """=-1 if none

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(self.address + 4)

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(self.address + 8)


class PlayerSkillCollection(Service):
    """_summary_

    Args:
        Service (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.update()

    def update(self):
        self._skills: list[PlayerSkill] = [None] * 15
        for i in range(0, 14):
            name = self.mem.read_string(0x00E8D6EC + 0x4C4C * i)
            level = self.mem.read_int(0x00E8D708 + 0x4C4C * i)
            customized_position = self.mem.read_int(0x00E8D724 + 0x4C4C * i)
            if len(name) > 0:
                max_level_cost = self.mem.read_int(
                    0x00E8D6EC + 0x4C4C * i + 0xB8 + 0x94 * (level - 1)
                )
                skill = PlayerSkill(i, max_level_cost, self.mem)
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
        """能够判断技能是否可用

        Returns:
            _type_: _description_
        """

        def is_bit_set(num, i):
            mask = 1 << i
            return (num & mask) != 0

        valids = self.mem.read_int(0x0059893C)
        for skill in self._skills:
            valid = is_bit_set(valids, skill.index)
            if valid and skill.name in [
                "亂射",
                "氣功彈",
                "刀刃亂舞",
                "因果報應",
                "追月",
                "月影",
                "精神衝擊波",
                "超強隕石魔法",
                "超強冰凍魔法",
                "超強火焰魔法",
                "超強風刃魔法",
            ]:
                return skill
        return None

    def find_craft(self, craft_id=0, craft_name=""):
        """_summary_

        Args:
            craft_id (_type_): _description_
            craft_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        for skill in self._skills:
            craft = skill.find_craft(craft_id, craft_name)
            if craft:
                return craft
        return None


class PetSkill:
    """_summary_

    Args:
        Skill (_type_): _description_
    """

    def __init__(self, index, name, cost) -> None:
        self.index = index
        self.name = name
        self.cost = cost
