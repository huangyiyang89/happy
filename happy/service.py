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

        #0050D3C9 打断点 看ecx地址 是指令字符串
        #吃药 料理iVfo

        self.mem.write_bytes(0x005064B1,bytes.fromhex("A1 18 A7 57 00 50 83 C0 40 90 90 8B 0D 18 A7 57 00 80 79 02 20 8B 11 66 89 51 40 74 03 89 51 40 8B 54 24 10 51 52 E8 F4 6D 00 00 83 C4 14 C3"),47)
        
        order = content.split()[0]
        self.mem.write_string(0x0057A31C,order)

        pointer = self.mem.read_int(0x0057A718)
        self.mem.write_string(pointer+0x40, content + " \0")

        # 改写push eax缓存地址
        self.mem.write_bytes(0x005064D5,bytes.fromhex("50"), 1)

        # 鼠标右击发包
        self.mem.write_short(0x00CDA984, 2)
        time.sleep(0.1)
        # 改回
        self.mem.write_string(0x0057A31C,"zA\0\0")
        self.mem.write_bytes(0x005064D5,bytes.fromhex("51"), 1)
        print(content)
