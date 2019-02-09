from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import sys
import controllerInterpreter
import json
from functools import wraps

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
            trustNecessaryFields = ["API Description", "API Port", "API Register Key"]
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
    apiAddr = request.remote_addr
    #print("Dados do post: {}, Endereço de origem: {}".format(data,request.remote_addr))

    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()
    cursor.execute("insert into SystemAPI (apihost,apiport,apiname,known,apikey) values (\"{0}\",{1},\"{2}\",1,\"{3}\");".format(apiAddr,int(apiPort),apiDescription,apiKey))
    conn.commit()
    cursor.execute('select description from ControllerConfig where id=1;')
    resultDesc = cursor.fetchall()
    cursor.execute('select registerkey from UntrustInfo where id = 1;')
    resultKey = cursor.fetchall()
    conn.close()

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

    return jsonify({"Status":"Success"})

if __name__ == "__main__":
    if sys.argv[1] == "run":
        app.run(debug=True,host="0.0.0.0", port=80)
    elif sys.argv[1] == "config":
        controllerInterpreter.interpreterMainLoop()
    else:
        print("ERROR - Invalid command line option...")