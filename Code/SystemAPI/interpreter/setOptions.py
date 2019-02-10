import sqlite3
from getmac import get_mac_address
import os
import hashlib

# ------- set command options function declaration ------------ #

def apiAddr(address):
    conn = sqlite3.connect("database/apiConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing API address...")
    cursor.execute('UPDATE APIConfig SET host = \"{0}\" WHERE id = 1;'.format(str(address)))
    conn.commit()
    conn.close()
    print("OK - API address successfulyy changed to: {}".format(address))


def apiPort(port):
    conn = sqlite3.connect("database/apiConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing API port...")
    cursor.execute('update APIConfig set port = \"{0}\" where id = 1;'.format(int(port)))
    conn.commit()
    conn.close()
    print("OK - API port successfully changed to: {}".format(port))


def apiInterface(interface):
    conn = sqlite3.connect("database/apiConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing API interface...")
    cursor.execute('update APIConfig set interface = \"{0}\" where id = 1;'.format(str(interface)))
    print("OK - API interface successfully changed to: {}".format(interface))
    interfaceMAC = get_mac_address(interface=interface)
    hostname = os.popen("hostname").read()
    hostname = hostname.strip("\n")
    rambleString = hostname+interfaceMAC+hostname+interfaceMAC
    ramble = hashlib.sha512(rambleString.encode('utf-8')).hexdigest()
    cursor.execute('update RegisterInfo set registerkey = \"{0}\" where id = 1;'.format(str(ramble)))
    print("OK - New register key created.")
    conn.commit()
    conn.close()

def apiDescription(description):
    conn = sqlite3.connect("database/apiConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing API description...")
    cursor.execute('update ApiConfig set description = \"{0}\" where id = 1;'.format(str(description)))
    print("OK - API description successfully changed to: {}".format(description))
    conn.commit()
    conn.close()
