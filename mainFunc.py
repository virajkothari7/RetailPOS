import databaseScripts.inventory as inv
import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.shifts as sf
import sqlite3, os, shutil
import pandas as pd
from datetime import datetime
from escpos.printer import Usb
from kivyScripts.screenManager import sm

global data, tabs, shift,variableButtons, printerSettings


from escpos.printer import Usb
class printer:
    printer = None

    def printReciept(printText,*args,**kwargs):
        try:
            if printer.printer:
                printer.printer.text(printText)
                printer.printer.print_and_feed(n=3)
                # printer.printer.cut()
        except: 
            printer.connectPrinter()
            printer.printReciept(printText)

    def connectPrinter():
        try : printer.printer = Usb(int(printerSettings['Printer_VendorID']),int(printerSettings['Printer_ProductID']))
        except Exception as e:
            printer.printer = None


def deleteFilePath(fileNameOrDir,dir=False):
    if dir:
        try:
            shutil.rmtree(fileNameOrDir)
        except Exception as e:
            with open('errorLog',"a") as file:
                file.write(f"\nDeleting Directory Error : {datetime.now()}\n Dir. Path : {fileNameOrDir}\n{e}\n\n")
    else:
        try:
            if os.path.exists(fileNameOrDir):
                os.remove(fileNameOrDir) 
        except Exception as e:
            with open('errorLog',"a") as file:
                file.write(f"\nDeleting File  Error : {datetime.now()}\n File Path : {fileNameOrDir}\n{e}\n\n")
 
def reset__():
    try:
        archiveDir = "./archive/"+str(datetime.now()).split('.')[0].replace(" ","_").replace(":","_").replace("-","_")
        shutil.copytree("./data",archiveDir+"/data/")
        shutil.copytree("./logsKivy",archiveDir+"/logsKivy/")
        shutil.copy2("variable.txt",archiveDir)
        shutil.copy2("errorLog",archiveDir)
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\nArchiveing Error : {datetime.now()}\n File Dir. : {archiveDir}\n{e}\n\n")

    try:
        deleteFilePath("./logsKivy",dir=True)
        deleteFilePath("./data/allTransactions.db")
        deleteFilePath("./data/transactions.db")
        deleteFilePath("./data/shifts.db")
        deleteFilePath("variable.txt")
        deleteFilePath("errorLog")
    except Exception as e:
        with open('errorLog',"a") as file:
            file.write(f"\Reset Error : {datetime.now()}\n{e}\n\n")
    quit()
 

def updateStoreInformation():
    with open("variable.txt","w") as file:
        file.write(f"{data}\n{shift}\n{tabs}\n{variableButtons}\n{printerSettings}")
    

def endShift(*args):
    endTime = str(datetime.now())
    Col_Names = ['date_time','date','transaction_id','shift_id','barcode','name','department','purchase_price', 'sales_price','qty','deposit','deposit_value','tax','tax_value','discount_value','payment_type']
    data1 = pd.DataFrame(at.getData(),columns = Col_Names)
    data1['sales_price'] = data1['qty'] * data1['sales_price']
    data1 = data1.rename(columns={"shift_id":"SHIFT ID","department":"DEPARTMENT",'sales_price':'Net_Sales','qty':"Net_QTY",'tax_value':"Net_Tax", 'deposit_value':"Net_Deposit",'discount_value':"Net_Discount"})
    group = data1.groupby("SHIFT ID")
    j = shift["Shift No"]
    shiftDetails = sf.getDataFromShiftID(j)
    shiftReport = "SHIFT Report".center(32)+"\n"+str(datetime.now()).center(32)+"\n"
    shiftReport += f"{'*'*32}\n\nSHIFT ID : {j}\nStart_DT : {shiftDetails[0][:-7]}\nEnd_DT : {endTime[:-7]}\n{shiftDetails[2]}\n"
    
    try:
        backupShift = shiftReport
        shiftReport += "\nDEPARTMENT DETAILS"
        for k in group.get_group(j).groupby("DEPARTMENT").groups.keys():
            shiftReport += "\n    "+k+f" {inv.getNameFromId(k)[:13]}\n"
            shiftReport += "\t"+"\n\t".join(group.get_group(j).groupby("DEPARTMENT").get_group(k)[["Net_QTY","Net_Sales"]].sum().to_string().split("\n")) 
        shiftReport += "\nDEPT. TOTAL\n    "+"\n    ".join(group.get_group(j)[["Net_QTY","Net_Sales"]].sum().to_string().split("\n")) 
        shiftReport += "\n\nTAX and DEPOSIT DETAILS\n"
        shiftReport += "    "+"\n    ".join(group.get_group(j)[["Net_Tax","Net_Deposit",]].sum().to_string().split("\n")) 
        shiftReport += "\n\nDISCOUNT\n    "+group.get_group(j)[["Net_Discount",]].sum().to_string()
        shiftReport += "\n\nPAYMENT TYPE DETAILS\n"
        for k in group.get_group(j).groupby("payment_type").groups.keys():
            amount = group.get_group(j).groupby("payment_type").get_group(k).apply(lambda i: i['Net_Sales'] + i["Net_Tax"] + i["Net_Deposit"] ,axis=1).sum().round(2)
            shiftReport +=  "    {:<12} {:>8}\n".format(k,amount)
    except:
        shiftReport = backupShift
        pass

    noSale = 0 
    cashOut = []
    cashOutTotal = 0
    for a in [[b[2],b[4]] for b in sf.get_data_C() if b[1] == j ]:
        if a[0] == "NO SALE":
            noSale += 1
        else:
            cashOut.append(f"  {a[0][:20]}   {a[1]}")
            cashOutTotal += a[1]
    if cashOutTotal: 
        shiftReport += "\nCASH-OUT DETAILS\n"+ '\n'.join(cashOut) + "\n" + f"TOTAL AMOUNT   {cashOutTotal}".rjust(24) + "\n"
    if noSale : shiftReport += f"\nNO SALE DRAWER OPEN   {noSale}\n"
    shiftReport += "\n"+"#"*32+"\n"+"END OF REPORT".center(32)
    # print(shiftReport)

    sf.endShift(str(endTime),str(shiftReport),shift["Shift No"])
    printer.printReciept(shiftReport)

    shift["Shift StartTime"] = ""
    shift["Shift Names"] = ""
    shift["Shift No"] = sf.nextShiftId()
    updateStoreInformation()

    sm.current = "login_shift"


def generateReceipt(transNo,productList, sub_total ,deposit_total, tax_total, total_amount):
    length = 32
    y = length -1
    productHead = "\nNo:  NAME/BARCODE  QTY   PRICE "
    receipt = []
    receipt.append(data["Store Name"].center(y))
    if len(data["Address Line-1"]) > 1 : receipt.append(data["Address Line-1"].center(y))
    if len(data["Address Line-2"]) > 1 : receipt.append(data["Address Line-2"].center(y))
    if len(data["Store Phone"]) > 1 : receipt.append(data["Store Phone"].center(y))
    if len(data["Additional Heading"]) > 1 : receipt.append(data["Additional Heading"].center(y))
    receipt.append((f"Date: {transNo[:4]}/{transNo[4:6]}/{transNo[6:8]}    Time: {transNo[8:10]}:{transNo[10:12]}").center(y))
    receipt.append("*"*length)
    receipt.append(("TransactionID : "+transNo).center(y))
    receipt.append(productHead)
    receipt.append("-"*length)
    for count, i in enumerate(productList):
        line1 = list(" "*length)  #For No; and Name     
        line2 = list(" "*length)  #For Barcode, Qty, Price, Tax
        line1[:len(str(count))+1] = f"{count+1})"
        line1[5:] = i["name"][:25]
        line2[:len(str(i["barcode"]))+1] = " "+str(i["barcode"])
        line2[19:22] = str(i["qty"]).center(3)
        line2[24:30] = str(i["sell_price"]).center(6)
        if i["tax_value"] : line2[31] = "T"
        receipt.append("".join(line1))
        receipt.append("".join(line2))
        if i["deposit_value"] : receipt.append(" "*7+"BTL/CAN Deposit : "+str(i["deposit_value"]))
    receipt.append(f"\nSub-Total{' '*8} =  {sub_total}")
    # if deposit_total: receipt.append(f"Deposit-Amount{' '*3} =  {deposit_total}")
    if tax_total : receipt.append(f"Tax-Amount{' '*7} =  {tax_total}")
    receipt.append(("-"*27).center(y))
    receipt.append(f"Total Sale Amount =  {total_amount}")
    receipt.append("*"*length)
    if len(data["Footer Line-1"]) > 1 : receipt.append(data["Footer Line-1"].center(y))
    if len(data["Footer Line-2"]) > 1 : receipt.append(data["Footer Line-2"].center(y))
    return "\n".join(receipt)


if os.path.exists("variable.txt"):
    with open("variable.txt","r") as file:
        lines=file.readlines()
        data = eval(lines[0])
        shift = eval(lines[1])
        tabs = eval(lines[2])
        variableButtons = eval(lines[3])
        printerSettings = eval(lines[4])
else :
    with open("variable.txt","w") as file:
        print("!!!!!   Initial Setup Starting   !!!!!")
        data = {"Store Name":"", "Address Line-1":"", "Address Line-2":"", "Store Phone":"","Additional Heading":"","Footer Line-1":"","Footer Line-2":""}
        shift =  {"Shift No": 1,"Shift Names":"","Shift StartTime":"" }
        tabs=[["Tab 1",None],["Tab 2",None],["Tab 3",None],["Tab 4",None]]
        variableButtons = { "MISC_GENERAL" : {'barcode':"MISC_GENERAL",'name':"Miscellaneous/General","department":"Department_2","purchase_price":0,'qty':1,'deposit':"s",'deposit_value':0,'tax':"",'tax_value':0,'discount':"",'discountPromo':"",'line_total':0},
                            "DELI_GENERAL" : {'barcode':"DELI_GENERAL",'name':"DELI/General","department":"Department_3","purchase_price":0,'qty':1,'deposit':"Deposit_1",'deposit_value':0,'tax':"",'tax_value':0,'discount':"",'discountPromo':"",'line_total':0} }
        printerSettings = {"Printer_VendorID": None, "Printer_ProductID":None,"Print_Reciept":False,"Cash_Drawer":False}
        file.write(f"{data}\n{shift}\n{tabs}\n{variableButtons}\n{printerSettings}")
    if not len(inv.getAllCategoryValue()):
        inv.addCategoryData(datetime.now(),'Department_Category',"Department_1","Default",None)
        inv.addCategoryData(datetime.now(),'Department_Category',"Department_2","Miscellaneous/General",None)
        inv.addCategoryData(datetime.now(),'Department_Category',"Department_3","Deli/General",None)
        inv.addCategoryData(datetime.now(),'Tax_Category',"Tax_1","No-Tax","N/A")
        inv.addCategoryData(datetime.now(),'Deposit_Category',"Deposit_1","No-Deposit","N/A")




"""

# Best Used for 80mm printer
def generateReceipt(productList, sub_total ,deposit_total, tax_total, total_amount):
    length = 40
    y = length - 1
    dep = "DEP" if deposit_total else "   "
    tax = "TAX" if tax_total else "   "
    productHead = f"No:  NAME/BARCODE  QTY   PRICE  {dep} {tax} "
    receipt = [" "+"*"*length] 
    receipt.append(data["Store Name"].center(y))
    if len(data["Address Line-1"]) > 1 : receipt.append(data["Address Line-1"].center(y))
    if len(data["Address Line-2"]) > 1 : receipt.append(data["Address Line-2"].center(y))
    if len(data["Store Phone"]) > 1 : receipt.append(data["Store Phone"].center(y))
    if len(data["Additional Heading"]) > 1 : receipt.append(data["Additional Heading"].center(y))
    receipt.append("-"*length)
    receipt.append("")
    receipt.append(productHead)
    receipt.append("")
    for count, i in enumerate(productList):
        line1 = list(" "*y)  #For No; and Name     
        line2 = list(" "*y)  #For Barcode, Qty, Price, Tax
        line1[:len(str(count))+1] = f"{count})"
        line1[5:len(i["name"])] = i["name"][:34]
        line2[:len(str(i["barcode"]))] = str(i["barcode"])
        line2[19:22] = str(i["qty"]).center(3)
        line2[24:30] = str(i["sell_price"]).center(6)
        if i["deposit_value"] : line2[31:35] = str(i["deposit_value"]).center(4)
        if i["tax_value"] : line2[37] = "T"
        receipt.append("".join(line1))
        receipt.append("".join(line2))
    receipt.append("\n")
    receipt.append(f"{' '*5}Sub-Total{' '*10} =  {sub_total}")
    if deposit_total: receipt.append(f"{' '*5}Deposit-Amount{' '*5} =  {deposit_total}")
    if tax_total : receipt.append(f"{' '*5}Tax-Amount{' '*9} =  {tax_total}")
    receipt.append(("-"*32+"  ").center(y))
    receipt.append(f"{' '*5}Total Sale Amount   =  {total_amount}")
    receipt.append("")
    receipt.append("-"*length)
    if len(data["Footer Line-1"]) > 1 : receipt.append(data["Footer Line-1"].center(y))
    if len(data["Footer Line-2"]) > 1 : receipt.append(data["Footer Line-2"].center(y))
    receipt.append("*"*length)
    return " \n ".join(receipt)




"""