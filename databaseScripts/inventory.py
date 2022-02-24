import sqlite3
from datetime import datetime

conn = sqlite3.connect('./data/inventory.db')

c = conn.cursor()

# creating a database at the first run
c.execute("""CREATE TABLE IF NOT EXISTS items (
                name varchar(128) NOT NULL, 
                barcode varchar(32) NOT NULL,
                department varchar(32) DEFAULT 'Misc',
                purchase_price real,
                sales_price real NOT NULL,
                qty integer,
                tax varchar(32) DEFAULT 'No-Tax',
                deposit varchar(32) DEFAULT 'No-Deposit',
                UNIQUE (barcode),
                CHECK (sales_price> 0.0)
            )"""
        )



# adding items into the database
def addData(item_name, barcode_number, department, purchase_price, sales_price, quantity,  tax,deposit):
    params = (item_name, barcode_number, department, purchase_price, sales_price, quantity, tax,deposit)
    try:
        c.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)", params)
        conn.commit()
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nInventory Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")
    


def isBarcode(barcode_number):
    c.execute("SELECT count(*) FROM items WHERE barcode = (?) ",(barcode_number,))
    count = c.fetchone()[0]
    if count == 1:
        return True
    return False



# fetching the items in the database
def getInventoryData():
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    return list(rows)

# fetching only names from database
def getNames():
    c.execute("SELECT name FROM items")
    rows = c.fetchall()
    return list(rows)

# fetching only Departments from database
def getDepartments():
    c.execute("SELECT UNIQUE department FROM items")
    rows = c.fetchall()
    return list(rows)

# fetching only barcodes from database
def getBarcodes():
    c.execute("SELECT barcode FROM items")
    rows = c.fetchall()
    return list(rows)

# fetching only purchase prices from database
def getPurchasePrices():
    c.execute("SELECT purchase_price FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only sale prices from database
def getSalesPrices():
    c.execute("SELECT sales_price FROM items")
    rows = c.fetchall()
    return list(rows)


# fetching only tax prices from database
def getTaxableItems():
    c.execute("SELECT * FROM items WHERE tax != 'No-Tax' ")
    rows = c.fetchall()
    return list(rows)

def getDepositItems():
    c.execute("SELECT * FROM items WHERE deposit != 'No-Deposit' ")
    rows = c.fetchall()
    return list(rows)

# adding a functions which will allow the name, p.price, s.price, and quantity to be changed
def updateName(barcode_number, new_name):
    params = (new_name, barcode_number)
    try:
        c.execute("UPDATE items SET name = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updatePurchasePrice(barcode_number,new_pp):
    params = (new_pp, barcode_number)
    try:
        c.execute("UPDATE items SET purchase_price = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updateSellPrice(barcode_number,new_sp ):
    params = (new_sp, barcode_number)
    try:
        c.execute("UPDATE items SET sales_price = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updateQuantity(barcode_number, new_qtn):
    params = (new_qtn, barcode_number)
    try:
        c.execute("UPDATE items SET qty = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updateDepartment(barcode_number, new_value):
    params = (new_value, barcode_number)
    try:
        c.execute("UPDATE items SET department = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updateTax(barcode_number, new_value):
    params = (new_value, barcode_number)
    try:
        c.execute("UPDATE items SET tax = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

def updateDeposit(barcode_number, new_value):
    params = (new_value, barcode_number)
    try:
        c.execute("UPDATE items SET deposit = (?) WHERE barcode = (?)", params)
        conn.commit()
    except Exception:
        pass

# adding functions that will allow name, s.price, p.price, and quantity to be returned given barcode
def getItemFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT * FROM items WHERE barcode = (?)", param)
        final_pp = pp.fetchone()
        return list(final_pp)
    except Exception:
        pass

def getSellPriceFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        sale_price = c.execute("SELECT sales_price FROM items WHERE  barcode = (?)", param)
        final_sale_price = sale_price.fetchone()
        return final_sale_price[0]
    except Exception:
        pass

def getNameFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        name = c.execute("SELECT name FROM items WHERE barcode = (?)", param)
        final_name = name.fetchone()
        return str(final_name[0])
    except Exception:
        pass

def getDepartmentFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        name = c.execute("SELECT department FROM items WHERE barcode = (?)", param)
        final_name = name.fetchone()
        return str(final_name[0])
    except Exception:
        pass

def getPPFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT purchase_price FROM items WHERE barcode = (?)", param)
        final_pp = pp.fetchone()
        return str(final_pp[0])
    except Exception:
        pass

def getQtyFromBarcode(barcode_number):
    param = (barcode_number,)
    try:
        pp = c.execute("SELECT qty FROM items WHERE barcode = (?)", param)
        final_qtn = pp.fetchone()
        return str(final_qtn[0])
    except Exception:
        pass




# Fetching barcodes from Name alike
def getItemsFromName(name):
    param = (f"%{name}%",)
    try:
        b = c.execute("SELECT * FROM items WHERE name Like (?)", param)
        final_b = b.fetchall()
        return list(final_b)
    except Exception:
        print("Error")
        pass



# adding a function that will decrement quantity of an item as it is transacted
def increaseQuantity(barcode_number, addQty ):
    try:
        originalQtn = getQtyFromBarcode(barcode_number)
        newQtn = int(originalQtn) + int(addQty)
        params = (newQtn, barcode_number)
        try:
            c.execute("UPDATE items SET qty = (?) WHERE barcode = (?)", params)
            conn.commit()
        except Exception:
            pass
    except TypeError:
        pass


# adding a function that will decrement quantity of an item as it is transacted
def decreaseQuantity(barcode_number, delQty = 1):
    try:
        originalQtn = getQtyFromBarcode(barcode_number)
        newQtn = int(originalQtn) - int(delQty)
        params = (newQtn, barcode_number)
        try:
            c.execute("UPDATE items SET qty = (?) WHERE barcode = (?)", params)
            conn.commit()
        except Exception:
            pass
    except TypeError:
        pass



def deleteItemFromBarcode(barcode_number):
    c.execute(f"DELETE FROM items WHERE barcode = {barcode_number}")
    conn.commit()
    return True

def deleteData():
    c.execute("DELETE FROM items")
    conn.commit()



#Creating Department and Tax and Deposit category
c.execute("""CREATE TABLE IF NOT EXISTS category (
                datetime datetime,
                category varchar(32) DEFAULT 'Misc',
                category_id varchar(32) NOT NULL,
                category_name varchar(64) NOT NULL,
                value varchar(16) DEFAULT None,
                UNIQUE (category_id)
            )"""
        )

def addCategoryData(datetime, category, category_id,category_name,value):
    params = (datetime, category, category_id,category_name,value)
    try:
        c.execute("INSERT INTO category VALUES (?, ?, ?, ?, ?)", params)
        conn.commit()
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nInventory Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")

def getAllCategoryValue():
    c.execute("SELECT * FROM category")
    rows = c.fetchall()
    return list(rows)

def getCategory(x):
    c.execute("SELECT * FROM category Where category = (?)",(x,))
    rows = c.fetchall()
    return list(rows)

def getNameFromId(x):
    c.execute("SELECT category_name FROM category Where category_id = (?)",(x,))
    rows = c.fetchone()
    return rows[0]

def getValueFromId(x):
    c.execute("SELECT value FROM category Where category_id = (?)",(x,))
    rows = c.fetchone()
    return rows[0]


def getCategoryFromId(x):
    c.execute("SELECT category FROM category Where category_id = (?)",(x,))
    rows = c.fetchone()
    return rows[0]

def updateNameFromId(y,x):
    c.execute("UPDATE category SET category_name = (?) Where category_id = (?)",(y,x,))
    conn.commit()

def updateValueFromId(y,x):
    c.execute("UPDATE category SET value = (?) Where category_id = (?)",(y,x,))
    conn.commit()


def deleteCategoryData():
    c.execute("DELETE FROM category")
    conn.commit()

def nextCategoryId(x):
    c.execute("SELECT category_id FROM category Where category = (?)",(x,))
    rows = c.fetchall()
    try: mx = max([(lambda x: int(x[0].split('_')[-1]))(i) for i in list(rows)]) + 1
    except:  mx = 1
    if x=="Department_Category" and mx<3: mx=4
    elif mx==1 : mx=2
    return mx 

conn.commit()
