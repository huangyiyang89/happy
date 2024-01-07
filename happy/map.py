"""Map"""
from happy.mem import CgMem
import happy.service


class Map(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)

    @property
    def x(self):
        """在切换地图以后，坐标不会立即切换。

        Returns:
            _type_: _description_
        """
        return self.mem.read_short(0x00BF6B54)

    @property
    def y(self):
        """在切换地图以后，坐标不会立即切换。

        Returns:
            _type_: _description_
        """
        return self.mem.read_short(0x00BF6C1C)

    @property
    def id(self):
        """地图ID

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00970430)

    @property
    def name(self):
        """地图名称

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(0x0095C870)
