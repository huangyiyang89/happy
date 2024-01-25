import happy
import time

class Script(happy.Script):

    def __init__(self) -> None:
        super().__init__()
        self.name = "自动生产"
        self.production_name="麻布帽"


    def on_not_battle(self, cg: happy.Cg):
        cg.produce(craft_name='麻布帽')
        time.sleep(3)
