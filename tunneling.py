#!/usr/bin/python3

import sys
from PySide2.QtCore import QCoreApplication, Slot, QTimer
from PySide2.QtNetwork import QTcpServer, QTcpSocket, QUdpSocket, QHostAddress, QAbstractSocket

REMOTE_HOST = "186.66.161.232"
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
        self.tcpServer.newConnection.connect(self.procNewConn)
        self.tcpServer.listen(QHostAddress('0.0.0.0'), LOCAL_TCP_PORT)

        self.tcpRemote = QTcpSocket()
        self.tcpRemote.stateChanged.connect(self.onStateChanged)
        self.tcpRemote.readyRead.connect(self.tcpR2L)
        self.tcpRemote.connectToHost(QHostAddress(REMOTE_HOST), REMOTE_TCP_PORT)

        self.udpLocal = QUdpSocket()
        self.udpLocal.readyRead.connect(self.udpL2R)
        self.udpLocal.bind(QHostAddress('0.0.0.0'), LOCAL_UDP_PORT)

        self.udpRemote = QUdpSocket()
        self.udpRemote.readyRead.connect(self.udpR2L)

    @Slot()
    def procNewConn(self):
        self.tpcLocal = self.tcpServer.nextPendingConnection()
        self.tpcLocal.readyRead.connect(self.tcpL2R)
        print("New Local Client Connected")

    @Slot(QAbstractSocket.SocketState)
    def onStateChanged(self, state):
        if state == QAbstractSocket.HostLookupState:
            print("Lookup for Remote Host")
        elif state == QAbstractSocket.ConnectingState:
            print("Connecting to Remote Host")
        elif state == QAbstractSocket.ConnectedState:
            print("Connected to Remote Host")
        elif state == QAbstractSocket.UnconnectedState:
            print("Disconnected to Remote Host")

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
        while self.udpLocal.hasPendingDatagrams() == True:
            datagram = self.udpLocal.receiveDatagram()
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
            self.udpLocal.writeDatagram(data, self.udpResponseIP, self.udpResponsePort)

if __name__ == "__main__":
    app=QCoreApplication(sys.argv)

    MyApp = App()

    sys.exit(app.exec_())