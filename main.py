################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import third_party_drivers.I2C_LCD_driver as LCDDriver
import RPi.GPIO as GPIO
import time
import logging
import threading

# Own Modules
from config import Configurations
from keypad import Keypad
from relay import RelaySwitch
from authentication import Authentication
from clientBTHandler import ClientBTHandler

################################################################################
# Class Main
################################################################################
class Main:

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self):

        # Setup GPIO to use Broadcom uses the actual pin number
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.keepRunning = True
        self.config = Configurations("config.conf")
        self.mainBluetooth = ClientBTHandler(int(self.config.bluetoothPin))
        self.mainRelay = RelaySwitch(self.config.relayPin)
        self.mainLCD = LCDDriver.lcd()
        self.mainKepad = Keypad(
            self.config.rowLength, 
            self.config.columnLength, 
            self.config.keypadRowPins,
            self.config.keypadColumnPins,
            self.config.keys)
        self.mainAuth = Authentication(
            self.config.pepper, 
            self.config.dbLocation)


    ############################################################################
    # Function 
    ############################################################################
    def CheckDataFromBT(self):

        # Check if the queue for received Data is not empty
        if(not self.mainBluetooth.inData.empty()):

            data = self.mainBluetooth.inData.get()
            logging.info("Data received: {0}".format(data))

            if(data == "lock"):
                self.mainRelay.OFF()
                msg = "Relay should be off.\n"

            elif(data == "unlock"):
                self.mainRelay.ON()
                msg = "Relay should be on.\n"

            elif(data == "shutdown"):
                msg = "Shutdown received.\n"
                self.mainBluetooth.keepRunning = False
                self.keepRunning = False

            else:
                msg = "Unkown message received.\n"

            self.mainBluetooth.inData.task_done()
            self.mainBluetooth.outData.put(msg)


    ############################################################################
    # Function 
    ############################################################################
    def Main(self):

        # Display a message on LCD
        self.mainLCD.lcd_display_string("2FA Running", 1)

        # Start a separate thread for bluetooth communications
        self.mainBluetooth.start()

        # Start main loop
        while(self.keepRunning):

            # Check if any data is received from BT
            self.CheckDataFromBT()

        # Once the bt thread ends it will rejoin here
        self.mainBluetooth.join()

        # Clean the GPIO and the LCD screen
        self.mainLCD.lcd_clear()
        GPIO.cleanup()


# Starting Point
if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main = Main()
    main.Main()
