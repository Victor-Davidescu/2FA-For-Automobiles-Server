################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import logging

################################################################################
# Class Relay Module
################################################################################
class RelayModule:

    ################################################################################
    # Class Constructor
    ################################################################################
    def __init__(self, pin:int) -> None:
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)


    ############################################################################
    # Function
    ############################################################################
    def TurnON(self) -> None:
        """Turn ON the relay module"""
        GPIO.output(self.pin, GPIO.LOW)
        logging.info("Relay module is ON (UNLOCKED)")


    ############################################################################
    # Function
    ############################################################################
    def TurnOFF(self) -> None:
        """Turn OFF the relay module"""
        GPIO.output(self.pin, GPIO.HIGH)
        logging.info("Relay module is OFF (LOCKED)")


    ############################################################################
    # Function
    ############################################################################
    def Switch(self) -> None:
        """It will switch between ON and OFF depending on the current state."""
        self.TurnOFF() if (self.CurrentState()) else self.TurnON()


    ############################################################################
    # Function
    ############################################################################
    def CurrentState(self) -> bool:
        """
        - `True` : Relay module is ON
        - `False` : Relay module is OFF
        """
        return (not GPIO.input(self.pin))
