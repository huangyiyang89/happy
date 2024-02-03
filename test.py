# import happy
# import struct
# import heapq
# import time
# from happy.util import b62
# import random

# cg = happy.Cg.open("百瀨飛鳥")
# while True:
#     cg.map.read_data()
#     if len(cg.map.exits) < 2:
#         e1 = random.randint(0, cg.map.width_east)
#         e2 = random.randint(0, cg.map.width_east)
#         s1 = random.randint(0, cg.map.height_south)
#         s2 = random.randint(0, cg.map.height_south)
#         cg._decode_send(
#             f"UUN 1 {b62(cg.map.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}"
#         )
#     else:
#         if cg.map.exits[-1][2] == 12002:
#             cg.go_astar(cg.map.exits[-1][0], cg.map.exits[-1][1])
#     time.sleep(0.1)
import requests

def send_markdown(content):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e0ce689b-5a47-4ae2-ab5e-0539268956d7'
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Markdown message sent successfully.")
    else:
        print("Failed to send Markdown message. Status code:", response.status_code)

# Example usage:
content = "### 游戏账号:mlbbhy01\n[验证链接](https://www.bluecg.net/plugin.php?id=gift:v3&ac=mlbbhy198901&time=1706625306)"
send_markdown(content)
    # cg._decode_send(
    #         f"UUN 1 {b62(cg.map.id)} {cg.map.x} {cg.map.y} {b62(cg.map.width_east)} {b62(cg.map.height_south)}"
    # )
    
# s = r"yJ 29 29 5o 4YS 0 9\\z3\\z10\\z3\\z11\\z3\\z12\\z3\\z13\\z3\\z14\\z1\\z15\\z3\\z16\\z3\\z18\\z3\\z19\\z1\\z21\\z3\\z22\\z3\\z23\\z2\\z24\\z3\\z25\\z1\\z26\\z1\\z27\\z1"
# print(len(s))

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
