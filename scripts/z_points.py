"script"
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "自动加点"

    def on_not_battle(self, cg: happy.Cg):
        if cg.player.remain_points > 3:
            cg.add_point(1)
            cg.add_point(1)
            cg.add_point(2)
            cg.add_point(3)

        if cg.pets.battle_pet is not None and cg.pets.battle_pet.remain_points > 0:
            cg.pets.battle_pet.add_point(1)

        cg.drop_item("國民袍", "國民靴")
