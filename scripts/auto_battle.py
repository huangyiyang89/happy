"script"
import time
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "自动战斗"
        self.strategy = None
        self.enable_use_potion = False
        self.force_use_first_skill = False
        self.try_to_eat = False

    def on_update(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """

    def on_battle(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        if self.strategy is None or self.strategy.job_name != cg.player.job_name:
            self.strategy = Strategy.get_strategy(cg)

        self.try_to_eat = False

    def on_player_turn(self, cg: happy.Cg):
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
                print("waiting anime...")
            else:
                time.sleep(1)
                self.strategy.player_action(cg)

    def on_pet_turn(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        self.strategy.pet_action(cg)

    def on_not_battle(self, cg: happy.Cg):
        if not self.try_to_eat:
            cg.eat_food()
        self.try_to_eat = True


class Strategy:
    """_summary_"""

    def __init__(self, cg: happy.Cg) -> None:
        self.job_name = cg.player.job_name

    @staticmethod
    def get_strategy(cg: happy.Cg):
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

    def player_action(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        enemies_count = len(cg.battle.units.enemies)
        target = cg.battle.units.get_random_enemy()
        skill = cg.player.skills.get_aoe_skill()

        if (
            enemies_count > 2
            and skill is not None
            and cg.player.mp >= skill.max_level_cost
        ):
            if "因果報應" in skill.name:
                target = cg.battle.units.get_line_unit()
            cg.player.cast(skill, target, skill.get_efficient_level(enemies_count))
        else:
            cg.player.attack(target)

    def pet_action(self, cg: happy.Cg):
        """_summary_

        Args:
            cg (happy.core.Cg): _description_
        """
        pet = cg.pets.battle_pet
        target = cg.battle.units.get_random_enemy()
        heal_skill = pet.get_skill("吸血", "明鏡止水")
        guard_counter = pet.get_skill("崩擊")
        enemies_count = len(cg.battle.units.enemies)
        if enemies_count < 6 and guard_counter is not None:
            pet.cast(guard_counter, target)
        elif pet.hp_per <= 70 and heal_skill is not None:
            pet.cast(heal_skill, target)
        else:
            pet.attack(target)


class ChuanJiao(Strategy):
    """_summary_

    Args:
        Strategy (_type_): _description_
    """

    def player_action(self, cg: happy.Cg):
        low_hp_friends_count = sum(
            1 for friend in cg.battle.units.friends if friend.hp_per <= 75
        )
        cross_heal_unit = cg.battle.units.get_cross_heal_unit(65)
        lowest_friend = cg.battle.units.get_lowest_hp_per_friend()
        if low_hp_friends_count > 4:
            skill = cg.player.skills.get_skill("超強補血魔法")
            if skill is not None and cg.player.mp > skill.max_level_cost:
                cg.player.cast(skill, cg.player)
                return
        elif cross_heal_unit is not None:
            skill = cg.player.skills.get_skill("強力補血魔法")
            if skill is not None and cg.player.mp > skill.max_level_cost:
                cg.player.cast(skill, cross_heal_unit)
                return
        elif lowest_friend.hp_per <= 50:
            skill = cg.player.skills.get_skill("補血魔法")
            if skill is not None and cg.player.mp > skill.max_level_cost:
                cg.player.cast(skill, lowest_friend)
                return
        cg.player.attack(cg.battle.units.get_random_enemy())
