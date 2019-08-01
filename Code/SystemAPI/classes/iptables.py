import os
import json
import sqlite3
import datetime
import time

class iptables():

    def __init__(self,table,action,chain,rule,address):
        self.tableName = table
        self.actionName = action
        self.chainName = chain.upper()
        if isinstance(rule, str):
            self.ruleOptions = json.loads(rule)
        else:
            self.ruleOptions = rule
        self.controllAddr = address
        self.statusCode = None
        self.ruleID = 0
        self.listResult = None

    def statusReponse(self):
        nktjson = {"Response":"Invalid Table passed.","Status":400}
        nkajson = {"Response":"Invalid Action passed","Status":400}
        bkjson = {"Response":"Valid Action and Table passed.","Status":200}
        urojson = {"Response":"Undefined rule options passed.","Status":400}
        drojson = {"Response":"Valid rule options passed.","Status":200}
        cyjson = {"Response":"Rule already exists","Status":200}
        cnjson = {"Response":"Rule doesn't exists","Status":200}
        sijson = {"Response":"Successfull rule insertion in the database.","Status":200}
        uijson = {"Response":"Unsuccesfull rule insertion in the database.","Status":500}
        sicjson = {"Response":"Successfull database insertion command construct","Status":200}
        sccjson = {"Response":"Successfull database check command construct","Status":200}
        sfcjson = {"Response" :"Successfull firewall command contrust","Status":200}
        slfcjson = {"Response":"Succesfull firewall rules flush","Status":200}
        scdrcjson = {"Response":"Successfull check/delete/replace command construct","Status":200}
        ipcjson = {"Response":"Succesfull firewall configuration","Status":200}
        sdjson = {"Response":"Successfull rule deletion","Status":200}
        udjson = {"Response":"Unsuccessfull rule deletion","Status":400}
        lpjson = {"Response":"List result","Status":200,"Rules":self.listResult}
        fejson = {"Response":"Flush failed","Status":400}
        statusDict = {"NKT":nktjson,"NKA":nkajson,"BK":bkjson,"URO":urojson,"DRO":drojson,"CY":cyjson,"CN":cnjson,"SI":sijson,"UI":uijson,"SIC":sicjson,"SCC":sccjson,"SFC":sfcjson,"SLFC":slfcjson,"SCDRC":scdrcjson,"IPC":ipcjson,"SD":sdjson,"UD":udjson,"LP":lpjson,"FE":fejson}

        return statusDict[self.statusCode]


    def execute(self):
        self.checkParameters()
        if self.statusCode == "BK":
            iptablesCommand = self.formatCommand()
            if iptablesCommand == None:
                return self.statusReponse()
            else:
                print(iptablesCommand)
                os.system(iptablesCommand)
                if self.statusCode == "SD":
                    return self.statusReponse()
                elif self.statusCode != "SD":
                    self.statusCode = "IPC"
                    return self.statusReponse()
        elif (self.statusCode == "NKT") or (self.statusCode == "NKA"):
            return self.statusReponse()

    def checkParameters(self):
        knownTables = ["filter", "nat", "mangle", "raw", "security"]
        knownActions = ["append", "check", "delete", "insert", "replace", "list", "flush"]

        if not self.tableName in knownTables:
            self.statusCode = "NKT" #Not Known Table
        elif not self.actionName in knownActions:
            self.statusCode = "NKA" #Not Known Action
        else:
            self.statusCode = "BK" #Both (Table an Action) Known

    def checkRuleParameters(self):
        knownFields = ["Destination", "Source", "Interface IN", "Interface OUT", "Protocol", "Destination Port", "Source Port","SYN", "TCP Flags","Jump"]
        ruleDict = self.ruleOptions
        ruleKeys = ruleDict.keys()

        for key in ruleKeys:
            if not key in knownFields:
                self.statusCode = "URO" # Undefined Rule Options

        self.statusCode = "DRO" # Defined Rule Options

    def formatJSON(self,queryResult):
        knownValues = ["Table", "Chain", "Protocol", "Destination Address", "Source Address", "Interface IN","Interface OUT", "Destination Port", "Source Port", "SYN", "TCP Flags", "Jump"]
        finalDict = {}
        jsonCount = 1
        for result in queryResult:
            jsonDict = {}
            iterator = 0
            while iterator <= 11:
                jsonDict[knownValues[iterator]] = result[iterator]
                iterator += 1
            finalDict[jsonCount] = jsonDict
            jsonCount += 1


        self.listResult = finalDict


    def executeSQL(self,queryString,type):
        conn = sqlite3.connect("./database/apiConfiguration.db")
        cursor = conn.cursor()

        if type == "check":
            numberOfRuleElements = len(self.ruleOptions.keys())+7
            cursor.execute("{0}".format(queryString))
            queryResult = cursor.fetchall()
            conn.close()

            for query in queryResult:
                finalResult = [result for result in query if result is not None]
                if len(finalResult) == numberOfRuleElements:
                    self.statusCode = "CY" # Check Yes (Rule exists)
                    self.ruleID = queryResult[0][0]
                    return None

            self.statusCode = "CN" # Check No (Rule doesn't exist)

        elif type == "insert":
            try:
                cursor.execute("{0}".format(queryString))
                conn.commit()
                conn.close()
                self.statusCode = "SI" # Successfull Insertion
            except sqlite3:
                self.statusCode = "UI" # Unsuccessfull Insertion

        elif type == "delete":
            try:
                cursor.execute("{0}".format(queryString))
                conn.commit()
                conn.close()
                self.statusCode = "SD" # Successfull Deletion
            except sqlite3:
                self.statusCode = "UD" # Unsuccessfull Deletion

        elif type == "list":
                cursor.execute("select tablename,chain,protocol,destinationaddr,sourceaddr,interfacein,interfaceout,destinationport,sourceport,synbased,tcpflags,jumpaction from IptablesLogs where action = \"{0}\";".format("append"))
                result = cursor.fetchall()
                self.listResult = result
                conn.close()
                self.formatJSON(result)

        elif type == "flush":
            try:
                cursor.execute("delete from IptablesLogs where action = \"append\";")
                conn.commit()
                conn.close()
            except sqlite3:
                self.statusCode = "FE" # Flush Error

    def queryInsertConstruct(self):
        knownFields = ["Destination", "Source", "Interface IN", "Interface OUT", "Protocol", "Destination Port","Source Port", "SYN", "TCP Flags", "Jump"]
        fieldType = ["string", "string", "string", "string", "string", "integer", "integer", "string", "string","string"]
        databaseFields = ["destinationaddr", "sourceaddr", "interfacein", "interfaceout", "protocol", "destinationport","sourceport", "synbased", "tcpflags", "jumpaction"]

        currentTime = datetime.datetime.today().strftime('%Y-%m-%d')
        currentTimeMili = int(round(time.time() * 1000))

        if self.actionName == "append":
            sqlCommand = "insert into IptablesLogs (ttl,controlleraddr,receivetime,tablename,action,chain,"
        else:
            sqlCommand = "insert into IptablesLogs (controlleraddr,receivetime,tablename,action,chain,"
        ruleDict = self.ruleOptions
        ruleDictKeys = list(ruleDict.keys())

        changeCounter = 0
        for field in knownFields:
            iterator = 0
            while iterator <= len(ruleDictKeys)-1:
                if (field == ruleDictKeys[iterator]):
                    fieldIndex = knownFields.index(field)
                    sqlOption = databaseFields[fieldIndex]
                    type = fieldType[fieldIndex]
                    if changeCounter != len(ruleDictKeys)-1:
                        sqlCommand += "{0},".format(sqlOption)
                        changeCounter += 1
                    elif changeCounter == len(ruleDictKeys)-1:
                        if self.actionName == "append" or self.actionName == "insert":
                            sqlCommand += "{0}) values ({6},\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",".format(sqlOption,self.controllAddr,currentTime,self.tableName,self.actionName,self.chainName,currentTimeMili)
                        else:
                            sqlCommand += "{0}) values (\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",".format(sqlOption,self.controllAddr,currentTime,self.tableName,self.actionName,self.chainName)
                        changeCounter += 1
                iterator += 1

        changeCounter = 0
        for field in knownFields:
            iterator = 0
            while iterator <= len(ruleDictKeys) - 1:
                if (field == ruleDictKeys[iterator]):
                    fieldIndex = knownFields.index(field)
                    sqlOption = databaseFields[fieldIndex]
                    type = fieldType[fieldIndex]
                    if changeCounter != len(ruleDictKeys) - 1:
                        if type == "string":
                            sqlCommand += "\"{0}\",".format(ruleDict[field])
                            changeCounter += 1
                        elif type == "integer":
                            sqlCommand += "{0},".format(ruleDict[field])
                            changeCounter += 1
                    elif changeCounter == len(ruleDictKeys) - 1:
                        if type == "string":
                            sqlCommand += "\"{1}\");".format(sqlOption, ruleDict[field])
                            changeCounter += 1
                        elif type == "integer":
                            sqlCommand += "{0});".format(ruleDict[field])
                            changeCounter += 1
                iterator += 1

        self.statusCode = "SIC" # Successfull Insert Construct
        return sqlCommand

    def queryCheckConstruct(self):
        knownFields = ["Destination", "Source", "Interface IN", "Interface OUT", "Protocol", "Destination Port","Source Port", "SYN", "TCP Flags", "Jump"]
        fieldType = ["string","string","string","string","string","integer","integer","string","string","string"]
        databaseFields = ["destinationaddr", "sourceaddr", "interfacein", "interfaceout", "protocol", "destinationport", "sourceport", "synbased", "tcpflags", "jumpaction"]

        sqlCommand = "select * from IptablesLogs where tablename=\"{0}\" and chain=\"{1}\" and action =\"append\" ".format(self.tableName,self.chainName)
        ruleDict = self.ruleOptions
        ruleDictKeys = list(ruleDict.keys())

        changeCounter = 0
        for field in knownFields:
            iterator = 0
            while iterator <= len(ruleDictKeys) - 1:
                if (field == ruleDictKeys[iterator]):
                    fieldIndex = knownFields.index(field)
                    sqlOption = databaseFields[fieldIndex]
                    type = fieldType[fieldIndex]
                    if changeCounter != len(ruleDictKeys)-1:
                        if type == "string":
                            sqlCommand += "and {0} = \"{1}\" ".format(sqlOption, ruleDict[field])
                            changeCounter += 1
                        elif type == "integer":
                            sqlCommand += "and {0} = {1} ".format(sqlOption, ruleDict[field])
                            changeCounter += 1
                    elif changeCounter == len(ruleDictKeys)-1:
                        if type == "string":
                            sqlCommand += "and {0} = \"{1}\";".format(sqlOption, ruleDict[field])
                            changeCounter += 1
                        elif type == "integer":
                            sqlCommand += "and {0} = {1};".format(sqlOption, ruleDict[field])
                            changeCounter += 1
                iterator += 1

        self.statusCode = "SCC" #Successfull Check Construct
        return sqlCommand


    def formatCommand(self):
        knownActions = ["append", "check", "delete", "insert", "replace", "list", "flush"]
        equivalentActionChar = ["A","C","D","I","R","L","F"]
        actionCharacter = ""
        for action in knownActions:
            if self.actionName == action:
                actionIndex = knownActions.index(action)
                actionCharacter += equivalentActionChar[actionIndex]

        if self.actionName in ["list","flush"]:
            insertString = self.queryInsertConstruct()
            self.executeSQL(insertString,"insert")
            if self.actionName == "list":
                self.statusCode = "LP"
                self.executeSQL(None,"list")
                return None
            elif self.actionName == "flush":
                self.executeSQL(None,"flush")
                finalCommand = "iptables -t {0} -{1}".format(self.tableName,actionCharacter)
                if self.statusCode != "FE":
                    self.statusCode = "SLFC"
                return finalCommand

        elif self.actionName in ["check","delete","replace"]:
            if self.actionName == "check":
                insertString = self.queryInsertConstruct()
                self.executeSQL(insertString,"insert")
                queryString = self.queryCheckConstruct()
                self.executeSQL(queryString,"check")
                return None

            elif self.actionName == "delete":
                queryCheckString = self.queryCheckConstruct()
                self.executeSQL(queryCheckString,"check")
                if self.statusCode == "CY":
                    deleteQuery = "delete from IptablesLogs where id = {0};".format(int(self.ruleID))
                    self.executeSQL(deleteQuery,"delete")
                    if self.statusCode == "UD":
                        return None
                #elif self.statusCode == "CN":
                 #   return None

            if self.statusCode == "CN":
                ruleString = self.formatRuleSpecifications()
                finalCommand = "iptables -t {0} -{1} {2} {3}".format(self.tableName, actionCharacter, self.chainName,ruleString)
                self.statusCode = "SCDRC"
                return finalCommand

            elif self.statusCode == "SD":
                ruleString = self.formatRuleSpecifications()
                self.statusCode = "SD"
                finalCommand = "iptables -t {0} -{1} {2} {3}".format(self.tableName, actionCharacter, self.chainName,ruleString)
                return finalCommand

            elif self.statusCode == "CY":
                return None
        else:
            queryString = self.queryCheckConstruct()
            self.executeSQL(queryString,"check")

            if self.statusCode == "CN":
                queryString = self.queryInsertConstruct()
                self.executeSQL(queryString,"insert")
                if self.statusCode == "SI":
                    ruleString = self.formatRuleSpecifications()
                    if ruleString == None:
                        return None
                    elif ruleString != None:
                        finalCommand = "iptables -t {0} -{1} {2} {3}".format(self.tableName,actionCharacter,self.chainName,ruleString)
                        return finalCommand
                elif self.statusCode == "UI":
                    return None
            elif self.statusCode == "CY":
                return None

    def formatRuleSpecifications(self):
        knownFields = ["Destination", "Source", "Interface IN", "Interface OUT", "Protocol", "Destination Port", "Source Port","SYN", "TCP Flags","Jump"]
        equivalentFieldOption = ["-d", "-s", "-i", "-o", "-p", "--dport", "--sport", "--syn", "--tcp-flags", "-j"]
        ruleDict = self.ruleOptions
        ruleDictKeys = list(ruleDict.keys())

        self.checkRuleParameters()
        if self.statusCode == "URO":
            return None
        elif self.statusCode == "DRO":
            ruleString = ""
            for field in knownFields:
                iterator = 0
                while iterator <= len(ruleDictKeys)-1:
                    if (field == ruleDictKeys[iterator]) and (field != "Jump"):
                        fieldIndex = knownFields.index(field)
                        option = equivalentFieldOption[fieldIndex]
                        ruleString += "{0} {1} ".format(option,ruleDict[field])
                    iterator += 1

            ruleString += "-j {0} ".format(ruleDict["Jump"])
            self.statusCode = "SFC" # Successfull Firewall Construct
            return ruleString


if __name__ == "__main__":
    obj = iptables("filter","append","input",{"Protocol":"tcp","Source":"192.168.102.60","Destination Port":"5000","Jump":"DROP"})
    obj.execute()
