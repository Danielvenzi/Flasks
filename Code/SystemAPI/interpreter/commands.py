import os
import sqlite3
import socket
from setOptions import *
from controllerActions import *
# ------- Command function declaration --------#

def set(action, options, values):
    if len(options) != len(values):
        return "ERROR - Missing options! Check help for correct usage."

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

        elif option == "-apiinterface":
            optionIndex = options.index(option)
            result = os.popen(r"ifconfig {} 1> /dev/null 2> /dev/null ; echo $?".format(values[optionIndex])).read()
            result = result.strip("\n")
            if result != "0":
                return "ERROR - {0} is not a valid interface".format(values[optionIndex])

    knowOptions = ["-apiaddr", "-apiport", "-apiinterface", "-apidescription"]
    optionFunction = [apiAddr, apiPort, apiInterface, apiDescription]
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


def clear(action, options, values):
    os.system("clear")
    return None


def help(action, options, values):
    return """
    API command line configuration.

        COMMANDS 
         1-) set [OPTIONS] [VALUES], used for API configuration.
         2-) controller [ACTION] [OPTIONS] [VALUES], used for trusted controller configuration.
         3-) config - displays the current API configuration.
         4-) reset - resets the API to it's "factory" state, port: 80, address: 127.0.0.1 and interface: lo.
         5-) help - displays the commands and options of the command line interpreter.
         6-) clear - clears the command prompt.
         7-) exit - exits the command line.


        COMMAND ACTIONS
         2-) controller command actions:
            config [OPTIONS] [VALUES] - does the configuration of a new Controller.
                OBS: OPTIONS and VALUES are discussed in the command options section.
                    For the config ACTION all the options (-controlleraddr,-controllerport,-controllername) must be used.

            list [VALUE] - list the trusted Controllers.
                [VALUE] = all  ,   lists the information about all the trusted Controllers.
                          name ,   lists the information about the trusted Controller with the given name,
                                   name must be passed with -controllername option.

            trust [VALUE] - initiates the trust process between the API and the Controller.
                [VALUE] = all  ,   initiates the trust process with all the configured Controllers.
                          name ,   initiates the trust process with the Controller associated with the given name,
                                   name must be passed with -controllername option.

            untrust [VALUE] - initiates the untrust process between the API and the Controller.
                [VALUE] = all  ,   initiates the untrust process with all the configured Controllers.
                          name ,   initiates the untrust process with the Controller associated with the given name,
                                   name must be passed with -controllername option.

        COMMAND OPTIONS
         1-) set command options:
            -apiport [port_value <integer>] , used for setting the port that the API will listen to.
            -apiaddr [address_value <ip>]   , used for setting the address that the API will be binded to. 
                OBS: address_values must be a valid IP address.
            -apiinterface [interface_name <string>] , used for setting the interface that holds the IP address of the API. 
                OBS: interface_name must be an existing interface in the system. 
            -apidescription [description <string>] , used for setting the description of the API, example: GatewayBSAN

         2-) controller command options for the "config" [ACTION]:
            -controllerport [port_value <integer>] , used for setting the port that the Controller listens to
            -controlleraddr [address_value <integer>] ,  used for setting the address that the Controller is binded to.
                OBS: address_value must be a valid IP address.
            -controllername [name_value] , used for setting the name for a specific Controller, this name will identify a
                trusted Controller.
    """


def exit(action, options, values):
    return "exit"


def reset(action, options, values):
    response = input(
        "WARN - You are about to reset the configurations of the API and the trusted Controllers. Are you sure [y/n]? ")
    if response == "y":

        conn = sqlite3.connect('database/apiConfiguration.db')
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS APIConfig;')
        cursor.execute('DROP TABLE IF EXISTS RegisterInfo;')
        cursor.execute('DROP TABLE IF EXISTS Controllers;')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS APIConfig (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, host TEXT, port INTEGER, interface TEXT,description TEXT);')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS RegisterInfo (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, registerkey TEXT NOT NULL);')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS Controllers (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, controllerhost TEXT, controllerport INTEGER, controllername TEXT, trusted INTEGER,controllerkey TEXT);')
        cursor.execute('INSERT INTO APIConfig (host) values (123);')
        cursor.execute(
            "UPDATE APIConfig SET host = \"{0}\",port = {1},interface = \"{2}\" WHERE id=1;".format("127.0.0.1", 80,
                                                                                                    "lo", "HostAPI"))
        cursor.execute('INSERT INTO RegisterInfo (registerkey) values ("None");')

        conn.commit()

        print("OK - API configuration has been successfully reset.")
        print("INFO - API current configuration - Address: 127.0.0.1, Port: 80, Interface: lo, Description: HostAPI")
        print("INFO - No configured/trusted Controllers.")

        conn.close()
    else:
        return None


def config(action, options, values):
    conn = sqlite3.connect('database/apiConfiguration.db')
    cursor = conn.cursor()

    cursor.execute('select * from APIConfig where id=1;')
    result = cursor.fetchall()
    global APIPort
    APIPort = result[0][1]
    global APIAddr
    APIAddr = result[0][2]
    APIInterface = result[0][3]
    APIDescription = result[0][4]
    conn.close()

    return "Running config - Address: {0}, Port: {1}, Interface: {2}, Description: {3}".format(APIPort, APIAddr,APIInterface,APIDescription)


def controller(action, options, values):
    knowActions = ["config", "list", "trust", "untrust"]
    knowOptions = ["-controlleraddr", "-controllerport", "-controllername"]
    actionFunction = [controllerConfig, controllerList, controllerTrust, controllerUntrust]

    if len(options) != len(values):
        return "ERROR - Incorrect usage of options! Use help command for more information."
    for actions in action:
        if not actions in knowActions:
            return "ERROR - '{0}' is not a valid action! Use help command for more information.".format(actions)
    for option in options:
        if not option in knowOptions:
            return "ERROR - '{0}' is not a valid option! Use help command for more information.".format(option)

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

    for act in action:
        iterator = 0
        for knowAction in knowActions:
            if act == knowAction:
                response = actionFunction[iterator](options, values)
            iterator += 1

    return None
