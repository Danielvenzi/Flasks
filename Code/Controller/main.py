from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import sys
import controllerInterpreter
import json


app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

def requestAuth(func):
    def funcWrapper():
        data = request.get_json(force=True)
        apiAddr = request.remote_addr
        apiKey = data["API Register Key"]

        conn = sqlite3.connect("database/controllerConfiguration.db")
        cursor = conn.cursor()
        cursor.execute('select apikey from SystemAPI where apihost  = \"{0}\";'.format(apiAddr))
        result = cursor.fetchall()
        if result[0][0] != apiKey:
            return "ERROR - Authentication with the controller failed",400
        elif result[0][0] == apiKey:
            return func()
    return funcWrapper

@app.route('/register',methods=['POST'])
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

    return jsonify({"Controller Key": resultKey[0][0],"Controller Description": resultDesc[0][0]})

@app.route('/unregister',methods=['POST'])
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

    return jsonify({"Response":"Success"})

if __name__ == "__main__":
    if sys.argv[1] == "run":
        app.run(debug=True,host="0.0.0.0", port=80)
    elif sys.argv[1] == "config":
        controllerInterpreter.interpreterMainLoop()
    else:
        print("ERROR - Invalid command line option...")