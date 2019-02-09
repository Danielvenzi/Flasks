from flask import Flask, request, jsonify, redirect, url_for
import sys
sys.path.insert(0, './classes')
from system import *
import interpreter
from functools import wraps
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


#@app.route('/')
#def hello_world():
#    return redirect(url_for('apiStandartHandler'))


#@app.route('/api', methods=['GET'])
#def apiStandartHandler():
#    if request.method() == "GET":
#        # Chamar a classe de informações gerais do sistema
#        print("123")
#    return "This is a first attemp!"

# -------------- Authentication function decorators ------------ #

def requestAuth(func):
    @wraps(func)
    def funcWrapper():
        data = request.get_json(force=True)
        apiAddr = request.remote_addr
        apiKey = data["API Register Key"]

        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()
        cursor.execute('select registerkey from RegisterInfo ;'.format(apiAddr))
        result = cursor.fetchall()
        if result[0][0] != apiKey:
            return "ERROR - Authentication with the controller failed",400
        elif result[0][0] == apiKey:
            return func()
    return funcWrapper

def requestFormat(requestSituation):
    def decorator(func):
        @wraps(func)
        def funcWrapper(*args,**kwargs):
            data = request.get_json(force=True)
            print(data)
            dataKeys = data.keys()
            print(dataKeys)

            allNecessary = []
            trustNecessaryFields = ["API Description", "API Port", "API Register Key"]
            untrustNecessaryFields = ["API Description", "Controller Key"]
            generalNecessaryFields = ["API Register Key"]
            allNecessary.extend((generalNecessaryFields,untrustNecessaryFields,trustNecessaryFields))

            knownRequestSituation = ["general","untrust","trust"]
            for known in knownRequestSituation:
                if known == requestSituation:
                    knownIndex = knownRequestSituation.index(known)
                    necessaryFields = allNecessary[knownIndex]
                    print(necessaryFields)

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

#-------------------- Rotas para API sobre métricas de sistema --------------------#

# Caminho da API onde o Controller coletainformações acerca da utiliadade de disco na unidade que deseja
#
# disk_name = Nome do disco que deseja ser análisado, exemplo: /dev/sda1 seria +dev+sda1. Caso queira listar
# de todos os discos/partições presentes no sistema us disk_name = all. OBS: Para que a API funcione corretamente
# o disco deve estar montado no sistema de arquivos.
#
# Tal caminho retorna um JSON contendo como Response um array de dicts, cada array carrega informações sobre um
# disco específico no sistema
@app.route('/api/system/disk/<disk_name>/<byte_unity>')
@requestFormat("general")
@requestAuth
def apiDisk(disk_name,byte_unity):
    disk_name = disk_name.replace("+","/")
    instanceDisk = System("DISK")
    if disk_name == "all":
        responseDisk = instanceDisk.disk(disk_name,byte_unity)
        return jsonify({"Response":responseDisk,"Status":"Success"})

    elif disk_name is not "all":
        diskExists = os.popen(r"df -h | grep -P '{0} ' 1> /dev/null 2> /dev/null 2> /dev/null; echo $?".format(disk_name)).read()
        diskExists = diskExists.strip("\n")
        if diskExists == "0":
            responseDisk = instanceDisk.disk(disk_name,byte_unity)

            return jsonify({"Response":responseDisk,"Status":"Success"})
        else:
            return jsonify({"Response": "Disco não existe ou não está montado no sistema.","Status":"Error"})


# -------------------------------------------------------------------------------------------------------------------------
# Caminho da API onde o Controller coleta as informações sobre o percentual utilizado de todos os cores existentes na CPU.
#
# Tal caminho retorna um JSON cotendo como Response um dicionário ondes as chaves representam os núcleos da CPU
@app.route('/api/system/cpu')
@requestFormat("general")
@requestAuth
def apiCPU():
    instance = System("CPU")
    responseCPU = instance.cpu()
    return jsonify({"Response": responseCPU,"Status":"Success"})

# -------------------------------------------------------------------------------------------------------------------
# Caminho da API onde o Controller coleta as informações sobre a utilização de memória com as mais diversas métricas
#
# Tal caminho retorna um JSON contendo como Response um dicionário onde as chaves contém métricas acerca da utilização
# de memória no sistema
@app.route('/api/system/mem')
@requestFormat("general")
@requestAuth
def apiMem():
    instance = System("MEM")
    responseMem = instance.gather()
    return jsonify({"Response": responseMem,"Status":"Success"})


# ----------------------------------------------------------------------------------------------------------------------
# Caminho da API onde o Controller coleta informações sobre as portas abertas no sistema e a quais serviços tais portas
# estão associadas.
#
# protocol = Protocolo que as portas abertas estarão utilizando. - Valores: tcp , udp e all. Se quiser listar tanto as
# portas TCP quando as UDP utilize protocol = all.
#
# Tal caminho retorna um JSON contendo como Response um dicionário cujas chaves representam o protocolo, os valores dessa
# chave são um array de dicionários contendo informações sobre os programas e suas portas.
@app.route('/api/system/port/<protocol>')
@requestFormat("general")
@requestAuth
def apiPort(protocol):
    if not protocol in ["all","tcp","udp"]:
        return jsonify({"Response":"Protocolo inválido."})
    else:
        instance = System("PORT")
        responsePort = instance.ports(protocol)
        return jsonify({"Response": responsePort,"Status":"Success"})


#-------------------- Rotas para API sobre configuração da iptables --------------------#

@app.route('/api/iptables/create/<table>/<chain>/')
def apiIptablesCreate():
    return "Work in progress"

@app.route('/api/iptables/list/<table>/<chain>/')
def apiIptablesList():
    return "Work in progress"

@app.route('/api/iptables/delete/<table>/<chain>/')
def apiIptablesDelete():
    return "Work in progress"

@app.route('/api/system/port/<port_number>')
def apiAuthentication(port_number):
    return port_number


if __name__ == "__main__":
    if sys.argv[1] == "run":
        conn = interpreter.sqlite3.connect('database/apiConfiguration.db')
        cursor = conn.cursor()

        cursor.execute('select * from APIConfig where id=1;')
        result = cursor.fetchall()

        host = str(result[0][1])
        port = int(result[0][2])

        conn.close()

        app.run(debug=True, host=host, port=port)

    elif sys.argv[1] == "config":
        interpreter.interpreterMainLoop()