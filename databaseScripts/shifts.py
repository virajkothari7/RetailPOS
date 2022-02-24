import sqlite3
from datetime import datetime

conn = sqlite3.connect('./data/shifts.db')

c = conn.cursor()

# creating a database table (at first run of program since there will be no table yet)
c.execute("""CREATE TABLE IF NOT EXISTS shifts (
                start_date_time datetime, 
                end_date_time datetime,
                shift_id INTEGER NOT NULL,
                shift_Names VARCHAR(256),
                endShift_reports LONGTEXT,
                UNIQUE (shift_id)
            )"""
        )

# adding data function which will be called from main to add transactions into the database
def addData(start_date_time,end_date_time,shift_id,shift_Names,endShift_reports):
    params = (start_date_time,end_date_time,shift_id,shift_Names,endShift_reports, )
    try:
        c.execute("INSERT INTO shifts VALUES (?, ?, ?, ?, ?)", params)
        conn.commit()
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nShift Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")

# obtaining a list of transactions present in the database
def getData():
    c.execute("SELECT * FROM shifts")
    rows = c.fetchall()
    return list(rows)

def getDataFromShiftID(id):
    c.execute("SELECT start_date_time, end_date_time, shift_Names FROM shifts WHERE shift_id = ?",(id,))
    rows = c.fetchone()
    return list(rows)

def nextShiftId():
    c.execute("SELECT shift_id FROM shifts")
    rows = c.fetchall()
    try: mx = max(rows)[0] + 1
    except: mx = 1
    return mx 

def endShift(time, endReport, id):
    c.execute("UPDATE shifts SET end_date_time = (?), endShift_reports = ? WHERE shift_id = ?",(time,endReport, id,))
    conn.commit()

# deleting the whole database (just in case function)
def deleteData():
    c.execute("DELETE FROM shifts")
    conn.commit()



c.execute( """CREATE TABLE IF NOT EXISTS CashOut_NoSale (
                date_time datetime,
                shift_id INTEGER NOT NULL,
                name VARCHAR(256),
                invoice_no INTEGER,
                amount real 
            )""" )

def add_data_C(date_time, shift_id, name, invoice_no, amount):
    params = (date_time, shift_id, name, invoice_no, amount)
    try:
        c.execute("INSERT INTO CashOut_NoSale VALUES (?, ?, ?, ?, ?)", params)
        conn.commit()
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nCashOut_NoSale Error : {datetime.now()}\naddData Params : {params}\n{e}\n\n")

def get_data_C():
    c.execute("SELECT * FROM CashOut_NoSale")
    rows = c.fetchall()
    return list(rows)


conn.commit()
