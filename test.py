import happy
import time


#自动加点

#宠物受伤治疗

#遇敌受伤停止



cg = happy.Cg.open(account="mlbbcc14")
cg2 = happy.Cg.open(account="mlbbcc15")
print(cg.account)
while True:
    print(cg.map.x,cg.map.y)
    if cg.map.x == 10:
        if cg.map.y == 22:
            cg.go_to(10,19)
        elif cg.map.y == 19:
            cg.go_to(10,22)
    else:
        if cg.map.y == 34:
            cg.go_to(18,37)
        elif cg.map.y == 37:
            cg.go_to(18,34)
    time.sleep(0.1)






##
