import sqlite3
import json
import requests

# ------- controllers trust action function declaration ---------------------------#

def getInfoFromAll(action):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    cursor.execute('select id,apihost,apiport,apiname from SystemAPI;')
    controllersInfo = cursor.fetchall()
    if action == "trust":
        cursor.execute('select description,port from ControllerConfig where id = 1;')
        apiDescription = cursor.fetchall()
        cursor.execute('select registerkey from UntrustInfo where id=1;')
        apiRegister = cursor.fetchall()
        conn.close()
        postData = {}
        postData["API Description"] = apiDescription[0][0]
        postData["API Port"] = apiDescription[0][1]
        postData['API Register Key'] = apiRegister[0][0]
        postData["Type"] = "local"

        returnDict = {}
        returnDict["postData"] = postData
        returnDict["controllerInfo"] = controllersInfo
        return returnDict
    elif action == "untrust":
        cursor.execute('select description from ControllerConfig where id = 1;')
        apiDescription = cursor.fetchall()
        cursor.execute('select apikey from SystemAPI;')
        controllerKey = cursor.fetchall()
        conn.close()
        postData = {}
        postData["API Description"] = apiDescription[0][0]
        postData["Controller Key"] = controllerKey

        returnDict = {}
        returnDict["postData"] = postData
        returnDict["controllerInfo"] = controllersInfo
        return returnDict


def getInfoFromController(controllerName,action):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()
    cursor.execute('select id,apihost,apiport,apiname from SystemAPI where apiname = \"{0}\";'.format(controllerName))
    controllerInfo = cursor.fetchall()
    if action == "trust":
        cursor.execute('select description,port from ControllerConfig where id = 1;')
        apiDescription = cursor.fetchall()
        cursor.execute('select registerkey from UntrustInfo where id = 1;')
        apiRegister = cursor.fetchall()
        conn.close()
        postData = {}
        postData["API Description"] = apiDescription[0][0]
        postData["API Port"] = apiDescription[0][1]
        postData["API Register Key"] = apiRegister[0][0]
        postData["Type"] = "local"

        returnDict = {}
        returnDict["postData"] = postData
        returnDict["controllerInfo"] = controllerInfo
        return returnDict

    elif action == "untrust":
        cursor.execute('select description from ControllerConfig where id = 1;')
        apiDescription = cursor.fetchall()
        cursor.execute('select registerkey from UntrustInfo where id = 1;')
        apiRegister = cursor.fetchall()
        cursor.execute('select apikey from SystemAPI where apiname = \"{0}\";'.format(controllerName))
        controllerKey = cursor.fetchall()
        conn.close()
        postData = {}
        postData["API Description"] = apiDescription[0][0]
        postData["Controller Key"] = controllerKey[0][0]
        postData["API Register Key"] = apiRegister[0][0]

        returnDict = {}
        returnDict["postData"] = postData
        returnDict["controllerInfo"] = controllerInfo
        return returnDict

def checkIfTrusted(controller):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select known from SystemAPI where apiname = \"{0}\";'.format(controller[3]))
    response = cursor.fetchall()
    conn.close()
    if response[0][0] == 0:
        return False
    elif response[0][0] == 1:
        return True

def checkIfUntrusted(controller):
    conn = sqlite3.connect('database/apiConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select known from SystemAPI where apiname = \"{0}\";'.format(controller[3]))
    reponse = cursor.fetchall()
    conn.close()
    if reponse[0][0] == 1:
        return False
    elif reponse[0][0] == 0:
        return True

def trustHTTPS(controller,postData):
    try:
        print("\tINFO - Attempting to connect to {0} at port {1}...".format(controller[1], controller[2]))
        postRequest = requests.post("https://{0}/register".format(controller[1]), data=json.dumps(postData),timeout=15.0)
        postResponse = postRequest.json()
        if postRequest.status_code == 200:
            status = postResponse["Status"]
            if status == 200:
                try:
                    conn = sqlite3.connect("database/controllerConfiguration.db")
                    cursor = conn.cursor()
                    cursor.execute('update SystemAPI set known = 1 where id = {0};'.format(controller[0]))
                    cursor.execute('update SystemAPI set apikey = \"{}\" where id = {};'.format(postResponse["Controller Key"],controller[0]))
                    conn.commit()
                    conn.close()
                    print("\tOK - Successfully registered the system API into global Controller: {0}".format(controller[3]))
                    print("\tINFO - Global Controller: {0} is now trusted by local controller".format(controller[3]))
                except sqlite3.OperationalError as err:
                    print("\tERROR - {0}".format(err))
            elif status == 400:
                print("\tERROR - Internal controller error: {0}".format(postResponse["Response"]))
            else:
                print("\tERROR - Internal controller error")
        else:
            print("\tERROR - Trust request came back with status {0}".format(postRequest.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(controller[1], controller[2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))


def trustHTTP(controller,postData):
    try:
        print("\tINFO - Attempting to connect to {0} at port {1}...".format(controller[1], controller[2]))
        postRequest = requests.post("http://{0}/register".format(controller[1]), data=json.dumps(postData),timeout=15.0)
        postResponse = postRequest.json()
        if postRequest.status_code == 200:
            status = postResponse["Status"]
            if (status == 200):
                try:
                    conn = sqlite3.connect("database/controllerConfiguration.db")
                    cursor = conn.cursor()
                    cursor.execute('update SystemAPI set known = 1 where id = {0};'.format(controller[0]))
                    cursor.execute('update SystemAPI set apikey = \"{0}\" where id = {1};'.format(postResponse["Controller Key"],controller[0]))
                    conn.commit()
                    conn.close()
                    print("\tOK - Successfully registered the system API into global Controller: {0}".format(controller[3]))
                    print("\t INFO - Global Controller: {0} is now trusted by the local controller.".format(controller[3]))
                except sqlite3.OperationalError as err:
                    print("\tERROR - {0}".format(err))
            elif status == 400:
                print("\tERROR - Internal controller error: {0}".format(postResponse["Response"]))
            else:
                print("\tERROR - A error has occured.")
        else:
            print("\tERROR - Trust process came back with status {0}".format(postRequest.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(controller[1], controller[2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))


def trustANY(controller):
    print("Work in progress..")

def untrustHTTPS(controller,postData):
    try:
        print("\tINFO - Attempting to connect to {0} at port {1}...".format(controller[1], controller[2]))
        postRequest = requests.post("https://{0}/unregister".format(controller[1]), data=json.dumps(postData),timeout=15.0)
        postResponse = postRequest.json()
        if postRequest.status_code == 200:
            status = postResponse["Status"]
            if status == 200:
                try:
                    conn = sqlite3.connect("database/controllerConfiguration.db")
                    cursor = conn.cursor()
                    cursor.execute('update SystemAPI set known = 0 where id = {0};'.format(controller[0]))
                    conn.commit()
                    conn.close()
                    print("\tOK - Successfully unregistered the local controller from the Global Controller: {0}".format(controller[3]))
                    print("\tINFO - Global Controller: {0} is now untrusted by the local controller".format(controller[3]))
                except sqlite3.OperationalError as err:
                    print("\tERROR - {0}".format(err))
            elif status == 400:
                print("\tERROR - Internal cotroller error: {0}".format(postResponse["Response"]))
            else:
                print("\tERROR - A error has occured")
        else:
            print("\tERROR - Untrust request came back with message: {0}, and status code: {1}".format(postRequest.text,postRequest.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(controller[1], controller[2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))


def untrustHTTP(controller,postData):
    try:
        print("\tINFO - Attempting to connect to {0} at port {1}...".format(controller[1], controller[2]))
        postRequest = requests.post("http://{0}/unregister".format(controller[1]), data=json.dumps(postData),timeout=15.0)
        postResponse = postRequest.json()
        if postRequest.status_code == 200:
            status = postResponse["Status"]
            if status == 200:
                try:
                    conn = sqlite3.connect("database/controllerConfiguration.db")
                    cursor = conn.cursor()
                    cursor.execute('update SystemAPI set known = 0 where id = {0};'.format(controller[0]))
                    conn.commit()
                    conn.close()
                    print("\tOK - Successfully unregistered the local controller from the Global Controller: {0}".format(controller[3]))
                    print("\tINFO - Global Controller: {0} is now untrusted by the local controller".format(controller[3]))

                except sqlite3.OperationalError as err:
                    print("\tERROR - {0}".format(err))
            elif status == 400:
                print("\tERROR - Internal controller error: {0}".format(postResponse["Response"]))
            else:
                print("\tERROR - A error has occured.")
        else:
            print("\tERROR - Untrust request came back with message: {0}, and status code: {1}".format(postRequest.text,postRequest.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(controller[1], controller[2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(controller[1],controller[2]))

def untrustANY(controller,postData):
    print("Work in progress...")