################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
from configparser import ConfigParser
import logging
import sys

CONFIG_FILE_PATH = "config.conf"

################################################################################
# Class Configurations
################################################################################
class Configurations:

    ############################################################################
    # Class Constructor
    ############################################################################
    def __init__(self) -> None:
        self.config = ConfigParser()
        try: self.config.read(CONFIG_FILE_PATH)
        except Exception as err:
            logging.critical("Could not read the configuration file. Details: {0}".format(err))
            sys.exit(err)
        else:
            logging.debug("Configuration file read successfully")


    ############################################################################
    # Function
    ############################################################################
    def GetString(self, category:str, name:str) -> str:
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
    def GetInt(self, category:str, name:str) -> int:
        try: data = self.config.getint(category, name)
        except Exception as err:
            logging.error("Could not read data located at [{0}] {1}. Details: {2}".format(category, name, err))
            return None
        else: return data


    ############################################################################
    # Function
    ############################################################################
    def GetIntList(self, category:str, name:str) -> list:
        data = self.GetString(category, name)
        if(data is not None):
            data = data.split(',')
            for i in range(0, len(data)):
                data[i] = int(data[i])
            return data
        else: return None


    ############################################################################
    # Function
    ############################################################################
    def GetKeypadKeysList(self, category:str, name:str) -> list:
        keysString = self.GetString(category, name)
        keysList = []
        if(keysString is not None):
            for rowKeys in keysString.split('|'):
                keysList.append(rowKeys.split(','))
            return keysList
        else: return None
