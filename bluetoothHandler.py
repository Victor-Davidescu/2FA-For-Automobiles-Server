################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import time
import bluetooth
import threading
import queue
import logging

################################################################################
# Class Bluetooth handler
################################################################################
class BluetoothHandler (threading.Thread):

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self, port:int) -> None:
        threading.Thread.__init__(self)
        self._serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._clientSocket = None
        self._clientAddress = None
        self._port = port
        self._clientConnected = False
        self.keepRunning = True
        self.importMsgs = queue.Queue()
        self.exportMsgs = queue.Queue()

    ############################################################################
    # Function 
    ############################################################################
    def _BindToPort(self) -> None:
        try: self._serverSocket.bind(("", self._port))

        except Exception as err:
            logging.error("Bluetooth failed to bind to port {0}. Details: {1}".format(self._port, err))
            self._CloseServerSocket()
        else: logging.debug("Bluetooth binded to port {0}".format(self._port))

    ############################################################################
    # Function 
    ############################################################################
    def _StartListening(self):
        try: self._serverSocket.listen(1)

        except Exception as error:
            logging.error("Bluetooth failed to listen Details: {0}".format(error))
            self._CloseServerSocket()
        else: logging.debug("Bluetooth socket started to listen.")

    ############################################################################
    # Function 
    ############################################################################
    def _WaitClientConnection(self):
        logging.info("Waiting for a client to connect.")
        self._clientSocket, self._clientAddress = self._serverSocket.accept()
        logging.info("Client connected.")
        self._clientConnected = True

    ############################################################################
    # Function 
    ############################################################################
    def _SendMessage(self):

        # Assign as message an item from queue or send a ping
        msg = (self.exportMsgs.get() if(not self.exportMsgs.empty()) else "ping\n")

        try:
            self._clientSocket.send(msg.encode())
            logging.debug("Message sent successfully.")

        except Exception as error:
            logging.error("Failed to send message. Details: {0}".format(error))
            self._clientConnected = False
            self._CloseClientSocket()

    ############################################################################
    # Function 
    ############################################################################
    def _ReceiveMessage(self):

        try: dataBytes = self._clientSocket.recv(1024)

        except Exception as error:
            logging.error("Failed to retreive message. Details: {0}".format(error))
            self._clientConnected = False
            self._CloseClientSocket()
            
        else:
            msg = dataBytes.decode('utf-8').rstrip()

            if(msg == "disconnect"):
                self._clientConnected = False
                self._CloseClientSocket()

            else: self.importMsgs.put(item=msg)

    ############################################################################
    # Function 
    ############################################################################
    def _CloseServerSocket(self):
        try:
            self._serverSocket.close()
            logging.debug("Server socket closed")

        except Exception as error:
            logging.error("Failed to close server socket. Details: {0}".format(error))

    ############################################################################
    # Function 
    ############################################################################
    def _CloseClientSocket(self):
        try:
            self._clientSocket.close()
            logging.info("Disconnected the client.")

        except Exception as error:
            logging.error("Failed to close client socket. Details: {0}".format(error))

    ############################################################################
    # Main Thread Function 
    ############################################################################
    def run(self):

        # Bind to a port and listen
        self._BindToPort()
        self._StartListening()

        # Start the main thread loop
        while(self.keepRunning):

            time.sleep(1)

            # If client is not connected, wait to connect back
            if(not self._clientConnected): self._WaitClientConnection()

            # Receive message if client is connected
            if(self._clientConnected): self._ReceiveMessage()

            if(not self.importMsgs.empty()):
                print(self.importMsgs.get())

            # Send message if client is connected
            if(self._clientConnected): self._SendMessage()

        # Close sockets
        self._CloseClientSocket()
        self._CloseServerSocket()


logging.basicConfig(level="DEBUG")
myBt = BluetoothHandler(1)
myBt.start()
