################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import time
import logging
from config import Configurations
from keypad import Keypad
from relay import RelaySwitch
from clientBTHandler import ClientBTHandler
from led import Led


################################################################################
# Class Main
################################################################################
class Main:

    ############################################################################
    # Constructor
    ############################################################################
    def __init__(self):
        # Setup the GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Get required configurations
        config = Configurations()
        relayPin = config.GetInt('gpio_pins','relay_pin')
        ledPowerPin = config.GetInt('gpio_pins','led_power_pin')

        # Declare instances
        self.ledPower = Led(ledPowerPin)
        self.relaySwitch = RelaySwitch(relayPin)
        self.mainBT = ClientBTHandler()
        self.mainKepad = Keypad()

        # Declare other variables
        self.keepRunning = True


    ############################################################################
    # Function
    ############################################################################
    def ProcessCMD(self, cmd:str):
        # Switch ON/OFF the relay
        if(cmd == "switch"):
            if(self.relaySwitch.Status()): self.relaySwitch.OFF()
            else: self.relaySwitch.ON()

        # Shutdown program
        elif(cmd == "shutdown"):
            if(not self.mainBT.clientConnected):
                self.Stop()
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
    def Stop(self):
        self.keepRunning = False
        self.mainBT.Stop()
        self.mainBT.join()
        self.mainKepad.Stop()
        self.mainKepad.join()
        self.ledPower.Stop()
        self.ledPower.join()


    ############################################################################
    # Function
    ############################################################################
    def Main(self):
        self.relaySwitch.OFF() # Turn off (lock) the relay switch
        self.ledPower.start() # Start the thread for power led
        self.ledPower.ON() # Turn on the power led
        self.mainBT.start() # Start thread for bluetooth connection
        self.mainKepad.start() # Start thread for keypad

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

        # Clean the GPIO
        GPIO.cleanup()


# Starting Point
if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main = Main()
    main.Main()
