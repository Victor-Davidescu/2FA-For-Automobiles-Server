################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import bluetooth
import threading
import queue
import logging
import re
from led import Led
from config import Configurations
from authentication import Authentication
from encryption import Encryption

################################################################################
# Class Bluetooth handler
################################################################################
class ServerBluetoothThread (threading.Thread):

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self) -> None:
        threading.Thread.__init__(self)

        # Get neccessary configurations
        self._port = Configurations.GetInt('bluetooth', 'port')
        socketTimeout = Configurations.GetInt('bluetooth', 'socket_timeout_seconds')
        self._maxLoginAttempts = Configurations.GetInt('bluetooth', 'max_login_attempts')
        btLedPin = Configurations.GetInt('gpio_pins', 'led_bluetooth_pin')
        self._maxStrangeInputDataAllowance = Configurations.GetInt('bluetooth','max_strange_input_data_allowance')

        # Declare the BT LED
        self.led = Led(btLedPin)

        # Declare the sockets
        self._serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._serverSocket.settimeout(socketTimeout) # Set timeout for waiting connection
        self._clientSocket = None

        # Declare variables related to the client
        self._clientAddress = None
        self._clientAuthenticated = False
        self.clientConnected = False

        # Declare other variables
        self._keepRunning = True
        self.cmdQueue = queue.Queue()
        self._currentAttempts = 0
        self._currentSuspiciousPoints = 0


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
    def _ReceiveMsg(self) -> str:

        try: encryptedMsgBytes:bytes = self._clientSocket.recv(1024)
        except Exception as error:
            logging.error("Failed to retreive message. Details: {0}".format(error))
            self._CloseClientSocket()
        else:
            logging.debug("Received msg: {0}".format(encryptedMsgBytes.decode("UTF-8")))
            encryptedMsg = encryptedMsgBytes.decode("UTF-8")
            msg = Encryption.DecryptMessage(encryptedMsg)
            return msg


    ############################################################################
    # Function
    ############################################################################
    def _SendMessage(self, msg:str) -> None:
        if(msg is not None):
            if(msg.endswith("\n")): msg = msg.replace("\n","") # Remove the newline
            encryptedMsg = Encryption.EncryptMessage(msg) # Encrypt msg

            if(encryptedMsg is not None): # If encryption failed, don't send any message
                encryptedMsg += "\n" # Add new line for the crypted msg
                encryptedMsgBytes = encryptedMsg.encode() # Convert to bytes
                try: self._clientSocket.send(encryptedMsgBytes)
                except Exception as error:
                    logging.error("Failed to send message. Details: {0}".format(error))
                    self._CloseClientSocket()
                else: logging.debug("Message sent successfully.")

        else: logging.error("The data received for sending is empty.")


    ############################################################################
    # Function
    ############################################################################
    def _AuthenticateClient(self, msg:str):
        # Check if user is already authenticated
        if(not self._clientAuthenticated):
            self._currentAttempts += 1

            # User regex to find group 1 (username) and group 2 (pin)
            result = re.match(r"login-([a-zA-Z]+),([0-9]+)",msg)

            # Check if the right format
            if (result):

                    username = result.group(1)
                    pin = result.group(2)

                    # Check if username and pin match
                    if(self.auth.CheckUserPin(username,pin)):
                        self._clientAuthenticated = True
                        self._currentAttempts = 0
                        self._SendMessage("logged in")

                    else:
                        if(self._currentAttempts < self._maxLoginAttempts):
                            self._SendMessage("wrong credentials")
                        else:
                            self._currentAttempts = 0
                            self._CloseClientSocket()
            else:
                if(self._currentAttempts < self._maxLoginAttempts):
                    self._SendMessage("wrong format")
                else:
                    self._currentAttempts = 0
                    self._CloseClientSocket()
        else:
            self._SendMessage("already logged in")

    ############################################################################
    # Function
    ############################################################################
    def _IsInputDataStrange(self, data:str=None) -> bool:

        if(data is not None and data is not ""):
            return False
        else:
            logging.warning("Received weird input data from the client.")
            return True

    ############################################################################
    # Function
    ############################################################################
    def _ProcessInputData(self, data:str=None):

        if(data is not None):
            if(data == "disconnect"):
                self._CloseClientSocket()

            elif(data.startswith("login")):
                self._AuthenticateClient(data)

            elif(data == "logout"):
                self._clientAuthenticated = False
                self._SendMessage("logged out")

            elif(data == "shutdown"):
                if(self._clientAuthenticated):
                    self._keepRunning = False
                    self.cmdQueue.put(data)
                    self._SendMessage("shutting down")
                else: self._SendMessage("unauthorised command")

            else:
                if(self._clientAuthenticated):
                    self.cmdQueue.put(data)
                    self._SendMessage("command '{0}' received".format(data))
                else: self._SendMessage("unauthorised command")

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
    # Function
    ############################################################################
    def Stop(self):
        logging.debug("BT Handler received stop command")
        self._keepRunning = False
        self.led.Stop() # Stop the led thread
        self.led.join() # Wait for thread to join


    ############################################################################
    # Main Thread Function
    ############################################################################
    def run(self) -> None:
        self._BindToPort() # Bind the server socket to a port
        self._StartListening() # Make the server socket listen to connections
        self.led.start() # Start the thread for BT led indicator

        # Initiate authentication class and delete pepper and path to DB
        self.auth = Authentication()

        # Start the main thread loop
        while(self._keepRunning):

            # Check if a client is connected
            if(not self.clientConnected):
                self.led.Blink()
                self._WaitClientConnection() # If client is not connected, wait to connect back
                self.led.ON()

            else:
                data = self._ReceiveMsg() # Wait for the client to send data

                if(self._IsInputDataStrange(data)): # Check if the input data from client is weird
                    self._currentSuspiciousPoints += 1

                    if(self._currentSuspiciousPoints == self._maxStrangeInputDataAllowance):
                        logging.warning("Disconnecting client due to too many weird input data received.")
                        self._CloseClientSocket()
                        self.cmdQueue.put("stopBT")
                        self.Stop()

                else: self._ProcessInputData(data) # Process the data received from client


        self._CloseClientSocket() # Close client socket
        self._CloseServerSocket() # Close server socket
        logging.debug("BT Handler has stopped.")
