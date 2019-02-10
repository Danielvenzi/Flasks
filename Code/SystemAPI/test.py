import os
import shutil
import sqlite3

#var = os.popen("netstat -tulpn | grep 'tcp\b'")
#value = var.read()
#print(value)
#var.close()

#protocolFile = open("volatile/"846, "r+")

#result = os.statvfs("./test.py")
#print(result)

#def num1():
#    print(123)

#def num2():
#    print(345)

#array = [num2,num1]
#command = input("Digite 1 para 123 ou 2 para 345: ")
#if command == "1":
#    array[1]()
#elif command == "2":
#    array[0]()
##tring = "comando option1 option2"
#or char in string:
#    print(char)

#result = shutil.disk_usage("/home")
#print(result[2])

print("Connecting to database...")
conn = sqlite3.connect('database/apiConfiguration.db')
cursor = conn.cursor()

print("Creating database common table...")
cursor.execute('CREATE TABLE APIConfig (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, host TEXT NOT NULL, port INTEGER NOT NULL);')
print("Table created.")

conn.close()