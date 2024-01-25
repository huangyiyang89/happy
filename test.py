import happy
import struct
import heapq
import time
from happy.util import b62
import random
cg =  happy.Cg.open()
cg.update()
print(cg.items[0].name+"1")
print(cg.map.width_east,cg.map.height_south)

#cg._decode_send(f'UUN 1 {b62(cg.map.id)} {b62(cg.map.width_east-1)} {b62(cg.map.height_south-1)} {b62(1)} {b62(1)}')
for i in range(100):
    e1 = random.randint(0,cg.map.width_east)
    e2 = random.randint(0,cg.map.width_east)
    s1 = random.randint(0,cg.map.height_south)
    s2 = random.randint(0,cg.map.height_south)
    cg._decode_send(f'UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}')
    cg.map.read_data()
    print(len(cg.map.exits))
    time.sleep(0.5)
    print(e1,e2,s1,s2)

#17954上
#17955下    

#74 65
# 左下走
# 41 28
# VAL 1 wj 24 11 25 11

# 右上走
# 41 28
# VAL 1 wj 58 11 59 11

# 右上走
# 42 28 
# VAL 1 wj 59 11 60 11


# 右下走 42 30
# VAL 1 wj 25 47 60 11