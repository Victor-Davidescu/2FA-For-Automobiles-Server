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

################################################################################
# Class Bluetooth handler
################################################################################
class ServerBluetoothThread (threading.Thread):

    ############################################################################
    # Constructor
    ############################################################################
    def __init__(self) -> None:
        threading.Thread.__init__(self)

        # Get neccessary configurations
        self._port = Configurations.GetInt('bluetooth', 'port')
        socketTimeout = Configurations.GetInt('bluetooth', 'socket_timeout_seconds')
        self._maxLoginAttempts = Configurations.GetInt('bluetooth', 'max_login_attempts')
        btLedPin = Configurations.GetInt('gpio_pins', 'led_bluetooth_pin')

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
    def _ReceiveData(self) -> str:

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
            self._SendData("enter user and pin")

            # Loop for the maximum login attempts
            for attempt in range(self._maxLoginAttempts, 0, -1):
                msg = self._ReceiveData() # msg should look like "username,pin"

                # User regex to find group 1 (username) and group 2 (pin)
                result = re.match(r"([a-zA-Z]+),([0-9]+)",msg)
                if (result):
                    username = result.group(1)
                    pin = result.group(2)

                    # Check if username and pin match
                    if(self.auth.CheckUserPin(username,pin)):
                        self._clientAuthenticated = True
                        self._SendData("logged in")
                        break
                    else: self._SendData("wrong credentials")
                else: self._SendData("wrong format")

            # Check if the client is authenticated, if not close the connection
            if(not self._clientAuthenticated):
                self._CloseClientSocket()

        else: self._SendData("already logged in")


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
            self._SendData("logged out")

        elif(data == "shutdown"):
            if(self._clientAuthenticated):
                self._keepRunning = False
                self.cmdQueue.put(data)
                self._SendData("shutting down")
            else: self._SendData("unauthorised command")

        else:
            if(self._clientAuthenticated):
                self.cmdQueue.put(data)
                self._SendData("command '{0}' received".format(data))
            else: self._SendData("unauthorised command")

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
                # Wait for the client to send data
                data = self._ReceiveData()
                # Process the data received from client
                self._ProcessInputData(data)


        self._CloseClientSocket() # Close client socket
        self._CloseServerSocket() # Close server socket
        logging.debug("BT Handler has stopped.")
