################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import logging


################################################################################
# Relay Switch
################################################################################
class RelaySwitch:

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self, pin):
        self.pin = pin  
        GPIO.setup(self.pin, GPIO.OUT)


    ############################################################################
    # Function 
    ############################################################################
    def ON(self) -> None:
        GPIO.output(self.pin, GPIO.LOW)


    ############################################################################
    # Function 
    ############################################################################
    def OFF(self) -> None:
        GPIO.output(self.pin, GPIO.HIGH)

    
    ############################################################################
    # Function 
    ############################################################################
    def Status(self) -> bool:
        """
        - `True` : Relay switch is ON
        - `False` : Relay switch is OFF
        """
        return (not GPIO.input(self.pin))
