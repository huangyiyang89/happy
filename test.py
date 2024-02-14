import happy
from happy.util import b62
import time 

#cg.right_click('A')

#cg.go_send_call('aa')
#cg.go_send_call('e')
import happy.dddocr
dddocr = happy.dddocr.DdddOcr()
with open("code.png", "rb") as f:
    image_bytes = f.read()
    verifycode = dddocr.classification(image_bytes)
    print(verifycode)