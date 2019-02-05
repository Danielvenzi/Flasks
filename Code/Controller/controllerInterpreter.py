import os
import socket
import sqlite3
from getmac import get_mac_address
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

# -------- Declaration of the commands functions --------- #

def set(action,options,values):
    if len(options) != len(values):
        return "ERROR - Missing options! Check help for correct usage."

    for option in options:
        if option == "-controlleraddr":
            optionIndex = options.index(option)
            ipAddr = values[optionIndex]
            if not "." in ipAddr:
                return "ERROR - {0} is not a valid ip address".format(ipAddr)
            try:
                socket.inet_aton(ipAddr)
            except socket.error:
                return "ERROR - {0} is not a valid ip address".format(ipAddr)

        elif option == "-controllerportport":
            optionIndex = options.index(option)
            port = values[optionIndex]
            try:
                port = int(port)
            except ValueError:
                return "ERROR - {0} is not a valid port".format(port)

        elif option == "-controllerinterface":
            optionIndex = options.index(option)
            result = os.popen(r"ifconfig {} 1> /dev/null 2> /dev/null ; echo $?".format(values[optionIndex])).read()
            result = result.strip("\n")
            if result != "0":
                return "ERROR - {0} is not a valid interface".format(values[optionIndex])

    knowOptions = ["-controlleraddr","-controllerport","-controllerinterface","-controllerdescription"]
    optionFunction = [controllerAddr,controllerPort,controllerInterface,controllerDescription]
    for option in options:
        if not option in knowOptions:
            return "ERROR - Option {0} not found".format(option)

    for option in options:
        iterator = 0
        for knowoption in knowOptions:
            if option == knowoption:
                optionIndex = options.index(option)
                response = optionFunction[iterator](values[optionIndex])
            iterator += 1

    return None


def help(action,options,values):
    print("help")

def clear(action,options,values):
    os.system("clear")
    return None

def reset(action,options,values):
    response = input("WARN - You are about to reset the configurations of the Controllers API and the known SystemAPI's. Are you sure [y/n]? ")
    if response == "y":
        conn = sqlite3.connect('database/controllerConfiguration.db')
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS ControllerConfig;')
        cursor.execute('DROP TABLE IF EXISTS UntrustInfo;')
        cursor.execute('DROP TABLE IF EXISTS SystemAPI;')
        cursor.execute('CREATE TABLE IF NOT EXISTS ControllerConfig (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, host TEXT, port INTEGER, interface TEXT,description TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS UntrustInfo (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, registerkey TEXT NOT NULL);')
        cursor.execute('CREATE TABLE IF NOT EXISTS SystemAPI (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, apihost TEXT, apiport INTEGER, apiname TEXT, known INTEGER,apikey TEXT);')
        cursor.execute('INSERT INTO ControllerConfig (host) values (123);')
        cursor.execute("UPDATE ControllerConfig SET host = \"{0}\",port = {1},interface = \"{2}\",description = \"{2}\" WHERE id=1;".format("127.0.0.1", 80,"lo", "ControllerAPI"))
        cursor.execute('INSERT INTO UntrustInfo (registerkey) values ("None");')
        conn.commit()

        print("OK - Controller API configuration has been successfully reset.")
        print("INFO - Controller API current configuration - Address: 127.0.0.1, Port: 80, Interface: lo, Description: ControllerAPI")
        print("INFO - No known SystemAPI's.")

        conn.close()
    else:
        return None

def exit(action,options,values):
    return "exit"

def config(action,options,values):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()

    cursor.execute('select * from ControllerConfig where id=1;')
    result = cursor.fetchall()
    global APIPort
    APIPort = result[0][1]
    global APIAddr
    APIAddr = result[0][2]
    APIInterface = result[0][3]
    APIDescription = result[0][4]
    conn.close()

    return "Running config - Address: {0}, Port: {1}, Interface: {2}, Description: {3}".format(APIPort, APIAddr, APIInterface,APIDescription)

def systemapi(action,options,values):
    print("systemapi")

# ------- Declaration of the interpreter core functions --------- #

def gatherCommandDetails(Command):
    Command += " "
    commandIntoArray = []
    string = ""
    for char in Command:
        if char != " ":
            string += char
        else:
            commandIntoArray.append(string)
            string = ""


    processResult = {}
    iterator = 0
    optionIterator = 0
    command = []
    action = []
    options = []
    values = []
    for elements in commandIntoArray:
        if commandIntoArray[0] != "systemapi":
            if not "-" in elements and (iterator == 0):
                command.append(elements)
                action.append(None)
            elif elements[0] == "-":
                options.append(elements)
                optionIterator = iterator
            elif iterator == optionIterator+1:
                values.append(elements)
            iterator += 1

        elif commandIntoArray[0] == "systemapi":
            if iterator == 0:
                command.append("systemapi")
            elif iterator == 1:
                action.append(elements)
            elif elements[0] == "-":
                options.append(elements)
                optionIterator = iterator
            elif iterator == optionIterator+1:
                values.append(elements)
            iterator += 1

    processResult["Command"] = command
    processResult["Options"] = options
    processResult["Values"] = values
    processResult["Action"] = action

    return processResult


def execute(arrayOfDirections):
    command = arrayOfDirections["Command"]
    action = arrayOfDirections["Action"]
    options = arrayOfDirections["Options"]
    values = arrayOfDirections["Values"]

    commands = ["set","help","clear","exit","reset","config","systemapi"]
    commandFunc = [set,help,clear,exit,reset,config,systemapi]

    if not command[0] in commands:
        print("{0} - No such command available".format(command[0]))
        return None

    commandResult = ""
    for commandExec in commands:
        if command[0] == commandExec:
            index = commands.index(commandExec)
            commandResult = commandFunc[index](action,options,values)

    return commandResult


# --------- Declaration of the interpreter main command ----------

def interpreterMainLoop():
    userName = os.popen("whoami").read()
    userName = userName.strip("\n")

    hostName = os.popen("hostname").read()
    hostName = hostName.strip("\n")
    print("# ------------- API configuration terminal --------------- #")
    while True:
        command = input(r"{0}@System-API: ".format(userName,hostName))
        arraySpecifics = gatherCommandDetails(command)
        print(arraySpecifics)
        commandResponse = execute(arraySpecifics)
        if commandResponse == "exit":
            break
        elif commandResponse == None:
            continue
        else:
            print(commandResponse)


if __name__ == "__main__":
    interpreterMainLoop()