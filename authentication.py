import hashlib
import secrets
from database import Database


################################################################################
# Class Authentication
################################################################################
class Authentication():

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self, pepper, dbPath) -> None:
        self.pepper = pepper
        self.database = Database(dbPath)
        self.database.ConnectToDB()


    ############################################################################
    # Function 
    ############################################################################
    def AddUserInDB(self, name, pin):
        
        # Generate random salt value
        salt = secrets.token_hex(32)

        # Hash the pin with salt and pepper
        pinHashed = hashlib.sha256(salt.encode() + pin.encode()  + self.pepper.encode())

        # Append user in the database
        self.database.CreateUser(name, salt, pinHashed.hexdigest())


    ############################################################################
    # Function 
    ############################################################################
    def CheckUserPin(self, name, pin) -> bool:

        # Obtain salt and hashed pin from database
        (saltFromDB, pinHashedFromDB) = self.database.GetSaltAndHashFromUser(name)

        # Check if salt and hash value are none, if they are none no user was found
        if(saltFromDB is not None and pinHashedFromDB is not None):

            # Hash the obtained pin
            pinHashed = hashlib.sha256(saltFromDB.encode() + pin.encode() + self.pepper.encode())

            # Return comparison result
            return pinHashed.hexdigest() == pinHashedFromDB

        else: return False
