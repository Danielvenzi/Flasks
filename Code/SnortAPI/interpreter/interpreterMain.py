import os
from commands import *
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
        #print(arraySpecifics)
        commandResponse = execute(arraySpecifics)
        if commandResponse == "exit":
            break
        elif commandResponse == None:
            continue
        else:
            print(commandResponse)
