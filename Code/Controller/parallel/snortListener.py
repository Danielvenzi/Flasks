LOG_FILE = 'logs/snortalerts.log'
HOST, PORT = "0.0.0.0", 514

import logging
import socketserver
import os
import datetime
import sqlite3
import time
import syslogParser
import json

os.system(r"touch {0}".format(LOG_FILE))

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')

class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        currentTime = datetime.datetime.today().strftime('%Y-%m-%d')
        #data = "Time: {3} - Source: {0}:{1} -> {2}".format(str(self.client_address[0]),str(self.client_address[1]),str(data),str(currentTime))

        #print("SyslogServer - Arriving Syslog packet -  {0}".format(data))

        #messages = syslogParser.read_log_file("parallel/logSnort2.txt")

        parsed_syslog = syslogParser.interpretAlert(data)
        parsed_syslog_keys = list(parsed_syslog.keys())
        if not "Source" in parsed_syslog_keys and not "Destination" in parsed_syslog_keys:
            pass
        else:
            conn = sqlite3.connect("database/controllerConfiguration.db")
            cursor = conn.cursor()

            if (parsed_syslog["Type"] == "TCP") or (parsed_syslog["Type"] == "UDP"):
                #print("Temos um tcp")
                source_ip = parsed_syslog["Source"]
                destination_ip = parsed_syslog["Destination"]

                sourced_ip = os.popen(r"echo '{0}' | cut -d: -f1".format(source_ip)).read()
                sourced_ip = sourced_ip.strip("\n")
                source_port = os.popen(r"echo '{0}' | cut -d: -f2".format(source_ip)).read()
                source_port = source_port.strip("\n")

                destinated_ip = os.popen(r"echo '{0}' | cut -d: -f1".format(destination_ip)).read()
                destinated_ip = destinated_ip.strip("\n")
                destinated_port = os.popen(r"echo '{0}' | cut -d: -f2".format(destination_ip)).read()
                destinated_port = destinated_port.strip("\n")

                final_parsed = {"Source":sourced_ip,
                                "Destination":destinated_ip,
                                "Source Port":source_port,
                                "Destination Port":destinated_port,
                                "Protocol":parsed_syslog["Type"]}

                print(final_parsed)
                try:
                    cursor.execute("""select * from knownAttackers where protocol=\"{0}\" and
                                dstaddr=\"%s\" and
                                srcaddr=\"%s\" and
                                dstport=%d and
                                srcport=%d;""" % (parsed_syslog["Type"],
                                                  destinated_ip,sourced_ip,int(destinated_port),int(source_port)))
                    result = cursor.fetchall()

                    if len(result) == 0:

                        current_milli_time = int(round(time.time() * 1000))

                        if ":" in parsed_syslog["Source"]:
                            pass
                        elif not ":" in parsed_syslog["Source"]:
                            try:
                                cursor.execute("insert into knownAttackers (srcaddr,dstaddr,srcport,dstport,protocol,ttl) values (\"{0}\",\"{1}\",{2},{3},\"{4}\",{5});".format(sourced_ip,destinated_ip,source_port,destinated_port,final_parsed["Protocol"],current_milli_time))
                                conn.commit()
                                conn.close()
                            except sqlite3.OperationalError as err:
                                print("\tERROR - Snort Listener TCP/UDP -Internal server error: {0}".format(err))
                except ValueError:
                    pass


            elif parsed_syslog["Type"] == "ICMP":
                current_milli_time = int(round(time.time() * 1000))

                try:
                    cursor.execute("""select id from knownAttackers where protocol=\"{0}\"and 
                                        dstaddr=\"{1}\"
                                        and srcaddr=\"{2}\";""".format(parsed_syslog["Type"],
                                                                   parsed_syslog["Destination"],
                                                                   parsed_syslog["Source"]))
                    result = cursor.fetchall()

                    if len(result) == 0:

                        if ":" in parsed_syslog["Source"]:
                            pass
                        if not ":" in parsed_syslog["Source"]:
                            try:
                                cursor.execute("insert into knownAttackers (srcaddr,dstaddr,protocol,ttl) values (\"{0}\",\"{1}\",\"{2}\",{3});".format(parsed_syslog["Source"],parsed_syslog["Destination"],parsed_syslog["Type"],current_milli_time))
                                conn.commit()
                            except sqlite3.OperationalError as err:
                                print("\tERROR - Snort Listener ICMP - Internal server error: {0}".format(err))

                except ValueError:
                    pass


        logging.info(str(data))
        #os.system(r"echo '{0}' >> logs/youlogfile.log".format(data))
        os.system(r"sed -i -e 's| \* Running on http://0\.0\.0\.0:80/ (Press CTRL+C to quit)||' {0} ;  sed -i '/^\s*$/d' {0}".format(LOG_FILE))

def mainSyslogServer():
    try:
        server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
        print(" * Status: succesfull syslog server initialization...")
        print(" * Server running on: {0}:{1} ...".format(HOST,PORT))
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Cntrl+C Pressed. Shutting down.")

if __name__ == "__main__":
    try:
        server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")