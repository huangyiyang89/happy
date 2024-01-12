# C5C长度 3164
import struct
import happy.service
import happy.mem


class Item:
    """z"""

    # """ //[0] = hat
    #     //[1] = cloth
    #     //[2] = right hand
    #     //[3] = left hand
    #     //[4] = foot
    #     //[5] = decoration 1
    #     //[6] = decoration 2
    #     //[7] = crystal
    #     typedef struct item
    #     {
    #             short valid;
    #             char name[46];
    #             char attr[8][96];
    #             char info[8][96];
    #             int flags;//2=right clickable  1=kapian
    #             int unk;
    #             int image_id;
    #             int level;
    #             int item_id;
    #             int count;
    #             int type;
    #             short double_clickable;
    #             short unk2;
    #             short unk3;
    #             short assess_flags;
    #             int assessed;//已鉴定
    #             int unk6;
    #     }"""

    def __init__(self, index, bytes_data: bytes) -> None:
        self._index = index
        self._valid = struct.unpack("H", bytes_data[:2])[0]
        self._name = bytes_data[2:48].decode("big5", errors="ignore")
        self._count = int.from_bytes(bytes_data[3140:3144], byteorder="little")
        self._type = int.from_bytes(bytes_data[3144:3148], byteorder="little")

    @property
    def index(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._index

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

    def update(self):
        self._items: list[Item] = []
        for i in range(28):
            self._items.append(
                Item(i, self.mem.read_bytes(0x00F4C494 + 0xC5C * i, 0xC5C))
            )

    @property
    def foods(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.type == 23:
                yield item

    @property
    def drugs(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.type == 43:
                yield item

    @property
    def bombs(self):
        """_summary_

        Yields:
            _type_: _description_
        """
        for item in self._items:
            if item.type == 51:
               yield item
