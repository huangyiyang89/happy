"""player class"""
import time
import happy.service
import happy.unit
import happy.skill
import happy.item
# typedef struct playerbase_s
# {
# 	short race;	//+0
# 	short padding;//+2
# 	int level;	//+4
# 	int unk;	//+8
# 	int punchclock;//+12
# 	int using_punchclock;	//+16
# 	int tickcount;	//+20
# 	CXorValue hp;//+24
# 	CXorValue maxhp;//+40
# 	CXorValue mp;//+56
# 	CXorValue maxmp;//+72
# 	CXorValue xp;//+88
# 	CXorValue maxxp;//+104
# 	int points_endurance;//+120
# 	int points_strength;//+124
# 	int points_defense;//+128
# 	int points_agility;//+132
# 	int points_magical;//+136		
# 	int manu_endurance;//+140
# 	int manu_skillful;//+144
# 	int manu_intelligence;//+148
# 	int value_attack; //+152
# 	int value_defensive;//+156
# 	int value_agility;//+160
# 	int value_spirit;//+164
# 	int value_recovery;//+168
# 	int value_charisma;//+172
# 	int unk3;//+176
# 	int resist_poison;//+180
# 	int resist_sleep;//+184
# 	int resist_medusa;//+188
# 	int resist_drunk;//+192
# 	int resist_chaos;//+196
# 	int resist_forget;//+200
# 	int fix_critical;//+204
# 	int fix_strikeback;//+208
# 	int fix_accurancy;//+212
# 	int fix_dodge;//+216
# 	int element_earth;//+220
# 	int element_water;//+224
# 	int element_fire;//+228
# 	int element_wind;//+232
# 	int health;//+236
# 	int souls;//+240
# 	int gold;//+244
# 	int use_title;//+248 //使用第几个称号
# 	int score;//+252
# 	char name[17];//+256
# 	char player_nick[17];//+273
# 	char what[33];//+290
# 	char what2[33];//+323
# 	int skillslots;//+356
# 	int move_speed;//+360 int unk
# 	int unk4;//+364
# 	int image_id;//+368
# 	int avatar_id;//+372
# 	int unitid;//+376
# 	int direction;//+380
# 	short unk7;//+384
# 	short unk8;//+386
# 	char unk9;//+388
# 	char padding2;
# 	short unk10;//+390
# 	int collect_type;//+392
# 	int enable_flags;//+396
# 	int unk11;//+400
# 	int unk12;//+404
# 	int battle_position;//+408
# 	item_info_t iteminfos[40];//+412 = itembase
# }playerbase_t;

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

    def use_item(self,item:happy.item.Item,unit: happy.unit.Unit = None):
        """使用物品"""
        order = "I|"+hex(item.index)
        if unit is not None:
            order+="|"+unit.position_hex
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
