from time import time
import RPi.GPIO as GPIO
import time
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
os.system('clear')
print("IDLE STATE | Waiting for button press")

keepRunning = True
while keepRunning:
    time.sleep(3)
    if (GPIO.input(16) == GPIO.HIGH):
        print("IDLE STATE | Button was pushed!")
        keepRunning = False

GPIO.cleanup() # Clean the GPIO