"""script"""


class Script:
    """Script interface"""

    def __init__(self,cg) -> None:
        self._state = 0
        self.name = "no name script"
        self.cg = cg

    @property
    def state(self):
        """0停止 1等待开始 2正在运行 3等待结束

        Returns:
            _type_: _description_
        """
        return self._state
    
    @state.setter
    def state(self,value):
        """0停止 1等待开始 2正在运行 3等待结束

        Returns:
            _type_: _description_
        """
        self._state = value

    @property
    def enable(self):
        """state > 0

        Returns:
            _type_: _description_
        """
        return self.state > 0

    @enable.setter
    def enable(self,value):
        if value:
            self.start()
        else:
            self.stop()

    def start(self):
        """设置state = 1 等待开始"""
        if self.state in (0,3):
            self.state = 1


    def stop(self):
        """设置state = 3 等待结束"""
        if self.state in (1,2):
            self.state = 3

    def on_start(self, cg):
        """_summary_"""

    def on_stop(self, cg):
        """_summary_"""

    def on_update(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_battle(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_player_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_player_second_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_pet_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_pet_second_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_battle(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_moving(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
