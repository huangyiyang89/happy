"Pet"
import time
from typing import Iterator
import happy.skill
import happy.unit
from happy.service import Service
from happy.mem import CgMem

# typedef struct pet_s
# {
# 	int flags;
# 	short race;
# 	short padding;
# 	int level;
# 	CXorValue hp;
# 	CXorValue maxhp;
# 	CXorValue mp;
# 	CXorValue maxmp;
# 	CXorValue xp;
# 	CXorValue maxxp;
# 	int points_remain;
# 	int points_endurance;
# 	int points_strength;
# 	int points_defense;
# 	int points_agility;
# 	int points_magical;
# 	int value_attack;
# 	int value_defensive;
# 	int value_agility;
# 	int value_spirit;
# 	int value_recovery;
# 	int value_loyality;
# 	int resist_poison;
# 	int resist_sleep;
# 	int resist_medusa;
# 	int resist_drunk;
# 	int resist_chaos;
# 	int resist_forget;
# 	int fix_critical;
# 	int fix_strikeback;
# 	int fix_accurancy;
# 	int fix_dodge;
# 	int element_earth;	//地0~100
# 	int element_water;	//水0~100
# 	int element_fire;	//火0~100
# 	int element_wind;	//风0~100
# 	int health;			//健康 0=绿 100=红
# 	pet_skill_t skills[10];
# 	char unk[84];
# 	int skillslots;//6A4
# 	short unk1;	//6A8
# 	short battle_flags;	//6AA, 1 = 待命 2=战斗 3=xiuxi
# 	char realname[17];//水龙蜥 6AC
# 	char name[19];
# 	int unk2;//6D0
# 	int walk;//6D4
# }pet_t;


class Pet(happy.unit.Unit):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(
        self, index, name, battle_flag, skills: list[happy.skill.PetSkill]
    ) -> None:
        """_summary_

        Args:
            index (_type_): _description_
            name (_type_): _description_
            battle_flag (_type_): _description_
            skills (list[happy.skill.PetSkill]): 不包含空技能
        """

        self.index = index
        self.name = name
        self.battle_flag = battle_flag
        self.skills = skills

    @property
    def is_battle_state(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.battle_flag == 2

    def get_skill(self, *skill_names) -> happy.skill.PetSkill | None:
        """获得第一个名字包含name1 或name2 的技能

        Args:
            name (_type_): _description_

        Returns:
            happy.skill.PetSkill|None: _description_
        """
        for skill in self.skills:
            for skill_name in skill_names:
                if skill_name in skill.name:
                    return skill
        return None

    def has_power_magic_skill(self) -> bool:
        """判断是否魔宠

        Returns:
            _type_: _description_
        """
        return (
            self.get_skill(
                "強力隕石魔法", "強力冰凍魔法", "強力火焰魔法", "強力風刃魔法"
            )
            is not None
        )


class BattlePet(Service, Pet):
    """_summary_

    Args:
        Service (_type_): _description_
        Pet (_type_): _description_
    """

    def __init__(self, mem: CgMem, pet: Pet) -> None:
        Service.__init__(self, mem)
        Pet.__init__(self, pet.index, pet.name, pet.battle_flag, pet.skills)

    def _execute_pet_command(self, pet_battle_order="W|0|E"):
        guard = self.get_skill("防禦", "明鏡止水", "座騎")
        flag = 1 << guard.index
        self.mem.write_short(0x005988B0, flag)
        # hook
        self.mem.write_string(0x00543EC0, pet_battle_order.ljust(8, "\0"))
        self.mem.write_bytes(0x00475A8C, bytes.fromhex("90 90"), 2)
        self.mem.write_bytes(0x00CDA984, bytes.fromhex("02"), 1)
        # 骑乘
        self.mem.write_bytes(0x00475D92, bytes.fromhex("90 90"), 2)
        # print(pet_battle_order)
        time.sleep(0.1)
        # 还原
        self.mem.write_string(0x00543EC0, r"W|%X|%X" + "\0")
        self.mem.write_bytes(0x00475A8C, bytes.fromhex("74 73"), 2)
        # 骑乘
        self.mem.write_bytes(0x00475D92, bytes.fromhex("74 6E"), 2)

    def cast(self, skill: happy.skill.PetSkill, unit: happy.unit.Unit = None):
        """normal attack while no mana

        Args:
            skill (happy.skill.PetSkill): _description_
            unit (happy.unit.Unit): _description_
        """
        position = unit.position if unit is not None else 0
        if self.mp >= skill.cost:
            if "強力" in skill.name:
                position = position + 0x14
            if "超強" in skill.name:
                position = 0x29 if unit.is_enemy else 0x28
            self._execute_pet_command(f"W|{skill.index:X}|{position:X}")
        else:
            self.attack(unit)

    def attack(self, unit: happy.unit.Unit):
        """_summary_

        Args:
            unit (_type_): _description_
        """
        skill = self.get_skill("攻擊")
        self._execute_pet_command(f"W|{skill.index:X}|{unit.position:X}")

    @property
    def hp(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_xor_value(0x00ED4FF8 + self.index * 0x5110)

    @property
    def hp_max(self):
        """_summary_"""
        return self.mem.read_xor_value(0x00ED5008 + self.index * 0x5110)

    @property
    def mp(self):
        """_summary_"""
        return self.mem.read_xor_value(0x00ED5018 + self.index * 0x5110)

    @property
    def mp_max(self):
        """_summary_"""
        return self.mem.read_xor_value(0x00ED5028 + self.index * 0x5110)


class PetCollection(Service):
    """_summary_

    Args:
        Service (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.battle_pet = None
        self.update()

    def update(self):
        """update all pets and petskills"""
        self._pets = []
        self.battle_pet = None
        # 0x00ED4FE8 Flag
        for i in range(5):
            name = self.mem.read_string(0x00ED5694 + i * 0x5110)
            battle_flag = self.mem.read_short(0x00ED5692 + i * 0x5110)
            if not name:
                continue
            skills = []
            for j in range(10):
                skill_name = self.mem.read_string(0x00ED50C6 + i * 0x5110 + j * 0x8C)
                skill_cost = self.mem.read_int(0x00ED5144 + i * 0x5110 + j * 0x8C)
                if len(skill_name) > 0:
                    skill = happy.skill.PetSkill(j, skill_name, skill_cost)
                    skills.append(skill)
            pet = Pet(i, name, battle_flag, skills)
            self._pets.append(pet)
            if battle_flag == 2:
                self.battle_pet = BattlePet(self.mem, pet)

    def __getitem__(self, index) -> Pet:
        return self._pets[index]

    def __iter__(self) -> Iterator[Pet]:
        return iter(self._pets)
