################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import time

CONFIG_FILENAME = "config.conf"

################################################################################
# Class Keypad
################################################################################
class Keypad:
    """
    Class Keypad for receiving inputs from the physical keypad
    """

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self, rowLength, columnLength, rowPins, columnPins, keys):
        self.rowLength = rowLength
        self.columnLength = columnLength
        self.rowPins = rowPins
        self.columnPins = columnPins
        self.keys = keys
        self.SetupGPIOPins()

    ############################################################################
    # Function for setting up the GPIO pins for the keypad
    ############################################################################
    def SetupGPIOPins(self) -> None:
        """
        Setup the GPIO pins for the keypad.
        """
        # Setup the row pins as output pins
        for pin in self.rowPins:
            GPIO.setup(int(pin), GPIO.OUT)
        # Setup the column pins as input pins
        for pin in self.columnPins:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
      
    ############################################################################
    # Function for reading key from the keypad
    ############################################################################
    def ReadKey(self) -> str:
        """
        Read key from the keypad.
        """
        keyReceived = None

        # Loop until an input is received
        while (keyReceived is None):
            time.sleep(0.1)

            # Interate thorugh row pins
            for (indexRow, pinRow) in zip(range(4), self.rowPins):

                # Send an output on the current row pin
                GPIO.output(int(pinRow), GPIO.HIGH)

                # Iterate thorugh column pins
                for (indexColumn, pinColumn) in zip(range(4), self.columnPins):

                    # Check if there is  an output
                    if(GPIO.input(int(pinColumn)) == 1):
                        keyReceived = self.keys[indexRow][indexColumn]

                # Stop sending an output on the current row pin
                GPIO.output(int(pinRow), GPIO.LOW)

        return keyReceived
