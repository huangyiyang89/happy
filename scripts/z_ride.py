"script"
import auto_battle
import happy


class Script(auto_battle.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "烧技骑乘"

    def on_player_turn(self, cg: happy.Cg):
        skill = cg.player.skills.get_skill("騎乘")
        if skill and cg.player.mp >= skill.max_level_cost:
            cg.player.cast(skill)
        else:
            super().on_player_turn(cg)

    def on_pet_turn(self, cg: happy.Cg):
        skill = cg.pets.battle_pet.get_skill("座騎")
        if skill:
            cg.pets.battle_pet.cast(skill)
        else:
            super().on_pet_turn(cg)
