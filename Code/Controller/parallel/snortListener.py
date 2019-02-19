LOG_FILE = 'logs/snortalerts.log'
HOST, PORT = "0.0.0.0", 514

import logging
import socketserver
import os
import datetime

os.system(r"touch {0}".format(LOG_FILE))

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')

class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        currentTime = datetime.datetime.today().strftime('%Y-%m-%d')
        data = "Time: {3} - Source: {0}:{1} -> {2}".format(str(self.client_address[0]),str(self.client_address[1]),str(data),str(currentTime))

        print("SyslogServer - Arriving Syslog packet -  {0}".format(data))

        logging.info(str(data))
        os.system(r"echo '{0}' >> logs/youlogfile.log".format(data))
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