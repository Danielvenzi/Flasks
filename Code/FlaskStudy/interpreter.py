import os
import sqlite3
from getmac import get_mac_address
import hashlib
import requests
import socket
import json

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

# ------- controller command actions function declaration ------- #

def controllerConfig(options,values):
    if len(options) == 3:
        if not "-controlleraddr" in options:
            print("ERROR - Option '-controlleraddr' is necessary for the config action.")
            return None
        elif not "-controllerport" in options:
            print("ERROR - Option '-controllerport' is necessary for the config action.")
            return None
        elif not "-controllername" in options:
            print("ERROR - Option '-controllername' is necessary for the config action.")
        else:
            addr = ""
            port = 0
            name = ""
            for option in options:
                if option == "-controlleraddr":
                    optionIndex = options.index(option)
                    addr += str(values[optionIndex])
                elif option == "-controllerport":
                    optionIndex = options.index(option)
                    port += int(values[optionIndex])
                elif option == "-controllername":
                    optionIndex = options.index(option)
                    name += (values[optionIndex])

            conn = sqlite3.connect("database/apiConfiguration.db")
            cursor = conn.cursor()

            cursor.execute('select 1 from Controllers where controllername = \"{0}\";'.format(name))
            existsResult = cursor.fetchall()

            if int(len(existsResult)) == int(0):
                cursor.execute('select 1 from Controllers where controllerhost = \"{0}\";'.format(addr))
                addressResult = cursor.fetchall()

                if int(len(addressResult)) == int(0):
                    cursor.execute('insert into Controllers (controllerhost,controllerport,controllername,trusted) values (\"{0}\",{1},\"{2}\",0);'.format(addr,port,name))
                    print("INFO - New controller added with: Address - {0}, Port - {1}, Name - {2}".format(addr,port,name))
                    print("INFO - The controller is configured but isn't trusted yet. Use help command for more information.")
                    conn.commit()

                    conn.close()

                elif len(addressResult) != int(0):
                    print("ERROR - A controller with {0} as it's address already exists.".format(addr))
                    conn.close()
            else:
                print("ERROR - A controller named {0} already exists.".format(name))
                conn.close()


    elif len(options) < 3:
        print("ERROR - Missing options! Expected '-controlleraddr','-controllerport' and '-controllername' for the config action. Use help command for more information.")


def controllerList(options,values):
    if len(options) == 1:
        if options[0] == "-controllername":
            conn = sqlite3.connect('database/apiConfiguration.db')
            cursor = conn.cursor()
            cursor.execute('select * from Controllers;')
            results = cursor.fetchall()

            if len(results) == 0:
                print("ERROR - No configured controllers. Use help command for more information.")
                return None

            if values[0] == "all":
                cursor.execute('select controllername,controllerhost,controllerport,trusted from Controllers;')
                results = cursor.fetchall()
                iterator = 1
                print("Configured controllers:")
                for result in results:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Trusted: {4}".format(iterator,result[0],result[1],result[2],result[3]))
                conn.close()
            else:
                cursor.execute('select controllername,controllerhost,controllerport from Controllers where controllername = \"{0}\"'.format(values[0]))
                result = cursor.fetchall()
                if len(result) == 0:
                    print("ERROR - No controller named {0} configured.".format(values[0]))
                    conn.close()
                else:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}".format(1,result[0][0],result[0][1],result[0][2]))
                    conn.close()
        else:
            print("ERROR - Missing option! Expect -controllername for the list action. Use help command for more information.")
    else:
        print("ERROR - More options than needed for ACTION list. Use help command for more information.")

def controllerTrust(options,value):
    if value[0] == "all":
        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()
        cursor.execute('select controllerhost,controllerport,controllername from Controllers;')
        controllersInfo = cursor.fetchall()
        cursor.execute('select description from ApiConfig where id = 1;')
        apiDescription = cursor.fetchall()
        cursor.execute('select registerkey from RegisterInfo where id=1;')
        apiRegister = cursor.fetchall()
        postData = {}
        postData["API Description"] = apiDescription[0][0]
        postData['API register key'] = apiRegister[0][0]

        for controller in controllersInfo:
            if int(controller[1]) == 443:
                try:
                    postRequest = requests.post("https://{0}/register".format(controller[0]),data=json.dumps(postData),timeout=20.0)
                except requests.exceptions.ConnectTimeout:
                    print("ERROR - Unable to connect to {0} at port {1}".format(controller[0],controller[1]))
                except requests.exceptions.ConnectionError:
                    print("ERROR - An error occured while trying to connect to {0} at port {1}".format(controller[0],controller[1]))
                except request.exceptions.SSLError:
                    print("ERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(controller[0],controller[1]))

                if postRequest.status_code == 200:
                    print("OK - Successfully registered the systems API into Controller: {0}".format(controller[2]))

            elif int(controller[1]) == 80:
                print("HTTP")
            else:
                print("Another port but still https")

    else:
        print("None")
def controllerUntrust(options,value):
    print(value)

# ------- Command function declaration --------#

def set(action,options,values):
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

    knowOptions = ["-apiaddr","-apiport","-apiinterface","-apidescription"]
    optionFunction = [apiAddr,apiPort,apiInterface,apiDescription]
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

def clear(action,options,values):
    os.system("clear")
    return None

def help(action,options,values):
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

def exit(action,options,values):
    return "exit"

def reset(action,options,values):
    response = input("WARN - You are about to reset the configurations of the API and the trusted Controllers. Are you sure [y/n]? ")
    if response == "y":

        conn = sqlite3.connect('database/apiConfiguration.db')
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS APIConfig;')
        cursor.execute('DROP TABLE IF EXISTS RegisterInfo;')
        cursor.execute('DROP TABLE IF EXISTS Controllers;')
        cursor.execute('CREATE TABLE IF NOT EXISTS APIConfig (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, host TEXT, port INTEGER, interface TEXT,description TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS RegisterInfo (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, registerkey TEXT NOT NULL);')
        cursor.execute('CREATE TABLE IF NOT EXISTS Controllers (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, controllerhost TEXT, controllerport INTEGER, controllername TEXT, trusted INTEGER);')
        cursor.execute('INSERT INTO APIConfig (host) values (123);')
        cursor.execute("UPDATE APIConfig SET host = \"{0}\",port = {1},interface = \"{2}\" WHERE id=1;".format("127.0.0.1",80,"lo","HostAPI"))
        cursor.execute('INSERT INTO RegisterInfo (registerkey) values ("None");')

        conn.commit()

        print("OK - API configuration has been successfully reset.")
        print("INFO - API current configuration - Address: 127.0.0.1, Port: 80, Interface: lo, Description: HostAPI")
        print("INFO - No configured/trusted Controllers.")

        conn.close()
    else:
        return None

def config(action,options,values):
    conn = sqlite3.connect('database/apiConfiguration.db')
    cursor = conn.cursor()

    cursor.execute('select * from APIConfig where id=1;')
    result = cursor.fetchall()
    global APIPort
    APIPort= result[0][1]
    global  APIAddr
    APIAddr = result[0][2]
    APIInterface = result[0][3]
    conn.close()

    return "Running config - Address: {0}, Port: {1}, Interface: {2}".format(APIPort,APIAddr,APIInterface)

def controller(action,options,values):
    knowActions = ["config","list","trust","untrust"]
    knowOptions = ["-controlleraddr","-controllerport","-controllername"]
    actionFunction = [controllerConfig,controllerList,controllerTrust,controllerUntrust]

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
                response = actionFunction[iterator](options,values)
            iterator += 1

    return None

# ------- Declaration of the interpreter core functions ---------

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
        if commandIntoArray[0] != "controller":
            if not "-" in elements and (iterator == 0):
                command.append(elements)
                action.append(None)
            elif elements[0] == "-":
                options.append(elements)
                optionIterator = iterator
            elif iterator == optionIterator+1:
                values.append(elements)
            iterator += 1

        elif commandIntoArray[0] == "controller":
            if iterator == 0:
                command.append("controller")
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

    commands = ["set","help","clear","exit","reset","config","controller"]
    commandFunc = [set,help,clear,exit,reset,config,controller]

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
        commandResponse = execute(arraySpecifics)
        if commandResponse == "exit":
            break
        elif commandResponse == None:
            continue
        else:
            print(commandResponse)


if __name__ == "__main__":
    interpreterMainLoop()