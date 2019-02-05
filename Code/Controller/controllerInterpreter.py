import os
import socket
import sqlite3
from getmac import get_mac_address
import hashlib
import requests

# -------- Declaration of the get command options functions ------ #

def getCPU(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    print(result[0][0])
    requestGet = requests.get('http://{0}/api/system/cpu'.format(result[0][0]),timeout=15.0)
    reponseJSON = requestGet.json()

    print(reponseJSON)

def getMem(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    requestGet = requests.get('http://{0}/api/system/mem'.format(result[0][0]), timeout=15.0)
    reponseJSON = requestGet.json()

    print(reponseJSON)

def getDisk(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    requestGet = requests.get('http://{0}/api/system/disk/all/mb'.format(result[0][0]), timeout=15.0)
    reponseJSON = requestGet.json()

    print(reponseJSON)

def getPort(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    requestGet = requests.get('http://{0}/api/system/port/all'.format(result[0][0]), timeout=15.0)
    reponseJSON = requestGet.json()

    print(reponseJSON)

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

# -------- Declaration of the systemapi command action functions -------- #

def apiConfig(options,values):
    if len(options) == 3:
        if not "-apiaddr" in options:
            print("ERROR - Option '-apiaddr' is necessary for the config action.")
            return None
        elif not "-apiport" in options:
            print("ERROR - Option '-apiport' is necessary for the config action.")
            return None
        elif not "-apiname" in options:
            print("ERROR - Option '-apiname' is necessary for the config action.")
        else:
            addr = ""
            port = 0
            name = ""
            for option in options:
                if option == "-apiaddr":
                    optionIndex = options.index(option)
                    addr += str(values[optionIndex])
                elif option == "-apiport":
                    optionIndex = options.index(option)
                    port += int(values[optionIndex])
                elif option == "-apiname":
                    optionIndex = options.index(option)
                    name += (values[optionIndex])

            conn = sqlite3.connect("database/controllerConfiguration.db")
            cursor = conn.cursor()

            cursor.execute('select 1 from SystemAPI where apiname = \"{0}\";'.format(name))
            existsResult = cursor.fetchall()

            if int(len(existsResult)) == int(0):
                cursor.execute('select 1 from SystemAPI where apihost = \"{0}\";'.format(addr))
                addressResult = cursor.fetchall()

                if int(len(addressResult)) == int(0):
                    cursor.execute('insert into SystemAPI (apihost,apiport,apiname,apikey,known) values (\"{0}\",{1},\"{2}\","None",0);'.format(addr,port,name))
                    print("OK - New SystemAPI added with: Address - {0}, Port - {1}, Name - {2}".format(addr,port,name))
                    print("INFO - The SystemAPI is configured but isn't known yet. Use help command for more information.")
                    conn.commit()

                    conn.close()

                elif len(addressResult) != int(0):
                    print("ERROR - A SystemAPI with {0} as it's address already exists.".format(addr))
                    conn.close()
            else:
                print("ERROR - A SystemAPI named {0} already exists.".format(name))
                conn.close()


    elif len(options) < 3:
        print("ERROR - Missing options! Expected '-apiaddr','-apiport' and '-apiname' for the config action. Use help command for more information.")


def apiList(options,values):
    if len(options) == 1:
        if options[0] == "-apiname":
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()
            cursor.execute('select * from SystemAPI;')
            results = cursor.fetchall()

            if len(results) == 0:
                print("ERROR - No configured SystemAPI's. Use help command for more information.")
                return None

            if values[0] == "all":
                cursor.execute('select apiname,apihost,apiport,known from SystemAPI;')
                results = cursor.fetchall()
                iterator = 1
                print("Configured SystemAPI's:")
                for result in results:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Known: {4}".format(iterator,result[0],result[1],result[2],result[3]))
                    iterator += 1
                conn.close()
            else:
                cursor.execute('select apiname,apihost,apiport,known from SystemAPI where apiname = \"{0}\"'.format(values[0]))
                result = cursor.fetchall()
                if len(result) == 0:
                    print("ERROR - No SystemAPI named {0} configured.".format(values[0]))
                    conn.close()
                else:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Known: {4}".format(1,result[0][0],result[0][1],result[0][2],result[0][3]))
                    conn.close()
        else:
            print("ERROR - Missing option! Expect -apiname for the list action. Use help command for more information.")
    else:
        print("ERROR - More options than needed for ACTION list. Use help command for more information.")


def apiAbsorb():
    print("Work in progress")

def apiFlush():
    print("Work in progress")
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

        elif option == "-controllerport":
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
    knowActions = ["config", "list", "absorb", "flush"]
    knowOptions = ["-apiaddr", "-apiport", "-apiname"]
    actionFunction = [apiConfig, apiList, apiAbsorb, apiFlush]

    if len(options) != len(values):
        return "ERROR - Incorrect usage of options! Use help command for more information."
    for actions in action:
        if not actions in knowActions:
            return "ERROR - '{0}' is not a valid action! Use help command for more information.".format(actions)
    for option in options:
        if not option in knowOptions:
            return "ERROR - '{0}' is not a valid option! Use help command for more information.".format(option)

    for option in options:
        if option == "-apiaddr":
            optionIndex = options.index(option)
            ipAddr = values[optionIndex]
            if not "." in ipAddr:
                return "ERROR - {0} is not a valid ip address".format(ipAddr)
            try:
                socket.inet_aton(ipAddr)
            except socket.error:
                return "ERROR - {0} is not a valid ip address".format(ipAddr)

        elif option == "-apiport":
            optionIndex = options.index(option)
            port = values[optionIndex]
            try:
                port = int(port)
            except ValueError:
                return "ERROR - {0} is not a valid port".format(port)

    for act in action:
        iterator = 0
        for knowAction in knowActions:
            if act == knowAction:
                response = actionFunction[iterator](options, values)
            iterator += 1

    return None


def get(action,options,values):
    if len(options) != len(values):
        return "ERROR - Missing options! Check help for correct usage."

    knowOptions = ["-apiname", "-apimetric"]
    knowMetrics = ["cpu", "port", "disk", "mem"]
    for option in options:
        if option == "-apiname":
            optionIndex = options.index(option)
            apiName = values[optionIndex]
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()
            cursor.execute('select * from SystemAPI;')
            result = cursor.fetchall()
            conn.close()
            if len(result) == 0:
                return "ERROR - Unknow SystemAPI: {0} passed as parameter.".format(apiName)
        elif option == "-apimetric":
            optionIndex = options.index(option)
            apiMetric = values[optionIndex]
            if not apiMetric in knowMetrics:
                return "ERROR - Unknow SystemAPI Metric: {0} passed as parameter.".format(apiMetric)
    for option in options:
        if not option in knowOptions:
            return "ERROR - Option {0} not found".format(option)

    apiName = ""
    apiMetric = ""
    for option in options:
        if option == "-apimetric":
            optionIndex = options.index(option)
            apiMetric += str(values[optionIndex])
        elif option == "-apiname":
            optionIndex = options.index(option)
            apiName += str(values[optionIndex])

    if apiMetric == "cpu":
        result = getCPU(apiName)
    elif apiMetric == "mem":
        result = getMem(apiName)
    elif apiMetric == "disk":
        result = getDisk(apiName)
    elif apiMetric == "port":
        result = getPort(apiName)

    return None

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

    commands = ["set","help","clear","exit","reset","config","systemapi","get"]
    commandFunc = [set,help,clear,exit,reset,config,systemapi,get]

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
        command = input(r"{0}@Controller: ".format(userName,hostName))
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