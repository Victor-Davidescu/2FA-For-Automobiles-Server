################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import RPi.GPIO as GPIO
import time
import threading
import logging


class Led (threading.Thread):

    def __init__(self, pin:int) -> None:
        threading.Thread.__init__(self)
        self._pin = pin
        self._status = "OFF"
        self._delay = 0.6
        self._keepRunning = True

    def ON(self) -> None: self._status = "ON"
    def OFF(self) -> None: self._status = "OFF"
    def Blink(self) -> None: self._status = "BLINK"
    def Stop(self) -> None: self._keepRunning = False

    def run(self):
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin,GPIO.LOW)
        logging.debug("LED has started.")

        # LED main loop
        while(self._keepRunning):
            time.sleep(self._delay)
            if(self._status == "ON"): GPIO.output(self._pin,GPIO.HIGH)
            elif(self._status == "OFF"): GPIO.output(self._pin,GPIO.LOW)
            elif(self._status == "BLINK"):
                while(self._status == "BLINK"):
                    GPIO.output(self._pin,GPIO.HIGH)
                    time.sleep(self._delay)
                    GPIO.output(self._pin,GPIO.LOW)
                    time.sleep(self._delay)

        GPIO.output(self._pin,GPIO.LOW)
        logging.debug("LED has stopped.")
