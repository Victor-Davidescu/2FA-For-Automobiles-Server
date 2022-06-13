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
    CONFIG_FILE_PATH = "config.conf"

    ############################################################################
    # Function
    ############################################################################
    def _GetDataFromConfigFile(category:str, name:str) -> str:
        config = ConfigParser()
        try:
            config.read(Configurations.CONFIG_FILE_PATH)
            data = config.get(category, name)
        except Exception as err:
            sys.exit(err)
        else:
            return data


    ############################################################################
    # Function
    ############################################################################
    def GetString(category:str, name:str) -> str:
        try: data = Configurations._GetDataFromConfigFile(category,name)

        except Exception as err:
            logging.error("Could not read data located at [{0}] {1}. Details: {2}".format(category, name, err))
            return None
        else:
            data = data.replace("'",'')
            return data


    ############################################################################
    # Function
    ############################################################################
    def GetInt(category:str, name:str) -> int:
        try: data = Configurations._GetDataFromConfigFile(category,name)
        except Exception as err:
            logging.error("Could not read data located at [{0}] {1}. Details: {2}".format(category, name, err))
            return None
        else: return int(data)


    ############################################################################
    # Function
    ############################################################################
    def GetIntList(category:str, name:str) -> list:
        data = Configurations.GetString(category, name)
        if(data is not None):
            data = data.split(',')
            for i in range(0, len(data)):
                data[i] = int(data[i])
            return data
        else: return None


    ############################################################################
    # Function
    ############################################################################
    def GetKeypadKeysList(category:str, name:str) -> list:
        keysString = Configurations.GetString(category, name)
        keysList = []
        if(keysString is not None):
            for rowKeys in keysString.split('|'):
                keysList.append(rowKeys.split(','))
            return keysList
        else: return None
