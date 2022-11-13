import sqlite3

try:
    sqliteConnection = sqlite3.connect('TEMOA_Italy.sqlite')
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)