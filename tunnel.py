from PySide2.QtCore import QCoreApplication, Slot, QTimer
from PySide2.QtNetwork import QTcpServer, QTcpSocket, QUdpSocket, QHostAddress, QAbstractSocket

class TunnelTCP():
    name = ""
    localServerPort = 0
    localTCPSocket = None

    clientPeerAddress = 0

    remoteIPAddress = 0
    remoteTCPport = 0

    def __init__(self, name = "N/A"):
        self.name = name
        self.localServer = QTcpServer()
        self.localServer.newConnection.connect(self.newConnectionProc)

        self.remoteTCPSocket = QTcpSocket()
        self.remoteTCPSocket.stateChanged.connect(self.onRemoteStateChanged)
        self.remoteTCPSocket.readyRead.connect(self.onRemote2Local)

        self.timerOpenRemote = QTimer()
        self.timerOpenRemote.timeout.connect(self.tryOpenRemote)
        self.timerOpenRemote.setInterval(5000)

    def setRemoteIPAddress(self, ip):
        self.remoteIPAddress = ip

    def setRemoteTCPPort(self, port):
        self.remoteTCPport = port

    def setServerPort(self, port):
        self.localServerPort = port

    def performListening(self):
        self.localServer.listen(QHostAddress('0.0.0.0'), self.localServerPort)

    @Slot()
    def tryOpenRemote(self):
        if self.remoteTCPSocket.isOpen() == False:
            print('%s: Try to open %s:%s' % (self.name, self.remoteIPAddress, self.remoteTCPport))
            self.remoteTCPSocket.connectToHost(QHostAddress(self.remoteIPAddress), self.remoteTCPport)

    @Slot(QAbstractSocket.SocketState)
    def onRemoteStateChanged(self, state):
        if state == QAbstractSocket.HostLookupState:
            print("%s: Lookup for Remote Host" % self.name)
        elif state == QAbstractSocket.ConnectingState:
            print("%s: Connecting to Remote Host" % self.name)
        elif state == QAbstractSocket.ConnectedState:
            print("%s: Connected to Remote Host" % self.name)
        elif state == QAbstractSocket.UnconnectedState:
            print("%s: Disconnected to Remote Host" % self.name)
            self.remoteTCPSocket.close()
            self.localTCPSocket.close()
            self.timerOpenRemote.stop()

    @Slot(QAbstractSocket.SocketState)
    def onLocalStateChanged(self, state):
        if state == QAbstractSocket.UnconnectedState:
            print("%s: Client disconnected" % self.name)
            self.remoteTCPSocket.close()
            self.timerOpenRemote.stop()

    @Slot()
    def newConnectionProc(self):
        self.localTCPSocket = self.localServer.nextPendingConnection()
        self.localTCPSocket.stateChanged.connect(self.onLocalStateChanged)
        self.localTCPSocket.readyRead.connect(self.onLocal2Remote)

        self.clientPeerAddress = self.localTCPSocket.peerAddress()

        self.timerOpenRemote.start()

        print("%s: %s client connected" % (self.name, self.clientPeerAddress.toString()))

    @Slot()
    def onLocal2Remote(self):
        if self.remoteTCPSocket.isOpen():
            data = self.localTCPSocket.readAll()
            print("%s: L2R: %s" % (self.name, data))
            self.remoteTCPSocket.write(data)

    @Slot()
    def onRemote2Local(self):
        if self.localTCPSocket.isOpen():
            data = self.remoteTCPSocket.readAll()
            print("%s: R2L: %s" % (self.name, data))
            self.localTCPSocket.write(data)

class TunnelUDP():
    name = ""
    localListenPort = 0

    remoteIPAddress = 0
    remoteUDPport = 0

    udpResponseIP = None
    udpResponsePort = None

    def __init__(self, name = "N/A"):
        self.name = name
        self.udpLocal = QUdpSocket()
        self.udpLocal.readyRead.connect(self.udpL2R)

        self.udpRemote = QUdpSocket()
        self.udpRemote.readyRead.connect(self.udpR2L)

    def setRemoteIPAddress(self, ip):
        self.remoteIPAddress = ip

    def setRemoteUDPPort(self, port):
        self.remoteUDPport = port

    def setBindPort(self, port):
        self.localListenPort = port

    def performBinding(self):
        self.udpLocal.bind(QHostAddress('0.0.0.0'), self.localListenPort)

    @Slot()
    def udpL2R(self):
        while self.udpLocal.hasPendingDatagrams() == True:
            datagram = self.udpLocal.receiveDatagram()
            data = datagram.data()
            self.udpResponseIP = datagram.senderAddress()
            self.udpResponsePort = datagram.senderPort()
            print("%s: FROM: %s %s TO: %s %s" % (
                self.name,
                datagram.senderAddress().toString(),
                datagram.senderPort(),
                datagram.destinationAddress().toString(),
                datagram.destinationPort()))
            print("%s: L2R: %s" % (self.name, data))
            self.udpRemote.writeDatagram(data, QHostAddress(self.remoteIPAddress), self.remoteUDPport)

    @Slot()
    def udpR2L(self):
        while self.udpRemote.hasPendingDatagrams() == True:
            datagram = self.udpRemote.receiveDatagram()
            data = datagram.data()
            print("%s: FROM: %s %s TO: %s %s" % (
                self.name,
                datagram.senderAddress().toString(),
                datagram.senderPort(),
                datagram.destinationAddress().toString(),
                datagram.destinationPort()))
            print("%s: R2L: %s" % (self.name, data))
            self.udpLocal.writeDatagram(data, self.udpResponseIP, self.udpResponsePort)

