from configparser import ConfigParser

class Configurations:

    def __init__(self, fileLocation) -> None:

        # Read the configuration file
        config = ConfigParser()
        config.read(fileLocation)

        # GPIO Pins
        self.relayPin = config.getint('gpio_pins','relay_pin')
        self.keypadRowPins = config.get('gpio_pins','keypad_row_pins').split(',')
        self.keypadColumnPins = config.get('gpio_pins','keypad_column_pins').split(',')

        # Keypad
        self.defaultUser = config.get('keypad','default_user').replace("'",'')
        self.rowLength = config.getint('keypad','row_length')
        self.columnLength = config.getint('keypad','column_length')
        self.keys = []
        allKeys = config.get('keypad','keys').replace("'",'')
        for rowKeys in allKeys.split('|'):
            self.keys.append(rowKeys.split(','))

        # Database
        self.dbLocation = config.get('database','location').replace("'",'')

        # Hash
        self.pepper = config.get('hash','pepper_value').replace("'",'')

        # Bluetooth
        self.bluetoothPin = config.get('bluetooth','port')
