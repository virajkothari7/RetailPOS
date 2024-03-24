from kivy.metrics import dp, sp
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDRaisedButton

import usb
import random
from datetime import datetime
import pandas as pd
from functools import partial
import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.inventory as inv
import databaseScripts.shifts as shifts
from kivyScripts.retailScreen import NumPad
from mainFunc import * 

class SettingsScreen(MDScreen):
    file_manager = None
    manager_open = False
    dialog = None
    resetdialog = None
    resetButton = None
    devices = []
    
    def on_pre_enter(self, *args):
        self.file_manager = MDFileManager( exit_manager = self.exit_fileManager, select_path = self.select_filePath, )

        try:
            for cfg in usb.core.find(find_all=True):
                self.devices.append([cfg.manufacturer , cfg.product ,str(cfg.idVendor), str(cfg.idProduct)] )
        except Exception as e:
                print(e)

        dropdown1 = DropDown()
        for i, idx in enumerate(self.devices):
            btn = Button(text=f"{i} {idx[0]}   {idx[1]}",font_size=36 ,size_hint=[1,None],halign="left" )
            btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
            dropdown1.add_widget(btn)
        mainbutton1 = Button(text='Select Printer', size_hint=[0.3,0.15],font_size=36 , pos_hint={"x":0.035,"y":0.515} )
        mainbutton1.bind(on_release=dropdown1.open)
        dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
        
        self.ids["mainButton"] = mainbutton1
        self.ids.fileManagerButton.on_press = self.open_fileManager
        self.add_widget(mainbutton1)    

        self.dialog = MDDialog(title= " Reseting Will delete all the DATA(Except Inventory)",
            text="You will not be able to get back the data, please back-up all data before deleting the data.\n\nInventory data won't be delted by this method to do so please delete APP itself.\n\nThank you for using Digister RetailPOS",
            buttons = [MDRaisedButton(text="Confirm Reset",size=[300,200],font_size=48,md_bg_color=[0.255,0,0,0.75] ,on_press = self.resetDialog )])
        self.resetButton = Button(text= " RESET\n   POS " , background_color = [1,0,0,1], pos_hint= {"x":0.9,"y":0.9}, size_hint = [0.1,0.1],font_size=36,on_press = self.dialog.open )
        self.add_widget(self.resetButton)
        

    def on_pre_leave(self, *args):
        self.file_manager = None
        self.ids.filePathLabel.text = ""
        self.devices =[]
        self.dialog = None
        self.resetdialog = None
        self.remove_widget(self.ids.mainButton)
        self.remove_widget(self.resetButton)
    
    def open_fileManager(self, *args):
        self.file_manager.show('/') 
        self.manager_open = True
    def exit_fileManager(self, *args):
        self.manager_open = False
        self.file_manager.close()
    def select_filePath(self, path,*args):
        self.ids.filePathLabel.text = path
        self.exit_fileManager()
     
    def submitPrinter(self,*args):
        if self.ids.mainButton.text != 'Select Printer':
            printerSettings["Printer_VendorID"] = self.devices[int(self.ids.mainButton.text.split(" ")[0])][2]
            printerSettings["Printer_ProductID"] = self.devices[int(self.ids.mainButton.text.split(" ")[0])][3]
            printerSettings["Cash_Drawer"] = self.ids.cashDrawer.active
            printer.connectPrinter()
            updateStoreInformation()
            if printer.printer is  None:
                MDDialog(title = "!!!   ERROR   !!!\n\nPrinter did not connect successfully",md_bg_color = [1,0,0,0.5]).open()
            else:
                MDDialog(title = "Printer Settings Successfully Updated",md_bg_color = [0,1,0,0.5]).open()

        
    def cashTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            columns = ["Date & Time","Shift ID","Names","Invoice No.","Amount"]
            df = pd.DataFrame(shifts.get_data_C(),columns=columns)
            path = self.ids.filePathLabel.text.strip()+"/CashOut_NoSale_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            try: kwargs['dialog']
            except:  MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()

    def shiftsTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            columns = ["Start Date & Time","End Date & Time","Shift ID","Shift Names","EndShift Report"]
            df = pd.DataFrame(shifts.getData(),columns=columns)
            path = self.ids.filePathLabel.text.strip()+"/ShiftsData_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            try: kwargs['dialog']
            except:  MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()

    def transactionsTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            columns = ["Date & Time","Shift ID","Transaction ID","Total Sale","Amount","Tax Amount","Payment Type","Reciept","Products"]
            df = pd.DataFrame( ts.getData(), columns=columns)
            path = self.ids.filePathLabel.text.strip()+"/TransactionsData_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            try: kwargs['dialog']
            except:  MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()

    def allTransactionsTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            columns = ["Date & Time","Date","Transaction ID","Shift ID","Barcode","Name","Department","Purchase Price", "Sales Price","Qty","Deposit Category",
                "Deposit Amount","Tax Category","Tax Amount","Discount Amount","Payment Type"]
            df = pd.DataFrame(at.getData(),columns = columns)
            df["Sale Amount"] = df["Sales Price"] * df["Qty"]
            df["Sale Amount"] = df["Sale Amount"].round(2)
            df = df[["Date & Time","Date","Transaction ID","Shift ID","Barcode","Name","Department","Tax Category","Deposit Category","Purchase Price", "Sales Price","Qty","Sale Amount",
                "Tax Amount","Deposit Amount","Discount Amount","Payment Type"]]
            path = self.ids.filePathLabel.text.strip()+"/ItemTransactionsData_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            try: kwargs['dialog']
            except:  MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()

    def inventoryTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            columns = ["Name","Barcode","Department CategoryID","Purchase Price","Sales Price","Inventory Qty","Tax CategoryID","Deposit CategoryID"]
            df = pd.DataFrame( inv.getInventoryData(), columns=columns)
            path = self.ids.filePathLabel.text.strip()+"/InventoryData_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            
            df = pd.DataFrame( inv.getAllCategoryValue(), columns=["Date & Time","Category","Category ID","Category Name","Category Value"] )
            path = self.ids.filePathLabel.text.strip()+"/InventoryCategoriesData_"+str(datetime.now())[:-7]+".xlsx"
            df.to_excel(path,index=False)
            
            try: kwargs['dialog']
            except:  MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()

    def allTableData(self,*args,**kwargs):
        if self.ids.filePathLabel.text.strip() != "":
            self.cashTableData(dialog=True)
            self.shiftsTableData(dialog=True)
            self.transactionsTableData(dialog=True)
            self.allTransactionsTableData(dialog=True)
            self.inventoryTableData(dialog=True)
            MDDialog(title="Successfully Saved Data at given directory",md_bg_color = [0,1,0,0.5]).open()
        else:
            MDDialog(title="!!!   Error   !!!\n\nPlease select a directory to save files").open()


    def resetDialog(self,*args):
        self.dialog.dismiss(force=True)
        number = random.randint(0,100000)
        self.resetdialog = MDDialog( title=f"Please type in {number} and press Reset",type="custom", content_cls= NumPad(),size_hint=[0.4,0.935],
                    buttons=[MDRaisedButton(text="RESET & CLOSE",on_press=partial(self.resetConfirm,number),size=[300,200],md_bg_color=[0.255,0,0,0.75],font_size = 58)] )
        self.resetdialog.open()

    def resetConfirm(self,number,*args):
        self.resetdialog.dismiss(force=True)
        if self.resetdialog.content_cls.ids.textField.text:
            try: value = int(self.resetdialog.content_cls.ids.textField.text)
            except: value = None
            if value: 
                if value == number:
                    reset__()