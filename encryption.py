################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
from config import Configurations
from Crypto.Cipher import AES
import base64
import os
import logging

BLOCK_SIZE = 16

################################################################################
# Class Encryption
################################################################################
class Encryption:

    ############################################################################
    # Function
    ############################################################################
    def _GetKey() -> bytes:
        keyFileLocation = Configurations.GetString("security","key_file_location")

        try:
            file = open(keyFileLocation,'rb')
            key:bytes = file.read()
            file.close()

        except Exception as err:
            logging.error(err)
            return None

        else: return key


    ############################################################################
    # Function
    ############################################################################
    def _Pad(byteArray:bytes) -> bytes:
        padLength = BLOCK_SIZE - len(byteArray) % BLOCK_SIZE
        return byteArray + (bytes([padLength]) * padLength)


    ############################################################################
    # Function
    ############################################################################
    def _Unpad(byteArray:bytes) -> bytes:
        last_byte = byteArray[-1]
        return byteArray[0:-last_byte]


    ############################################################################
    # Function
    ############################################################################
    def EncryptMessage(msg:str) -> str:
        try:
            byteArray = msg.encode("UTF-8")
            padded = Encryption._Pad(byteArray)
            initVector = os.urandom(AES.block_size)
            cipher = AES.new(Encryption._GetKey(), AES.MODE_CBC, initVector )
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(initVector+encrypted).decode("UTF-8")

        except Exception as err:
            logging.error("Failed to encrypt message. {0}".format(err))
            return None


    ############################################################################
    # Function
    ############################################################################
    def DecryptMessage(msg:str) -> str:
        try:
            byteArray = base64.b64decode(msg)
            initVector = byteArray[0:16]
            msgBytes = byteArray[16:]
            cipher = AES.new(Encryption._GetKey(), AES.MODE_CBC, initVector)
            decryptedPad = cipher.decrypt(msgBytes)
            decrypted = Encryption._Unpad(decryptedPad)
            return decrypted.decode("UTF-8")

        except Exception as err:
            logging.error("Failed to decrypt message. {0}".format(err))
            return None
