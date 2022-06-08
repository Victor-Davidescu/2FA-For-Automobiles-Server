################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import time
import threading
import queue
import logging
import RPi.GPIO as GPIO
from buzzer import Buzzer
from authentication import Authentication
from config import Configurations
from third_party_drivers.I2C_LCD_driver import lcd as LCD


################################################################################
# Class Keypad
################################################################################
class Keypad (threading.Thread):
    """
    Class Keypad for receiving inputs from the physical keypad
    """

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self):
        threading.Thread.__init__(self)

        # Get necessary configurations
        self._rowLength = Configurations.GetInt('keypad','row_length')
        self._columnLength = Configurations.GetInt('keypad','column_length')
        self._rowPins = Configurations.GetIntList('gpio_pins','keypad_row_pins')
        self._columnPins = Configurations.GetIntList('gpio_pins','keypad_column_pins')
        self._keys = Configurations.GetKeypadKeysList('keypad','keys')
        self._defaultUser = Configurations.GetString('keypad','default_user')
        buzzerPin = Configurations.GetInt('gpio_pins','buzzer_pin')
        self.keypadLockTime = Configurations.GetInt('keypad','keypad_lock_time_seconds')

        # Declare instances
        self.lcd = LCD()
        self.buzzer = Buzzer(buzzerPin)

        # Declare other variables
        self._loginAttempts = 3
        self._userAuthenticated = False
        self._keepRunning = True
        self.cmdQueue = queue.Queue()


    ############################################################################
    # Function
    ############################################################################
    def _SetupGPIOPins(self) -> None:
        # Setup the row pins as output pins
        for pin in self._rowPins: GPIO.setup(int(pin), GPIO.OUT)
        # Setup the column pins as input pins
        for pin in self._columnPins: GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


    ############################################################################
    # Function
    ############################################################################
    def _ReadKey(self) -> str:
        keyReceived = None

        # Loop until an input is received or until thread needs to be stopped
        while (keyReceived is None and self._keepRunning):
            time.sleep(0.2) # Delay the key input to not receive repetitive same input

            # Interate thorugh row pins
            for (indexRow, pinRow) in zip(range(4), self._rowPins):
                GPIO.output(int(pinRow), GPIO.HIGH) # Send an output on the current row pin

                # Iterate thorugh column pins
                for (indexColumn, pinColumn) in zip(range(4), self._columnPins):

                    # Check if there is  an output
                    if(GPIO.input(int(pinColumn)) == 1):
                        keyReceived = self._keys[indexRow][indexColumn]
                        logging.debug("From keypad received key '{0}'.".format(keyReceived))

                # Stop sending an output on the current row pin
                GPIO.output(int(pinRow), GPIO.LOW)

        return keyReceived


    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionA(self):
        self.lcd.lcd_clear()

        # Check if user is already authenticated
        if(not self._userAuthenticated):
            logging.debug("Keypad: User requested to login.")
            logging.debug("Keypad: Used default user: {0}".format(self._defaultUser))
            self.lcd.lcd_display_string("Enter Pin",1)
            self.buzzer.Beep(noOfBeeps=2)

            pin = ""
            loop = True
            pinConfirmed= False

            # Loop until user enters the PIN and confirms it or cancel
            while(loop and self._keepRunning):
                key = self._ReadKey() # Wait for user to enter a key
                self.buzzer.Beep()
                if(key == 'A'): # A for cancelling authentication
                    logging.debug("Keypad: PIN received")
                    pinConfirmed = True
                    loop = False
                elif(key == 'B'): # B for confirming PIN
                    logging.debug("Keypad: Authentication cancelled")
                    self.lcd.lcd_display_string("Login cancelled", 1)
                    loop = False
                elif(key == 'C'): # C for reseting PIN
                    logging.debug("Keypad: PIN resetted")
                    self.lcd.lcd_display_string(" "*16,2)
                    pin = ""
                elif(key.isdigit()):
                    pin = pin + key
                    self.lcd.lcd_display_string("*"*len(pin),2)

            # Check if user confirmed pin
            if(pinConfirmed):
                # Check if the pin received is correct
                if(self.auth.CheckUserPin(self._defaultUser, pin)):
                    logging.debug("Authentication is successful.")
                    self._userAuthenticated = True
                    self.lcd.lcd_clear()
                    self.lcd.lcd_display_string("Logged in", 1)
                    self.buzzer.Beep()
                else:
                    logging.debug("Keypad: Authentication failed.")
                    self.lcd.lcd_clear()

                    # Check if there are any login attempts left
                    if(self._loginAttempts == 0):
                        self.lcd.lcd_display_string("Keypad is locked for",1)
                        self.lcd.lcd_display_string("{0} seconds".format(self.keypadLockTime),2)
                        time.sleep(self.keypadLockTime)
                    else:
                        self.lcd.lcd_display_string("Wrong PIN",1)
                        self.lcd.lcd_display_string("{0} tries left.".format(self._loginAttempts),2)
                        self.buzzer.Beep(longBeep=True)
                        self._loginAttempts -= 1
            else:
                logging.debug("Keypad: Authentication is cancelled")
                self.lcd.lcd_clear()
                self.lcd.lcd_display_string("Login Cancelled",1)
                self.buzzer.Beep(longBeep=True)
        else:
            logging.debug("Keypad: User logged out.")
            self._userAuthenticated = False
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string("You logged out", 1)
            self.buzzer.Beep(noOfBeeps=2)


    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionB(self):
        if(self._userAuthenticated):
            logging.debug("User requested to switch the relay")
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string("Relay switched", 1)
            self.buzzer.Beep()
            self.cmdQueue.put("switch")
        else: logging.debug("Switch command denied.")


    ############################################################################
    # Function
    ############################################################################
    def _KeyFunctionC(self):
        logging.debug("User requested to shutdown the program")
        self.lcd.lcd_clear()
        self.lcd.lcd_display_string("Shutting down",1)
        self.lcd.lcd_display_string("Please wait...",2)
        self.buzzer.Beep(longBeep=True)
        self.cmdQueue.put("shutdown")


    ############################################################################
    # Function
    ############################################################################
    def _ProcessKey(self, key):
        if(key == 'A'): self._KeyFunctionA() # Login/Logout Key
        elif(key=='B'): self._KeyFunctionB() # Lock/Unlock Key
        elif(key=='C'): self._KeyFunctionC() # Shutdown Key
        elif(key=='D'): pass # Nothing assigned here, yet?
        elif(key=='*'): pass # Nothing assigned here, yet?
        elif(key=='#'): pass # Nothing assigned here, yet?


    ############################################################################
    # Function
    ############################################################################
    def Stop(self): self._keepRunning = False


    ############################################################################
    # Function
    ############################################################################
    def run(self):
        self.auth = Authentication() # Setup the authentication class
        self._SetupGPIOPins() # Setup the GPIO pins for the keybad (pins for output/input)

        self.lcd.lcd_clear() # Clean the LCD
        self.lcd.backlight(1) # Turn ON the LCD backlight
        self.lcd.lcd_display_string("System Active",1)
        self.lcd.lcd_display_string("Press A to login",2)

        # Thread main loop
        while(self._keepRunning): # Run the keypad loop
            key = self._ReadKey() # Wait for a key press from keypad
            if(key is not None): self._ProcessKey(key) # Process the received key

        self.lcd.lcd_clear() # Clear the LCD
        self.lcd.backlight(0) # Turn off the LCD backlight
        logging.debug("Keypad has stopped.")
