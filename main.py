################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
from xmlrpc.client import Boolean
import RPi.GPIO as GPIO
import time
import logging
import sys
from config import Configurations
from keypad import Keypad
from relayModule import RelayModule
from serverBluetoothThread import ServerBluetoothThread
from led import Led

################################################################################
# Class Main
################################################################################
class Main:

    # Global Variables
    keepRunning:bool = True
    loopDelay:int = 1
    ledPower:Led = None
    relaySwitch:RelayModule = None
    bluetooth:ServerBluetoothThread = None
    keypad:Keypad = None


    ############################################################################
    # Function
    ############################################################################
    def _InitLogging() -> None:
        try:
            logging.basicConfig(
                level="DEBUG",
                format="%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%H:%M:%S")

        except Exception as err:
            logging.critical(err)
            Main.Stop()


    ############################################################################
    # Function
    ############################################################################
    def _InitGPIO() -> None:
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

        except Exception as err:
            logging.critical(err)
            Main.Stop()


    ############################################################################
    # Function
    ############################################################################
    def _InitComponents() -> None:
        relayPin = Configurations.GetInt('gpio_pins','relay_pin')
        ledPowerPin = Configurations.GetInt('gpio_pins','led_power_pin')

        if(relayPin and ledPowerPin):
            Main.ledPower = Led(ledPowerPin)
            Main.relaySwitch = RelayModule(relayPin)
            Main.bluetooth = ServerBluetoothThread()
            Main.keypad = Keypad()

        else:
            logging.critical("Relay pin and/or Power led pin is 'None'.")
            Main.Stop()


    ############################################################################
    # Function
    ############################################################################
    def _StartComponents() -> None:
        Main.relaySwitch.TurnOFF() # Turn off (lock) the relay switch
        Main.ledPower.start() # Start the thread for power led
        Main.ledPower.ON() # Turn on the power led
        Main.bluetooth.start() # Start thread for bluetooth connection
        Main.keypad.start() # Start thread for keypad


    ############################################################################
    # Function | Proccess the recived command
    ############################################################################
    def _ProcessCMD(cmd:str = None) -> None:
        if(cmd):
            if(cmd == "switch"): Main.relaySwitch.Switch()
            elif(cmd == "stopBT"): Main.StopBluetooth()
            elif(cmd == "startBT"): Main.StartBluetooth()
            elif(cmd == "shutdown"):
                if(not Main.bluetooth.clientConnected): Main.Stop()
                else: logging.error("Cannot shutdown, because there is an active BT connection.")

            else: logging.warning("Unkown command received. {0}".format(cmd))
        else: logging.error("Received command 'None' for processing.")


    ############################################################################
    # Function
    ############################################################################
    def _CheckCmdQueueFromBT() -> None:
        if(not Main.bluetooth.cmdQueue.empty()):
            Main._ProcessCMD(Main.bluetooth.cmdQueue.get())
            Main.bluetooth.cmdQueue.task_done()


    ############################################################################
    # Function
    ############################################################################
    def _CheckCmdQueueFromKeypad() -> None:
        if(not Main.keypad.cmdQueue.empty()):
            Main._ProcessCMD(Main.keypad.cmdQueue.get())
            Main.keypad.cmdQueue.task_done()


    ############################################################################
    # Function
    ############################################################################
    def StopBluetooth() -> None:
        Main.bluetooth.Stop() # Stop & wait for bluetooth
        Main.bluetooth.join()


    ############################################################################
    # Function
    ############################################################################
    def StartBluetooth() -> None:
        Main.bluetooth = ServerBluetoothThread()
        Main.bluetooth.start() # Start thread for bluetooth connection


    ############################################################################
    # Function
    ############################################################################
    def Stop() -> None:
        Main.keepRunning = False
        Main.bluetooth.Stop() # Stop & wait for bluetooth
        Main.bluetooth.join()
        Main.keypad.Stop() # Stop & wait for keypad
        Main.keypad.join()
        Main.ledPower.Stop() # Stop & wait for power led
        Main.ledPower.join()

    ############################################################################
    # Function
    ############################################################################
    def Start() -> None:
        Main._InitLogging()
        Main._InitGPIO()
        Main._InitComponents()
        Main._StartComponents()

        while(Main.keepRunning): # Main Loop
            time.sleep(Main.loopDelay) # Time delay
            Main._CheckCmdQueueFromBT()
            Main._CheckCmdQueueFromKeypad()

        GPIO.cleanup() # Clean the GPIO
        sys.exit(0) # Close the program

################################################################################
#   STARTING POINT
################################################################################
if __name__ == "__main__": Main.Start()
