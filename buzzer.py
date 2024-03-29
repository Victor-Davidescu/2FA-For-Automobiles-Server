################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import logging
import time


################################################################################
# Class Buzzer
################################################################################
class Buzzer:

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self, pin:int) -> None:
        self._pin = pin
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin,GPIO.LOW)


    ############################################################################
    # Function
    ############################################################################
    def Beep(self, longBeep=False, noOfBeeps=1) -> None:
        for i in range(0, noOfBeeps):
            delay = 1 if(longBeep) else 0.05
            GPIO.output(self._pin,GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self._pin,GPIO.LOW)
            logging.debug("Beep")
            time.sleep(0.1)
