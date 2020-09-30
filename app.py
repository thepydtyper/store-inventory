import datetime
import os
import sys
import csv
from collections import OrderedDict

from peewee import *

db = SqliteDatabase("inventory.db")

class Product(Model):

    product_id = IntegerField(primary_key=True)
    product_name = CharField(max_length=255)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0.0)
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([Product], safe=True)

    with open("inventory.csv", "a") as file:
        data = csv.reader(file, delimiter=",")
    print(data)


def menu_loop():
    """show the menu"""
    # print if user doesn't type v, a, or b, then reloop
    choice = None
    while choice != "q":
        #clear()
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print(f"{key}) {value.__doc__}")

        choice = input("\nAction: ").lower().strip()
        
        if choice in menu:
            #clear()
            menu[choice]()


def view_inventory():
    """view the inventory"""
    pass


def add_from_csv():
    """add items from inventory.csv"""
    pass


def show_by_id():
    """show item by id"""
    #print error if ID doesn't exist
    print("showing id..")

def add_item():
    """add item to inventory"""
    #if dup found while trying to add, check which entry most recent and only save that data
    print("adding item..")

def backup_database():
    """backup the database"""
    # the backup CSV file should only contain a single header row with all field titles
    print("backinig up db..")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


menu = OrderedDict([
    ('a', add_item),
    ('v', show_by_id),
    ('b', backup_database)
])


if __name__ == "__main__":
    initialize()    
    menu_loop()
