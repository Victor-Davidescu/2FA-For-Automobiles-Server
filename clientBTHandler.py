################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
from subprocess import TimeoutExpired
import bluetooth
import threading
import queue
import logging
from authentication import Authentication

################################################################################
# Class Bluetooth handler
################################################################################
class ClientBTHandler (threading.Thread):

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self, port:int, pepper, dbPath) -> None:
        threading.Thread.__init__(self)
        self._serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._serverSocket.settimeout(10)
        self._clientSocket = None
        self._clientAddress = None
        self._port = port
        self.clientConnected = False
        self._clientAuthenticated = False
        self._pepper = pepper
        self._dbPath = dbPath
        self.keepRunning = True
        self.cmdQueue = queue.Queue()


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
        try:
            self._clientSocket, self._clientAddress = self._serverSocket.accept()
        except Exception as err:
            logging.error("{0}".format(err))
        else:
            logging.info("Client connected.")
            self.clientConnected = True


    ############################################################################
    # Function 
    ############################################################################
    def _ReceiveData(self) -> None:

        try: dataBytes = self._clientSocket.recv(1024)
        except Exception as error:
            logging.error("Failed to retreive message. Details: {0}".format(error))
            self._CloseClientSocket()  
        else:
            data = dataBytes.decode('utf-8').rstrip()
            return data


    ############################################################################
    # Function 
    ############################################################################
    def _SendData(self, data:str) -> None:
        # Check if data is empty
        if(data is not None):

            # Add end of line if data does't have it
            if(not data.endswith("\n")): data = data + "\n"

            # Send Data
            try: self._clientSocket.send(data.encode())
            except Exception as error:
                logging.error("Failed to send message. Details: {0}".format(error))
                self._CloseClientSocket()            
            else: logging.debug("Message sent successfully.")

        else: logging.error("The data received for sending is empty.")
        

    ############################################################################
    # Function 
    ############################################################################
    def _AuthenticateClient(self):
        if(not self._clientAuthenticated):
            self._SendData("Enter your username:")
            username = self._ReceiveData()
         
            # Allow maximum 3 attempts for the pin
            for attempt in range(3,0,-1):
                self._SendData("Enter your pin:")
                pin = self._ReceiveData()

                # Check if username and pin match
                if(self.auth.CheckUserPin(username,pin)):
                    self._clientAuthenticated = True
                    self._SendData("Authenticated successfully.\n")
                    break         
                else: self._SendData("Wrong pin, you have {0} attempts left.\n".format(attempt-1))

            # Check if the client is authenticated, if not close the connection
            if(not self._clientAuthenticated):
                self._SendData("Too many failed attempts, disconnecting.\n")
                self._CloseClientSocket()

        else: self._SendData("You are already logged in.\n")

                
    ############################################################################
    # Function 
    ############################################################################                
    def _ProcessInputData(self, data):

        if(data == "disconnect"): 
            self._CloseClientSocket()

        elif(data == "login"):
            self._AuthenticateClient()

        elif(data == "logout"):
            self._clientAuthenticated = False
            self._SendData("You logged out.")

        elif(data == "shutdown"):
            if(self._clientAuthenticated):
                self.keepRunning = False
                self.cmdQueue.put(data)
                self._SendData("2FA is shutting down.")
            else: self._SendData("You need to authenticate first. Use 'login' command.")
                
        else:
            if(self._clientAuthenticated):
                self.cmdQueue.put(data)
                self._SendData("Command '{0}' received.".format(data))
            else: self._SendData("You need to authenticate first. Use 'login' command.")

    ############################################################################
    # Function 
    ############################################################################
    def _CloseClientSocket(self) -> None:
        try:
            self.clientConnected = False
            self._clientAuthenticated = False
            self._clientSocket.close()
            logging.info("Disconnected the client.")

        except Exception as error:
            logging.error("Failed to close client socket. Details: {0}".format(error))


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
    # Main Thread Function 
    ############################################################################
    def run(self) -> None:

        # Bind to a port and listen
        self._BindToPort()
        self._StartListening()

        # Initiate authentication class and delete pepper and path to DB
        self.auth = Authentication(self._pepper, self._dbPath)
        del self._pepper
        del self._dbPath

        # Start the main thread loop
        while(self.keepRunning):

            # Check if a client is connected
            if(not self.clientConnected):
                # If client is not connected, wait to connect back
                self._WaitClientConnection()

            else:
                # Wait for the client to send data
                data = self._ReceiveData()

                # Process the data received from client    
                self._ProcessInputData(data)

        # Close sockets
        self._CloseClientSocket()
        self._CloseServerSocket()
