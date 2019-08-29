import sqlite3
import keep_rule
import time
import os

# Função que pega do banco de dados as regras que ainda n foramc caadastradas nas controllers locais
# crypt = tabela do banco de dados da controller global
def dig_grave(crypt):
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()

    cursor.execute('select * from \"{}\" where status = 1;'.format(crypt))
    fetch_result = cursor.fetchall()
    conn.commit()

    conn.close()

    return fetch_result

# Função que pega uma regra e inicializa um processo de keep_rule para tentar aplica-lá a sua controller local associada
def defile_bodies(body_bag,typeof):
    conn  = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()

    for body in body_bag:

        # Pega as informações do controller local a qual a regra deve ser cadastrada
        cursor.execute('select host,port from LocalController where controllername = \"{}\";'.format(body[5]))
        result = cursor.fetchall()
    
        host = result[0][0]
        port = result[0][1]

        rule_json = {}
        rule_json["name"] = body[1]
        rule_json["premise"] = body[2]
        rule_json["test"] = body[3]
        rule_json["action"] = body[4]
        rule_json["Type"]

        send_rule_pid = os.fork()
        if send_rule_pid == 0:
            keep_rule.keep_trying(rule_json,host,port)
        else:
            time.sleep(300)

    conn.close()

# Função que define a mente do xafado que vai pegar as regras e as aplicar
def grave_mind():
    # Pega as regras ainda não cadastradas do hids remoto para tentar aplicar novamente
    net_grave = dig_grave("ConfiguredRulesHIDS")
    # Pega as regras da systemapi não cadastradas para tentar aplicar novamente
    iptables_grave = dig_grave("ConfiguredRulesIptables")
    # Pega as regras de HIDS não cadastradas para tentar aplicar novamente
    hids_grave = dig_grave("ConfiguredRulesHIDS")

    # Função que cria processos para cadastrar as regras n cadastradas
    defile_bodies(net_grave,"NET")
    defile_bodies(iptables_grave,"Iptables")
    defile_bodies(hids_grave,"HIDS")



    