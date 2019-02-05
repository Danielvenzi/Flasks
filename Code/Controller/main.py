from flask import Flask, request, jsonify, redirect, url_for
import sqlite3
import sys
import controllerInterpreter
import json


app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

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
def unregisterApi():
    data = request.data
    print("Ddados do post: {}, Endereço de origem: {}".format(data,request.remote_addr))

    return "Success"

if __name__ == "__main__":
    if sys.argv[1] == "run":
        app.run(debug=True,host="0.0.0.0", port=80)
    elif sys.argv[1] == "config":
        controllerInterpreter.interpreterMainLoop()
    else:
        print("ERROR - Invalid command line option...")