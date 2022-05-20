################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import third_party_drivers.I2C_LCD_driver as LCDDriver
import RPi.GPIO as GPIO
import time
import logging
from config import Configurations
from keypad import Keypad
from relay import RelaySwitch
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
        self.mainBluetooth = ClientBTHandler(int(self.config.bluetoothPin),self.config.pepper, 
            self.config.dbLocation)
        self.mainRelay = RelaySwitch(self.config.relayPin)
        self.mainLCD = LCDDriver.lcd()
        self.mainKepad = Keypad(
            self.config.rowLength, 
            self.config.columnLength, 
            self.config.keypadRowPins,
            self.config.keypadColumnPins,
            self.config.keys)


    ############################################################################
    # Function 
    ############################################################################
    def CheckCMDQueueFromBT(self):

        # Check if the queue is not empty
        if(not self.mainBluetooth.cmdQueue.empty()):

            cmd = self.mainBluetooth.cmdQueue.get()
            logging.info("Command received from BT: {0}".format(cmd))

            if(cmd == "lock"):
                self.mainRelay.OFF()
                logging.debug("Relay should switch off.")

            elif(cmd == "unlock"):
                self.mainRelay.ON()
                logging.debug("Relay should switch on.")

            elif(cmd == "shutdown"):
                self.mainBluetooth.keepRunning = False
                self.keepRunning = False

            self.mainBluetooth.cmdQueue.task_done()


    ############################################################################
    # Function 
    ############################################################################
    def Main(self):

        # Making sure the relay stays locked at the beginning of the program
        self.mainRelay.OFF()

        # Display a message on LCD
        self.mainLCD.lcd_display_string("2FA Running", 1)

        # Start a separate thread for bluetooth communications
        self.mainBluetooth.start()

        # Start main loop
        while(self.keepRunning):

            # Check if any data is received from BT
            self.CheckCMDQueueFromBT()

            time.sleep(1)

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
