from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import os
import sys
from functools import wraps
import requests
import json
import keep_rule

app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

@app.route('/rule',methods=['POST'])
def interact_rule():
    data = request.get_json(force=True)
    controller_name = data["ControllerName"]
    
    conn = sqlite3.connect('database/controllerConfiguration.db')
    cursor = conn.cursor()

    cursor.execute('select host,port from LocalController where controllername = {};'.format(controller_name))
    result = cursor.fetchall()
    conn.close()

    host = result[0][0]
    port = result[0][1]

    try:
        postRequest = requests.post("http://{0}:{1}/create_rule".format(host,port), data=json.dumps(data),timeout=15.0)
        postResponse = postRequest.json()
        if postRequest.status_code == 200:
            status = postResponse["Status"]
            if (status == 200):
                conn = sqlite3.connect('database/controllerConfiguration.db')
                cursor = conn.cursor()

                if data['Type'] == "Iptables":
                    cursor.execute('update ConfiguredRulesIptables set status = 1 where;')
                elif data['Type'] == "NET":
                    cursor.execute('update ConfiguredRulesNET set status = 1 where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(data["name"],data["premise"],data["action"],data["test"]))
                elif data['Type'] == "HIDS":
                    cursor.execute('update ConfiguredRulesNET set status = 1 where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(data["name"],data["premise"],data["action"],data["test"]))
            
                conn.commit()
                conn.close()

            elif (status == 400):
                print("ERROR - The configuration of a rule came back with status of {}}".format(status))
            else:
                print("ERROR - The Configuration of a rule came back with a status of {}".format(status))
        
        else:
            keepPID = os.fork()
            if keepPID == 0:
                 keep_rule.keep_trying(data,host,port)
            else:
                print("ERROR - Couldnt apply the rule to the controller, starting a keep_rule process")

    except requests.exceptions.ConnectTimeout:
        print("\tERROR - Unable to connect to {0} at port {1}".format(host,port))
        keepPID = os.fork()
        if keepPID == 0:
            keep_rule.keep_trying(data,host,port)
        else:
            print("ERROR - Couldnt apply the rule to the controller, starting a keep_rule process")
    except requests.exceptions.ConnectionError:
        print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(host,port))
        keepPID = os.fork()
        if keepPID == 0:
            keep_rule.keep_trying(data,host,port)
        else:
            print("ERROR - Couldnt apply the rule to the controller, starting a keep_rule process")
    except requests.exceptions.SSLError:
        print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(host,port))
        keepPID = os.fork()
        if keepPID == 0:
            keep_rule.keep_trying(data,host,port)
        else:
            print("ERROR - Couldnt apply the rule to the controller, starting a keep_rule process")

# Método pelo qual a controller global avisa o serviço de regras para repassar uma nova regra cadastrada
# @app.route('/apply_rule',methods=['POST'])
# def apply_create():
#     data = request.get_json(force=True)
#     controller_name = data["ControllerName"]
    
#     conn = sqlite3.connect('database/controllerConfiguration.db')
#     cursor = conn.cursor()

#     cursor.execute('select host,port from LocalController where controllername = {};'.format(controller_name))
#     result = cursor.fetchall()
#     conn.close()

#     host = result[0][0]
#     port = result[0][1]

#     # Evidencia o que o Controller Local deveria fazer com a regra
#     data["Action"] = "Create"

#     try:
#         postRequest = requests.post("https://{0}:{1}/create_rule".format(host,port), data=json.dumps(data),timeout=15.0)
#     except requests.exceptions.ConnectTimeout:
#         print("\tERROR - Unable to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.ConnectionError:
#         print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.SSLError:
#         print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(host,port))


# Método pelo qual a controller global aviso o serviço de regras para pausar uma regra cadastrada
# @app.route('/pause_rule',methods=['POST'])
# def pause_rule():
#     data = request.get_json(force=True)
#     controller_name = data["ControllerName"]

#     conn = sqlite3.connect('database/controllerConfiguration.db')
#     cursor = conn.cursor()

#     cursor.execute('select host,port from LocalController where controllername = {};'.format(controller_name))
#     result = cursor.fetchall()
#     conn.close()

#     host = result[0][0]
#     port = result[0][1]

#     # Evidencia o que o Controller Local deveria fazer com a regra
#     data["Action"] = "Pause"

#     try:
#         postRequest = requests.post("https://{0}:{1}/pause_rule".format(host,port), data=json.dumps(data),timeout=15.0)
#     except requests.exceptions.ConnectTimeout:
#         print("\tERROR - Unable to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.ConnectionError:
#         print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.SSLError:
#         print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(host,port))


# Método pelo qual o controller global aviso o serviço de regras para deletar uma regra cadastrada
# @app.route('/delete_rule',methods=['POST'])
# def delete_rule():
#     data = request.get_json(force=True)
#     controller_name = data["ControllerName"]

#     conn = sqlite3.connect('database/controllerConfiguration.db')
#     cursor = conn.cursor()

#     cursor.execute('select host,port from LocalController where controllername = {};'.format(controller_name))
#     result = cursor.fetchall()
#     conn.close()

#     host = result[0][0]
#     port = result[0][1]

#     # Evidencia o que o Controller Local deveria fazer com a regra
#     data["Action"] = "Delete"

#     try:
#         postRequest = requests.post("https://{0}:{1}/pause_rule".format(host,port), data=json.dumps(data),timeout=15.0)
#     except requests.exceptions.ConnectTimeout:
#         print("\tERROR - Unable to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.ConnectionError:
#         print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(host,port))
#     except requests.exceptions.SSLError:
#         print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(host,port))


def initialize():
    try:
        print("STATUS - Inicializou o processo de aplicação de regras")
        app.run(debug=True, host="127.0.0.1", port=5050, use_reloader=False)
    except OSError:
        print("ERROR - Inicializou o processo em uma porta que já está sendo utilizado (8080)")

if __name__ == "__main__":
    initialize()
