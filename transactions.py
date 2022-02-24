import sqlite3
from datetime import datetime, timedelta
import databaseScripts.allTransactions as AT

conn = sqlite3.connect('./data/transactions.db')

c = conn.cursor()

# creating a database table (at first run of program since there will be no table yet)
c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                date_time datetime, 
                shift_id INTEGER NOT NULL,
                transaction_id INTEGER NOT NULL,
                total_sale REAL NOT NULL,
                total_amount REAL NOT NULL,
                tax_amount REAL,
                payment_type TEXT DEFAULT 'CASH',
                receipt LONGTEXT,
                products LONGTEXT,
                UNIQUE (transaction_id)
            )"""
        )


# adding data function which will be called from main to add transactions into the database
def addData(detailDict):
    params = (
        detailDict['date_time'], detailDict['shift_id'], detailDict['transaction_id'], detailDict['total_sale'], detailDict['total_amount'],
            detailDict['tax_amount'], detailDict['payment_type'], detailDict['receipt'], str(detailDict['products'])
        )
    try:
        c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
        conn.commit()
        #Adding Individual entries
        for i in detailDict['products']:
            AT.addData(
                date_time = detailDict['date_time'],
                date = detailDict['date_time'].date(),
                transaction_id = detailDict['transaction_id'],
                shift_id = detailDict['shift_id'],
                barcode = i['barcode'],
                name = i['name'], 
                department = i["department"],
                purchase_price = i["purchase_price"],
                sales_price = i['sell_price'], 
                qty = i['qty'], 
                deposit = i['deposit'],
                deposit_value = i['deposit_value'],
                tax = i['tax'],
                tax_value = i['tax_value'],
                discount = i['discount'] if i['discount'] else 0,
                payment_type = detailDict['payment_type'], 
            )
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nTransactions Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")



# obtaining a list of transactions present in the database
def getData():
    c.execute("SELECT * FROM transactions ORDER BY date_time DESC")
    rows = c.fetchall()
    return list(rows)


# fetching only names from database
def getTransactionView():
    c.execute("SELECT date_time, transaction_id, total_sale, receipt FROM transactions ORDER BY date_time DESC LIMIT 1000")
    rows = c.fetchall()
    return list(rows)

def getLastRecipt():
    c.execute("SELECT receipt FROM transactions ORDER BY date_time DESC LIMIT 1")
    rows = c.fetchone()
    return rows

# fetching only sale prices from database
def getReceiptFromTransaction(transaction_id):
    c.execute("SELECT transaction_id, receipt FROM transactions WHERE transaction_id = (?) ",(transaction_id,))
    rows = c.fetchall()
    return list(rows)


# fetching only dates from database
def getTransactionsFromShift(shift_id):
    c.execute("SELECT * FROM transactions WHERE shift_id = (?) ",(shift_id,))
    rows = c.fetchall()
    return list(rows)


def getYearTransactions():
    c.execute("SELECT * FROM transactions WHERE date_time > (?) ",
                (datetime.now().replace(month=1,day=1, hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getMonthTransactions():
    c.execute("SELECT * FROM transactions WHERE date_time > (?) ",
                (datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)


def getWeekTransactions():
    startWeek = datetime.now() - timedelta(datetime.now().weekday())
    c.execute("SELECT * FROM transactions WHERE date_time > (?) ",
                (startWeek.replace(hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)


# fetching only payment types from database
def getDayTransactions():
    c.execute("SELECT * FROM transactions WHERE date_time > (?) ",
                (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),))
    rows = c.fetchall()
    return list(rows)


def getTransactionsByDate(date):
    c.execute("SELECT * FROM transactions WHERE date = (?) ",(date,))
    rows = c.fetchall()
    return list(rows)


# deleting the whole database (just in case function)
def deleteData():
    c.execute("DELETE FROM transactions")
    conn.commit()



conn.commit()
