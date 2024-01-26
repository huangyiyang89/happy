"""Map"""
import os
import struct
import heapq
from happy.mem import CgMem
from happy.util import b62
import happy.service


class Map(happy.service.Service):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self.map_data = []
        self.exits = []
        self.width_east = 0
        self.height_south = 0
        self.last_map_id = 0
        self.file_last_mtime = 0

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
        return self.mem.get_directory() + "\\" + self.mem.read_string(0x0018CCCC)

    def read_data(self):
        """_summary_"""
        print("read map data")
        try:
            with open(self.file_path, "rb") as file:
                # 读取檔頭 (20字节)
                header = file.read(20)

                # 解析檔頭
                magic_word, self.width_east, self.height_south = struct.unpack(
                    "3s9x2I", header
                )

                # 检查魔术字是否为 'MAP'
                if magic_word != b"MAP":
                    print("Invalid map file.")

                # 读取地面數據
                file.read(self.width_east * self.height_south * 2)

                # 读取地上物件/建築物數據
                object_data = file.read(self.width_east * self.height_south * 2)

                # 读取地圖標誌
                flag_data = file.read(self.width_east * self.height_south * 2)

                self.map_data = []
                self.exits = []
                # 解析地圖標誌數據
                for i in range(0, self.height_south):
                    east = []
                    for j in range(0, self.width_east):
                        # map_id = struct.unpack(
                        #     "H",
                        #     ground_data[
                        #         (j + i * width_east) * 2 : (j + i * width_east) * 2 + 2
                        #     ],
                        # )
                        flag = struct.unpack(
                            "H",
                            flag_data[
                                (j + i * self.width_east)
                                * 2 : (j + i * self.width_east)
                                * 2
                                + 2
                            ],
                        )
                        object_id = struct.unpack(
                            "H",
                            object_data[
                                (j + i * self.width_east)
                                * 2 : (j + i * self.width_east)
                                * 2
                                + 2
                            ],
                        )

                        if flag[0] == 49155:
                            self.exits.append((j, i, object_id[0]))
                            east.append(1)
                        else:
                            east.append(0 if object_id[0] else 1)
                    self.map_data.append(east)
        except FileNotFoundError:
            print("未能打开地图文件")

    def astar(self, x, y):
        """_summary_

        Args:
            goal (_type_): _description_
        """

        def neighbors(node, grid):
            x, y, _ = node
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            result = []

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 1:
                    result.append((nx, ny, node))

            return result

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

            for neighbor in neighbors(current, self.map_data):
                if neighbor[:2] not in visited:
                    h = abs(neighbor[0] - goal[0]) + abs(neighbor[1] - goal[1])
                    heapq.heappush(heap, (cost + h, neighbor))

        return None

    def update(self):
        if self.id != self.last_map_id:
            self.read_data()
            self.last_map_id = self.id

        # try:
        #     # 获取文件的最后修改时间
        #     mtime = os.path.getmtime(self.file_path)
        #     if mtime > self.file_last_mtime:
        #         print("map dat updated")
        #         self.read_data()
        #         self.file_last_mtime = mtime
        # except FileNotFoundError:
        #     print("dat文件未找到。")
