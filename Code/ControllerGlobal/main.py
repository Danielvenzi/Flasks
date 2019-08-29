from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import os
import sys
from functools import wraps
import controllerglobal

app=Flask(__name__)
app.config['JSON_AS_ASACII'] = False

controller = controllerglobal.ControllerGlobal()

@app.route("/success",methods=['GET'])
def succes():
    print("Funciona")
    return "success"

# Método para registro de uma nova controller local
@app.route('/register',methods=['POST'])
def register():
    data = request.get_json(force=True)
    controller = controllerglobal.ControllerGlobal()
    response = controller.register_cl(data)

    return jsonify(response)
    
# Método para registro de uma nova regra
@app.route('/entity',methods=['POST'])
def register_entites():
    data = request.get_json(force=True)
    controller = controllerglobal.ControllerGlobal()
    response = controller.register_entities(data)

    print(response)

    return jsonify(response)

# Método para registro de uma nova regra
@app.route('/rule',methods=['POST'])
def register_rule():
    data = request.get_json(force=True)
    controller = controllerglobal.ControllerGlobal()
    response = controller.register_rules(data)

    return jsonify(response)

# Método para listagem de regras
@app.route('/list',methods=['POST'])
def list_rule():
    data = request.get_json(force=True)
    response = controller.register_rules(data)

    return jsonify(response)

# Método para iteração com as regras associadas a um dispositivo
@app.route('/interaction',methods=['POST'])
def interact():
    data = request.get_json(force=True)
    response = controller.interaction(data)

    return jsonify(response)

if __name__ == "__main__":
    controller.initialize()
    app.run(debug=True, host="0.0.0.0", port=8080, use_reloader=True)
