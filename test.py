import happy
import struct
import heapq
import time
from happy.util import b62
import random

cg = happy.Cg.open("中指通")
cg.right_click('A')
s = r"yJ 29 29 5o 4YS 0 9\\z3\\z10\\z3\\z11\\z3\\z12\\z3\\z13\\z3\\z14\\z1\\z15\\z3\\z16\\z3\\z18\\z3\\z19\\z1\\z21\\z3\\z22\\z3\\z23\\z2\\z24\\z3\\z25\\z1\\z26\\z1\\z27\\z1"
print(len(s))
while True:
    s = cg.mem.read_string(0x222F0008,byte=5000)
    if s:
        print(s)
#GraphicInfo_66.bin 4100+
#GraphicInfo_Joy_54 243021
#GraphicInfo_Joy_CH1 91500
#GraphicInfo_Joy_EX_9 1199994
#GraphicInfoEX_5 223018
#GraphicInfoV3_19 27660
#puk3\Graphicinfo_PUK3_1 301119
#puk2\GraphicInfo_PUK2_2 300001


# 17954上
# 17955下

# 74 65
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
