import sys
sys.path.insert(0, './interpreter')
sys.path.insert(0, './parallel')
from interpreterMain import *
from snortListener import *
from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import sys
#import controllerInterpreter
import json
from functools import wraps
import os
import time

app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

# -------------- Authentication function decorators ------------ #

def requestAuth(func):
    @wraps(func)
    def funcWrapper():
        data = request.get_json(force=True)
        apiAddr = request.remote_addr
        apiKey = data["API Register Key"]
        controllerKey = data["Controller Key"]

        conn = sqlite3.connect("database/controllerConfiguration.db")
        cursor = conn.cursor()
        cursor.execute('select apikey from SystemAPI where apihost  = \"{0}\";'.format(apiAddr))
        result = cursor.fetchall()
        cursor.execute('select registerkey from UntrustInfo;')
        resultkey = cursor.fetchall()
        if result[0][0] != apiKey:
            return "ERROR - Authentication with the controller failed",400
        elif result[0][0] == apiKey:
            if resultkey[0][0] == controllerKey:
                return func()
            elif resultkey[0][0] != controllerKey:
                return "Error - Authentication with the controller failed",400
    return funcWrapper


def requestFormat(requestSituation):
    def decorator(func):
        @wraps(func)
        def funcWrapper(*args,**kwargs):
            data = request.get_json(force=True)
            dataKeys = data.keys()

            allNecessary = []
            trustNecessaryFields = ["API Description", "API Port", "API Register Key", "Type"]
            untrustNecessaryFields = ["API Description", "Controller Key","API Register Key"]
            generalNecessaryFields = ["API Register Key"]
            allNecessary.extend((generalNecessaryFields,untrustNecessaryFields,trustNecessaryFields))

            knownRequestSituation = ["general","untrust","trust"]
            for known in knownRequestSituation:
                if known == requestSituation:
                    knownIndex = knownRequestSituation.index(known)
                    necessaryFields = allNecessary[knownIndex]

                    if len(dataKeys) != len(necessaryFields):
                        return "ERROR - Not all the necessary fields for the specific situation transaction were passed.",400
                    else:
                        for key in dataKeys:
                            if not key in necessaryFields:
                                return "ERROR - Incorrect request format for the specific situation",400
                            else:
                                continue
                    break
            return func()
        return funcWrapper
    return decorator

# --------------- Flask route function declaration ------------- #

@app.route('/register',methods=['POST'])
@requestFormat("trust")
def registApi():
    data = request.get_json(force=True)
    apiDescription = data["API Description"]
    apiKey = data["API Register Key"]
    apiPort = data["API Port"]
    apiType = data["Type"]
    apiAddr = request.remote_addr

    #if (apiType != "snortapi") or (apiType != "systemapi"):
    #    return jsonify({"Response":"Undefined API Type","Status":400})

    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute("insert into SystemAPI (apihost,apiport,apiname,known,apikey,apitype) values (\"{0}\",{1},\"{2}\",1,\"{3}\",\"{4}\");".format(apiAddr,int(apiPort),apiDescription,apiKey,apiType))
    conn.commit()
    cursor.execute('select description from ControllerConfig where id=1;')
    resultDesc = cursor.fetchall()
    cursor.execute('select registerkey from UntrustInfo where id = 1;')
    resultKey = cursor.fetchall()
    conn.close()

    if apiType == "snortapi":
        os.system(r"iptables -t filter -A INPUT -p udp -s {0} --dport 514 -j ACCEPT".format(apiAddr))
    elif apiType == "systemapi":
        os.system(r"iptables -t filter -A INPUT -p tcp -s {0} --dport 80 -j ACCEPT".format(apiAddr))
        os.system(r"iptables -t filter -A INPUT -p tcp -s {0} --dport 443 -j ACCEPT".format(apiAddr))

    return jsonify({"Controller Key": resultKey[0][0],"Controller Description": resultDesc[0][0],"Status":"Success"})


@app.route('/unregister',methods=['POST'])
@requestFormat("untrust")
@requestAuth
def unregisterApi():
    data = request.get_json(force=True)
    apiKey = data["API Register Key"]
    apiAddr = request.remote_addr

    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute('delete from SystemAPI where apikey = \"{}\";'.format(apiKey))
    conn.commit()
    conn.close()

    os.system(r"iptables -t filter -D INPUT -p udp -s {0} --dport 514 -j ACCEPT &> /dev/null".format(apiAddr))
    os.system(r"iptables -t filter -D INPUT -p tcp -s {0} --dport 80 -j ACCEPT &> /dev/null".format(apiAddr))
    os.system(r"iptables -t filter -D INPUT -p tcp -s {0} --dport 443 -j ACCEPT &> /dev/null".format(apiAddr))


    return jsonify({"Status":"Success"})

if __name__ == "__main__":
    if sys.argv[1] == "run":
        snortListenerPID = os.fork()
        if snortListenerPID == 0:
            time.sleep(1)
            print("Info - Iniatizaling Syslog server...")
            mainSyslogServer()
        else:
            print("Info - Initializing Controller Restfull API")
            app.run(debug=True,host="0.0.0.0", port=80, use_reloader=False)

    elif sys.argv[1] == "config":
        #controllerInterpreter.interpreterMainLoop()
        interpreterMainLoop()
    else:
        print("ERROR - Invalid command line option...")