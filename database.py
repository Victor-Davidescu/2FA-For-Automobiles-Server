################################################################################
# Author: Victor Davidescu
# SID: 1705734
################################################################################
import sqlite3
import logging
from config import Configurations

################################################################################
# Class Database
################################################################################
class Database:

    ############################################################################
    # Function
    ############################################################################
    def __init__(self) -> None:

        # Get neccessary configurations
        self.config = Configurations()
        self.pathToDB = self.config.GetString('database','location')
        del self.config

        self.connection = None
        self.connectedToDB = False
        self.usersTableName = "USERS"


    ############################################################################
    # Function
    ############################################################################
    def ConnectToDB(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.pathToDB)
        except Exception as err:
            logging.error(err)
            return False
        else:
            logging.info("Connected successfully to the DB.")
            self.connectedToDB = True
            return True


    ############################################################################
    # Function
    ############################################################################
    def _DeleteTable(self, tableName:str) -> None:
        try: self.connection.execute("DROP TABLE {0}".format(tableName))
        except Exception as err: logging.error(err)
        else:
            self.connection.commit()
            logging.debug("Deleted the table {0} from DB.".format(tableName))


    ############################################################################
    # Function
    ############################################################################
    def _CreateUsersTable(self) -> None:
        try:
            self.connection.execute('''CREATE TABLE {0} (
                ID INT PRIMARY KEY NOT NULL,
                NAME CHAR(10) NOT NULL,
                SALT CHAR(100) NOT NULL,
                HASH CHAR(100) NOT NULL);
                '''.format(self.usersTableName))
        except Exception as err: logging.error(err)
        else:
            self.connection.commit()
            logging.debug("Created the table {0} in DB.".format(self.usersTableName))


    ############################################################################
    # Function
    ############################################################################
    def ResetUsersTable(self):
        # Check if there is a connection to DB.
        if(self.connectedToDB):
            self._DeleteTable(self.usersTableName)
            self._CreateUsersTable()
        else:
            logging.error("There is no connection made to DB, reset for user's table is aborted.")


    ############################################################################
    # Function
    ############################################################################
    def _GetNewUserID(self) -> int:
        records = self.GetDetailsFromAllUsers()
        return len(records)


    ############################################################################
    # Function
    ############################################################################
    def InsertUserInDB(self, name:str, salt:str, hash:str) -> bool:
        # Check if there is a connection to DB
        if(self.connectedToDB):
            userID = self._GetNewUserID()
            sqlQuery = "INSERT INTO {0} (ID,NAME,SALT,HASH) VALUES ({1},'{2}','{3}','{4}');".format(self.usersTableName,userID,name,salt,hash)
            try: self.connection.execute(sqlQuery)
            except Exception as err:
                logging.error(err)
                return False
            else:
                self.connection.commit()
                logging.info("Inserted user {0} in database".format(name))
                return True
        else: logging.error("There is no connection made to DB, inserting new user is aborted.")


    ############################################################################
    # Function
    ############################################################################
    def GetSaltAndHashFromUser(self, name:str):
        # Check if there is a connection to DB
        if(self.connectedToDB):
            sqlQuery = "SELECT * FROM {0} WHERE NAME = '{1}'".format(self.usersTableName, name)
            saltValue = None
            hashValue = None

            try:
                cursor = self.connection.execute(sqlQuery)
                for row in cursor:
                    saltValue = row[2]
                    hashValue = row[3]
                    break

            except Exception as err: logging.error(err)
            return (saltValue, hashValue)

        else:
            logging.error("There is no connection made to DB, could not get salt and hash values.")
            return (None,None)


    ############################################################################
    # Function
    ############################################################################
    def GetDetailsFromAllUsers(self) -> list:
        # Check if there is a connection to DB
        if(self.connectedToDB):
            records = []

            try:
                cursor = self.connection.execute("SELECT * FROM USERS")
                for row in cursor:
                    records.append(row)
            except Exception as err:
                logging.error(err)
                return None
            else:
                return records
        else:
            logging.error("There is no connection made to DB, reset for user's table is aborted.")
            return None


    ############################################################################
    # Function
    ############################################################################
    def CloseConnectionToDB(self):
        # Check if there is a connection to DB
        if(self.connectedToDB):
            self.connection.close()
        else:
            logging.error("There is no connection to be closed.")
