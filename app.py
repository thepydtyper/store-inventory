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
    cleaned_data = clean_csv_data()
    build_database(cleaned_data)


def menu_loop():
    """show the menu"""

    # print if user doesn't type v, a, or b, then reloop
    choice = None
    while choice not in ['q', 'a', 'v', 'b']:
        print("\n--Inventory System--\n")
        for key, value in menu.items():
            print(f"{key}) {value.__doc__}")

        choice = input("\nAction: >> ").lower().strip()
        
        if choice in menu:
            clear()
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
            Product.create(
                product_name = row["product_name"],
                product_price = row["product_price"],
                product_quantity = row["product_quantity"],
                date_updated = row["date_updated"]
            ).save()
        except IntegrityError:
            product = Product.get(product_name=row["product_name"])
            product.product_name = row["product_name"]
            product.product_quantity = row["product_quantity"]
            product.product_price = row["product_price"]
            product.date_updated = row["date_updated"]
            product.save()


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

    print("backinig up db..")
    with open("db_backup.csv", 'w') as backup:
        headers = ["product_id", "product_name", "product_price", "product_quantity", "date_updated"]
        dbwriter = csv.DictWriter(backup, fieldnames=headers)

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
