"""Map"""
from happy.mem import CgMem
from happy.util import b62
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
        """

        Returns:
            _type_: _description_
        """
        return int(self.mem.read_float(0x00BF6CE8)/64)

    @property
    def y(self):
        """

        Returns:
            _type_: _description_
        """
        return int(self.mem.read_float(0x00BF6CE4)/64)
    @property
    def x_62(self):
        """

        Returns:
            _type_: _description_
        """
        return b62(self.x)

    @property
    def y_62(self):
        """

        Returns:
            _type_: _description_
        """
        return b62(self.y)
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
