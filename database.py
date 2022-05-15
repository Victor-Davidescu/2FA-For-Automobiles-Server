import sqlite3

from numpy import record

################################################################################
# Class Database
################################################################################
class Database:

    ############################################################################
    # Function 
    ############################################################################
    def __init__(self, dbLocation) -> None:
        self.connection = sqlite3.connect(dbLocation)
        self.tableName = "USERS"


    ############################################################################
    # Function 
    ############################################################################
    def DeleteTable(self):
        try:
            self.connection.execute("DROP TABLE {0}".format(self.tableName))
            self.connection.commit()
            print("Table deleted")
        except Exception as error:
            print("ERROR: {0}".format(error))


    ############################################################################
    # Function 
    ############################################################################
    def CreateTable(self):
        try:
            self.connection.execute('''CREATE TABLE {0} (
                ID INT PRIMARY KEY NOT NULL,
                NAME CHAR(10) NOT NULL,
                SALT CHAR(100) NOT NULL,
                HASH CHAR(100) NOT NULL);
                '''.format(self.tableName))
            self.connection.commit()
            print("table created")
        except Exception as error:
            print("ERROR: {0}".format(error))


    ############################################################################
    # Function 
    ############################################################################
    def CreateUser(self, id, name, salt, hash):
        sqlQuery = "INSERT INTO {0} (ID,NAME,SALT,HASH) VALUES ({1},'{2}','{3}','{4}');".format(self.tableName,id,name,salt,hash)
        self.connection.execute(sqlQuery)
        self.connection.commit()
        print("User created.")


    ############################################################################
    # Function 
    ############################################################################
    def RetreiveAllRecords(self):
        records = []
        cursor = self.connection.execute("SELECT * FROM USERS")

        for row in cursor:
            records.append(row)

        return records


    ############################################################################
    # Function 
    ############################################################################
    def RetreiveUserDetails(self, name):
        sqlQuery = "SELECT * FROM {0} WHERE NAME = '{1}'".format(self.tableName, name)
        cursor = self.connection.execute(sqlQuery)
        for row in cursor:
            saltValue = row[2]
            hashValue = row[3]
            break
        return (saltValue, hashValue)


    ############################################################################
    # Function 
    ############################################################################
    def CloseConnection(self):
        self.connection.close()
