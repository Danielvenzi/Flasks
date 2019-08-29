from flask import Flask, request, jsonify, redirect, url_for, abort
import sqlite3
import os
import sys
from functools import wraps
import ruleApply
import json
import requests
import multiprocessing

class ControllerGlobal():
    # Método de inicialização dos programas paralelos da controller global e verficação do bando de dados
    def initialize(self):
        status = self.check_db()
        if status:
            print("STATUS - O Banco de dados está funcionando normalmente.")
        else:
            self.reintegrate_db()
            self.initialize()

        #self.initialize_rule_service

    # Método para verificação de integridade da base de dados da controller global
    def check_db(self):
        try:
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()

            cursor.execute('select * from LocalController;')
            cursor.execute('select * from ConfiguredEntities;')
            cursor.execute('select * from ConfiguredRulesHIDS;')
            cursor.execute('select * from ConfiguredRulesIptables;')
            cursor.execute('select * from ConfiguredRulesNet;')

            conn.close()
            # O banco de dados está integro
            return True

        except sqlite3.OperationalError as err:
            print("ERROR - An internal server error has occured: {} Status: 400".format(err))
            # O banco de dados não está integro 
            return False

    # Método para reconstrução do banco de dados da controller global
    def reintegrate_db(self):
        try:
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()  

            cursor.execute('DROP TABLE IF EXISTS LocalController;')
            cursor.execute('DROP TABLE IF EXISTS ConfiguredEntities;')
            cursor.execute('DROP TABLE IF EXISTS ConfiguredRulesHIDS;')
            cursor.execute('DROP TABLE IF EXISTS ConfiguredRulesIptables;')
            cursor.execute('DROP TABLE IF EXISTS ConfiguredRulesNet;')

            cursor.execute('CREATE TABLE IF NOT EXISTS LocalController (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, host TEXT, port INTEGER,description TEXT);')
            cursor.execute('CREATE TABLE IF NOT EXISTS ConfiguredEntities (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, type TEXT, host TEXT, port INTEGER, controllername TEXT);')
            cursor.execute('CREATE TABLE IF NOT EXISTS ConfiguredRulesHIDS (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created TEXT, premise TEXT NOT NULL, action TEXT NOT NULL, test TEXT NOT NULL, status INTEGER, controllername Text);')
            cursor.execute('CREATE TABLE IF NOT EXISTS ConfiguredRulesIptables (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, controlleraddr TEXT NOT NULL, receivetime TEXT NOT NULL, tablename TEXT NOT NULL, action TEXT NOT NULL, chain TEXT, protocol TEXT, destinationaddr TEXT, sourceaddr TEXT,interfacein TEXT, interfaceout TEXT, destinationport INTEGER, sourceport INTEGER, synbased INTEGER, tcpflags TEXT, jumpaction TEXT, ttl INTEGER, status INTEGER, controllername TEXT);')
            cursor.execute('CREATE TABLE IF NOT EXISTS ConfiguredRulesNET (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, created TEXT, premise TEXT NOT NULL, action TEXT NOT NULL, test TEXT NOT NULL, status INTEGER, controllername TEXT);')

            conn.commit()

            conn.close()

        except sqlite3.OperationalError as err:
            print("ERROR - An internal server error has occured: {} Status: 400".format(err))

    # Método de registro de controller locais
    def register_cl(self,sent_json):
        try:
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()

            cursor.execute('select * from LocalController where description = \"{}\";'.format(sent_json['Description']))
            result = cursor.fetchall()
            if (len(result)) == 0:
                cursor.execute("insert into LocalController (host,port,description) values (\"{0}\",{1},\"{2}\");".format(sent_json["Host"],sent_json["Port"],sent_json["Description"]))
                conn.commit()
                dictio = {"Response":"Successfull Local Controller Configuration","Status":200}
            else:
                dictio = {"Response":"Local Controller already exists.","Status":400}
                
            conn.close()
            return dictio

        except sqlite3.OperationalError as err:
            return jsonify({"Response": "Internal server error has occured","Status":400})

    # Método de registro de entidades (dispositivos de rede legado)
    def register_entities(self,sent_json):
        try:
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()

            cursor.execute('select * from ConfiguredEntities where type = \"{}\" and host = \"{}\" and port = {} and controllername = \"{}\";'.format(sent_json['Type'],sent_json['Host'],int(sent_json['Port']),sent_json["Controller"]))
            result = cursor.fetchall()
            if (len(result)) == 0:
                cursor.execute("insert into ConfiguredEntities (type,host,port,controllername) values (\"{0}\",\"{1}\",{2},\"{3}\");".format(sent_json["Type"],sent_json["Host"],int(sent_json["Port"]),sent_json["Controller"]))
                conn.commit()
                dictio = {"Response":"Successfull Local entity configuration.","Status":200}
            else:
                dictio = {"Response":"Local entity already exists.","Status":400}
                
            conn.close()
            return dictio

        except sqlite3.OperationalError as err:
            return jsonify({"Response": "Internal server error has occured","Status":400})

    def register_rules(self,sent_json):
        rule_type = sent_json['Type']
        if rule_type == "Iptables":
            print("STATUS - Iptables rule - Work in progress")


        # Cadastro de regras associados a dispositivos de rede legado
        elif rule_type == "NET":
            try:
                conn = sqlite3.connect('database/controllerConfiguration.db')
                cursor = conn.cursor()

                cursor.execute('select * from ConfiguredRulesNET where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(sent_json['name'],sent_json['premise'],sent_json['action'],sent_json["test"]))
                result = cursor.fetchall()
                if (len(result)) == 0:
                    cursor.execute("insert into ConfiguredRulesNET (name,premise,action,test, status, controllername) values (\"{0}\",\"{1}\",\"{2}\",\"{3}\",0,\"{4}\");".format(sent_json["name"],sent_json["premise"],sent_json["action"],sent_json["test"],sent_json["Controller"]))
                    conn.commit()

                    try:
                        postRequest = requests.post("http://127.0.0.1:5050/rule", data=json.dumps(sent_json),timeout=15.0)
                    except requests.exceptions.ConnectTimeout:
                        print("\tERROR - Unable to connect to 127.0.0.1. at port 5050")
                    except requests.exceptions.ConnectionError:
                        print("\tERROR - An error occured while trying to connect to 127.0.0.1 at port 5050")
                    except requests.exceptions.SSLError:
                        print("\tERROR - An SSL error has occured while trying to connect to 127.0.0.1 at port 5050")

                    dictio = {"Response":"Successfull rule configuration","Status":200}
                else:
                    dictio = {"Response":"Local rule already exists.","Status":400}
                    
                conn.close()
                return dictio

            except sqlite3.OperationalError as err:
                return jsonify({"Response": "Internal server error has occured","Status":400})


        # Cadastro de regras associados a disposiitvos de IoT com HIDS
        elif rule_type == "HIDS":
            try:
                conn = sqlite3.connect('database/controllerConfiguration.db')
                cursor = conn.cursor()

                cursor.execute('select * from ConfiguredRulesHIDS where name = \"{}\" and premise = \"{}\" and action = \"{}\" and test = \"{}\";'.format(sent_json['name'],sent_json['premise'],sent_json['action'],sent_json["test"]))
                result = cursor.fetchall()
                if (len(result)) == 0:
                    cursor.execute("insert into ConfiguredRulesHIDS (name,premise,action,test,status,controllername) values (\"{0}\",\"{1}\",\"{2}\",\"{3}\",0,\"{4}\");".format(sent_json["name"],sent_json["premise"],sent_json["action"],sent_json["test"],sent_json["Controller"]))
                    conn.commit()

                    try:
                        postRequest = requests.post("http://127.0.0.1:5050/rule", data=json.dumps(sent_json),timeout=15.0)
                    except requests.exceptions.ConnectTimeout:
                        print("\tERROR - Unable to connect to 127.0.0.1. at port 5050")
                    except requests.exceptions.ConnectionError:
                        print("\tERROR - An error occured while trying to connect to 127.0.0.1 at port 5050")
                    except requests.exceptions.SSLError:
                        print("\tERROR - An SSL error has occured while trying to connect to 127.0.0.1 at port 5050")

                    dictio = {"Response":"Successfull rule configuration","Status":200}
                else:
                    dictio = {"Response":"Local rule already exists.","Status":400}
                    
                conn.close()
                return dictio

            except sqlite3.OperationalError as err:
                return jsonify({"Response": "Internal server error has occured","Status":400})


    # Método para interação com as regras associadas a entidades
    def interaction(self,sent_json):
        try:
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()


            conn.close()
        except sqlite3.OperationalError as err:
            return jsonify({"Response": "Internal server error has occured","Status":400})

    # Método de inicialização do serviço de aplicação de regras e iteração com as entidades
    # def initialize_rule_service(self):
    #     # rule_service = os.fork()
    #     # if rule_service == 0:
    #     #     ruleApply.initialize()
    #     # else:
    #     #     print("STATUS - Iniciando o processo de aplicação de regras")
    #     #ruleApply.initialize()
    #     #ruleApply.initialize()
    #     print("STATUS - NONE")
    

if __name__ == "__main__":
    controller = ControllerGlobal()
    controller.initialize()
    #controller.initialize_rule_service()