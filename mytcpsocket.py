from PySide2.QtCore import Slot, Signal
from PySide2.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

class MyTCPSocket(QTcpSocket):
    connected = False
    changeState = Signal(bool)

    def __init__(self, parent=None):
        super(MyTCPSocket, self).__init__(parent)
        self.stateChanged.connect(self.on_stateChanged)
        self.connected = False

    def open(self, address=QHostAddress.Any, port=9999):
        return self.connectToHost(QHostAddress(address), port)

    @Slot(QAbstractSocket.SocketState)
    def on_stateChanged(self, state):
        if state == QAbstractSocket.ConnectedState:
            self.connected = True
            print("connected")
        elif state == QAbstractSocket.UnconnectedState:
            self.connected = False
            print("disconnected")
        self.changeState.emit(self.connected)

    def writeFrame(self, frame):
        self.write(frame.encode())