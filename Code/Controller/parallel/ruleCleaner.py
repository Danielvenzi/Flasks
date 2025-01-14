import time
import sqlite3

# Function that retrieves the current time in epochmilis, this time will be used to determine if a rule is expired
def currentEpochMilis():
    current_milli_time = int(round(time.time() * 1000))
    return current_milli_time

# Function that retrives the id and ttl from all the logged rules in the local API Database
def getRulesTTL(databasePath):
    conn = sqlite3.connect(databasePath)
    cursor = conn.cursor()

    try:
        cursor.execute("select id,ttl from knownAttackers;")
        query = cursor.fetchall()
        conn.close()

        finalResult = [result for result in query if result[1] is not None]
        return finalResult

    except sqlite3.OperationalError as err:
        print("ERROR - ruleCleaner Daemon - An error has occured: {0}".format(err))


# Function that checks expiration rule by rule, if the rule is expired delete them
def checkIfExpired():
    print("INFO - Initializing rule cleaner daemon...")
    print(" * SUCCESS - Rule cleaner is up and running")
    try:
        while True:
            listOfRules = getRulesTTL(databasePath="database/controllerConfiguration.db")

            if len(listOfRules) == 0:
                print("INFO - ruleCleaner Daemon - No known attackers... waiting...")
                time.sleep(300)
                continue

            conn = sqlite3.connect("database/controllerConfiguration.db")
            cursor = conn.cursor()

            # The time to live of a specific rule is 2 hours
            twoHoursInMiliSeconds = 7200000

            for rule in listOfRules:
                # rule[0] = Rule ID
                # rule[1] = TTL of a iptables rule
                currentTime = currentEpochMilis()
                if ((currentTime-rule[1]) >= twoHoursInMiliSeconds):
                    try:
                        cursor.execute("delete from knownAttackers where id = {0};".format(rule[0]))
                        cursor.execute("delete from vaccineLogs where id = {0};".format(rule[0]))
                        conn.commit()
                        print("RuleCleaner - INFO - Deleting rule with id: {0}".format(rule[0]))
                    except sqlite3.OperationalError as err:
                        print("RuleCleaner - ERROR - ruleCleaner Daemon -  An error has occured: {0}".format(err))

                continue
            conn.close()
            time.sleep(300)

    except KeyboardInterrupt:
        print("INFO - ruleCleaner Daemon - Closing the rule cleaner daemon...")

if __name__ == "__main__":
    checkIfExpired()