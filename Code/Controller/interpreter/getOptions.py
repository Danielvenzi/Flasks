import requests
import json
import sqlite3

# -------- Declaration of the get command options functions ------ #

def getCPU(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost,apikey,apiport from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    dict = {}
    dict["API Register Key"] = result[0][1]

    try:
        print("INFO - Attempting to connect to {0} at port {1}...".format(result[0][0],result[0][2]))
        requestGet = requests.get('http://{0}/api/system/cpu'.format(result[0][0]),data=json.dumps(dict),timeout=15.0)
        if requestGet.status_code == 200:
            reponseJSON = requestGet.json()
            print(reponseJSON)
        else:
            print("\tERROR - The SystemAPI request returned an error with status code: {0}".format(requestGet.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(result[0][0], result[0][2]))


def getMem(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost,apikey,apiport from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    dict = {}
    dict["API Register Key"] = result[0][1]

    try:
        print("INFO - Attempting to connect to {0} at port {1}...".format(result[0][0], result[0][2]))
        requestGet = requests.get('http://{0}/api/system/mem'.format(result[0][0]), data=json.dumps(dict),timeout=15.0)
        if requestGet.status_code == 200:
            reponseJSON = requestGet.json()
            print(reponseJSON)
        else:
            print("\tERROR - The SystemAPI request returned an error with status code: {0}".format(requestGet.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(result[0][0],result[0][2]))

def getDisk(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost,apikey,apiport from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    dict = {}
    dict["API Register Key"] = result[0][1]

    try:
        print("INFO - Attempting to connect to {0} at port {1}...".format(result[0][0], result[0][2]))
        requestGet = requests.get('http://{0}/api/system/disk/all/mb'.format(result[0][0]), data=json.dumps(dict),timeout=15.0)
        if requestGet.status_code == 200:
            reponseJSON = requestGet.json()
            print(reponseJSON)
        else:
            print("\tERROR - The SystemAPI request returned an error with status code: {0}".format(requestGet.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(result[0][0],result[0][2]))

def getPort(apiName):
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('select apihost,apikey,apiport from SystemAPI where apiname = \"{0}\";'.format(apiName))
    result = cursor.fetchall()
    conn.close()

    dict = {}
    dict["API Register Key"] = result[0][1]

    try:
        print("INFO - Attempting to connect to {0} at port {1}...".format(result[0][0], result[0][2]))
        requestGet = requests.get('http://{0}/api/system/port/all'.format(result[0][0]), data=json.dumps(dict),timeout=15.0)
        if requestGet.status_code == 200:
            reponseJSON = requestGet.json()
            print(reponseJSON)
        else:
            print("\tERROR - The SystemAPI request returned an error with status code: {0}".format(requestGet.status_code))
    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(result[0][0], result[0][2]))
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(result[0][0],result[0][2]))
