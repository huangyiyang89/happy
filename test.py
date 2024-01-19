# # """test"""
#import struct
import happy
import time
cg = happy.Cg.open()
#cg.decode_export()
#cg.start_print_packet(True)
#00508C26
cg._decode_send("IPy q")
#cg._decode_send("Ivfo q")
time.sleep(8)
cg._decode_send("sM 0 0 -1 912|8|9|10|11|12")

# with open(r'C:\BlueCrossgate\map\1\3\148.dat', 'rb') as file:
#     # 读取檔頭 (20字节)
#     header = file.read(20)

#     # 解析檔頭
#     magic_word, width_east, height_south = struct.unpack('3s9x2I', header)

#     # 检查魔术字是否为 'MAP'
#     if magic_word != b'MAP':
#         print("Invalid map file.")
#         exit()

#     # 读取地面數據
#     ground_data = file.read(width_east * height_south * 2)
    
#     # 读取地上物件/建築物數據
#     object_data = file.read(width_east * height_south * 2)

#     # 读取地圖標誌
#     flag_data = file.read(width_east * height_south * 2)

#     # 解析地圖標誌數據
#     for i in range(1,height_south+1):
#         for j in range(1,width_east+1):
#             map_id = struct.unpack('H', ground_data[i*j * 2-2 : i*j* 2])
#             object_id = struct.unpack('H', object_data[i*j * 2-2 : i*j* 2])
#             flag = struct.unpack('H', flag_data[i*j * 2-2 : i*j* 2])
#             transition, obstacle = struct.unpack('BB', flag_data[i*j * 2-2 : i*j* 2])
#             if object_id[0]!=0 and object_id[0]!=2:
#                 print(f"east: {j},south:{i},object_id: {object_id[0]}, Transition: {transition}, Obstacle: {obstacle},flag{flag[0]}")