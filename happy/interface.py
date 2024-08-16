''''''
import pymem


class Interface:
    def __init__(self):
        self.pm = pymem.Pymem("cg.exe")
        self.base_address = pymem.process.module_from_name(self.pm.process_handle, "cg.exe").lpBaseOfDll

    def get_pointer(self, offset):
        return self.pm.read_int(self.base_address + offset)