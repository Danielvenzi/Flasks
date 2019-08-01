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
            intResultAPI.append(int(ttl[0]))
            i += 1
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
            intResultAPI.append(int(ttl[0]))
            i += 1
    else:
        intResultAPI = []

    return intResultAPI


def firewallMetrics(controllerTTL, apiTTL):
    difference = []
    i = 0
    for ttl in controllerTTL:
        difference.append(apiTTL[i] - ttl)
        i += 1
    avgr = statistics.mean(difference)
    stdev = statistics.stdev(difference)
   
    print("Media dos tempos: {}".format(avgr))
    print("Descrio padrao med: {}".format(stdev))

if __name__ == "__main__":
    firewallMetrics(getTTLController(),getTTLSystemAPI())
