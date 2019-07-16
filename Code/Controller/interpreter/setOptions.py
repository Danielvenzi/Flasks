import sqlite3
from getmac import get_mac_address
import os
import hashlib

# -------- Declaration of set command options functions -------- #

def controllerAddr(address):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing Controller API address...")
    cursor.execute('UPDATE ControllerConfig SET host = \"{0}\" WHERE id = 1;'.format(str(address)))
    conn.commit()
    conn.close()
    print("OK - Controller API address successfulyy changed to: {}".format(address))


def controllerPort(port):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing Controller API port...")
    cursor.execute('update ControllerConfig set port = \"{0}\" where id = 1;'.format(int(port)))
    conn.commit()
    conn.close()
    print("OK - Controller API port successfully changed to: {}".format(port))


def controllerInterface(interface):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing ControllerAPI interface...")
    cursor.execute('update ControllerConfig set interface = \"{0}\" where id = 1;'.format(str(interface)))
    print("OK - Controller API interface successfully changed to: {}".format(interface))
    interfaceMAC = get_mac_address(interface=interface)
    hostname = os.popen("hostname").read()
    hostname = hostname.strip("\n")
    rambleString = hostname+interfaceMAC+hostname+interfaceMAC
    ramble = hashlib.sha512(rambleString.encode('utf-8')).hexdigest()
    cursor.execute('update UntrustInfo set registerkey = \"{0}\" where id = 1;'.format(str(ramble)))
    print("OK - New untrust key created.")
    conn.commit()
    conn.close()

def controllerDescription(description):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    print("INFO - Changing Controller API description...")
    cursor.execute('update ControllerConfig set description = \"{0}\" where id = 1;'.format(str(description)))
    print("OK - ControllerAPI description successfully changed to: {}".format(description))
    conn.commit()
    conn.close()