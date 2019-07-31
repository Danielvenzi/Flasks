import time
import sqlite3
import os
import requests
import json

# Function that connects to the local api database and returns a list with every registered SystemAPI
# needed information (apihost,apiport,apikey)
def getSAPIs():
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()

    try:
        cursor.execute('select id,apihost,apiport,apikey from SystemAPI where apitype=\"{0}\";'.format("systemapi"))
        query_result = cursor.fetchall()
        conn.close()

        return query_result

    except sqlite3.OperationalError as err:
        print("ERROR - Internal server error: {0}".format(err))
        os._exit(0)

# Function that connects to the local api database and returns a list with every registered rule
# needed information (protocol,srcaddr,dstaddr,srcport,dstport)
def getRULES():
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()

    try:
        cursor.execute('select id,protocol,srcaddr,dstaddr,srcport,dstport from knownAttackers;')
        query_result = cursor.fetchall()
        conn.close()

        return query_result

    except sqlite3.OperationalError as err:
        print("ERROR - Internal server error: {0}".format(err))
        os._exit(0)


def encodeRuleJSON(rule):
    dest = rule["Destination"]
    src = rule["Source"]
    proto = rule["Protocol"]
    final_json = {"Rule":"{{\"{3}\":\"{0}\",\"{4}\":\"{1}\",\"{5}\":\"DROP\",\"{6}\":\"{2}\"}}".format(dest, src, proto,"Destination", "Source", "Jump", "Protocol")}

    return final_json["Rule"]

# Function that connects to the local database and checks: if for a given SystemAPI a specific rule is not enforced
# send the rule parameters to the SystemAPI Rest API
def applyVaccines(hosts,rules):
    print("INFO - Initialiazing Health Agent daemon...")
    print(" * SUCCESS - Health Agent daemon initialiazed")
    conn = sqlite3.connect("database/controllerConfiguration.db")
    cursor = conn.cursor()

    try:

        for rule in rules:
            rule_id = rule[0]
            rule_protocol = rule[1]
            rule_srcaddr = rule[2]
            rule_dstaddr = rule[3]
            rule_srcport = rule[4]
            rule_dstport = rule[5]

            for host in hosts:
                host_id = host[0]
                host_ip = host[1]
                host_port = host[2]
                host_key = host[3]

                cursor.execute('select * from vaccineLogs where apiid = {0} and attackerid = {1};'.format(host_id,rule_id))
                query_result = cursor.fetchall()

                if len(query_result) == 0:
                    if (rule_protocol == "TCP") or (rule_protocol == "UDP"):
                        try:
                            rule_param = {"Protocol":rule_protocol.lower(),"Source":rule_srcaddr,"Destination":rule_dstaddr,"Destination Port":rule_dstport,"Jump":"DROP"}
                            #rule_param = encodeRuleJSON(rule_param)
                            #post_rule = {"API Register Key":host_key,"Table":"filter","Action":"append","Chain":"input","Rule":rule_param}
                            post_rule = {"API Register Key":host_key,"Table":"filter","Action":"append","Chain":"forward","Rule":rule_param}
                            json_post_rule = json.dumps(post_rule)
                            headers = {'Content-Type': 'text/plain;charset=UTF-8'}
                            postRequest = requests.post("http://{0}:{1}/api/iptables".format(host_ip,host_port), headers=headers, data=json_post_rule, timeout=15.0)
                            try:
                                postResponse = postRequest.json()
                                if postResponse["Status"] == 200:
                                    print("HealthAgent - INFO - Successfull SystemAPI Configuration")
                                    cursor.execute('insert into vaccineLogs (apiid,attackerid) values ({0},{1});'.format(host_id,rule_id))
                                    conn.commit()
                                else:
                                    print("HealthAgent - ERROR - SystemAPI Failed to configure the rule")
                            except json.decoder.JSONDecodeError as err:
                                print("HealthAgent - ERROR - The response is not a JSON: {0}".format(err))
                        except requests.exceptions.ConnectTimeout as err:
                            print("ERROR - Health Agent daemon - Connection timeout: {0}".format(err))
                        except requests.exceptions.ConnectionError as err:
                            print("ERROR - Health Agent daemon - Connection error: {0}".format(err))
                    elif rule_protocol == "ICMP":
                        try:
                            headers = {'Content-Type': 'text/plain;charset=UTF-8'}
                            #post_rule = {"API Register Key": host_key, "Table": "filter", "Action": "append","Chain": "input","Rule": {"Protocol": rule_protocol.lower(), "Source": rule_srcaddr,"Destination": rule_dstaddr}}
                            post_rule = {"API Register Key": host_key, "Table": "filter", "Action": "append","Chain": "forward","Rule": {"Protocol": rule_protocol.lower(), "Source": rule_srcaddr,"Destination": rule_dstaddr}}
                            postRequest = requests.post("http://{0}:{1}/api/iptables".format(host_ip, host_port), headers=headers, data=json.dumps(post_rule), timeout=15.0)
                            try:
                                postResponse = postRequest.json()
                                if postResponse["Status"] == 200:
                                    print("HealthAAgent - INFO - Successfull SystemAPI Configuration")
                                    cursor.execute('insert into vaccineLogs (apiid,attackerid) values ({0},{1});'.format(host_id,rule_id))
                                    conn.commit()
                                else:
                                    print("HealthAgent - ERROR - SystemAPI Failed to configure the rule")
                            except json.decoder.JSONDecodeError as err:
                                print("HealthAgent - ERROR - The response is not a JSON: {0}".format(err))
                        except requests.exceptions.ConnectTimeout as err:
                            print("ERROR - Health Agent daemon - Connection timeout: {0}".format(err))
                        except requests.exceptions.ConnectionError as err:
                            print("ERROR - Heath Agent daemon - Connection error: {0}".format(err))


    except KeyboardInterrupt as err:
        print("INFO - Closing the Health Agent daemon")
        conn.close()
        os._exit(0)


def main():
    while True:
        applyVaccines(getSAPIs(),getRULES())
        time.sleep(5)


if __name__ == "__main__":
    applyVaccines(getSAPIs(),getRULES())
