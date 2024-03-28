"script"
import happy
from happy.core import Cg
from happy.util import bet


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "自动战斗"
        self.strategy = None
        self.enable_use_potion = False
        self.force_use_first_skill = False

    def on_start(self, cg: Cg):
        cg.disable_shell()

    def on_stop(self, cg: Cg):
        cg.disable_shell(False)

    def on_update(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        # cg.send_wechat_notification()

    def on_battle(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        
        if self.strategy is None or self.strategy.job_name != cg.player.job_name:
            self.strategy = Strategy.get_strategy(cg)

    def on_player_turn(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        a = cg.mem.read_int(0x005988AC)
        b = cg.mem.read_int(0x00598940)

        if a == 0 and b == 0:
            self.strategy.player_action(cg)
        else:
            if a != b:
                pass
            else:
                self.strategy.player_action(cg)

    def on_pet_turn(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        self.strategy.pet_action(cg)

    def on_not_battle(self, cg: Cg):
        cg.eat_food()
        cg.call_nurse()
        cg.solve_if_captch()


class Strategy:
    """_summary_"""

    def __init__(self, cg: Cg) -> None:
        self.job_name = cg.player.job_name

    @staticmethod
    def get_strategy(cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_

        Returns:
            _type_: _description_
        """
        job_name = cg.player.job_name
        if job_name in ["見習傳教士", "傳教士", "牧師", "主教", "大主教"]:
            return ChuanJiao(cg)
        return Strategy(cg)

    def player_action(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        enemies_count = len(cg.battle.units.enemies)
        target = cg.battle.units.get_random_enemy()
        skill = cg.player.skills.get_aoe_skill()

        if target is None:
            return

        if cg.player.hp_per < 80:
            drug = cg.items.first_drug
            if drug :
                recovery = drug.is_drug * cg.player.value_recovery / 100
                if cg.player.hp_lost>=recovery:
                    cg.player.use_battle_item(drug, cg.player)
                    return

        if (
            enemies_count > 2
            and skill is not None
            and cg.player.mp >= skill.max_level_cost
        ):
            if "因果報應" in skill.name or "精神衝擊波" in skill.name:
                target = cg.battle.units.get_line_unit()
            cg.player.cast(skill, target, skill.get_efficient_level(enemies_count))
        else:
            cg.player.attack(target)

    def pet_action(self, cg: Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        pet = cg.pets.battle_pet

        target = cg.battle.units.get_random_enemy()
        if target is None:
            return

        heal_skill = pet.get_skill("吸血", "明鏡止水")
        if pet.hp_per <= 70 and heal_skill:
            pet.cast(heal_skill, target)
            return

        power_magic = pet.get_skill(
            "強力隕石魔法", "強力冰凍魔法", "強力火焰魔法", "強力風刃魔法"
        )
        cross_target = cg.battle.units.get_cross_enemy()
        if power_magic and cross_target:
            pet.cast(power_magic, cross_target)
            return

        magic = pet.get_skill(
            "隕石魔法",
            "冰凍魔法",
            "火焰魔法",
            "風刃魔法",
            "強力隕石魔法",
            "強力冰凍魔法",
            "強力火焰魔法",
            "強力風刃魔法",
        )
        if magic:
            pet.cast(magic, target)
            return

        guard_counter = pet.get_skill("崩擊")
        enemies_count = len(cg.battle.units.enemies)
        friends_count = len(cg.battle.units.friends)
        first_skill = pet.skills[0]
        if enemies_count < 4 and guard_counter and friends_count > 6 and bet(50):
            pet.cast(guard_counter, target)
            return

        pet.cast(first_skill, target)
        # pet.attack(target)


class ChuanJiao(Strategy):
    """_summary_

    Args:
        Strategy (_type_): _description_
    """

    def player_action(self, cg: Cg):
        low_hp_friends_count = sum(
            1 for friend in cg.battle.units.friends if friend.hp_per <= 75
        )
        cross_heal_unit = cg.battle.units.get_cross_heal_unit(80)
        lowest_friend = cg.battle.units.get_lowest_hp_per_friend()
        ultra = cg.player.skills.get_skill("超強補血魔法")
        cross = cg.player.skills.get_skill("強力補血魔法")
        single = cg.player.skills.get_skill("補血魔法")
        spirit = cg.player.skills.get_skill("精神衝擊波")
        if low_hp_friends_count > 4 and ultra is not None and cg.player.mp > ultra.max_level_cost:
            cg.player.cast(ultra, cg.player)
            return
        if cross_heal_unit is not None and cross is not None and cg.player.mp > cross.max_level_cost:
            cg.player.cast(cross, cross_heal_unit)
            return
        if lowest_friend is not None and lowest_friend.hp_per <= 80 and single is not None and cg.player.mp > single.max_level_cost:
            cg.player.cast(single, lowest_friend)
            return

        target = cg.battle.units.get_random_enemy()
        if target is None:
            return
        
        if spirit is not None and spirit.pos == 1:
            target = cg.battle.units.get_line_unit()
            cg.player.cast(spirit,target)
            return
        
        cg.player.attack(cg.battle.units.get_random_enemy())


class QiCheng(Strategy):
    """_summary_

    Args:
        Strategy (_type_): _description_
    """

    def player_action(self, cg: Cg):
        skill = cg.player.skills.get_skill("騎乘")
        print(skill)

    def pet_action(self, cg: Cg):
        return super().pet_action(cg)
