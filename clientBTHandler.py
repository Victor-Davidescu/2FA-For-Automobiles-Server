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
class ClientBTHandler (threading.Thread):

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
        self.inData = queue.Queue()
        self.outData = queue.Queue()


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
    def _StartListening(self) -> None:
        try: self._serverSocket.listen(1)
        except Exception as error:
            logging.error("Bluetooth failed to listen Details: {0}".format(error))
            self._CloseServerSocket()
        else: logging.debug("Bluetooth socket started to listen.")


    ############################################################################
    # Function 
    ############################################################################
    def _WaitClientConnection(self) -> None:
        logging.info("Waiting for a client to connect.")
        self._clientSocket, self._clientAddress = self._serverSocket.accept()
        logging.info("Client connected.")
        self._clientConnected = True


    ############################################################################
    # Function 
    ############################################################################
    def _SendData(self) -> None:
        if(not self.outData.empty()):
            data = self.outData.get()
            try:
                self._clientSocket.send(data.encode())
                logging.debug("Message sent successfully.")
            except Exception as error:
                logging.error("Failed to send message. Details: {0}".format(error))
                self._clientConnected = False
                self._CloseClientSocket()
            self.outData.task_done()


    ############################################################################
    # Function 
    ############################################################################
    def _ReceiveData(self) -> None:
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
            else: self.inData.put(msg)


    ############################################################################
    # Function 
    ############################################################################
    def _CloseServerSocket(self) -> None:
        try:
            self._serverSocket.close()
            logging.debug("Server socket closed")
        except Exception as error:
            logging.error("Failed to close server socket. Details: {0}".format(error))


    ############################################################################
    # Function 
    ############################################################################
    def _CloseClientSocket(self) -> None:
        try:
            self._clientSocket.close()
            logging.info("Disconnected the client.")
        except Exception as error:
            logging.error("Failed to close client socket. Details: {0}".format(error))

    ############################################################################
    # Main Thread Function 
    ############################################################################
    def run(self) -> None:

        # Bind to a port and listen
        self._BindToPort()
        self._StartListening()

        # Start the main thread loop
        while(self.keepRunning):

            # If client is not connected, wait to connect back
            if(not self._clientConnected): self._WaitClientConnection()

            # Receive data if client is connected
            if(self._clientConnected): self._ReceiveData()

            # Time delay (needs to be here to give time for receiving items for outData queue)
            time.sleep(0.5)

            # Send data if client is connected
            if(self._clientConnected): self._SendData()

        # Close sockets
        self._CloseClientSocket()
        self._CloseServerSocket()
