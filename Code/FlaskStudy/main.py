from flask import Flask, request, jsonify, redirect, url_for
import sys
sys.path.insert(0, './classes')
from system import *
app = Flask(__name__)


#@app.route('/')
#def hello_world():
#    return redirect(url_for('apiStandartHandler'))


#@app.route('/api', methods=['GET'])
#def apiStandartHandler():
#    if request.method() == "GET":
#        # Chamar a classe de informações gerais do sistema
#        print("123")
#    return "This is a first attemp!"

@app.route('/api/disk')
def apiDisk():
    instance = System("DISK")
    responseDisk = instance.gather()
    return jsonify({"Response": responseDisk})


@app.route('/api/cpu')
def apiCPU():
    instance = System("CPU")
    responseCPU = instance.gather()
    return jsonify({"Response": responseCPU})


@app.route('/api/mem')
def apiMem():
    instance = System("MEM")
    responseMem = instance.gather()
    return jsonify({"Response": responseMem})


@app.route('/api/port')
def apiPort():
    instance = System("PORT")
    responsePort = instance.gather()
    return jsonify({"Response": responsePort})

def apiAuthentication():
    return "Working"



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)