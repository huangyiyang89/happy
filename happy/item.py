"""Item"""

import struct
from typing import Iterator
import happy.service
import happy.mem
from happy.util import b62


class Item:
    """C5C长度 3164
    //[0] = hat
    //[1] = cloth
    //[2] = right hand
    //[3] = left hand
    //[4] = foot
    //[5] = decoration 1
    //[6] = decoration 2
    //[7] = crystal
    typedef struct item
    {
            short valid;
            char name[46];
            char attr[8][96];
            char info[8][96];
            int flags;//2=right clickable  1=kapian
            int unk;
            int image_id;
            int level;
            int item_id;
            int count;
            int type;
            short double_clickable;
            short unk2;
            short unk3;
            short assess_flags;
            int assessed;//已鉴定
            int unk6;
    }"""

    def __init__(self, index, bytes_data: bytes) -> None:
        self._index = index
        self._valid = struct.unpack("H", bytes_data[:2])[0]
        if self._valid:
            null_index = bytes_data[2:48].find(b"\x00")
            self._name = bytes_data[2 : 2 + null_index].decode("big5", errors="ignore")
            self._id = int.from_bytes(bytes_data[3136:3140], byteorder="little")
            self._count = int.from_bytes(bytes_data[3140:3144], byteorder="little")
            self._type = int.from_bytes(bytes_data[3144:3148], byteorder="little")
        else:
            self._name = ""
            self._id = -1
            self._count = -1
            self._type = -1

    @property
    def index(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._index

    @property
    def index_62(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return b62(self._index)

    @property
    def valid(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._valid

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._name

    @property
    def id(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._id

    @property
    def count(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._count

    @property
    def type(self):
        """_summary_

        Returns:
            _type_: 料理23,血瓶43
        """
        return self._type


class ItemCollection(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, mem: happy.mem.CgMem) -> None:
        super().__init__(mem)
        self.update()

    def __getitem__(self, index) -> Item:
        return self._items[index]

    def __iter__(self) -> Iterator[Item]:
        return iter(self._items)

    def update(self):
        self._items: list[Item] = []
        for i in range(28):
            self._items.append(
                Item(i, self.mem.read_bytes(0x00F4C494 + 0xC5C * i, 0xC5C))
            )
        return self

    @property
    def bags_valids(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for i in range(8, 28):
            item = self._items[i]
            if item.valid:
                yield item

    @property
    def blanks_count(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        count = 0
        for i in range(8, 28):
            item = self._items[i]
            if not item.valid:
                count = count + 1
        return count

    @property
    def foods(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.valid == 1 and item.type == 23:
                yield item

    @property
    def drugs(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.valid == 1 and item.type == 43:
                yield item

    @property
    def bombs(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.valid == 1 and item.type == 51:
                yield item

    @property
    def gold(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C3EC)

    def put(self, item: Item, position: int):
        """拿起item放到指定position

        Args:
            item1 (Item): _description_
            position (int): _description_
        """
        self._decode_send(f"yi {item.index_62} {position} -1 ")

    def tidyup(self):
        """整理背包，直接调用游戏聊天框/r"""
        self._decode_send("uSr 19 1k P|/r")

    def find(self, item_name="", quantity=0):
        """模糊匹配包含item_name的第一个物品

        Args:
            item_name (str, optional): _description_. Defaults to "".
            quantity (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        for item in self._items:
            if item.valid == 1 and (item_name in item.name) and item.count >= quantity:
                return item
        return None

    def find_box(self, item_name=""):
        """模糊匹配包含item_name的第一个盒子

        Args:
            name (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        for item in self._items:
            if (
                item.valid == 1
                and "『" in item.name
                and "』" in item.name
                and item_name in item.name
            ):
                return item
        return None

    def find_food_box(self):
        """_summary_

        Args:
            name (str, optional): _description_. Defaults to "".

        Returns:
            _type_: _description_
        """
        for item in self._items:
            if item.valid == 1 and (
                "『壽喜鍋』" in item.name or "『魚翅湯』" in item.name
            ):
                return item
        return None


    def weapon_is_gong(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        for item in self._items[1:3]:
            if "弓" in item.name:
                return True
        return False