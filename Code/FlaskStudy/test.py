import os
import shutil

#var = os.popen("netstat -tulpn | grep 'tcp\b'")
#value = var.read()
#print(value)
#var.close()

#protocolFile = open("volatile/"846, "r+")

#result = os.statvfs("./test.py")
#print(result)




result = shutil.disk_usage("/home")
print(result[2])

