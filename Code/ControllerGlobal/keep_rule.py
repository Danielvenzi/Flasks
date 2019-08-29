import requests
import time
import datetime
import sys
import sqlite3
import json

# Função que executa o keep trying da aplicação de regras da conttroller global para a controller local
def keep_trying(rule_json,host,port):
    iterations = 0
    while True:
        # Se não forem feitas 18 iterações teremos que não passaram 3 horas ainda e o processo continuará tentando aplicar a regra na controller local
        if iterations != 18:
            try:
                postRequest = requests.post("http://{0}:{1}/create_rule".format(host,port), data=json.dumps(rule_json),timeout=15.0)
                postResponse = postRequest.json()
                if postRequest.status_code == 200:
                    status = postResponse["Status"]
                    if (status == 200):
                        conn = sqlite3.connect('database/controllerConfiguration.db')
                        cursor = conn.cursor()

                        if rule_json['Type'] == "Iptables":
                            cursor.execute('update ConfiguredRulesIptables set status = 1 where;')
                        elif rule_json['Type'] == "NET":
                            cursor.execute('update ConfiguredRulesNET set status = 1 where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(rule_json["name"],rule_json["premise"],rule_json["action"],rule_json["test"]))
                        elif rule_json['Type'] == "HIDS":
                            cursor.execute('update ConfiguredRulesNET set status = 1 where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(rule_json["name"],rule_json["premise"],rule_json["action"],rule_json["test"]))
                    
                        conn.commit()
                        conn.close()

                    elif (status == 400):
                        print("ERROR - The configuration of a rule came back with status of {}}".format(status))
                    else:
                        print("ERROR - The Configuration of a rule came back with a status of {}".format(status))


            except requests.exceptions.ConnectTimeout:
                print("\tERROR - Unable to connect to {0} at port {1}".format(host,port))
            except requests.exceptions.ConnectionError:
                print("\tERROR - An error occured while trying to connect to {0} at port {1}".format(host,port))
            except requests.exceptions.SSLError:
                print("\tERROR - An SSL error has occured while trying to connect to {0} at port {1}".format(host,port))
        
        # Se tivermos 18 repetições no keep_rule o processo será morto para ser ressucitado pelo grave digger (18 iterações representam 3 horas passadas)
        elif iterations == 18:
            sys.exit(1)

        # Espere 10 minutos para tentar novamente
        time.sleep(600)
        iterations += 1
