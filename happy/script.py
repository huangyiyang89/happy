"""script"""

class Script:
    """Script interface"""

    def __init__(self) -> None:
        self.enable = False
        self.name = "no name script"

    @property
    def enable(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._enable

    @enable.setter
    def enable(self, enable):
        """_summary_

        Args:
            new_value (_type_): _description_
        """
        self._enable = enable
        self.on_enable(enable)

    def on_enable(self, enable):
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

    def on_pet_turn(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_battle(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """

    def on_not_walking(self, cg):
        """_summary_

        Args:
            cg (_type_): _description_
        """
