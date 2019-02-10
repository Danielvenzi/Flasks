import socket
import os
import sqlite3
from systemapiOptions import *
from setOptions import *
from getOptions import *

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
            cursor.execute('select * from SystemAPI where apiname = \"{0}\";'.format(apiName))
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