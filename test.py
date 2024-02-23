import happy

cg = happy.Cg.open()
print(cg.account)
cg.set_auto_ret_blackscreen(enable=False)
cg.set_auto_login(enable=False)
cg.set_auto_select_charater(enable=False)
#自动重登测试