import sqlite3

# -------- Declaration of the systemapi command action functions -------- #

def apiConfig(options,values):
    if len(options) == 3:
        if not "-apiaddr" in options:
            print("ERROR - Option '-apiaddr' is necessary for the config action.")
            return None
        elif not "-apiport" in options:
            print("ERROR - Option '-apiport' is necessary for the config action.")
            return None
        elif not "-apiname" in options:
            print("ERROR - Option '-apiname' is necessary for the config action.")
        else:
            addr = ""
            port = 0
            name = ""
            for option in options:
                if option == "-apiaddr":
                    optionIndex = options.index(option)
                    addr += str(values[optionIndex])
                elif option == "-apiport":
                    optionIndex = options.index(option)
                    port += int(values[optionIndex])
                elif option == "-apiname":
                    optionIndex = options.index(option)
                    name += (values[optionIndex])

            conn = sqlite3.connect("database/controllerConfiguration.db")
            cursor = conn.cursor()

            cursor.execute('select 1 from SystemAPI where apiname = \"{0}\";'.format(name))
            existsResult = cursor.fetchall()

            if int(len(existsResult)) == int(0):
                cursor.execute('select 1 from SystemAPI where apihost = \"{0}\";'.format(addr))
                addressResult = cursor.fetchall()

                if int(len(addressResult)) == int(0):
                    cursor.execute('insert into SystemAPI (apihost,apiport,apiname,apikey,known) values (\"{0}\",{1},\"{2}\","None",0);'.format(addr,port,name))
                    print("OK - New SystemAPI added with: Address - {0}, Port - {1}, Name - {2}".format(addr,port,name))
                    print("INFO - The SystemAPI is configured but isn't known yet. Use help command for more information.")
                    conn.commit()

                    conn.close()

                elif len(addressResult) != int(0):
                    print("ERROR - A SystemAPI with {0} as it's address already exists.".format(addr))
                    conn.close()
            else:
                print("ERROR - A SystemAPI named {0} already exists.".format(name))
                conn.close()


    elif len(options) < 3:
        print("ERROR - Missing options! Expected '-apiaddr','-apiport' and '-apiname' for the config action. Use help command for more information.")


def apiList(options,values):
    if len(options) == 1:
        if options[0] == "-apiname":
            conn = sqlite3.connect('database/controllerConfiguration.db')
            cursor = conn.cursor()
            cursor.execute('select * from SystemAPI;')
            results = cursor.fetchall()

            if len(results) == 0:
                print("ERROR - No configured SystemAPI's. Use help command for more information.")
                return None

            if values[0] == "all":
                cursor.execute('select apiname,apihost,apiport,known from SystemAPI;')
                results = cursor.fetchall()
                iterator = 1
                print("Configured SystemAPI's:")
                for result in results:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Known: {4}".format(iterator,result[0],result[1],result[2],result[3]))
                    iterator += 1
                conn.close()
            else:
                cursor.execute('select apiname,apihost,apiport,known from SystemAPI where apiname = \"{0}\"'.format(values[0]))
                result = cursor.fetchall()
                if len(result) == 0:
                    print("ERROR - No SystemAPI named {0} configured.".format(values[0]))
                    conn.close()
                else:
                    print("\t{0}-) {1}: Address: {2}, Port: {3}, Known: {4}".format(1,result[0][0],result[0][1],result[0][2],result[0][3]))
                    conn.close()
        else:
            print("ERROR - Missing option! Expect -apiname for the list action. Use help command for more information.")
    else:
        print("ERROR - More options than needed for ACTION list. Use help command for more information.")


def apiAbsorb():
    print("Work in progress")

def apiFlush():
    print("Work in progress")