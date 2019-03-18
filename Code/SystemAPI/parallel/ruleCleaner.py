import sqlite3
import time
import requests
import json

# Function that retrieves the current time in epochmilis, this time will be used to determine if a rule is expired
def currentEpochMilis():
    current_milli_time = int(round(time.time() * 1000))
    return current_milli_time

# Function that retrives the id and ttl from all the logged rules in the local API Database
def getRulesTTL(databasePath):
    conn = sqlite3.connect(databasePath)
    cursor = conn.cursor()

    try:
        cursor.execute("select id,ttl from IptablesLogs;")
        query = cursor.fetchall()
        conn.close()

        finalResult = [result for result in query if result[1] is not None]
        return finalResult

    except sqlite3.OperationalError as err:
        print("ERROR - ruleCleaner Daemon - An error has occured: {0}".format(err))


def deleteIptables(ruleID):
    print("Vamos começar o delete")
    conn = sqlite3.connect("database/apiConfiguration.db")
    cursor = conn.cursor()

    cursor.execute("select * from IptablesLogs where id = {0};".format(ruleID))
    result = cursor.fetchall()

    iptables_log = result[0]
    iterator = 6
    rule_json = {}
    print("Chegamos aqui com iptables_logs: {0}".format(iptables_log))
    equivalent_postion = ["Protocol", "Destination", "Source", "Interface IN", "Interface OUT",
                          "Destination Port","Source Port", "SYN", "TCP Flags", "Jump"]

    while (iterator <= len(iptables_log)-1):
        if iterator == len(iptables_log)-1:
            continue
        elif iptables_log[iterator] != None:
            rule_json[equivalent_postion[iterator-6]] = iptables_log[iterator]
        elif iptables_log[iterator] == None:
            continue

    api_delete_request = {"Table":iptables_log[3], "Action":"delete", "Chain":iptables_log[5], "Rule":rule_json}
    print("This is the delete request: {0}".format(api_delete_request))
    cursor.execute("select host,port from APIConfig;")
    result = cursor.fetchall()
    api_config = result[0]
    conn.close()

    try:
        json_post_rule = json.dumps(api_delete_request)
        headers = {'Content-Type': 'text/plain;charset=UTF-8'}
        if api_config[0] != "0.0.0.0":
            addr = "127.0.0.1"
        else:
            addr = api_config[0]

        postRequest = requests.post("http://{0}:{1}/api/iptables".format(addr,api_config[1]), headers=headers,
                                data=json_post_rule, timeout=15.0)
        try:
            postResponse = postRequest.json()
            if postResponse["Status"] == 200:
                print("ruleCleaner - INFO - Successfull rule Deletion")
            else:
                print("ruleCleaner - ERROR - ruleCleaner Failed to configure the rule")
        except json.decoder.JSONDecodeError as err:
            print("ruleCleaner - ERROR - The response is not a JSON: {0}".format(err))
    except requests.exceptions.ConnectTimeout as err:
        print("ERROR - ruleCleaner - Connection timeout: {0}".format(err))
    except requests.exceptions.ConnectionError as err:
        print("ERROR - ruleCleaner - Connection error: {0}".format(err))


# Function that checks expiration rule by rule, if the rule is expired delete them
def checkIfExpired():
    print("INFO - Initializing rule cleaner daemon...")
    print("SUCCESS - Rule cleaner is up and running")
    try:
        while True:
            listOfRules = getRulesTTL(databasePath="database/apiConfiguration.db")

            if len(listOfRules) == 0:
                print("INFO - ruleCleaner Daemon - No configured rules... waiting...")
                time.sleep(300)
                continue

            conn = sqlite3.connect("database/apiConfiguration.db")
            cursor = conn.cursor()

            # The time to live of a specific rule is 2 hours
            twoHoursInMiliSeconds = 7200000

            for rule in listOfRules:
                # rule[0] = Rule ID
                # rule[1] = TTL of a iptables rule
                currentTime = currentEpochMilis()
                if ((currentTime-rule[1]) >= twoHoursInMiliSeconds):
                    try:
                        print("INFO - ruleCleaner - Deleting the rule...")
                        deleteIptables(rule[0])
                        cursor.execute("delete from IptablesLogs where id = {0};".format(rule[0]))
                        conn.commit()
                        print("INFO - Deleting rule with id: {0}".format(rule[0]))
                    except sqlite3.OperationalError as err:
                        print("ERROR - ruleCleaner Daemon -  An error has occured: {0}".format(err))

                continue
            conn.close()
            time.sleep(300)

    except KeyboardInterrupt:
        print("INFO - ruleCleaner Daemon - Closing the rule cleaner daemon...")

if __name__ == "__main__":
    checkIfExpired()