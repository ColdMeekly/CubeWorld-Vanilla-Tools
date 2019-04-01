#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from psutil import process_iter, net_connections
from threading import Thread, Event
from sys import platform
from os import startfile
from json import dumps

# Game Settings

G_HOSTNAME      =   'screenman.pro'
G_PROCESS       =   'Server.exe'
G_PATH          =   'D:\\Games\\Cube World\\cw-miuchiz\\Cube World\\'
G_MAXPLAYERS    =   60

# API Settings

A_PORT          =   8082
A_HOST          =   '0.0.0.0'

# Monitor Settings

M_SECONDSDELAY  =   10

# =============== DO NOT EDIT BELOW THIS LINE ===============

class ServerManager:
    def __init__(self, hostname, process, path):
        self.hostname   = hostname
        self.process    = process
        self.path       = path
        self.exe        = self.path + self.process

        self.startServer()

        # Fetch the port automatically
        self._port       = self.getServerPort()
    
    def isServerOnline(self):
        try:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect(('127.0.0.1', self._port))
            return True
        except Exception:
            return False
    
    def getRunningServer(self):
        for process in process_iter():
            # You have to call process.name to be able to call process.exe WTF!
            if process.name() == self.process:
                if process.exe() == self.exe:
                    return process
        return False

    def isServerRunning(self):
        return self.getRunningServer() != False

    def startServer(self):
        if not self.isServerRunning():
            startfile(self.exe)
            print("[UNKOWN] Server Started!")

    def closeServer(self):
        server = self.getRunningServer()
        if server != False:
            server.kill()
  
    def restartServer(self):
        if self.isServerRunning():
            self.closeServer()
        self.startServer()

    def getServerPort(self):
        if not self.isServerRunning():
            return

        processID = self.getRunningServer().pid
        for connection in net_connections(kind='inet'):
            if (connection.family, connection.type) != ( 2, 1 ) or connection.pid != processID or connection.status != 'LISTEN':
                continue
            return connection.laddr[1]
        return False

    # Common statuses: ESTABLISHED, LISTEN
    def countNetwork(self, status='ESTABLISHED'):
        if not self.isServerRunning():
            return

        processID = self.getRunningServer().pid
        count = 0

        for connection in net_connections(kind='inet'):
            if (connection.family, connection.type) != ( 2, 1 ) or connection.pid != processID or connection.status != status:
                continue
            count += 1
        return count
    
    
class APIManager(BaseHTTPRequestHandler):
    def __init__(self, serverInstance, *args):
        self.serverInstance = serverInstance
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        seed = 0
        with open( "server.cfg", encoding="utf8" ) as f:
            seed = int(f.readlines( )[0])
        
        x = {
            "players"   :   self.serverInstance.countNetwork(),
            "maxplayers":   G_MAXPLAYERS,
            "seed"      :   seed,
            "platform"  :   platform,
            "hostname"  :   self.serverInstance.hostname
            }
        message = dumps( x )

        self.wfile.write(bytes(message, "utf8"))
        return

    def log_message(self, format, *args):
        return

class ServerMonitor(Thread):
    def __init__(self, cubeworld, interval, event):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval
        self.cubeworld = cubeworld
    
    def run(self):
        while not self.stopped.wait(self.interval):
            if not self.cubeworld.isServerRunning():
                print("** [OFFLINE] **  CRASHED - Starting Server")
                self.cubeworld.startServer()
            elif not self.cubeworld.isServerOnline():
                print("** [OFFLINE] **  DEADLOCKED - Restarting Server")
                self.cubeworld.restartServer()
            print(f'[ONLINE] {self.cubeworld.countNetwork()}/{G_MAXPLAYERS}') if self.cubeworld.isServerOnline() else print("** [OFFLINE] **")

class APIWrapper(Thread):
    def __init__(self, serverInstance, address, event):
        Thread.__init__(self)
        self.stopped = event
        self.serverInstance = serverInstance
        self.address = address
    
    def run(self):
        def HTTP_Handler(*args):
            APIManager(self.serverInstance, *args)
        server = HTTPServer(self.address, HTTP_Handler)
        print(f'API Launched on http://127.0.0.1:{self.address[1]}/')
        server.serve_forever()

            
if __name__ == "__main__":
    cubeworld = ServerManager(G_HOSTNAME, G_PROCESS, G_PATH)
    my_event = Event()
    thread  = ServerMonitor(cubeworld, M_SECONDSDELAY, my_event)
    thread.start()
    my_event2 = Event()
    thread2  = APIWrapper(cubeworld, ('', A_PORT), my_event)
    thread2.start()
    thread1.join()
    thread2.join()
    cubeworld.closeServer()

    


