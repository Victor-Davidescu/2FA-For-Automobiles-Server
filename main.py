################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import time
import logging
from config import Configurations
from keypad import Keypad
from relay_module import RelayModule
from serverBluetoothThread import ServerBluetoothThread
from led import Led


################################################################################
# Class Main
################################################################################-
class Main:

    ############################################################################
    # Function
    ############################################################################
    def __init__(self):
        # Setup the GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Get required configurations
        relayPin = Configurations.GetInt('gpio_pins','relay_pin')
        ledPowerPin = Configurations.GetInt('gpio_pins','led_power_pin')

        # Declare instances
        self.ledPower = Led(ledPowerPin)
        self.relaySwitch = RelayModule(relayPin)
        self.mainBT = ServerBluetoothThread()
        self.mainKepad = Keypad()

        # Declare other variables
        self.keepRunning = True


    ############################################################################
    # Function
    ############################################################################
    def ProcessCMD(self, cmd:str):
        """Process the received command."""

        # Switch ON/OFF the relay
        if(cmd == "switch"):
            self.relaySwitch.Switch()

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
        self.relaySwitch.TurnOFF() # Turn off (lock) the relay switch
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


################################################################################
#   STARTING POINT
################################################################################
if __name__ == "__main__":
    logging.basicConfig(
        level="DEBUG",
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S")

    main = Main()
    main.Main()
