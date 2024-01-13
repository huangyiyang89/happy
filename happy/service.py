"""mem"""
import time
import happy.mem


class Service:
    """add mem"""

    def __init__(self, mem: happy.mem.CgMem) -> None:
        self.mem = mem

    def update(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self

    def _decode_send(self, content):
        """发明文包"""
        # 0057A718 缓存指针
        # 00581000 空内存
        # 使用空内存写入字符串
        self.mem.write_string(0x00581000, content + " \0")
        # 改写缓存地址
        self.mem.write_bytes(0x005064BC, bytes.fromhex("B9 00 10 58 00 90"), 6)
        # 鼠标右击发包
        self.mem.write_short(0x00CDA984, 2)
        time.sleep(0.1)
        # 改回原地址
        self.mem.write_bytes(0x005064BC, bytes.fromhex("8B 0D 18 A7 57 00"), 6)
        print(content)
