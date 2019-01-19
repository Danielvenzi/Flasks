import os
import psutil
from random import randint
import shutil

class System():

    def __init__(self,info):
        self.systeminfo = info


    def gather(self):
        if self.systeminfo == "Geral":
            cpu = self.cpu()
            mem = self.mem()
            ports = self.ports()
            disk = self.disk()
            print("Geral")

        elif self.systeminfo == "CPU":
            cpu = self.cpu()
            return cpu

        elif self.systeminfo == "MEM":
            mem = self.mem()
            return mem

        elif self.systeminfo == "PORT":
            ports = self.ports()
            return ports

        elif self.systeminfo == "DISK":
            disk = self.disk()
            return disk

    def cpu(self):
        cpuPercent = psutil.cpu_percent(interval=0.1,percpu=True)
        percentDict = {}
        i = 1
        for cpu in cpuPercent:
                percentDict["CPU{0}".format(i)] = cpuPercent[i-1]
                i += 1
        # print(percentDict)
        return percentDict


    def mem(self):
        mem = psutil.virtual_memory()
        memDict = {}
        fields = ["Total", "Disponível", "Percentual Usado", "Usado", "Livre", "Ativa", "Inativa", "Buffer", "Cached", "Shared", "Slab"]
        i = 0
        for information in mem:
            memDict[fields[i]] = information
            i += 1

        return memDict


    def ports(self):
        portsArray = []
        tcpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'tcp\b'").read()
        udpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'udp\b'").read()
        portsArray.extend([tcpOpenPorts,udpOpenPorts])

        fileArray = []
        volatileUdpFile = str(randint(0,10000))
        volatileTCPFile = str(randint(0,10000))
        fileArray.extend([volatileTCPFile, volatileUdpFile])
        i = 1

        arrayOfDicts = []

        for file in fileArray:
            os.system("touch volatile/{0}".format(file))

            protocolFile = open("volatile/{0}".format(file),"r+")
            protocolFile.write(portsArray[i-1])
            protocolFile = open("volatile/{0}".format(file), "r+")
            for line in protocolFile:
                if i == 1:
                    tcp = {}
                elif i == 2:
                    udp = {}
                firstLineCut = os.popen(r"echo '{0}' | cut -c1-38".format(line)).read()
                secondLineCut = os.popen(r"echo '{0}' | cut -c78-100".format(line)).read()

                firstCutPort = os.popen(r"echo '{0}' | grep -Po ':\K\d+'".format(firstLineCut)).read()
                secondCutService = os.popen(r"echo '{0}' | grep -Po '/\K.*'".format(secondLineCut)).read()
                secondCutService = secondCutService.replace(" ","")
                secondCutPID = os.popen(r"echo '{0}' | grep -Po '\K\d+'".format(secondLineCut)).read()

                if i == 1:
                    tcp["Porta"] = firstCutPort.strip("\n")
                    tcp["Nome do processo"] = secondCutService.strip("\n")
                    tcp["PID do processo"] = secondCutPID.strip("\n")
                    tcp["Protocolo"] = "TCP"
                    arrayOfDicts.append(tcp)
                elif i == 2:
                    udp["Porta"] = firstCutPort.strip("\n")
                    udp["Nome do processo"] = secondCutService.strip("\n")
                    udp["PID do processo"] = secondCutPID.strip("\n")
                    udp["Protocolo"] = "UDP"
                    arrayOfDicts.append(udp)

            protocolFile.close()
            os.system("rm -f ./volatile/{0}".format(file))
            i += 1

        tcpDicts = []
        for object in arrayOfDicts:
            if object["Protocolo"]  == "TCP":
                tcpDicts.append(object)

        udpDicts = []
        for object in arrayOfDicts:
            if object["Protocolo"] == "UDP":
                udpDicts.append(object)

        finalDict = {}
        finalDict["TCP"] = tcpDicts
        finalDict["UDP"] = udpDicts

        return finalDict


    def disk(self):
        valuesArray = []
        diskPath = os.popen(r"mount | grep ^/dev").read()
        mountPoint = os.popen(r"mount | grep ^/dev | grep -Po 'on \K.*'").read()
        valuesArray.extend((diskPath,mountPoint))

        pathArray = []
        volatileDiskPath = randint(10000,20000)
        volatileMountPointPath = randint(10000,20000)
        pathArray.extend((volatileDiskPath,volatileMountPointPath))

        j = 0
        devicePath = []
        mountPath = []
        for file in pathArray:
            os.system("touch volatile/{0}".format(file))
            diskFile = open("volatile/{0}".format(file),"r+")
            diskFile.write(valuesArray[j])
            diskFile = open("volatile/{0}".format(file),"r+")


            for line in diskFile:
                device = ""
                i = 0
                while i <= len(line):
                    if line[i] != " ":
                        device += line[i]
                    elif line[i] == " ":
                        break
                    i += 1
                if j == 0:
                    devicePath.append(device)
                elif j == 1:
                    mountPath.append(device)
            os.system("rm -f volatile/{0}".format(file))
            j += 1

        responseList = []
        i = 0
        while i <= len(devicePath)-1:
            deviceDict = {}
            infoDict = {}

            fileSystemPath = mountPath[i]
            diskUsage = shutil.disk_usage(fileSystemPath)
            infoDict["Disco total"] = diskUsage[0]
            infoDict["Disco usado"] = diskUsage[1]
            infoDict["Disco livre"] = diskUsage[2]

            deviceDict[devicePath[i]] = infoDict
            responseList.append(deviceDict)
            i += 1

        return responseList

if __name__ == "__main__":
    obj = System("CPU")
    print(obj.gather())