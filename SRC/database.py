"""
This file contains functions pertaining to the creation of the database
"""
import sqlite3 as sq3

class database:
    
    @staticmethod
    def innitDB():
        """
        Creates empty database for (ID_token, pattern) storage
        """
        con = sq3.connect("database.db")
        cur = con.cursor()
        
        cur.execute("CREATE TABLE user_info(user_ID, pattern)")
        
        # res = cur.execute("SELECT name FROM sqlite_master")
        # print(res.fetchone())
        
        con.close()
        
    @staticmethod
    def clearDB():
        """
        Clears database for testing and pre-submission resetting
        """
        con = sq3.connect("database.db")
        cur = con.cursor()
        
        cur.execute("DROP TABLE IF EXISTS user_info")
        
        # res = cur.execute("SELECT name FROM sqlite_master")
        # print(res.fetchone())
        
        
# if __name__ == "__main__":
#     db = database()
#     db.innitDB()
#     db.clearDB()
    