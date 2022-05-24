################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
from configparser import ConfigParser
import logging
import sys

################################################################################
# Class Configurations
################################################################################
class Configurations:


    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self, fileLocation) -> None:
        self.config = ConfigParser()
        try: self.config.read(fileLocation)
        except Exception as err:
            logging.critical("Could not read the configuration file. Details: {0}".format(err))
            sys.exit(err)
        else:
            logging.debug("Configuration file read successfully")
            self._GetConfigurations()


    ############################################################################
    # Function
    ############################################################################
    def _GetString(self, category:str, name:str) -> str:
        try: data = self.config.get(category, name)
        except Exception as err:
            logging.error("Could not read data located at [{0}] {1}. Details: {2}".format(category, name, err))
            return None
        else:
            data = data.replace("'",'')
            return data


    ############################################################################
    # Function
    ############################################################################
    def _GetInt(self, category:str, name:str) -> int:
        try: data = self.config.getint(category, name)
        except Exception as err:
            logging.error("Could not read data located at [{0}] {1}. Details: {2}".format(category, name, err))
            return None
        else: return data


    ############################################################################
    # Function
    ############################################################################
    def _GetIntList(self, category:str, name:str) -> list:
        data = self._GetString(category, name)
        if(data is not None):
            data = data.split(',')
            for i in range(0, len(data)):
                data[i] = int(data[i])
            return data
        else: return None


    ############################################################################
    # Function
    ############################################################################
    def _GetKeypadKeysList(self, category:str, name:str) -> list:
        keysString = self._GetString(category, name)
        keysList = []
        if(keysString is not None):
            for rowKeys in keysString.split('|'):
                keysList.append(rowKeys.split(','))
            return keysList
        else: return None


    ############################################################################
    # Function
    ############################################################################
    def _GetConfigurations(self):
        # GPIO Pins
        self.relayPin = self._GetInt('gpio_pins','relay_pin')
        self.buzzerPin = self._GetInt('gpio_pins','buzzer_pin')
        self.keypadRowPins = self._GetIntList('gpio_pins','keypad_row_pins')
        self.keypadColumnPins = self._GetIntList('gpio_pins','keypad_column_pins')

        # Keypad Configurations
        self.defaultUser = self._GetString('keypad','default_user')
        self.rowLength = self._GetInt('keypad','row_length')
        self.columnLength = self._GetInt('keypad','column_length')
        self.keys = self._GetKeypadKeysList('keypad','keys')

        # Database configuration
        self.dbLocation = self._GetString('database','location')

        # Hash configuration
        self.pepper = self._GetString('hash','pepper_value')

        # Bluetooth configuration
        self.bluetoothPin = self._GetInt('bluetooth','port')
