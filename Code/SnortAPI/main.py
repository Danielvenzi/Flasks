from flask import Flask, request, jsonify, redirect, url_for
import sys
sys.path.insert(0, './classes')
sys.path.insert(0,'./interpreter')
sys.path.insert(0,'./ruleParser')
from snort import *
from interpreterMain import *
from functools import wraps
from snortparser import Parser
import sqlite3
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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
            return jsonify({"Reponse":"ERROR - Authentication with the SystemAPI failed","Status":"400"}),400
        elif result[0][0] == apiKey:
            return func()
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
            iptablesNecessaryFields = ["API Register Key","Table","Action","Chain","Rule"]
            snortNecessaryFields = ["API Register Key","Rule","Action"]
            allNecessary.extend((generalNecessaryFields,untrustNecessaryFields,trustNecessaryFields,iptablesNecessaryFields,snortNecessaryFields))

            knownRequestSituation = ["general","untrust","trust","iptables","snort"]
            for known in knownRequestSituation:
                if known == requestSituation:
                    knownIndex = knownRequestSituation.index(known)
                    necessaryFields = allNecessary[knownIndex]

                    if len(dataKeys) != len(necessaryFields):
                        return jsonify({"Response":"ERROR - Not all the necessary fields for the specific situation transaction were passed.","Status":"400"}),400
                    else:
                        for key in dataKeys:
                            if not key in necessaryFields:
                                return jsonify({"Response":"ERROR - Incorrect request format for the specific situation","Status":"400"}),400
                            else:
                                continue
                    break
            return func()
        return funcWrapper
    return decorator

# ---------------------- Rotas para API do Snort ------------------------------

@app.route("/snort", methods=['POST'])
#@requestFormat("snort")
#@requestAuth
def snort():
    try:
        data = request.get_json(force=True)
        address = request.remote_addr
        rule = data["Rule"]
        # Creates a instance of the Parser class, the Parser class is responsible for the rules analysis
        parsed = Parser(rule)

        # Creates a instance of the snortClass class, this class is responsible for the operations regardind the given rule
        snortInstance = snortClass(data["Rule"],address,data["Action"])
        result = snortInstance.execute()

        return jsonify(result)

    except ValueError as err:
        err = str(err)
        return jsonify({"Respose":err,"Status":400}),400
    except SystemError as err:
        err = str(err)
        return jsonify({"Respnse":err,"Status":400}),400
    except SyntaxError as err:
        err = str(err)
        return jsonify({"Response":err,"Status":400}),400

if __name__ == "__main__":
    try:
        if sys.argv[1] == "run":
            try:
                conn = sqlite3.connect('database/apiConfiguration.db')
                cursor = conn.cursor()

                cursor.execute('select * from APIConfig where id=1;')
                result = cursor.fetchall()

                host = str(result[0][1])
                port = int(result[0][2])

                conn.close()
            except sqlite3.OperationalError as err:
                print("ERROR - An error has occured when accessing the database: {0}".format(err))

            try:
                app.run(debug=True, host=host, port=port, use_reloader=False)
            except OSError as err:
                print("ERROR - An error has occurred when initializing the SnortAPI: {0}".format(err))
            except KeyboardInterrupt as err:
                print("INFO - Finishing...")

        elif sys.argv[1] == "config":
            interpreterMainLoop()

        else:
            print("ERROR - Invalid command: {0}".format(sys.argv[1]))

    except IndexError as err:
        print("ERROR - No command line option given: {0}".format(err))
