import happy
import time

cg = happy.Cg.open()

while True:
    time.sleep(0.1)
    pointer = cg.mem.read_int(0x0057A718)
    content = cg.mem.read_string(pointer)
    print(content)
