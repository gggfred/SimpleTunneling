#!/usr/bin/python3

import sys
from PySide2.QtCore import QCoreApplication

from tunnel import TunnelTCP

REMOTE_HOST = " 172.27.200.143"
REMOTE_TCP_PORT = 50509

LOCAL_TCP_PORT = 50509

class App():
    def __init__(self, *args, **kwargs):
        self.tunnel1 = TunnelTCP("Tunnel 1")
        self.tunnel1.setServerPort(LOCAL_TCP_PORT)
        self.tunnel1.setRemoteIPAddress(REMOTE_HOST)
        self.tunnel1.setRemoteTCPPort(REMOTE_TCP_PORT)
        self.tunnel1.performListening()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    MyApp = App()

    sys.exit(app.exec_())
