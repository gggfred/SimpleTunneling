#!/usr/bin/python3

import sys
from PySide2.QtCore import QCoreApplication, Slot, QTimer
from PySide2.QtNetwork import QTcpServer, QTcpSocket, QUdpSocket, QHostAddress, QAbstractSocket

from tunnel import TunnelTCP, TunnelUDP

REMOTE_CONTROLLER_IP = "192.168.0.1"
REMOTE_TCP_CONTROLLER_PORT = 3001
REMOTE_UDP_CONTROLLER_PORT = 52001
REMOTE_TCP_TERMINAL_PORT = 19001

LOCAL_TCP_CONTROLLER_PORT = 3001
LOCAL_UDP_CONTROLLER_PORT = 52001
LOCAL_TCP_TERMINAL_PORT = 19001

class App():
    def __init__(self, *args, **kwargs):
        self.tunnel1 = TunnelTCP("Tunnel 1")
        self.tunnel1.setServerPort(LOCAL_TCP_CONTROLLER_PORT)
        self.tunnel1.setRemoteIPAddress(REMOTE_CONTROLLER_IP)
        self.tunnel1.setRemoteTCPPort(REMOTE_TCP_CONTROLLER_PORT)
        self.tunnel1.performListening()

        self.tunnel2 = TunnelTCP("Tunnel 2")
        self.tunnel2.setServerPort(LOCAL_TCP_TERMINAL_PORT)
        self.tunnel2.setRemoteIPAddress(REMOTE_CONTROLLER_IP)
        self.tunnel2.setRemoteTCPPort(REMOTE_TCP_TERMINAL_PORT)
        self.tunnel2.performListening()

        self.tunnel3 = TunnelUDP("Tunnel 3")
        self.tunnel3.setBindPort(LOCAL_UDP_CONTROLLER_PORT)
        self.tunnel3.setRemoteIPAddress(REMOTE_CONTROLLER_IP)
        self.tunnel3.setRemoteUDPPort(REMOTE_UDP_CONTROLLER_PORT)
        self.tunnel3.performBinding()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    MyApp = App()

    sys.exit(app.exec_())
