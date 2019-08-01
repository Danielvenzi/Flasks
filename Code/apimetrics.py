import sqlite3
import statistics

################################# SystemAPI Metrics ##############################

def getTTLSystemAPI():
    conn = sqlite3.connect("SystemAPI/database/apiConfiguration.db")
    cursor = conn.cursor()

    cursor.execute("select ttl from IptablesLogs;")
    result = cursor.fetchall()


    if len(result) != 0: 
        intResultAPI = []
        i = 0
        for ttl in result:
            intResultAPI[i] = int(ttl))

    else:
        intResultAPI = []

    return intResultAPI

################################ Controller Metrics #################################

def getTTLController():
    conn = sqlite3.connect("Controller/database/controllerConfiguration.db")
    cursor = conn.cursor()

    cursor.execute("select ttl from knownAttackers;")
    result = cursor.fetchall()


    if len(result) != 0: 
        intResultAPI = []
        i = 0
        for ttl in result:
            intResultAPI[i] = int(ttl))

    else:
        intResultAPI = []

    return intResultAPI


def firewallMetrics(controllerTTL, apiTTL):
    difference = []
    i = 0
    for ttl in controllerTTL:
        difference[i] = apiTTL[i] - ttl

    return statistics.mean(difference)

if __name__ == "__main__":
    print("Essa é média dos tempos: {}".format(firewallMetrics(getTTLController(),getTTLSystemAPI())))