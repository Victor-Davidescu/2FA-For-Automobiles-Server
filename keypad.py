################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import time
import threading
import queue
import logging
from authentication import Authentication


################################################################################
# Class Keypad
################################################################################
class Keypad (threading.Thread):
    """
    Class Keypad for receiving inputs from the physical keypad
    """

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self, rowLength, columnLength, rowPins, columnPins, keys, defaultUser,pepper,dbPath):
        threading.Thread.__init__(self)
        self._rowLength = rowLength
        self._columnLength = columnLength
        self._rowPins = rowPins
        self._columnPins = columnPins
        self._keys = keys
        self._defaultUser = defaultUser
        self._pepper = pepper
        self._dbPath = dbPath
        self._userAuthenticated = False
        self.cmdQueue = queue.Queue()
        self.keepRunning = True

        self._SetupGPIOPins()


    ############################################################################
    # Function
    ############################################################################
    def _SetupGPIOPins(self) -> None:
        # Setup the row pins as output pins
        for pin in self._rowPins:
            GPIO.setup(int(pin), GPIO.OUT)
        # Setup the column pins as input pins
        for pin in self._columnPins:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


    ############################################################################
    # Function
    ############################################################################
    def _ReadKey(self) -> str:
        keyReceived = None

        # Loop until an input is received
        while (keyReceived is None and self.keepRunning):
            time.sleep(0.1)

            # Interate thorugh row pins
            for (indexRow, pinRow) in zip(range(4), self._rowPins):

                # Send an output on the current row pin
                GPIO.output(int(pinRow), GPIO.HIGH)

                # Iterate thorugh column pins
                for (indexColumn, pinColumn) in zip(range(4), self._columnPins):

                    # Check if there is  an output
                    if(GPIO.input(int(pinColumn)) == 1):
                        keyReceived = self._keys[indexRow][indexColumn]
                        logging.debug("From keypad received key '{0}'.".format(keyReceived))

                # Stop sending an output on the current row pin
                GPIO.output(int(pinRow), GPIO.LOW)
        
        return keyReceived


    ############################################################################
    # Function
    ############################################################################
    def _Authenticate(self):

        logging.debug("Keypad - Entered in Authentication mode.")
        logging.debug("Keypad - Default user is: {0}".format(self._defaultUser))
        pin = ""
        loop = True
        pinReceived = False

        # Loop until user enters the PIN or it cancels
        while(loop and self.keepRunning):
            # Avoid getting repeated keys
            time.sleep(1)

            # Read key from user
            key = self._ReadKey()

            if(key == 'A'): # A for cancelling authentication
                logging.debug("Authentication cancelled.")
                loop = False

            elif(key == 'B'): # B for confirming PIN
                logging.debug("PIN received")
                pinReceived = True
                loop = False

            elif(key == 'C'): # C for reseting PIN
                logging.debug("PIN resetted")
                pin = ""
            
            elif(key.isdigit()):
                pin = pin + key


        if(pinReceived):
            if(self.auth.CheckUserPin(self._defaultUser,pin)):
                logging.debug("Authentication is successful.")
                self._userAuthenticated = True
            else:
                logging.debug("Authentication failed.")
        else:
            logging.debug("Authentication is cancelled")

    
    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionA(self):
        # Check if user is already authenticated
        if(self._userAuthenticated):
            logging.debug("User logged out.")
            self._userAuthenticated = False
        else: self._Authenticate()


    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionB(self):
        if(self._userAuthenticated):
            logging.debug("User requested to switch the relay")
            self.cmdQueue.put("switch")
        else: logging.debug("Switch command denied.")


    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionC(self):
        if(self._userAuthenticated):
            logging.debug("User requested to shutdown the program")
            self.cmdQueue.put("shutdown")
        else: logging.debug("Shutdown command denied.")


    ############################################################################
    # Function
    ############################################################################
    def _ProcessKey(self, key):
        # Login/Logout Key
        if(key=='A'): self._KeyFunctionA()

        # Lock/Unlock Key
        elif(key=='B'): self._KeyFunctionB()

        # Shutdown Key
        elif(key=='C'): self._KeyFunctionC()


    ############################################################################
    # Function
    ############################################################################
    def run(self):
        # Setup the GPIO Pins
        self._SetupGPIOPins()

        # Setup the authentication
        self.auth = Authentication(self._pepper, self._dbPath)

        # Run the keypad loop
        while(self.keepRunning):
            time.sleep(1)

            # Read key
            key = self._ReadKey()

            # Process the recceived key
            if(key is not None): self._ProcessKey(key)
