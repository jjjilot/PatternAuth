"""
This file contains functions pertaining to the creation of the database
"""
import sqlite3 as sq3
import json

class Database:
    
    @staticmethod
    def initDB():
        """
        Creates an empty database for (ID_token, pattern) storage.
        """
        con = None
        try:
            con = sq3.connect("database.db")
            cur = con.cursor()
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_info(
                user_ID TEXT PRIMARY KEY, 
                pattern TEXT
            )""")
            
            con.commit()
        finally:
            if con:
                con.close()
    
    @staticmethod
    def add_user(user_ID, pattern_list):
        """
        Adds a user ID paired with a list that stores a passcode.
        """
        con = None
        try:
            con = sq3.connect("database.db")
            cur = con.cursor()
            
            pattern_str = json.dumps(pattern_list)  # Convert list to JSON string
            
            # Check if user already exists
            cur.execute("SELECT user_ID FROM user_info WHERE user_ID = ?", (user_ID,))
            if cur.fetchone():
                print(f"User {user_ID} already exists.")
                return
            
            cur.execute("INSERT INTO user_info (user_ID, pattern) VALUES (?, ?)", 
                        (user_ID, pattern_str))
            
            con.commit()
        finally:
            if con:
                con.close()
    
    @staticmethod
    def clearDB():
        """
        Clears database for testing and pre-submission resetting.
        """
        con = None
        try:
            con = sq3.connect("database.db")
            cur = con.cursor()
            
            cur.execute("DROP TABLE IF EXISTS user_info")
            
            con.commit()
        finally:
            if con:
                con.close()

if __name__ == "__main__":
    Database.initDB()
    Database.add_user("test", [1, 2, 3, 4, 5, 6, 7, 8, 9])