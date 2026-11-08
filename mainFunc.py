import databaseScripts.inventory as inv
import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.shifts as sf
import sqlite3, os, shutil, ast
import pandas as pd
from datetime import datetime
from escpos.printer import Usb
from kivyScripts.screenManager import sm
import usb.backend.libusb1

global data, tabs, shift,variableButtons, printerSettings

# pyusb needs an actual libusb-1.0 shared library to talk to any USB device
# (the receipt printer, and the device list on the Settings screen) - it is
# not something Windows ships, and PyInstaller can't discover it on its own
# since nothing `import`s it directly (pyusb loads it by name via ctypes at
# runtime). Without it, usb.core.find() raises NoBackendError, which was
# being silently swallowed wherever it's called, showing up to the user as
# "nothing happens" when opening the printer dropdown or trying to print -
# confirmed to be the cause by reading pyusb's own backend-loading code,
# which (with no explicit backend passed) never looks next to our own exe,
# only the OS's standard library search path.
#
# The "libusb" PyPI package exists specifically to solve this: it bundles
# the official prebuilt libusb-1.0 binary for Windows/macOS/Linux as plain
# package data (libusb._platform.DLL_PATH points at the right one for the
# running OS/architecture), so pointing pyusb's backend at that file makes
# USB work without requiring the user to install anything separately or run
# Zadig at all - the WinUSB/libusb-win32 driver swap users normally have to
# do by hand is only needed because Windows' default USB-class driver (or
# none at all for most scanners) won't let a userspace library like libusb
# open the device directly; bundling the library itself is a separate,
# unrelated requirement and doesn't remove that step for the printer.
try:
    import libusb
    usb_backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb._platform.DLL_PATH)
except Exception:
    usb_backend = None


from escpos.printer import Usb
class printer:
    printer = None

    def printReciept(printText,*args,**kwargs):
        try:
            if printer.printer:
                # CP1256 is the standard Windows Arabic codepage - ESC/POS
                # printers that advertise Arabic support (common on Gulf-
                # market thermal printers) do the actual letter-shaping and
                # right-to-left layout in firmware once this codepage is
                # selected; this library just needs to send plain Arabic
                # Unicode text encoded as CP1256 bytes, no pre-shaping
                # needed on our side. ASCII/English text encodes identically
                # under CP1256 as under the default codepage, so one
                # printer.text() call can freely mix English and Arabic.
                # Needs testing on the actual printer model once known -
                # not every printer's firmware maps this codepage the same
                # way, even though CP1256 selection itself is a standard
                # ESC/POS command.
                try: printer.printer.charcode('CP1256')
                except Exception: pass
                printer.printer.text(printText)
                printer.printer.print_and_feed(n=3)
                # printer.printer.cut()
        except:
            printer.connectPrinter()
            printer.printReciept(printText)

    def connectPrinter():
        try:
            usb_args = {"backend": usb_backend} if usb_backend else None
            printer.printer = Usb(int(printerSettings['Printer_VendorID']),int(printerSettings['Printer_ProductID']),usb_args=usb_args)
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


# Bilingual (English/Arabic) tax-invoice labels. These are fixed, standard
# receipt wording - not something a store manager needs to translate or
# edit per-shop, unlike the Store Information fields - so they're hardcoded
# here rather than added to Store Information. Printed one language per
# line (English, then its Arabic translation directly below) rather than
# packed onto one line, since the shared 32-char layout is narrow; a wider
# (e.g. 80mm/42-char) printer could combine them onto single lines instead.
_LABELS = {
    "tax_invoice":   ("TAX Invoice",     "فاتورة ضريبية"),
    "vat_no":        ("VAT No",          "رقم ضريبي"),
    "inv_no":        ("Invoice No",      "رقم الفاتورة"),
    "date":          ("Date",            "التاريخ"),
    "description":   ("Description",     "وصف"),
    "total_amount":  ("Total Amount",    "اجمالي السعر"),
    "discount":      ("Discount",        "خصم"),
    "vat":           ("VAT",             "ضريبة"),
    "grand_total":   ("Grand Total",     "المبلغ الاجمالي"),
    "tender_cash":   ("Tender Cash",     "المدفوع"),
    "cash_return":   ("Cash Return",     "الباقي"),
    "thank_you_en":  "Thank you, Please Come Again",
    # Split across two shorter lines rather than one long one - a single
    # line this length doesn't fit the 32-char width without wrapping
    # mid-word. Exact line lengths may still need tuning once tested on
    # the actual printer (Arabic glyph widths can render slightly
    # differently printer to printer).
    "thank_you_ar":  ("شكراً لتعاملكم معنا", "نتطلع لزيارتكم مرة أخرى"),
}


def _bilingual_line(key, value, y):
    en, ar = _LABELS[key]
    return f"{en} : {value}".ljust(y) + "\n" + ar.center(y)


def _money(value):
    try: return f"{float(value):.2f}"
    except (TypeError, ValueError): return str(value)


def generateReceipt(transNo, productList, sub_total, deposit_total, tax_total, total_amount,
                     cash_tendered=None, change=None):
    length = 32
    y = length - 1
    receipt = []

    receipt.append(data["Store Name"].center(y))
    if len(data.get("Store Name (Arabic)", "")) > 1: receipt.append(data["Store Name (Arabic)"].center(y))
    if len(data["Address Line-1"]) > 1 : receipt.append(data["Address Line-1"].center(y))
    if len(data["Address Line-2"]) > 1 : receipt.append(data["Address Line-2"].center(y))
    if len(data["Store Phone"]) > 1 : receipt.append(data["Store Phone"].center(y))
    if len(data["Additional Heading"]) > 1 : receipt.append(data["Additional Heading"].center(y))

    receipt.append(_LABELS["tax_invoice"][0].center(y))
    receipt.append(_LABELS["tax_invoice"][1].center(y))
    if len(data.get("VAT Number","")) > 1:
        receipt.append(_bilingual_line("vat_no", data["VAT Number"], y))
    receipt.append("-"*length)

    receipt.append(_bilingual_line("inv_no", transNo, y))
    receipt.append(_bilingual_line("date",
        f"{transNo[:4]}/{transNo[4:6]}/{transNo[6:8]} {transNo[8:10]}:{transNo[10:12]}", y))
    receipt.append("-"*length)

    receipt.append(_LABELS["description"][0].center(y))
    receipt.append(_LABELS["description"][1].center(y))
    receipt.append("-"*length)

    discount_total = 0
    for count, i in enumerate(productList):
        receipt.append(f"{count+1}) {i['name'][:27]}")
        # Rate = the line's own unit price (tax-exclusive, same figure this
        # app already shows as "Price" everywhere else); Vat and Total are
        # this item's own already-computed tax_value/line_total - no new
        # calculation, just displaying per-line numbers that were already
        # being tracked but previously only shown in the running totals.
        rate = i["sell_price"]
        vat = i["tax_value"]
        lineTotal = i.get("line_total", round(float(i["qty"])*float(rate) + vat, 2))
        receipt.append("  {:<5} {:>7} {:>6} {:>8}".format(
            str(i["qty"]), f"{rate:.2f}" if isinstance(rate,(int,float)) else rate,
            f"{vat:.2f}" if isinstance(vat,(int,float)) else vat,
            f"{lineTotal:.2f}" if isinstance(lineTotal,(int,float)) else lineTotal))
        if i["deposit_value"]: receipt.append("  BTL/CAN Deposit : "+str(i["deposit_value"]))
        try: discount_total += float(i["discount"]) if i["discount"] else 0
        except (TypeError, ValueError): pass
    receipt.append("-"*length)

    receipt.append(_bilingual_line("total_amount", _money(sub_total), y))
    if discount_total: receipt.append(_bilingual_line("discount", _money(discount_total), y))
    if tax_total: receipt.append(_bilingual_line("vat", _money(tax_total), y))
    receipt.append(_bilingual_line("grand_total", _money(total_amount), y))
    receipt.append("-"*length)

    # Tender/change only make sense for an actual cash payment - card/EBT
    # transactions pass neither, so these lines are skipped rather than
    # showing a misleading 0.00/0.00.
    if cash_tendered is not None and change is not None:
        receipt.append(_bilingual_line("tender_cash", _money(cash_tendered), y))
        receipt.append(_bilingual_line("cash_return", _money(change), y))
        receipt.append("-"*length)

    receipt.append(_LABELS["thank_you_en"].center(y))
    for _line in _LABELS["thank_you_ar"]: receipt.append(_line.center(y))
    if len(data["Footer Line-1"]) > 1 : receipt.append(data["Footer Line-1"].center(y))
    if len(data["Footer Line-2"]) > 1 : receipt.append(data["Footer Line-2"].center(y))
    return "\n".join(receipt)


# Default shape for the editable store/receipt info. New keys can be appended here
# in the future and _DEFAULT_DATA.setdefault-merging below will backfill them into
# any variable.txt saved by an older version of the app, without wiping existing data.
_DEFAULT_DATA = {"Store Name":"", "Store Name (Arabic)":"", "Address Line-1":"", "Address Line-2":"", "Store Phone":"",
                  "VAT Number":"", "Additional Heading":"","Footer Line-1":"","Footer Line-2":""}

_corruptVariableFile = False
if os.path.exists("variable.txt"):
    try:
        with open("variable.txt","r") as file:
            lines=file.readlines()
            data = ast.literal_eval(lines[0])
            shift = ast.literal_eval(lines[1])
            tabs = ast.literal_eval(lines[2])
            variableButtons = ast.literal_eval(lines[3])
            printerSettings = ast.literal_eval(lines[4])
        for key, default in _DEFAULT_DATA.items():
            data.setdefault(key, default)
    except Exception as e:
        # variable.txt exists but is unreadable/corrupted (e.g. the app was killed
        # mid-write). Don't let that permanently brick the register on next launch;
        # archive the bad file and fall through to a fresh default setup below.
        _corruptVariableFile = True
        with open('errorLog',"a") as errFile:
            errFile.write(f"\nCorrupt variable.txt, regenerating defaults : {datetime.now()}\n{e}\n\n")
        try: shutil.move("variable.txt", f"variable.txt.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        except Exception: pass

if (not os.path.exists("variable.txt")) or _corruptVariableFile:
    with open("variable.txt","w") as file:
        print("!!!!!   Initial Setup Starting   !!!!!")
        data = dict(_DEFAULT_DATA)
        shift =  {"Shift No": 1,"Shift Names":"","Shift StartTime":"" }
        tabs=[["Tab 1",None],["Tab 2",None],["Tab 3",None],["Tab 4",None]]
        variableButtons = { "MISC_GENERAL" : {'barcode':"MISC_GENERAL",'name':"Miscellaneous/General","department":"Department_2","purchase_price":0,'qty':1,'deposit':"Deposit_1",'deposit_value':0,'tax':"",'tax_value':0,'discount':"",'discountPromo':"",'line_total':0},
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