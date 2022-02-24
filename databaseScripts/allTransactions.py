import sqlite3
import databaseScripts.inventory as inventory
from datetime import datetime, timedelta

conn = sqlite3.connect('./data/allTransactions.db')
c = conn.cursor()           

# creating a database table (at first run of program since there will be no table yet)
c.execute("""CREATE TABLE IF NOT EXISTS all_transactions( 
                date_time datetime,
                date Date,
                transaction_id INTEGER NOT NULL,
                shift_id INTEGER NOT NULL,
                barcode varchar(32) NOT NULL,
                name varchar(128) NOT NULL,
                department varchar(32) DEFAULT 'Misc',
                purchase_price real,
                sales_price real NOT NULL,
                qty INTEGER NOT NULL,
                deposit varchar(64) DEFAULT 'No-Deposit',
                deposit_value REAL DEFAULT 0,
                tax varchar(64) DEFAULT 'No-Tax',
                tax_value REAL DEFAULT 0,
                discount_value REAL DEFAULT 0,
                payment_type varchar(32) DEFAULT 'CASH',
                UNIQUE (transaction_id, barcode)
            )""")

#Col_Names = ['date_time','date','transaction_id','shift_id','barcode','name','department','purchase_price', 'sales_price','qty','deposit','deposit_value','tax','tax_value','discount_value','payment_type']

# adding data function which will be called from main to add transactions into the database
#Need to add try catch and all other values also I think we should cosider subtracting from inventory here
def addData(date_time,date,transaction_id,shift_id,barcode,name, department,purchase_price,sales_price, qty,deposit,deposit_value, tax,tax_value,discount, payment_type):
    try:
        params = (date_time, date, transaction_id, shift_id, barcode, name, department,purchase_price, sales_price, qty, deposit,deposit_value, tax,tax_value,discount,payment_type)
        c.execute("INSERT INTO all_transactions VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
        conn.commit()
        try:
            inventory.decreaseQuantity(barcode,qty)
        except Exception as b :
            with open('errorLog',"a") as file:
                file.write(f"\Error Deleting Qty : {datetime.now()}\n Parameters : {params}\n{b}\n\n")
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\All Transactions Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")


# obtaining a list of transactions present in the database
def getData():
    c.execute("SELECT * FROM all_transactions")
    rows = c.fetchall()
    return list(rows)

def isBarcode(barcode_number):
    c.execute("SELECT count(*) FROM all_transactions WHERE barcode = (?) ",(barcode_number,))
    count = c.fetchone()[0]
    if count > 0:
        return True
    return False


# fetching only names from database
def getNames():
    c.execute("SELECT name FROM all_transactions")
    rows = c.fetchall()
    return list(rows)

# fetching only names from database
def getBarcodes():
    c.execute("SELECT barcode FROM all_transactions")
    rows = c.fetchall()
    return list(rows)

def getDataFromBarcode(barcode_num):
    params = (barcode_num,)
    c.execute("SELECT * FROM all_transactions WHERE barcode = ?",params)
    rows = c.fetchall()
    return list(rows)

def getNameFromBarcode(barcode_num):
    params = (barcode_num,)
    c.execute("SELECT name FROM all_transactions WHERE barcode = ? ORDER BY date_time DESC LIMIT 1",params)
    rows = c.fetchone()[0]
    return rows

def getTransactionData(trans_id):
    params = (trans_id,)
    c.execute("SELECT * FROM all_transactions WHERE transaction_id = ?",params)
    rows = c.fetchall()
    return list(rows)

def getItemTransaction(trans_id,barcode_num):
    params = (trans_id,barcode_num)
    c.execute("SELECT * FROM all_transactions WHERE transaction_id = ? AND barcode_num = ?",params)
    rows = c.fetchone()
    return list(rows)

# fetching only dates from database
def getDates():
    c.execute("SELECT date FROM all_transactions")
    rows = c.fetchall()
    return list(rows)



# fetching only dates from database
def getTransactionsFromShift(shift_id):
    c.execute("SELECT * FROM all_transactions WHERE shift_id = (?) ",(shift_id,))
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getYearTransactions():
    c.execute("SELECT * FROM all_transactions WHERE date_time > (?) ",
                (datetime.now().replace(month=1,day=1, hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)

# fetching only payment types from database
def getMonthTransactions():
    c.execute("SELECT * FROM all_transactions WHERE date_time > (?) ",
                (datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)

def getWeekTransactions():
    startWeek = datetime.now() - timedelta(datetime.now().weekday())
    c.execute("SELECT * FROM all_transactions WHERE date_time > (?) ",
                (startWeek.replace(hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)

# fetching only payment types from database
def getDayTransactions():
    c.execute("SELECT * FROM all_transactions WHERE date = (?) ",(datetime.now().date(),))
    rows = c.fetchall()
    return list(rows)

def getTransactionsByDate(date):
    c.execute("SELECT * FROM all_transactions WHERE date = (?) ",(date,))
    rows = c.fetchall()
    return list(rows)


# deleting the whole database (just in case function)
def deleteData():
    c.execute("DELETE FROM all_transactions")


c.execute("""CREATE TABLE IF NOT EXISTS registerTabs( 
                button_id INT NOT NULL,
                tab_name varchar(32) NOT NULL, 
                display_name varchar(32), 
                barcode varchar(32),
                Primary Key (button_id)
            )""")

def isTabs():
    c.execute("SELECT COUNT(DISTINCT tab_name) FROM registerTabs")
    count = c.fetchone()[0]
    if count == 4:
        return False
    return True

def addTab(num,tab_name):
    for i in range(1,16):
        try:
            c.execute("INSERT INTO registerTabs VALUES (?, ?, ?, ?)", (num+i,tab_name,"Add Item",""))
            conn.commit()
        except Exception as b :
            with open('errorLog',"a") as file:
                file.write(f"\Error Inserting Tabs : {datetime.now()}\n Parameters : {tab_name}\n{b}\n\n")
    
if isTabs():
    for j,i in enumerate(["Tab1","Tab2","Tab3","Tab4"]):
        addTab(j*15,i)
    

def getTab(tab_name):
    c.execute("SELECT * FROM registerTabs WHERE tab_name = (?) ",(tab_name,))
    rows = c.fetchall()
    return list(rows)

def getButtonBarcode(tab_id):
    c.execute("SELECT barcode FROM registerTabs WHERE button_id = (?) ",(tab_id,))
    rows = c.fetchone()
    return list(rows)[0]

def updateTabId(tabId,dName,brcd):
    c.execute("UPDATE registerTabs SET display_name = (?),barcode = (?) WHERE button_id = (?)", (dName,brcd,tabId,))
    conn.commit()


conn.commit()

