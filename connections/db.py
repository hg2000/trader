from settings import Settings
import mysql.connector

class Db():

    def __init__(self):
        
        self.connection = mysql.connector.connect(user=Settings.db_user,
                                                  host=Settings.db_host,
                                                  password=Settings.db_password,
                                                  database=Settings.db_database)


