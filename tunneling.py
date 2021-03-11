#!/usr/bin/python3

import sys
from PySide2.QtCore import QCoreApplication, Slot, QTimer
from PySide2.QtNetwork import QTcpServer, QUdpSocket, QHostAddress

from mytcpsocket import MyTCPSocket

REMOTE_HOST = "192.168.0.208"
REMOTE_TCP_PORT = 3001
REMOTE_UDP_PORT = 52001

LOCAL_TCP_PORT = 3001
LOCAL_UDP_PORT = 52001

class App():
    tpcLocal = None
    udpResponseIP = None
    udpResponsePort = None

    def __init__(self, *args, **kwargs):
        self.tcpServer = QTcpServer()
        self.tcpServer.listen(QHostAddress('0.0.0.0'), LOCAL_TCP_PORT)
        self.tcpServer.newConnection.connect(self.procNewConn)

        self.udpServer = QUdpSocket()
        self.udpServer.bind(QHostAddress('0.0.0.0'), LOCAL_UDP_PORT)
        self.udpServer.readyRead.connect(self.udpL2R)

        self.tcpRemote = MyTCPSocket()
        self.tcpRemote.readyRead.connect(self.tcpR2L)
        self.tcpRemote.open(REMOTE_HOST, REMOTE_TCP_PORT)

        self.udpRemote = QUdpSocket()
        self.udpRemote.readyRead.connect(self.udpR2L)

    @Slot()
    def procNewConn(self):
        self.tpcLocal = self.tcpServer.nextPendingConnection()
        self.tpcLocal.readyRead.connect(self.tcpL2R)
        print("cliente conectado")

    @Slot()
    def tcpL2R(self):
        data = self.tpcLocal.readAll()
        print("TPC L2R: %s" % data)
        self.tcpRemote.write(data)

    @Slot()
    def tcpR2L(self):
        data = self.tcpRemote.readAll()
        print("TPC R2L: %s" % data)
        self.tpcLocal.write(data)

    @Slot()
    def udpL2R(self):
        while self.udpServer.hasPendingDatagrams() == True:
            datagram = self.udpServer.receiveDatagram()
            data = datagram.data()
            print("UDP L2R: %s" % data)
            self.udpResponseIP = datagram.senderAddress()
            self.udpResponsePort = datagram.senderPort()
            self.udpRemote.writeDatagram(data, QHostAddress(REMOTE_HOST), REMOTE_UDP_PORT)

    @Slot()
    def udpR2L(self):
        while self.udpRemote.hasPendingDatagrams() == True:
            datagram = self.udpRemote.receiveDatagram()
            data = datagram.data()
            print("UDP R2L: %s" % data)
            self.udpServer.writeDatagram(data, self.udpResponseIP, self.udpResponsePort)

if __name__ == "__main__":
    app=QCoreApplication(sys.argv)

    MyApp = App()

    sys.exit(app.exec_())