import sqlite3
import statistics
import os

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

def deleteLogs():
    ############ Deletando os dados do Controller ##############
    connController = sqlite3.connect("Controller/database/controllerConfiguration.db")
    cursorController = connController.cursor()
    cursorController.execute("delete from IptablesLogs;")
    cursorController.execute("delete from vaccineLogs;")
    connController.commit()

    ########### Deletando os dados da SystemAPI ################
    conn = sqlite3.connect("SystemAPI/database/apiConfiguration.db")
    cursor = conn.cursor()
    cursor.execute("delete from IptablesLogs;")
    conn.commit()


def runAttack(count):
    os.system("hping3 --faster -c {} -p 22 172.16.5.93".format(count))


if __name__ == "__main__":
    print("\nIncializando o ataque...")
    runAttack(input("Quantidade de pacotes: "))
    print("\nTerminando ataque...")

    firewallMetrics(getTTLController(),getTTLSystemAPI())
    print("\nDeletando os logs da solução...")
    deleteLogs()
    print("\n\nFeito!")
    
