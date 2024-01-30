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
        # 0057E998 客户端随机数，找到写入注释掉
        # 说话call 00507780
        # 0050D3C9 打断点 看ecx地址 是指令字符串
        # 0050D2D0 打断点 看指针0057A718是完整加密字符串

        # jump hook
        self.mem.write_int(0x00507780, 0x0799CBE9)
        # 汇编指令写入
        self.mem.write_bytes(
            0x00581150,
            bytes.fromhex(
                "FF 25 D0 11 58 00 8B 05 00 10 58 00 A3 40 11 58 00 C7 05 44 11 58 00 00 00 00 00 68 40 11 58 00 68 40 11 58 00 E8 E6 C1 F8 FF 83 C4 08 B8 00 10 58 00 8B 0D 40 11 58 00 80 3D 02 10 58 00 20 66 89 08 74 12 80 3D 03 10 58 00 20 89 08 75 07 C6 05 03 10 58 00 20 8B 54 24 10 50 52 E8 1F C1 F8 FF 83 C4 08 C7 05 D0 11 58 00 C0 11 58 00 C3 90 8B 05 18 A7 57 00 E9 BA 65 F8 FF 90 90 90 90 90 56 11 58 00"
            ),
            132,
        )

        self.mem.write_string(0x00581000, content + " \0")

        # 触发说话
        # 聊天栏字符长度
        self.mem.write_int(0x00613904, 1)
        # 回车
        self.mem.write_int(0x0072BD15, 26)

        # 延迟防止不触发
        time.sleep(0.1)
        print(content)

    def decode_export(self):
        """导出加密表"""
        for i in range(0, 1088, 4):
            start = 0x0057A31C + i
            content = self.mem.read_string(start)
            if content:
                self.mem.write_int(0x00507780, 0x0798CBE9)
                # 汇编指令写入
                self.mem.write_bytes(
                    0x00581050,
                    bytes.fromhex(
                        "FF 25 D0 10 58 00 8B 05 00 10 58 00 A3 40 10 58 00 C7 05 44 10 58 \
                            00 00 00 00 00 68 40 10 58 00 68 40 10 58 00 E8 E6 C2 F8 FF 83 C4 \
                                08 B8 00 10 58 00 8B 0D 40 10 58 00 80 3D 02 10 58 00 20 66 89 \
                                    08 74 12 80 3D 03 10 58 00 20 89 08 75 07 C6 05 03 10 58 00 \
                                        20 8B 54 24 10 50 52 90 90 90 90 90 83 C4 08 C7 05 D0 10 \
                                            58 00 C0 10 58 00 C3 90 8B 05 18 A7 57 00 E9 BA 66 F8 \
                                                FF 90 90 90 90 90 56 10 58 00"
                    ),
                    132,
                )

                self.mem.write_string(0x00581000, content + " \0")

                # 触发说话
                # 聊天栏字符长度
                self.mem.write_int(0x00613904, 1)
                # 回车
                self.mem.write_int(0x0072BD15, 26)

                # 延迟防止不触发
                time.sleep(0.1)
                text = self.mem.read_string(0x00581000)
                print(content, text)

    def start_print_packet(self, flag):
        """_summary_"""
        pointer = self.mem.read_int(0x0057A718)
        if flag:
            pointer = 0x00580CE1
        last = self.mem.read_string(pointer)
        while True:
            new = self.mem.read_string(pointer)
            new = new.split("\n")[0]
            if new == last:
                continue
            else:
                print(new)
                last = new

    def debug_print(self):
        # 使用 dir 获取类的属性和方法列表
        all_attributes = dir(self)

        # 筛选出属性和带有 @property 装饰器的方法
        property_attributes = [
            attr
            for attr in all_attributes
            if isinstance(getattr(self.__class__, attr, None), property)
        ]
        methods_with_property = [
            attr
            for attr in all_attributes
            if callable(getattr(self, attr, None))
            and isinstance(getattr(self.__class__, attr, None), property)
        ]

        # 打印属性
        print("Properties:")
        for attr in property_attributes:
            attr_value = getattr(self, attr)
            print(f"  {attr}: {attr_value}")

        # 打印带 @property 装饰器的方法
        print("Methods with @property:")
        for attr in methods_with_property:
            attr_value = getattr(self, attr)
            print(f"  {attr}: {attr_value}")
