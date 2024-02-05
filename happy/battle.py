"""Battle"""
from happy.mem import CgMem
import happy.service
import happy.unit

class Battle(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
    """
    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.units = happy.unit.UnitCollection(mem)
        self.update()

    def update(self):
        self.units.update()

    @property
    def is_fighting(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        return self.mem.read_short(0x0072B9D0) > 0

    @property
    def is_player_turn(self)-> bool:
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return self.mem.read_int(0x00598974) == 1 and self.mem.read_short(0x0072B9D0) ==3

    @property
    def is_pet_turn(self)-> bool:
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return self.mem.read_int(0x00598974) == 4 and self.mem.read_short(0x0072B9D0) ==3
    
    @property
    def is_pet_second_turn(self)-> bool:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.is_pet_turn and  self.mem.read_int(0x005988F4) == 1

    @property
    def is_player_second_turn(self)-> bool:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.is_player_turn and self.mem.read_int(0x0059892C) == 1
