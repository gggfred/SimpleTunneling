#!/usr/bin/python3

import sys
from PySide2.QtCore import QCoreApplication, Slot, QTimer
from PySide2.QtNetwork import QTcpServer, QTcpSocket, QUdpSocket, QHostAddress, QAbstractSocket

REMOTE_CONTROLLER_IP = "192.168.0.1"
REMOTE_TCP_CONTROLLER = 3001
REMOTE_UDP_CONTROLLER = 52001
REMOTE_TCP_TERMINAL = 19001

LOCAL_TCP_CONTROLLER = 3001
LOCAL_UDP_CONTROLLER = 52001
LOCAL_TCP_TERMINAL = 19001

class App():
    TCPLocal = None
    udpResponseIP = None
    udpResponsePort = None

    def __init__(self, *args, **kwargs):
        self.tcpServer = QTcpServer()
        self.tcpServer.newConnection.connect(self.procNewConn)
        self.tcpServer.listen(QHostAddress('0.0.0.0'), LOCAL_TCP_CONTROLLER)

        self.tcpRemote = QTcpSocket()
        self.tcpRemote.stateChanged.connect(self.onRemoteStateChanged)
        self.tcpRemote.readyRead.connect(self.tcpR2L)

        self.udpLocal = QUdpSocket()
        self.udpLocal.readyRead.connect(self.udpL2R)
        self.udpLocal.bind(QHostAddress('0.0.0.0'), LOCAL_UDP_CONTROLLER)

        self.udpRemote = QUdpSocket()
        self.udpRemote.readyRead.connect(self.udpR2L)

        self.timerOpenRemote = QTimer()
        self.timerOpenRemote.timeout.connect(self.tryOpenRemote)
        self.timerOpenRemote.setInterval(2000)
        self.timerOpenRemote.start()

    @Slot()
    def tryOpenRemote(self):
        if self.tcpRemote.isOpen() == False:
            print('Try open')
            self.tcpRemote.connectToHost(
                QHostAddress(REMOTE_CONTROLLER_IP), REMOTE_TCP_CONTROLLER)

    @Slot()
    def procNewConn(self):
        self.TCPLocal = self.tcpServer.nextPendingConnection()
        self.TCPLocal.readyRead.connect(self.tcpL2R)
        print("TCP IP: %s Server Connected" %
              self.TCPLocal.peerAddress().toString())

    @Slot(QAbstractSocket.SocketState)
    def onRemoteStateChanged(self, state):
        if state == QAbstractSocket.HostLookupState:
            print("Lookup for Remote Host")
        elif state == QAbstractSocket.ConnectingState:
            print("Connecting to Remote Host")
        elif state == QAbstractSocket.ConnectedState:
            print("Connected to Remote Host")
        elif state == QAbstractSocket.UnconnectedState:
            print("Disconnected to Remote Host")
            self.tcpRemote.close()

    @Slot()
    def tcpL2R(self):
        data = self.TCPLocal.readAll()
        print("TCP L2R: %s" % data)
        self.tcpRemote.write(data)

    @Slot()
    def tcpR2L(self):
        data = self.tcpRemote.readAll()
        print("TCP R2L: %s" % data)
        self.TCPLocal.write(data)

    @Slot()
    def udpL2R(self):
        while self.udpLocal.hasPendingDatagrams() == True:
            datagram = self.udpLocal.receiveDatagram()
            data = datagram.data()
            self.udpResponseIP = datagram.senderAddress()
            self.udpResponsePort = datagram.senderPort()
            print("%s %s %s %s" % (
                datagram.senderAddress().toString(),
                datagram.senderPort(),
                datagram.destinationAddress().toString(),
                datagram.destinationPort()))
            print("UDP L2R: %s" % data)
            self.udpRemote.writeDatagram(
                data, QHostAddress(REMOTE_CONTROLLER_IP), REMOTE_UDP_CONTROLLER)

    @Slot()
    def udpR2L(self):
        while self.udpRemote.hasPendingDatagrams() == True:
            datagram = self.udpRemote.receiveDatagram()
            data = datagram.data()
            print("%s %s %s %s" % (
                datagram.senderAddress().toString(),
                datagram.senderPort(),
                datagram.destinationAddress().toString(),
                datagram.destinationPort()))
            print("UDP R2L: %s" % data)
            self.udpLocal.writeDatagram(
                data, self.udpResponseIP, self.udpResponsePort)


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    MyApp = App()

    sys.exit(app.exec_())
