import struct
import happy.core
import happy.item
cg = happy.core.Cg.open()

items = happy.item.ItemCollection(cg.mem)

for item in items._items:
    print(item.valid,item.index,item.name,item.count,item.type)

cg.eat_food()
#给自己使用第一格物品
#cg._decode_send("jBdn 1j 1q 8 0 OO c")