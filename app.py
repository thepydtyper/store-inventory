import datetime
import os
import sys
import csv
from collections import OrderedDict

from peewee import *


db = SqliteDatabase("inventory.db")

class Product(Model):

    product_id = AutoField(primary_key=True)
    product_name = TextField(unique=True)
    product_price = IntegerField()
    product_quantity = IntegerField(default=0)    
    date_updated = DateTimeField()

    class Meta:
        database = db


def initialize():
    """database connection and add items from the provided-CSV into the table"""
    db.connect()
    db.create_tables([Product], safe=True)

    with open("inventory.csv", newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",")
        prod_dicts = list(reader)

        for prod in prod_dicts:
            try:
                Product.insert(
                    product_name = prod["product_name"],                    
                    product_price = fix_price(prod["product_price"]),
                    product_quantity = fix_quantity(prod["product_quantity"]),
                    date_updated = fix_date(prod["date_updated"])
                ).execute()
            except IntegrityError:
                duplicate = Product.get(product_name = prod["product_name"])
                if duplicate.date_updated <= fix_date(prod["date_updated"]):
                    duplicate.product_price = fix_price(prod["product_price"])
                    duplicate.product_quantity = fix_quantity(prod["product_quantity"])                    
                    duplicate.date_updated = fix_date(prod["date_updated"])
                    duplicate.save()


def menu_loop():
    """show the menu"""

    # print if user doesn't type v, a, or b, then reloop
    choice = None
    while choice != 'q':
        print("\n--Inventory System--\n")
        for key, value in menu.items():
            print(f"{key}) {value.__doc__}")

        choice = input("\nAction: >> ").lower().strip()
        
        if choice in menu:
            clear()
            menu[choice]()
        else:
            print("ERROR: Please enter either: 'a', 'v', 'b', or 'q'\n")


def fix_price(price):
    """given a price value, removes the $ sign and converts to an int"""

    fixed = price.replace("$", "")
    fixed = int(float(fixed) * 100)

    return fixed


def fix_date(date):
    """returns a datetime-formatted object"""

    return datetime.datetime.strptime(date, "%m/%d/%Y")


def fix_quantity(quantity):
    """converts the given quantity to an int"""

    return int(quantity)


def show_by_id(id=None):
    """show item by id"""

    #print error if ID doesn't exist
    while True:
        try:
            prod_id = input("Find product by ID: >> ")
            prod_id = int(prod_id)
            break
        except ValueError:
            print("ERROR: a NUMBER not entered!")

    items = Product.select().where(Product.product_id == prod_id)
    if items:
        print("Products found: ")
        for item in items:
            print(f"\tProduct name: {item.product_name}")
            print(f"\tProduct price (in cents): {item.product_price}")
            print(f"\tProduct quantity: {item.product_quantity}")
            print(f"\tDate updated: {item.date_updated}")
    else:
        print(f"ID {prod_id} not found!")


def add_item():
    """add item to inventory"""

    prod_name = input("Enter product name: >> ")

    while True:
        try:
            prod_amount = input("Enter quantity: >> ")
            prod_amount = int(prod_amount)
            break
        except ValueError:
            print("ERROR: a NUMBER not entered!")
            continue

    while True:
        try:
            prod_price = input("Enter price: >> ")
            prod_price = fix_price(prod_price)
            break
        except ValueError:
            print("ERROR: a NUMBER must be entered!")
            continue

    try:
        Product.create(
            product_name = prod_name,
            product_quantity = prod_amount,
            product_price = prod_price,
            date_updated = datetime.datetime.now()
        ).save()
    except IntegrityError:
        product = Product.get(product_name = prod_name)
        product.product_quantity = prod_amount
        product.product_price = prod_price
        product.date_updated = datetime.datetime.now()
        product.save()


def backup_database():
    """backup the database"""

    headers = ["product_id", "product_name", "product_price", "product_quantity", "date_updated"]

    with open("db_backup.csv", 'w', newline="") as backup:
        dbwriter = csv.DictWriter(backup, fieldnames=headers)
        dbwriter.writeheader()
        
        inventory = Product.select()
        for item in inventory:
            dbwriter.writerow({
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_price": item.product_price,
                "product_quantity": item.product_quantity,
                "date_updated": item.date_updated
            })

    if not os.path.isfile("db_backup.csv"):
        print("Error during backup..")
    else:
        print("Database backed up to 'db_backup.csv'")



def escape():
    """exit the program"""

    sys.exit()


def clear():
    """clears the console window"""
    os.system("cls" if os.name == "nt" else "clear")


menu = OrderedDict([
    ('a', add_item),
    ('v', show_by_id),
    ('b', backup_database),
    ('q', escape)
])


if __name__ == "__main__":
    initialize()    
    menu_loop()
