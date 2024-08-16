"script"
import happy


class Script(happy.Script):
    """_summary_

    Args:
        happy (_type_): _description_
    """

    def __init__(self, cg) -> None:
        super().__init__(cg)
        self.name = "自动加点"


    def on_not_battle(self, cg: happy.Cg):
        if cg.player.remain_points > 0:
            if cg.player.endurance_points<0:
                cg.add_point(0)
            if cg.player.strength_points<125:
                cg.add_point(1)
                cg.add_point(1)
            if cg.player.agility_points<60:
                cg.add_point(3)
                cg.add_point(3)
            if cg.player.defense_points<50:
                cg.add_point(2)
            if cg.player.magical_points<30:
                cg.add_point(4)
        if cg.player.job_name == "見習弓箭手" and cg.map.name == "弓箭手公會":
            bag = cg.items.find("初心者背包")
            if bag:
                cg.use_item(bag)
            
            for item in cg.items.bags_valids:
                if "訓練用" in item.name:
                    cg.use_item(item)
            cg.drop_item("弓箭手推薦信")

        if cg.pets.battle_pet is not None and cg.pets.battle_pet.remain_points > 0:
            pet = cg.pets.battle_pet
            if pet.name in ["改造樹精"]:
                cg.pets.battle_pet.add_point(0)
            if pet.name in ["小蝙蝠","使魔","影蝙蝠"]:
                cg.pets.battle_pet.add_point(1)

        if cg.map.x in [149,150,151,155,156,157] and cg.map.y in [122,123] and cg.get_dialog_type()==5:
            cg.sell()
        
        if cg.items.find("止痛藥") is None:
            cg.engage_npc(16,35,5,335,r"0 1\\z1")

        if cg.map.x==8 and cg.map.y==6 and cg.items.find("止痛藥"):
            cg.right_click("C")
            cg.engage_npc(10,6,0,326,"4")

        if cg.items.find("試煉洞穴通行證") and cg.get_team_count()==0: 
            cg.right_click("A")
            cg.engage_npc(9,14,0,326,r"1BA 0 3 5g 2CU \\")


        cg.use_item("大女神蘋果")
        cg.drop_item("國民袍", "國民靴","卡片？")
