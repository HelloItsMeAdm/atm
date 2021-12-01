import sqlite3 as sq
from tabulate import tabulate

class database():
    def printCurrentClients():
        connection = sq.connect("main.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT, card_id TEXT, card_pin TEXT, balance INTEGER)")
        currentClientsArray = cursor.execute("SELECT name, card_id, card_pin, balance FROM clients").fetchall()
        print("Fetching all clients from database...")
        print("Fetching complete!")
        print("")
        if not currentClientsArray:
            print("Current client list is EMPTY!")
            print("")
        else:
            print("Current client list:")
            print(tabulate(currentClientsArray, headers=["Name", "ID", "PIN", "Balance"]))
            print("")