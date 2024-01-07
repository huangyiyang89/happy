"""cgmem"""
import pymem


class CgMem(pymem.Pymem):
    """_summary_

    Args:
        pymem (_type_): _description_
    """

    def read_string(self, address, byte=50, encoding="big5", end=b"\x00"):
        buff = self.read_bytes(address, byte)
        i = buff.find(end)
        if i != -1:
            buff = buff[:i]
        buff = buff.decode(encoding, "replace")
        return buff

    @staticmethod
    def list_cg_processes(process_name=b"bluecg.exe"):
        """not write yet"""
        cg_list = pymem.process.list_processes()
        for process in cg_list:
            if process.szExeFile == process_name:
                yield process.th32ProcessID

    def read_xor_value(self,address) -> int:
        """_summary_

        Args:
            address (_type_): _description_

        Returns:
            _type_: _description_
        """
        x = self.read_int(address)
        y = self.read_int(address+4)
        return x^y