import sqlite3
import datetime
import os

class snortClass():
    def __init__(self,rule,controllerAddr,action):
        self.rulesFile = "/etc/snort/rules/apiRules.rules"
        self.apiFile = "apiRules.rules"
        self.snortConf = "/etc/snort/snort.conf"
        self.rule = rule
        self.action = action
        self.controllerAddr = str(controllerAddr)
        self.status = None

    # Method that goes in the local API database and selects the IP's of the Trusted controllers
    def getIPFromTrustedControllers(self):
        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()

        cursor.execute("select controllerhost from Controllers where trust = 1;")
        result = cursor.fetchall()
        conn.close()

        return result

    # Method that get receives a list of trusted Controller IP's and checks if the the syslog output was already configured for them
    def checkIfSyslogConfigured(self,listOfTrustedIP):
        for IP in listOfTrustedIP:
            print(IP)
            syslogConfString = "output alert_syslog: host = {0}:514, LOG_AUTH LOG_ALERT".format(IP)
            with open(self.snortConf,"r+") as snortfile:
                for line in snortfile:
                    line = line.strip("\n")
                    if line == syslogConfString:
                        self.status = "SC" # Syslog Configured
                        break
                os.system("echo '{0}' >> {1}".format(syslogConfString,self.snortConf))
                snortfile.close()

        self.status = "SSC" # Successfull Syslog Configuration


    # Class method that return the Text response and status code for the status of other methods
    def statusText(self):
        rdeDict = {"Response":"Rule Doesn't Exist","Status":200}
        reDict = {"Response":"Rule Already Exists","Status":400}
        srcDict = {"Response":"Successfull Rule Configuration","Status":200}
        srlDict = {"Response":"Successfull Rule Logging","Status":200}
        srdDict = {"Response":"Succesfull Rule Deletion","Status":200}
        srcoDict = {"Response":"Succesfull Rule Comment","Status":200}
        srucDict = {"Response":"Successfull Rule Uncomment","Status":200}
        uaDict = {"Response":"Unregistered Action","Status":400}
        raDict = {"Response":"Registered Action","Status":200}
        feDict = {"Response":"Rule file Exists","Status":200}
        fdeDict = {"Response":"Rule file doesn't exist","Status":400}
        faiDict = {"Response":"Rule file already included","Status":200}
        fniDict = {"Response":"Rule file not included","Status":400}


        statusDict = {"RDE":rdeDict,"RE":reDict,"SRC":srcDict,"SRL":srlDict,"SRD":srdDict,"SRCo":srcoDict,"SRUc":srucDict,"UA":uaDict,"RA":raDict,"FE":feDict,"FDE":fdeDict,"FAI":faiDict,"FNI":fniDict}

        return statusDict[self.status]

    # Method that checks if file apiRules.rules already exists in the system, if not the file is created
    def checkFileExistance(self):
        response = os.popen(r"ls {0} ; echo $?".format(self.rulesFile)).read()
        response = response.strip("\n")
        if response == "0":
            self.status = "FE" # File exists
        else:
            self.status = "FDE" # File doesn't exists
            os.system(r"touch {0}".format(self.rulesFile))

    # Method that checks if the Action passed by the controller is a valid action
    def checkAction(self):
        knownActions = ["Create","Delete","Comment","Uncomment"]
        if not self.action in knownActions:
            self.status = "UA" # Unregistered Action
        else:
            self.status = "RA" # Registered Action

    # Method that checks is the passed rule already exists in the local API database
    def checkExistance(self):
        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()

        cursor.execute("select * from RulesLogs where ruleString = \"{0}\";".format(self.rule))
        result = cursor.fetchall()
        conn.close()

        if len(result) == 0:
            self.status = "RDE" # Rule Doesn't Exists
        else:
            self.status = "RE" # Rule Exists

    # Method that checks if the apiRules.rules is included in the snort.conf file
    def checkIfFileIncluded(self):
        with open(self.snortConf,"r+") as snortfile:
            for line in snortfile:
                line = line.strip("\n")
                if "include $RULE_PATH/"+self.apiFile == line:
                    self.status = "FAI" # File Already Included
                    break

            self.status = "FNI" # File Not Included
            os.system(r"echo 'include $RULE_PATH/{0}' >> {1}".format(self.apiFile,self.snortConf))

    # Method that logs a new rule in the local API database if it already doesn't exists
    def logRule(self):
        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()

        currentTime = datetime.datetime.today().strftime('%Y-%m-%d')

        cursor.execute("insert into RulesLogs (controlleraddr,receivetime,ruleString) values (\"{0}\",\"{1}\",\"{2}\");".format(self.controllerAddr,currentTime,self.rule))
        conn.commit()

        self.status = "SRL" # Successfull Rule Logging

        conn.close()

    # Method that appends the passed rule to the apiRules.rules file
    def ruleExecute(self):
        os.system("echo '{0}' >> {1}".format(self.rule,self.rulesFile))
        self.status = "SRC" # Successfull rule configuration

    # Method that rewrites the apiRules.rules file depending of the passed action (Delete, Comment, Uncomment).
    #
    # If the action is to Delete a rule, all the lines inside apiRules.rules except the line of the given rule will be appended to a volatile file
    # that will later be appended to apiRules.rules, resulting in a rule deletion.
    #
    # If the action is to Comment a rule, all the lines inside apiRules.rules except the line of the given rule will be appended normally to
    # a volatile file, the line that corresponds to the rule however will be appended to the volatile file with a # at the beggining. The volatile
    # file will later be appended to apiRules.rules resulting in the Comment of a specific rule.
    #
    # If the action is to Uncomment a rule, all the lines inside apiRules.rules except the line of the given rule will be appended normally to a
    # volatile file, the line that matches : #+rule will be appended without the # at the beginning. The volatile file will later be appended to
    # apiRules.rules resulting in a Uncomment of a specific rule.
    def snortRewrite(self):
        if self.action == "Delete":
            with open(self.rulesFile,"r+") as file:
                for line in file:
                    line = line.strip("\n")
                    if line == self.rule:
                        continue
                    elif line == "#"+self.rule:
                        continue
                    elif line != self.rule:
                        os.system("echo '{0}' >> volatile/volatileSnortrules".format(line))
                os.system("cat volatile/volatileSnortrules > {0} ; rm -f volatile/volatileSnortrules".format(self.rulesFile))
                file.close()
            self.status = "SRD" # Successfull Rule Deletion

        elif self.action == "Comment":
            with open(self.rulesFile,"r+") as file:
                for line in file:
                    line = line.strip("\n")
                    if line == self.rule:
                        line = "#"+line
                        os.system("echo '{0}' >> volatile/volatileSnortrules".format(line))
                    elif line != self.rule:
                        os.system("echo '{0}' >> volatile/volatileSnortrules".format(line))
                os.system("cat volatile/volatileSnortrules > {0} ; rm -f volatile/volatileSnortrules".format(self.rulesFile))
                file.close()
            self.status = "SRCo" # Succesfull Rule Comment

        elif self.action == "Uncomment":
            with open(self.rulesFile,"r+") as file:
                for line in file:
                    line = line.strip("\n")
                    if line == "#"+self.rule:
                        os.system("echo '{0}' >> volatile/volatileSnortrules".format(self.rule))
                    elif line != self.rule:
                        os.system("echo '{0}' >> volatile/volatileSnortrules".format(line))
                os.system("cat volatile/volatileSnortrules > {0} ; rm -f volatile/volatileSnortrules".format(self.rulesFile))
                file.close()
            self.status = "SRUc" # Successfull Rule Uncomment

    # Method that retrieves the rule ID in the local API database to correctly delete the rule from the API database
    def deleteRule(self):
        conn = sqlite3.connect("database/apiConfiguration.db")
        cursor = conn.cursor()
        cursor.execute("select id from RulesLogs where ruleString = \"{0}\";".format(self.rule))
        result = cursor.fetchall()
        id = result[0][0]
        cursor.execute("delete from RulesLogs where id = {0};".format(int(id)))
        conn.commit()
        conn.close()

    # Method that checks if apiRules.rules exists in the filesystem, checks if he is included in snort.conf, checks if the passed Action is a valid
    # one, to later execute the action (Delete, Comment, Uncomment, Create) on a passed rule
    def execute(self):
        self.checkFileExistance()
        self.checkIfFileIncluded()
        listOfIP = self.getIPFromTrustedControllers()
        self.checkIfSyslogConfigured(listOfIP)

        self.checkAction()
        if self.status == "RA":
            if self.action == "Create":
                self.checkExistance()
                if self.status == "RE":
                    return self.statusText()
                elif self.status == "RDE":
                    self.logRule()
                    self.ruleExecute()
                    return self.statusText()
            elif self.action == "Delete":
                self.checkExistance()
                if self.status == "RE":
                    self.deleteRule()
                    self.snortRewrite()
                    return self.statusText()
                elif self.status == "RDE":
                    return self.statusText()
            elif self.action == "Comment":
                self.checkExistance()
                if self.status == "RE":
                    self.snortRewrite()
                    return self.statusText()
                elif self.status == "RDE":
                    return self.statusText()
            elif self.action == "Uncomment":
                self.checkExistance()
                if self.status == "RE":
                    self.snortRewrite()
                    return self.statusText()
                elif self.status == "RDE":
                    return self.statusText()

        elif self.status == "UA":
            return self.statusText()