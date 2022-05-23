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
        self.mainBT = ClientBTHandler(
            int(self.config.bluetoothPin),
            self.config.pepper, 
            self.config.dbLocation)

        self.mainRelay = RelaySwitch(self.config.relayPin)
        self.mainLCD = LCDDriver.lcd()
        self.mainKepad = Keypad(
            self.config.rowLength, 
            self.config.columnLength, 
            self.config.keypadRowPins,
            self.config.keypadColumnPins,
            self.config.keys,
            self.config.defaultUser,
            self.config.pepper, 
            self.config.dbLocation)


    ############################################################################
    # Function 
    ############################################################################
    def ProcessCMD(self, cmd:str):
        # Switch ON/OFF the relay
        if(cmd == "switch"):
            if(self.mainRelay.Status()): self.mainRelay.OFF()
            else: self.mainRelay.ON()

        # Shutdown program
        elif(cmd == "shutdown"):

            if(not self.mainBT.clientConnected):
                self.keepRunning = False
                self.mainBT.keepRunning = False
                self.mainKepad.keepRunning = False
            else:
                logging.error("Cannot shutdown, because there is an active BT connection.")

        else: logging.debug("Unkown command received.")


    ############################################################################
    # Function 
    ############################################################################
    def CheckCMDQueue(self, queueFromBT:bool):
        cmd = None
        # Get cmds from BT queue if requested and available
        if(queueFromBT and not self.mainBT.cmdQueue.empty()):
            cmd = self.mainBT.cmdQueue.get()
            self.mainBT.cmdQueue.task_done()

        # Get cmds from keypad queue if requested and available
        if(not queueFromBT and not self.mainKepad.cmdQueue.empty()):
            cmd = self.mainKepad.cmdQueue.get()
            self.mainKepad.cmdQueue.task_done()

        return cmd


    ############################################################################
    # Function 
    ############################################################################
    def Main(self):

        # Making sure the relay stays locked at the beginning of the program
        self.mainRelay.OFF()

        # Display a message on LCD
        #self.mainLCD.lcd_display_string("2FA Running", 1)

        # Start a separate thread for BT and keypad communication
        self.mainBT.start()
        self.mainKepad.start()

        # Start main loop
        while(self.keepRunning):
            time.sleep(1)

            # Check and process any command from keypad
            cmd = self.CheckCMDQueue(False)
            if(cmd is not None):
                self.ProcessCMD(cmd)

            # Check and process any command from BT
            cmd = self.CheckCMDQueue(True)
            if(cmd is not None):
                self.ProcessCMD(cmd)

        # Once the bt thread ends it will rejoin here
        self.mainBT.join()
        self.mainKepad.join()

        # Clean the GPIO and the LCD screen
        #self.mainLCD.lcd_clear()
        GPIO.cleanup()


# Starting Point
if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main = Main()
    main.Main()
