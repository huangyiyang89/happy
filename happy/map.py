"""Map"""

import struct
import heapq
import random
import time
from happy.mem import CgMem
from happy.util import b62
import happy.service
from happy.dict import map_info_dict, map_flag_30001


class Map(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
    """
    map_dict = {}

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.map_flag_data = []
        self.exits = []
        self.width_east = 0
        self.height_south = 0
        self.last_map_id = 0
        self.file_last_mtime = 0
        self.graphic_info_dict = {}

    @property
    def x(self):
        """

        Returns:
            _type_: _description_
        """
        return int(self.mem.read_float(0x00BF6CE8) / 64)

    @property
    def y(self):
        """

        Returns:
            _type_: _description_
        """
        return int(self.mem.read_float(0x00BF6CE4) / 64)

    @property
    def x_62(self):
        """

        Returns:
            _type_: _description_
        """
        return b62(self.x)

    @property
    def y_62(self):
        """

        Returns:
            _type_: _description_
        """
        return b62(self.y)

    @property
    def id(self):
        """地图ID

        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00970430)

    @property
    def name(self):
        """地图名称

        Returns:
            _type_: _description_
        """
        return self.mem.read_string(0x0095C870)

    @property
    def file_path(self):
        """_summary_

        Returns:
            _type_: _description_
        """

        path = self.mem.read_string(0x0018CCCC,encoding="UTF-8")
        if "map" not in path:
            path = self.mem.read_string(0x0018CCCC - 4,encoding="UTF-8")
        if "map" not in path:
            return ""
        return self.mem.get_directory() + "\\" + path


    def update(self):
        if self.id != self.last_map_id:
            time.sleep(1)
            self.last_map_id = self.id
            self.exits = []

    def read_data(self):
        """_summary_"""

        def set_rectangle_to_zero(map_array, x1, y1, x2, y2,flag = 0):
            """
            将地图数组中指定矩形区域的值全部设置为0。

            参数：
            - map_array: 地图数组
            - x1, y1: 矩形区域左上角的坐标
            - x2, y2: 矩形区域右下角的坐标
            """
            for i in range(x1, x2 + 1):
                for j in range(y1, y2 + 1):
                    map_array[j][i] = flag

        if self.id == 30001:
            self.map_flag_data = map_flag_30001
            set_rectangle_to_zero(self.map_flag_data, 150, 334, 151, 344,1)
            set_rectangle_to_zero(self.map_flag_data, 148, 333, 150, 335,1)
            set_rectangle_to_zero(self.map_flag_data, 161,325,300, 340)
            # set_rectangle_to_zero(self.map_flag_data, 124, 310, 143, 325)
            # with open("exported_array.py", "w") as f:
            #     f.write("exported_array = ")
            #     f.write(str(self.map_flag_data))

            return True
        try:
            if self.file_path == "":
                return False
            with open(self.file_path, "rb") as file:
                header = file.read(20)
                magic_word, self.width_east, self.height_south = struct.unpack(
                    "3s9x2I", header
                )
                if magic_word != b"MAP":
                    print("Invalid map file.")
                ground_data = file.read(self.width_east * self.height_south * 2)
                object_data = file.read(self.width_east * self.height_south * 2)
                flag_data = file.read(self.width_east * self.height_south * 2)
                self.map_flag_data = [
                    [1 for _ in range(self.width_east)]
                    for _ in range(self.height_south)
                ]
                self.exits = []
                for i in range(0, self.height_south):
                    for j in range(0, self.width_east):
                        map_id = struct.unpack(
                            "H",
                            ground_data[
                                (j + i * self.width_east)
                                * 2 : (j + i * self.width_east)
                                * 2
                                + 2
                            ],
                        )[0]
                        object_id = struct.unpack(
                            "H",
                            object_data[
                                (j + i * self.width_east)
                                * 2 : (j + i * self.width_east)
                                * 2
                                + 2
                            ],
                        )[0]
                        flag = struct.unpack(
                            "H",
                            flag_data[
                                (j + i * self.width_east)
                                * 2 : (j + i * self.width_east)
                                * 2
                                + 2
                            ],
                        )[0]

                        # if map_id == 0:
                        # self.map_flag_data[i][j] = 0

                        # flag == 49162是出口切换地图 49155是水晶传送上下楼梯 49152正常通过
                        if flag == 49155:
                            self.exits.append((j, i, object_id))
                            # print(f"找到场景转换坐标={j},{i},object_id={object_id}")

                        # if flag == 0:未读取地图，不能加
                        #     self.map_flag_data[i][j] = 0

                        if object_id:
                            if object_id == 2 and flag == 49152:
                                pass
                            elif str(object_id) in map_info_dict:
                                e, s, f = map_info_dict[str(object_id)]
                                for l in range(e):
                                    for m in range(s):
                                        self.map_flag_data[i - m][j + l] = f
                            else:
                                # self.map_flag_data[i][j] = 0
                                print(
                                    f"该地图{self.name} 存在字典中不存在的object_id={object_id}"
                                )

                self.exits = sorted(self.exits, key=lambda x: x[2])
                return True
        except FileNotFoundError:
            # print("未能打开地图文件")
            return False

    def paint_map(self):
        """_summary_"""
        for line in self.map_flag_data:
            for point in line:
                if not point:
                    print("■", end="")
                else:
                    print(" ", end="")
            print("")

    def astar(self, x, y):
        """_summary_

        Args:
            goal (_type_): _description_
        """

        def neighbors(node, grid):
            x, y, _ = node
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            result = []

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                # Check if the neighbor is within bounds
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and 0 <= x < len(grid[0]) and 0 <= y < len(grid):
                    # Check if the neighbor cell is walkable
                    if grid[ny][nx] == 1:
                        # For diagonal movement, ensure both horizontal and vertical paths are clear
                        if dx != 0 and dy != 0:
                            if grid[y][nx] == 1 and grid[ny][x] == 1:
                                result.append((nx, ny, node))
                        else:
                            result.append((nx, ny, node))

            return result

        if len(self.map_flag_data) == 0:
            return None

        goal = (x, y)

        heap = [(0, (self.x, self.y, None))]
        visited = set()

        while heap:
            cost, current = heapq.heappop(heap)

            if current[:2] == goal:
                path = []
                while current:
                    path.append(current[:2])
                    current = current[2]
                return list(reversed(path))

            if current[:2] in visited:
                continue

            visited.add(current[:2])

            for neighbor in neighbors(current, self.map_flag_data):
                if neighbor[:2] not in visited:
                    hx = abs(neighbor[0] - goal[0])
                    hy = abs(neighbor[1] - goal[1])
                    # Use Euclidean distance as heuristic for diagonal movement
                    h = (hx ** 2 + hy ** 2) ** 0.5
                    heapq.heappush(heap, (cost + h, neighbor))

        return None

    def request_map_data(self):
        """_summary_"""
        e1 = random.randint(0, self.width_east)
        e2 = random.randint(0, self.width_east)
        s1 = random.randint(0, self.height_south)
        s2 = random.randint(0, self.height_south)
        self._decode_send(
            f"UUN 1 {b62(self.id)} {b62(e1)} {b62(s1)} {b62(e2)} {b62(s2)}"
        )

    def read_info_data(self):
        """_summary_"""
        # GraphicInfo_66.bin 4100+
        # GraphicInfo_Joy_54 243021
        # GraphicInfo_Joy_CH1 91500
        # GraphicInfo_Joy_EX_9 1199994
        # GraphicInfoEX_5 223018
        # GraphicInfoV3_19 27660
        # puk3\Graphicinfo_PUK3_1 301119
        # puk2\GraphicInfo_PUK2_2 300001
        pass

    def find_largest_square_area(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        except_exit_data = self.map_flag_data
        for _exit in self.exits:
            except_exit_data[_exit[1]][_exit[0]] = 0

        if not except_exit_data:
            return []

        m, n = len(except_exit_data), len(except_exit_data[0])
        dp = [[0] * n for _ in range(m)]

        # 初始化第一行和第一列
        for i in range(m):
            dp[i][0] = except_exit_data[i][0]
        for j in range(n):
            dp[0][j] = except_exit_data[0][j]

        # 填充动态规划表
        for i in range(1, m):
            for j in range(1, n):
                if except_exit_data[i][j] == 1:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

        # 找出最大正方形区域
        max_size = 0
        max_i, max_j = 0, 0
        for i in range(m):
            for j in range(n):
                if dp[i][j] > max_size:
                    max_size = dp[i][j]
                    max_i, max_j = i, j

        # 构造最大正方形区域的位置列表
        square_area = []
        for i in range(max_i - max_size + 1, max_i + 1):
            for j in range(max_j - max_size + 1, max_j + 1):
                square_area.append((i, j))

        return square_area
