import sqlite3
from controllerActionFunctions import *

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
                    cursor.execute('insert into Controllers (controllerhost,controllerport,controllername,controllerkey,trusted) values (\"{0}\",{1},\"{2}\","None",0);'.format(addr,port,name))
                    print("OK - New controller added with: Address - {0}, Port - {1}, Name - {2}".format(addr,port,name))
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
                    iterator += 1
                conn.close()
            else:
                cursor.execute('select controllername,controllerhost,controllerport,trusted from Controllers where controllername = \"{0}\"'.format(values[0]))
                result = cursor.fetchall()
                if len(result) == 0:
                    print("ERROR - No controller named {0} configured.".format(values[0]))
                    conn.close()
                else:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Trusted: {4}".format(1,result[0][0],result[0][1],result[0][2],result[0][3]))
                    conn.close()
        else:
            print("\bERROR - Missing option! Expect -controllername for the list action. Use help command for more information.")
    else:
        print("ERROR - More options than needed for ACTION list. Use help command for more information.")

def controllerTrust(options,value):
    if value[0] == "all":
        response = getInfoFromAll("trust")

        for controller in response["controllerInfo"]:
            trusted = checkIfTrusted(controller)
            if trusted == False:
                print("INFO - Initializating trust process on controller: {0}".format(controller[3]))
                if int(controller[2]) == 443:
                    trustHTTPS(controller,response["postData"])

                elif int(controller[2]) == 80:
                    trustHTTP(controller,response["postData"])

                else:
                    print("Another port but still https")
            elif trusted == True:
                print("INFO - Controller: {} is already trusted by the SystemAPI".format(controller[3]))

    else:
        response = getInfoFromController(value[0],"trust")

        for controller in response["controllerInfo"]:
            trusted = checkIfTrusted(controller)
            if trusted == False:
                print("INFO - Initializating trust process on controller: {0}".format(controller[3]))
                if int(controller[2]) == 443:
                    trustHTTPS(controller,response["postData"])

                elif int(controller[2]) == 80:
                    trustHTTP(controller,response["postData"])
                else:
                    print("Anotger port but still https")
            elif trusted == True:
                print("INFO - Controller {} is already trusted by the SystemAPI".format(controller[3]))

def controllerUntrust(options,value):
    if value[0] == "all":
        response = getInfoFromAll("untrust")
        for controller in response["controllerInfo"]:
            untrusted = checkIfUntrusted(controller)
            if untrusted == False:
                print("INFO - Initializing untrust process on controller: {}".format(controller[3]))
                if int(controller[2]) == 443:
                    untrustHTTPS(controller,response["postData"])

                elif int(controller[2]) == 80:
                    untrustHTTP(controller,response["postData"])
                else:
                    print("Another port but still https")
            elif untrusted == True:
                print("INFO - Controller {} is already untruted by the SystemAPI".format(controller[3]))
    else:
        response = getInfoFromController(value[0],"untrust")
        for controller in response["controllerInfo"]:
            untrusted = checkIfUntrusted(controller)
            if untrusted == False:
                print("INFO - Initializing untrust process on controller: {}".format(controller[3]))
                if int(controller[2]) == 443:
                    untrustHTTPS(controller,response["postData"])

                elif int(controller[2]) == 80:
                    untrustHTTP(controller,response["postData"])
                else:
                    print("Another port but still https")
            elif untrusted == True:
                print("INFO - Controller {} is already untrusted by the SystemAPI".format(controller[3]))
