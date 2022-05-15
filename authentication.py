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

    ############################################################################
    # Function 
    ############################################################################
    def RetreiveNewUserID(self):
        records = self.database.RetreiveAllRecords()
        return len(records)

    ############################################################################
    # Function 
    ############################################################################
    def ResetDatabase(self):
        self.database.DeleteTable()
        self.database.CreateTable()


    ############################################################################
    # Function 
    ############################################################################
    def AddUserInDB(self, name, pin):
        
        # Generate random salt value
        salt = secrets.token_hex(32)

        # Hash the pin with salt and pepper
        pinHashed = hashlib.sha256(salt.encode() + pin.encode()  + self.pepper.encode())

        # Obtain new user ID
        userID = self.RetreiveNewUserID()

        # Append user in the database
        self.database.CreateUser(userID, name, salt, pinHashed.hexdigest())


    ############################################################################
    # Function 
    ############################################################################
    def CheckUserPin(self, name, pin) -> bool:

        # Obtain salt and hashed pin from database
        (saltFromDB, pinHashedFromDB) = self.database.RetreiveUserDetails(name)

        # Hash the obtained pin
        pinHashed = hashlib.sha256(saltFromDB.encode() + pin.encode() + self.pepper.encode())

        # Compare the hashed pin with the hashed pin from the database
        if(pinHashed.hexdigest() == pinHashedFromDB):
            return True
        else:
            return False
