import datetime
import os
import sys
import csv
from collections import OrderedDict

from peewee import *


db = SqliteDatabase("inventory.db")

class Product(Model):

    product_id = AutoField(primary_key=True)
    product_name = CharField(unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField()
    date_updated = DateTimeField()

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([Product], safe=True)

    with open("inventory.csv", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",")
        prod_dicts = list(reader)

        for prod in prod_dicts:
            try:
                Product.insert(
                    product_name = prod["product_name"],
                    product_quantity = prod["product_quantity"],
                    product_price = prod["product_price"],
                    date_updated = prod["dated_updated"]
                ).execute()
            except IntegrityError:
                duplicate = Product.get(product_name = prod["product_name"])
                if duplicate.date_updated <= prod["date_updated"]:
                    duplicate.product_quantity = prod["product_quantity"]
                    duplicate.product_price = prod["product_price"]
                    duplicate.date_updated = prod["date_updated"]
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
            print(f"calling up {menu[choice]()}")
            menu[choice]()
        else:
            print("ERROR: Please enter either: 'a', 'v', 'b', or 'q'\n")


def clean_csv_data():
    """cleans fields from inventory.csv"""

    with open("inventory.csv", newline="") as file:
        data = csv.DictReader(file, delimiter=",")
        rows = list(data)

        for row in rows:
            row["product_quantity"] = int(row["product_quantity"])
            row["product_price"] = int(row["product_price"].replace("$", "").replace(".", ""))
            row["date_updated"] = datetime.datetime.strptime(row["date_updated"], "%m/%d/%Y")
    
    return rows


def build_database(data):
    """adds cleaned data into the inventory.db file"""

    for row in data:
        try:
            Product.insert(
                product_name = row["product_name"],
                product_price = row["product_price"],
                product_quantity = row["product_quantity"],
                date_updated = row["date_updated"]
            ).execute()
            print(f"created {row}")
        except IntegrityError:
            print(f"error so adding {row}")
            product = Product.get(product_name=row["product_name"])
            product.product_name = row["product_name"]
            product.product_quantity = row["product_quantity"]
            product.product_price = row["product_price"]
            product.date_updated = row["date_updated"]
            product.save()


def show_by_id(id=None):
    """show item by id"""

    #print error if ID doesn't exist
    while True:
        try:
            prod_id = input("Enter product's ID: >> ")
            prod_id = int(prod_id)
            break
        except ValueError:
            print("ERROR: a NUMBER not entered!")

    items = Product.select().where(Product.product_id == prod_id)
    if items:
        print("Products found: ")
        for item in items:
            print(f"    Product name: {item.product_name}")
            print(f"\tProduct price: {item.product_price}")
            print(f"\tProduct quantity: {item.product_quantity}")
            print(f"\tDate updated: {item.date_updated}")
    else:
        print(f"ID {prod_id} not found!")


def add_item():
    """add item to inventory"""

    #if dup found while trying to add, check which entry most recent and only save that data
    prod_name = input("Enter product name: >> ")

    while True:
        try:
            prod_amount = input("Enter amount: >> ")
            prod_amount = int(prod_amount)
            break
        except ValueError:
            print("ERROR: a NUMBER not entered!")
            continue

    while True:
        try:
            prod_price = input("Enter product price: >> ")
            prod_price = float(prod_price)
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
    print("backinig up db..")
    with open("db_backup.csv", 'w', newline="") as backup:
        dbwriter = csv.DictWriter(backup, fieldnames=headers, delimiter=",")
        dbwriter.writeheader()
        
        inventory = Product.select()
        for item in inventory:
            dbwriter.writerow({
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_price": item.product_price,
                "date_updated": item.date_updated
            })

    if not os.path.isfile("db_backup.csv"):
        print("Error during backup..")



def escape():
    """exit the program"""

    sys.exit()


def clear():
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
