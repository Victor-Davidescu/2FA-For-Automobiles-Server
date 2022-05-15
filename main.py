################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import third_party_drivers.I2C_LCD_driver as LCDDriver
import RPi.GPIO as GPIO
import time

# Own Modules
from config import Configurations
from keypad import Keypad
from relay import RelaySwitch
from authentication import Authentication
from bluetoothHandler import BluetoothHandler

class Main:

    def __init__(self):
        # Setup GPIO to use Broadcom uses the actual pin number
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.config = Configurations("config.conf")
        self.mainRelay = RelaySwitch(self.config.relayPin)

        self.mainLCD = LCDDriver.lcd()

        self.mainBluetooth = BluetoothHandler(int(self.config.bluetoothPin))

        self.mainBluetooth.start()


        """
        self.mainKepad = Keypad(
            self.config.rowLength,
            self.config.columnLength,
            self.config.keypadRowPins,
            self.config.keypadColumnPins,
            self.config.keys)
        self.mainAuth = Authentication(
            self.config.pepper, 
            self.config.dbLocation)
        """
        


    def Loop(self):

        self.mainLCD.lcd_display_string("BT Disconnected ", 1)
        self.mainLCD.lcd_display_string("LOCKED", 2)

        #self.mainBluetooth.InitiateConnection()
        self.mainLCD.lcd_display_string("BT Connected    ", 1)

        loop = True
        while(loop):

            time.sleep(1)

            """
            if(self.mainKepad.ReadKey() == 'A'):
                self.mainRelay.ON()
                self.mainLCD.lcd_display_string("Relay: OPEN", 2)

            elif(self.mainKepad.ReadKey() == 'B'):
                self.mainRelay.OFF()
                self.mainLCD.lcd_display_string("Relay: CLOSED", 2)

            elif(self.mainKepad.ReadKey() == 'C'):
                loop = False
            """

            if(self.mainBluetooth.ReceiveMessage() == 'unlock'):
                print("unlock")
                self.mainRelay.ON()
                self.mainLCD.lcd_display_string("UNLOCKED", 2)

            elif(self.mainBluetooth.ReceiveMessage() == 'lock'):
                print("lock")
                self.mainRelay.OFF()
                self.mainLCD.lcd_display_string("LOCKED  ", 2)

            elif(self.mainBluetooth.ReceiveMessage() == 'exit'):
                print("exit")
                self.mainRelay.OFF()
                self.mainBluetooth.CloseConnection()
                self.mainLCD.lcd_display_string("BT Disconnected ", 1)
                loop = False



        self.mainLCD.lcd_clear()
        self.mainLCD.lcd_display_string("Stopping...", 1)
        time.sleep(1)
        self.mainLCD.lcd_clear()
        GPIO.cleanup()



# Starting Point
if __name__ == "__main__":
    main = Main()
    #main.Loop()
    
