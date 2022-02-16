#!/bin/env python3

import socket
import logger as lg
import  threading
import sys
import os
import time
from func import getHash

# defs
server_host = '0.0.0.0'
server_port = 5000
cwd = './uploads/'

def log(func, cmd):
        logmsg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
        print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (logmsg, cmd))

class Server(threading.Thread):
    def __init__(self, commSock, address):
        threading.Thread.__init__(self)
        self.pasv_mode     = False
        self.rest          = False
        self.cwd           = cwd
        self.commSock      = commSock   # communication socket as command channel
        self.address       = address

    def sendWelcome(self):
        """
        when connection created with client will send a welcome message to the client
        """
        self.sendCommand('220 Welcome.\r\n')


    def run(self):
        self.sendWelcome()
        while True:
            try:
                data = self.commSock.recv(1024).rstrip()
                try:
                    cmd = data.decode('utf-8')
                except AttributeError:
                    cmd = data
                if not cmd:
                    break
                #print(data)
            except socket.error as err:
                pass

            try:
                cmd, arg = cmd[:4].strip().upper(), cmd[4:].strip() or None
                func = getattr(self, cmd)
                func(arg)
            except AttributeError as err:
                pass


    def TYPE(self, type):
        log('TYPE', type)
        self.mode = type
        if self.mode == 'I':
            self.sendCommand('200 Binary mode.\r\n')
        elif self.mode == 'A':
            self.sendCommand('200 Ascii mode.\r\n')

    def PASV(self, cmd):
        log("PASV", cmd)
        self.pasv_mode  = True
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((server_host, 0))
        self.serverSock.listen(5)
        addr, port = self.serverSock.getsockname( )
        self.sendCommand('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(addr.split('.')), port>>8&0xFF, port&0xFF))

    def STOR(self, data):
        data = data.split(';')
        filename = data[0]
        file_hash = data[1]
        directory_path = self.cwd + os.path.dirname(filename)
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
            except:
                pass
        pathname = self.cwd  + filename

        log('STOR', pathname)
        try:
            if self.mode == 'I':
                file = open(pathname, 'wb')
            else:
                file = open(pathname, 'w')
        except OSError as err:
            log('STOR', err)

        self.sendCommand('150 Opening data connection.\r\n' )
        self.startDataSock( )
        while True:
            data = self.dataSock.recv(1024)
            if not data: break
            file.write(data)
        file.close( )
        self.stopDataSock(pathname, file_hash)
        self.sendCommand('226 Transfer completed.\r\n')

    def startDataSock(self):
        log('startDataSock', 'Opening a data channel')
        try:
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.pasv_mode:
                self.dataSock, self.address = self.serverSock.accept( )

            else:
                self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dataSock.connect((self.dataSockAddr, self.dataSockPort))
        except socket.error as err:
            log('startDataSock', err)

    def stopDataSock(self, filepath, file_hash):
        log('stopDataSock', 'Closing a data channel')
        try:
            self.dataSock.close( )
            if self.pasv_mode:
                self.serverSock.close( )
        except socket.error as err:
            log('stopDataSock', err)
        if getHash(filepath) != file_hash:
            self.sendCommand('501 File integrity check failed.\r\n')
            os.remove(pathname)


    def sendCommand(self, cmd):
        self.commSock.send(cmd.encode('utf-8'))

    def sendData(self, data):
        self.dataSock.send(data.encode('utf-8'))


def server_listener():
    global  s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server_host, server_port))
    s.listen(5)

    lg.success('[✅] Server started: {}:{}'.format(server_host, server_port))
    while True:
        con, addr = s.accept()
        f = Server(con, addr)
        f.start()
        lg.warning('[🗂] New connection from: {} <=> {}'.format(con, addr))




if __name__ == '__main__':
    lg.default('[ℹ️] Starting server...: Press Ctrl + C to stop.')
    t = threading.Thread(target=server_listener)
    t.start()
