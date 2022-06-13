################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import logging


class RelayModule:

    def __init__(self, pin:int):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)


    def TurnON(self) -> None:
        """Turn ON the relay module"""
        GPIO.output(self.pin, GPIO.LOW)
        logging.info("Relay module is ON (UNLOCKED)")


    def TurnOFF(self) -> None:
        """Turn OFF the relay module"""
        GPIO.output(self.pin, GPIO.HIGH)
        logging.info("Relay module is OFF (LOCKED)")


    def Switch(self) -> None:
        """It will switch between ON and OFF depending on the current state."""
        self.TurnOFF() if (self.CurrentState()) else self.TurnON()


    def CurrentState(self) -> bool:
        """
        - `True` : Relay module is ON
        - `False` : Relay module is OFF
        """
        return (not GPIO.input(self.pin))
