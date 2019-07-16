import os
import psutil
from random import randint
import shutil
import re
# -*- coding: utf-8 -*-

# --------------- Definição das funções associadas a gerenciamento de portas -------------------#

# Função que coleta as informações acerca das portas por protocolo, tanto udp quanto
def gatherPortInfo(protocol):
    portsArray = []
    if protocol == "all":
        tcpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'tcp\b'").read()
        udpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'udp\b'").read()
        portsArray.extend([tcpOpenPorts,udpOpenPorts])
    elif protocol == "tcp":
        tcpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'tcp\b'").read()
        portsArray.append(tcpOpenPorts)
    elif protocol == "udp":
        udpOpenPorts = os.popen(r"netstat -tulpn | grep -P 'udp\b'").read()
        portsArray.append(udpOpenPorts)

    return portsArray

# Função que realiza a criação de arquivos voláteis para armazenamento temporário de valores
# quantity = quantidade de arquivos aleatórios a serem gereados - Tipo: integer
# rangeBegin = início de intervalo de seleção pseudo aleatória para criação de arquivos - Tipo: integer
# rangeEnd = fim do intervalo de seleção pseudo aleatória - Tipo: integer
def generateRandomFiles(quantity,rangeBegin, rangeEnd):
    fileArray = []
    i = 1
    while i <= quantity:
        volatileFile = str(randint(rangeBegin, rangeEnd))
        fileArray.append(volatileFile)
        i += 1

    return fileArray

# Função que realiza a criação de um dicionário a partir do protocolo
# type = Tipo de protocolo - Valores: "TCP" ou "UDP"
# sourceDict = dicionário origem onde serão criados os pares - Tipo: estrutura de dados dicionário {}
# portString = Número da porta - Tipo: string
# serviceString = Nome do serviço - Tipo: string
# pidString =  PID (Process Identifier) do serviço - Tipo: string
def generatePortDict(type, sourceDict,portString,addressString,serviceString,pidString):
    characteristicsArray = ["Porta","Endereço","Nome do processo","PID do processo","Protocolo"]
    stringArray = [portString,addressString,serviceString,pidString]
    i = 0
    for characteristic in characteristicsArray:
        if characteristic != "Protocolo":
            sourceDict[characteristic] = stringArray[i]
        elif characteristic == "Protocolo":
            sourceDict["Protocolo"] = type
        i += 1

    return sourceDict

# Função que realiza o corte das string mais gerais para facilitar o processamento
# string = Linha que será cortada pelas colunas - Tipo: string
def portStringCut(string):
    cutArray = []
    firstLineCut = os.popen(r"echo '{0}' | cut -c1-38".format(string)).read()
    secondLineCut = os.popen(r"echo '{0}' | cut -c78-100".format(string)).read()
    cutArray.extend((firstLineCut,secondLineCut))

    return cutArray

# Função que realiza o processamento da string cortada para retirada completa das informações
# cutArray = Array que contém as strings cortadas pelas colunas - Tipo: string
def portStringProcess(cutArray):
    processArray = []
    firstCutPort = os.popen(r"echo '{0}' | grep -Po ':\K\d+'".format(cutArray[0])).read()
    firstCutPort = firstCutPort.strip("\n")
    firstCutAddress = re.findall(r'[0-9]+(?:\.[0-9]+){3}',cutArray[0])
    firstCutAddress = firstCutAddress[0].strip("\n")
    secondCutService = os.popen(r"echo '{0}' | grep -Po '/\K.*'".format(cutArray[1])).read()
    secondCutService = secondCutService.replace(" ", "")
    secondCutService = secondCutService.strip("\n")
    secondCutPID = os.popen(r"echo '{0}' | grep -Po '\K\d+'".format(cutArray[1])).read()
    secondCutPID = secondCutPID.strip("\n")

    processArray.extend((firstCutPort,firstCutAddress,secondCutService,secondCutPID))

    return processArray

# Função que organiza os dicionários associados à portas a partir de um tipo de protocolo
# arrayOfDicts = Array que contém todos os dicionários vindos de generatePortDict()
# protocol = Tipo de protocolo  - Tipo: string "TCP" ou "UDP"
def sortByProtocol(arrayOfDicts,protocol):
    protocolDicts = []
    for object in arrayOfDicts:
        if object["Protocolo"] == protocol:
            protocolDicts.append(object)

    return protocolDicts

# --------------- Definição das funções associadas a gerenciamento de disco -------------------#

# Função que pega as informações acerca de todos os discos /dev/* como: nome completo do disco /dev/sda e ponto de montagem do disco
def gatherDiskInfo():
    valuesArray = []
    diskPath = os.popen(r"mount | grep ^/dev").read()
    mountPoint = os.popen(r"mount | grep ^/dev | grep -Po 'on \K.*'").read()
    valuesArray.extend((diskPath, mountPoint))

    return valuesArray

# Função que pega as infnormações acerca de um disco específico e retorna o nome do disco com seu ponto de montagem
# diskName = Nome do disco Ex: /dev/sda - Tipo: string
def gatherSpecificDiskInfo(diskName):
    valuesArray = []
    mountPoint = os.popen(r"mount | grep ^{0} | grep -Po 'on \K.*'".format(diskName)).read()
    valuesArray.extend((diskName,mountPoint))

    return valuesArray

def gatherDiskMetrics(devicePath, mountPoint, unity):
    responseList = []
    i = 0
    while i <= len(devicePath) - 1:
        deviceDict = {}
        infoDict = {}

        fileSystemPath = mountPoint[i]
        diskUsage = shutil.disk_usage(fileSystemPath)
        unities = ["tb","gb","mb","b"]
        calculations = [1024000000000,1024000000,1024000,1]
        for un in unities:
            if un == unity:
                position = unities.index(un)
                infoDict["Disco total"] = (diskUsage[0]/calculations[position])
                infoDict["Disco usado"] = (diskUsage[1]/calculations[position])
                infoDict["Disco livre"] = (diskUsage[2]/calculations[position])
                infoDict["Unidade"] = unity


        deviceDict[devicePath[i]] = infoDict
        responseList.append(deviceDict)
        i += 1

    return responseList

class System():

    def __init__(self,info):
        self.systeminfo = info

    # Método da classe System que pega o percentual utilizado dos núcleos da CPU e retorna um dicionário em que
    # as chaves são os núcleos e os valores as porcentagens.
    def cpu(self):
        cpuPercent = psutil.cpu_percent(interval=0.1,percpu=True)
        percentDict = {}
        i = 1
        for cpu in cpuPercent:
                percentDict["CPU{0}".format(i)] = cpuPercent[i-1]
                i += 1
        # print(percentDict)
        return percentDict

    # Método da classe System que pega as informações de utilização acerca da memória RAM e retorna
    # um dicionário cujas chaves são descritas no array fields
    def mem(self,*args):
        mem = psutil.virtual_memory()
        memDict = {}
        fields = ["Total", "Disponível", "Percentual Usado", "Usado", "Livre", "Ativa", "Inativa", "Buffer", "Cached", "Shared", "Slab"]
        i = 0
        for information in mem:
            memDict[fields[i]] = information
            i += 1

        return memDict

    # Método da classe System que pega as informações acerca das portas abertas e retorna um dicionário
    # cujas chaves são "Nome do processo", "PID do processo", "Porta", "Protocolo"
    def ports(self,protocol):
        portsArray = gatherPortInfo(protocol)
        if protocol == "all":
            fileArray = generateRandomFiles(2,0,10000)
        else:
            fileArray = generateRandomFiles(1,0,10000)

        i = 1
        arrayOfDicts = []
        for file in fileArray:
            os.system("touch volatile/{0}".format(file))
            protocolFile = open("volatile/{0}".format(file),"r+")
            protocolFile.write(portsArray[i-1])
            protocolFile = open("volatile/{0}".format(file), "r+")
            for line in protocolFile:
                if (i == 1) and (protocol == "all") or (protocol == "tcp"):
                    tcp = {}
                elif (i == 2) or (protocol == "udp"):
                    udp = {}
                cutLines = portStringCut(line)

                processArray = portStringProcess(cutLines)

                if (i == 1) and (protocol == "all") or (protocol == "tcp"):
                    tcpDict = generatePortDict("TCP",tcp,processArray[0],processArray[1],processArray[2],processArray[3])
                    arrayOfDicts.append(tcpDict)
                elif (i == 2) or (protocol == "udp"):
                    udpDict = generatePortDict("UDP",udp,processArray[0],processArray[1],processArray[2],processArray[3])
                    arrayOfDicts.append(udpDict)

            protocolFile.close()
            os.system("rm -f ./volatile/{0}".format(file))
            i += 1

        if protocol == "all":
            tcpDicts = sortByProtocol(arrayOfDicts,"TCP")
            udpDicts = sortByProtocol(arrayOfDicts,"UDP")
        elif protocol == "udp":
            udpDicts = sortByProtocol(arrayOfDicts,"UDP")
        elif protocol == "tcp":
            tcpDicts = sortByProtocol(arrayOfDicts,"TCP")

        finalDict = {}
        if protocol == "all":
            finalDict["TCP"] = tcpDicts
            finalDict["UDP"] = udpDicts
        elif protocol == "tcp":
            finalDict["TCP"] = tcpDicts
        elif protocol == "udp":
            finalDict["UDP"] = udpDicts

        return finalDict

    # Método da classe System que pega as informações acerca da utilização de disco no sistema e retorna
    # um dicionário com as chaves: "Disco livre", "Disco total", "Disco usado", "Unidade"
    def disk(self,diskName,byteUnity):
        if diskName == "all":
            valuesArray = gatherDiskInfo()
        else:
            valuesArray = gatherSpecificDiskInfo(diskName+" ")

        pathArray = generateRandomFiles(2, 10000, 20000)

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

        reponseList = gatherDiskMetrics(devicePath,mountPath,byteUnity)

        return reponseList

if __name__ == "__main__":
    obj = System("CPU")
    print(obj.gather())