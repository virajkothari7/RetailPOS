from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine

from functools import partial
from datetime import datetime

from kivyScripts.screenManager import sm, fontsize, Window
import databaseScripts.inventory as inv
import re


class InventoryScreen(MDScreen):
    buttons = []
    label = None
    main = None
    layout = None
    mainmenu = None
    barcode = None
    sv = None
    nameField = None
    dialog = None

    def on_pre_enter(self, *args):
        self.main = Button(pos_hint = {"x":0,"y":0},size_hint=[ 0.15,  0.125], text= "[b]Back[/b]", markup = True, font_size = fontsize['button'],
        on_press = self.on_leave)
        self.add_widget(self.main)
        self.buttons = [
            MDRaisedButton( pos_hint = {"x":0.25,"y":0.6175}, size_hint = [0.5, 0.15] , on_press=self.newInventory,
                text= "Add New Inventory", font_style = "H5", font_size = fontsize['label'], md_bg_color= [0.144,0.238,0.144,0.65] ),
            MDRaisedButton( pos_hint = {"x":0.05,"y":0.4}, size_hint = [0.25, 0.1],on_press=self.newProduct,
                text="New Product" , font_style="Subtitle1" , md_bg_color= [0,0.255,0,0.75] ),
            MDRaisedButton( pos_hint = {"x":0.375,"y":0.4}, size_hint = [0.25, 0.1],on_press=self.updateProduct,
                text= "Update Product", font_style="Subtitle1", md_bg_color= [0.139,0.69,0.19,0.75] ),
            MDRaisedButton( pos_hint = {"x":0.05,"y":0.23}, size_hint = [0.25, 0.1],on_press=self.deleteProduct,
                text= "Delete Product",  font_style="Subtitle1", md_bg_color= [0.255,0,0,0.75] ),
            MDRaisedButton( pos_hint = {"x":0.375,"y":0.23}, size_hint = [0.25, 0.1],on_press=self.lookUpProduct,
                text= "Look-Up Product", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,0.5] ),
            MDRaisedButton( pos_hint = {"x":0.7,"y":0.4}, size_hint = [0.25, 0.1],on_press=self.department,
                text= "Department Category", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,0.25] ),
            MDRaisedButton( pos_hint = {"x":0.7,"y":0.23}, size_hint = [0.25, 0.1],on_press=self.taxandDeposit,
                text= "Tax / Deposit Category", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,1] ),
        ]

        for i in self.buttons:
            self.add_widget(i)
        
    def on_leave(self, *args):
        self.removeButtons()
        sm.current = "main"
        
    def on_pre_leave(self, *args):
        if not self.main is None: 
            self.remove_widget(self.main)
            self.main = None
        if not self.layout is None:
            self.remove_widget(self.layout)
            self.layout = None
        if not self.label is None:
            self.remove_widget(self.label)
            self.layout = None
        if not self.mainmenu is None:
            self.remove_widget(self.mainmenu)
            self.mainmenu = None
        if not self.barcode is None:
            self.remove_widget(self.barcode)
            self.barcode = None
        if not self.nameField is None:
            self.remove_widget(self.nameField)
            self.nameField = None
        if not self.sv is None:
            self.remove_widget(self.sv)
            self.sv = None
        if not self.dialog is None:
            self.remove_widget(self.dialog)
            self.dialog = None

    def removeButtons(self, *args):
        for i in self.buttons:
            self.remove_widget(i)
        
    def chnageBack(self, *args):
        self.on_pre_leave()
        self.main = Button(pos_hint = {"x":0,"y":0},size_hint=[ 0.15,  0.125], text= "[b]Back[/b]", markup = True, font_size = fontsize['button'],
        on_press = self.goBack)
        self.add_widget(self.main)
    
    def goBack(self, *args):
        self.on_pre_leave()
        self.on_pre_enter()

    def closeDialog(self,*args):
        self.dialog.dismiss(force=True)

    def getLabel(self,y, *args):
        x= {"add":"Add New Inventory","new":"New Product","update":"Update Product", "delete":"Delete Product","look":"Look-Up Product","department":"Department Categories","tax_deposit":"Tax and Deposit Categories"}
        self.label = MDLabel(pos_hint = {"x":0.149,"y":0},size_hint=[ 0.702,  0.125],halign= "center",
                text= x[y], font_style="H4", md_bg_color= [0.120,0.120,0.120,0.35] )
        self.mainmenu = Button(pos_hint = {"x":0.85,"y":0},size_hint=[ 0.15,  0.125], text= "[b]Main\nMenu[/b]", markup = True, font_size = fontsize['button'],
        on_press = self.on_leave)
        self.add_widget(self.mainmenu)
        self.add_widget(self.label)


    # Add New Inventory Code
    def newInventory(self, *args):
        self.removeButtons()
        self.chnageBack()
        layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.15},size_hint=[1,0.7],)
        self.barcode = MDTextField(hint_text="Enter or Scan Barcode Here... ",mode="fill",size_hint=[0.35,0.05],
            pos_hint= {"x":0.05,"y":0.725}, on_text_validate=self.newInventoryEnter )
        
        layout.add_widget(self.barcode)
        layout.add_widget(
            MDLabel(text="[b] Enter Barcode : [/b]",pos_hint= {"x":0.02,"y":0.915},size_hint=[0.35,0.05],markup=True)
        )
        self.layout = layout
        self.add_widget(self.layout)
        self.getLabel(y="add")

    def newInventoryEnter(self, *args):
        barcode = self.barcode.text.strip()
        self.newInventory()
        self.barcode.text = barcode
        if inv.isBarcode(barcode):
            qty = MDTextField(hint_text="Quantity...",mode="fill",size_hint=[0.2,0.05],
                    pos_hint= {"x":0.48,"y":0.725}, input_filter = "float")
            self.layout.add_widget(qty)
            self.layout.add_widget(
                MDLabel(text="[b] Enter Additional Qty : [/b]",pos_hint= {"x":0.45,"y":0.915},size_hint=[0.35,0.05],markup=True) )
            self.layout.add_widget(
                MDRaisedButton(text='Add Qty',pos_hint={"x":0.75,"y":0.725},font_size=fontsize['button'],
                    size_hint=[0.25,0.15], on_press= partial(self.newInventoryAdd, barcode, qty ) ) )
            columns = ["Name","Barcode","Department Category","Purchase Price","Selling Price","Quantity","Tax Category","Deposit Category"]
            columns = dict(zip(columns,inv.getItemFromBarcode(self.barcode.text.strip())))
            grid = MDGridLayout(cols=4,pos_hint= {"x":0.04,"y":0.24},size_hint=[0.9,0.4],spacing=[70,20])
            for i in ["Barcode","Name","Department Category","Selling Price","Tax Category","Purchase Price","Deposit Category","Quantity"]:
                j = columns[i]
                grid.add_widget( MDLabel(text=f"[b]{i} : [/b]",markup=True) )
                grid.add_widget( MDLabel(text=f"{j}",markup=True,halign="right") )
            self.layout.add_widget(grid)
            self.layout.add_widget(
                MDLabel(text="[b]* Only add additional quantity that you are adding as to the inventory.\n      For Example; If new order has 10, add 10 in Quantity that makes Current Qty + 10[/b]",pos_hint= {"x":0.0135,"y":0.085},size_hint=[0.95,0.05],markup=True) )
            self.layout.add_widget(
                MDLabel(text="[b]* If you like to update Purchase-Price or Selling-Price do it in [u]Update Product Tab[/u] after adding Quantity [/b]",pos_hint= {"x":0.0135,"y":0.01},size_hint=[0.95,0.05],markup=True) )
            
        else:
            pass
    
    def newInventoryAdd(self, barcode, qty,*args):
        qty = qty.text.strip()
        if qty != "" and int(qty) > 0 :
            inv.increaseQuantity(barcode, qty)
            if self.dialog:
                self.remove_widget(self.dialog)
                self.dialog = None
            self.dialog = MDDialog( title="!! Inventory successfully Added  !!", )
            self.dialog.open()
        else:
            if self.dialog:
                self.remove_widget(self.dialog)
                self.dialog = None
            self.dialog = MDDialog( title="!! ERROR !!" )
            self.dialog.open()
        self.newInventory()

    # New Product Code
    def newProduct(self, *args):
        self.removeButtons()
        self.chnageBack()
        self.layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.15},size_hint=[1,0.7],)
        self.sv = ScrollView(size_hint=[0.7,None],pos_hint={'x':0,'y':0.035},scroll_type=['bars','content'], 
                    do_scroll_x = False,size=(Window.width/2, Window.height/1.5),bar_width="7dp")
        stack = MDGridLayout(size_hint=(1,None),cols = 2, adaptive_height= True,row_force_default =True,row_default_height=Window.height/11,
                    col_force_default =True,col_default_width=Window.width/3.5,padding = [100,70,50,0],spacing=[20,20])
        stack.bind(minimum_height=stack.setter('height'))
        columns = ["Barcode","Name","Department Category","Purchase Price","Selling Price","Quantity","Tax Category","Deposit Category"]
        columnData = {}
        
        for i in columns:
            if i not in ["Department Category","Tax Category","Deposit Category"]:
                stack.add_widget(MDLabel(text=f"[b]{i} : [/b]",font_size=fontsize['label'],markup=True,valign="center"))
                columnData[i] = MDTextField(hint_text=f"Enter {i} Here... ",mode="rectangle",required=True)
                stack.add_widget(columnData[i])
            elif i == "Department Category":
                dropdown1 = DropDown()
                for idx in inv.getCategory("Department_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
                    dropdown1.add_widget(btn)
                
                mainbutton1 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton1.bind(on_release=dropdown1.open)
                dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
                
                stack.add_widget(MDLabel(text=f"[b]{i} : [/b]",font_size=fontsize['label'],markup=True))
                columnData[i] = mainbutton1
                stack.add_widget(columnData[i])
            elif i == "Tax Category":
                dropdown2 = DropDown()
                for idx in inv.getCategory("Tax_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
                    dropdown2.add_widget(btn)
                
                mainbutton2 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton2.bind(on_release=dropdown2.open)
                dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
                
                stack.add_widget(MDLabel(text=f"[b]{i} : [/b]",font_size=fontsize['label'],markup=True))
                columnData[i] = mainbutton2
                stack.add_widget(columnData[i])
            elif i == "Deposit Category":
                dropdown3 = DropDown()
                for idx in inv.getCategory("Deposit_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None] ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown3.select(btn.text))
                    dropdown3.add_widget(btn)
                
                mainbutton3 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton3.bind(on_release=dropdown3.open)
                dropdown3.bind(on_select=lambda instance, x: setattr(mainbutton3, 'text', x))
                
                stack.add_widget(MDLabel(text=f"[b]{i} : [/b]",font_size=fontsize['label'],markup=True))
                columnData[i] = mainbutton3
                stack.add_widget(columnData[i])

        self.sv.add_widget(stack)
        self.layout.add_widget(
            MDRaisedButton(text='Add New\n   ITEM',pos_hint={"x":0.75,"y":0.35},font_size=fontsize['button'],halign="center",
                size_hint=[0.2,0.3],on_press=partial(self.newProductConfirm ,columnData))
        )
        self.layout.add_widget(self.sv)
        self.add_widget(self.layout)
        self.getLabel(y="new")

    def newProductConfirm(self,columnData,*args,**kwargs):
        error = {}
        for i in columnData:
            if columnData[i].text.strip() == "" or columnData[i].text.strip()=="Select Category":
                error[i] = True
            else:
                error[i] = False
        if any(error.values()):
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Oops, Invalid Input !!",
                text = "\n".join([f"Error in {i}" for i in error if error[i]]),
                )
            self.dialog.open()
        elif inv.isBarcode(columnData['Barcode'].text.strip()):
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Item already exists !!",
                )
            self.dialog.open()
        elif not re.search(r"^\d*$", columnData['Purchase Price'].text.strip().replace(".","") ):
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Invalid Input, Purchase Price !!\nMust be Number or Decimal value only...",
                )
            self.dialog.open()
        elif (not re.search(r"^\d*$", columnData['Selling Price'].text.strip().replace(".","") )) or float(columnData['Selling Price'].text.strip()) <= 0 :
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Invalid Input, Selling Price !!\nMust be Number or Decimal value and greater than 0.0 ",
                )
            self.dialog.open()
        elif (not re.search(r"^\d*$",columnData['Quantity'].text.strip())) or int(columnData['Quantity'].text.strip()) < 0   :
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Invalid Input, Quantity !!\nMust be Number value and greater than 0 ",
                )
            self.dialog.open()
        else:
            inv.addData( columnData["Name"].text.strip(),columnData["Barcode"].text.strip(), 
                columnData["Department Category"].text.strip().split("\n")[0], columnData["Purchase Price"].text.strip(),
                columnData["Selling Price"].text.strip(), columnData["Quantity"].text.strip(), 
                columnData["Tax Category"].text.strip().split("\n")[0], columnData["Deposit Category"].text.strip().split("\n")[0]  )
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Item was successfully was added !!",
                )
            self.dialog.open()
            self.newProduct()


    # Product Update Code
    def updateProduct(self, *args):
        self.removeButtons()
        self.chnageBack()
        self.layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.15},size_hint=[1,0.7],)
        self.barcode = MDTextField(hint_text="Enter or Scan Barcode Here... ",mode="fill",size_hint=[0.35,0.05],
            pos_hint= {"x":0.1,"y":0.8},on_text_validate=self.updateProductBarcode )
        self.layout.add_widget(self.barcode)
        self.layout.add_widget(
            MDRaisedButton(text='Clear',pos_hint={"x":0.7,"y":0.83},font_size=fontsize['button'],md_bg_color= [0.255,0,0,0.38],
                    size_hint=[0.15,0.1],on_press= self.updateProduct ))
        self.add_widget(self.layout)
        self.getLabel(y="update")

    def updateProductBarcode(self, *args):
        if inv.isBarcode(self.barcode.text.strip()):
            if not self.sv is None:
                self.layout.remove_widget(self.sv)
                self.sv = None 
            
            self.sv = ScrollView(size_hint=[1,None],pos_hint={'x':0,'y':0},scroll_type=['bars','content'], 
                        do_scroll_x = False,size=(Window.width/2, Window.height/1.8),bar_width="7dp")
            stack = MDGridLayout(size_hint=(1,None),cols = 4, row_force_default =True,row_default_height=Window.height/12.75,
                        col_force_default =True,col_default_width=Window.width/4.70,padding = [20,30,20,20],spacing=[65,30])
            stack.bind(minimum_height=stack.setter('height'))
            
            columns = ["Name","Barcode","Department Category","Purchase Price","Selling Price","Quantity","Tax Category","Deposit Category"]
            columnData = {}
            
            stack.add_widget(MDLabel(text="",font_size=fontsize['label'],markup=True,valign="center"))
            stack.add_widget(MDLabel(text="[b][u]Current Value[/u][/b]",font_size=fontsize['label'],markup=True,halign="center"))
            stack.add_widget(MDLabel(text="[b][u]Update Value[/u][/b]",font_size=fontsize['label'],markup=True,halign="center"))
            stack.add_widget(MDLabel(text="",font_size=fontsize['label'],markup=True,valign="center"))
                    
            for i,j in zip(columns,inv.getItemFromBarcode(self.barcode.text.strip())):
                if i == "Barcode":
                    continue
                stack.add_widget(MDLabel(text=f"[b]{i} : [/b]",font_size=fontsize['label'],markup=True,valign="center"))
                stack.add_widget(MDLabel(text=f"{j}",font_size=fontsize['label'],markup=True,valign="center"))
                if i not in ["Department Category","Tax Category","Deposit Category"]:
                    columnData[i] = MDTextField(hint_text=f"Enter {i} Here... ",mode="rectangle")
                    if i in ["Purchase Price","Selling Price","Quantity"]: columnData[i].input_filter = "float"
                    stack.add_widget(columnData[i])
                elif i == "Department Category":
                    dropdown1 = DropDown()
                    for idx in inv.getCategory("Department_Category"):
                        btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                        btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
                        dropdown1.add_widget(btn)
                    mainbutton1 = Button(text='Select Category', size_hint=[1,1] )
                    mainbutton1.bind(on_release=dropdown1.open)
                    dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
                    columnData[i] = mainbutton1
                    stack.add_widget(columnData[i])
                elif i == "Tax Category":
                    dropdown2 = DropDown()
                    for idx in inv.getCategory("Tax_Category"):
                        btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                        btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
                        dropdown2.add_widget(btn)
                    mainbutton2 = Button(text='Select Category', size_hint=[1,1] )
                    mainbutton2.bind(on_release=dropdown2.open)
                    dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
                    columnData[i] = mainbutton2
                    stack.add_widget(columnData[i])
                elif i == "Deposit Category":
                    dropdown3 = DropDown()
                    for idx in inv.getCategory("Deposit_Category"):
                        btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None] ,background_color=[0.150, 0.60, 1.0, 1.0])
                        btn.bind(on_release=lambda btn: dropdown3.select(btn.text))
                        dropdown3.add_widget(btn)
                    mainbutton3 = Button(text='Select Category', size_hint=[1,1] )
                    mainbutton3.bind(on_release=dropdown3.open)
                    dropdown3.bind(on_select=lambda instance, x: setattr(mainbutton3, 'text', x))
                    columnData[i] = mainbutton3
                    stack.add_widget(columnData[i])
                
                stack.add_widget(
                    MDRaisedButton(text='Update',size_hint=[1,1],on_press=partial(self.updateValue, i, columnData[i], self.barcode.text.strip()))
                    )
            self.sv.add_widget(stack)
            self.layout.add_widget(self.sv)
        else:
            if not self.dialog is None:
                self.remove_widget(self.dialog)
                self.dialog =None
            self.dialog = MDDialog( size_hint = [0.5, 0.2],
                pos_hint = {"x":0.25,"y":0.4}, title="[b]No Item Found[/b]" )
            self.dialog.open()
        
    def updateValue(self,col,value,barcode,*args):
        if value.text.strip():
            if value.text.strip()=="Select Category":
                pass
            else:
                if not self.dialog is None:
                    self.remove_widget(self.dialog)
                    self.dialog =None
                self.dialog = MDDialog(
                    size_hint = [0.5, 0.2],
                    pos_hint = {"x":0.25,"y":0.4},
                    title="Please confirm changes to the product ?",
                    text= f"Name: {inv.getNameFromBarcode(self.barcode.text.strip())} and Barcode: {self.barcode.text.strip()}",
                    buttons=[MDFlatButton(text="Cancel" ,on_press = self.closeDialog ,font_size = fontsize['button']),
                        MDRaisedButton(text="Confirm",on_press =partial(self.updateConfirm, col, value.text.strip(), barcode) ,font_size = fontsize['button'])],
                    )
                self.dialog.open()
    
    def updateConfirm(self,col,value,barcode,*args):
        self.closeDialog()
        
        if col == "Name": inv.updateName(barcode,value),
        elif col == "Department Category": inv.updateDepartment(barcode,value.split("\n")[0]),
        elif col == "Purchase Price": inv.updatePurchasePrice(barcode,value) ,
        elif col == "Selling Price": inv.updateSellPrice(barcode,value),
        elif col == "Quantity": inv.updateQuantity(barcode,value),
        elif col == "Tax Category": inv.updateTax(barcode,value.split("\n")[0]),
        elif col == "Deposit Category": inv.updateDeposit(barcode,value.split("\n")[0]),
        
        if not self.dialog is None:
            self.remove_widget(self.dialog)
            self.dialog =None
        self.dialog = MDDialog( size_hint = [0.5, 0.2],
                pos_hint = {"x":0.25,"y":0.7}, title="!! Successfully Updated !!", )
        self.dialog.open()
        
        self.updateProductBarcode()
        

    # Product Delete Code
    def deleteProduct(self, *args):
        self.removeButtons()
        self.chnageBack()
        layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.15},size_hint=[1,0.6],)
        self.barcode = MDTextField(hint_text="Enter or Scan Barcode Here... ",mode="fill",size_hint=[0.35,0.05],
            pos_hint= {"x":0.025,"y":0.75},on_text_validate=self.deleteEnter )
        layout.add_widget(self.barcode)
        self.layout = layout
        self.add_widget(self.layout)
        self.getLabel(y="delete")
        
    def deleteEnter(self, *args):
        if not self.sv is None:
            self.layout.remove_widget(self.sv)
            self.sv = None 
        self.sv = MDRelativeLayout(pos_hint={"x":0.45,"y":0},size_hint=[0.5,0.7])
        if self.barcode.text.strip() != "" and inv.isBarcode(self.barcode.text.strip()):
            self.sv.add_widget(self.productDisplay(inv.getItemFromBarcode(self.barcode.text.strip())))
            self.layout.add_widget(MDRaisedButton(text="Delete",size_hint=[0.3,0.2],on_press=self.deleteDialog,pos_hint= {"x":0.045, "y":0.27}, md_bg_color= [0.255,0,0,0.5] ))
        else:
            self.sv.add_widget(MDLabel(
                text="[b]No Product Found[/b]",font_style="H4",pos_hint={"x":0.2,"y":0.3},markup=True))
        self.layout.add_widget(self.sv )

    def deleteDialog(self, *args):
        if inv.getNameFromBarcode(self.barcode.text.strip()):
            if not self.dialog is None:
                self.remove_widget(self.dialog)
                self.dialog =None
            self.dialog = MDDialog(
                    size_hint = [0.5, 0.2],
                    pos_hint = {"x":0.25,"y":0.4},
                    title="Please confirm deletion of the product ?",
                    text= f"Name: {inv.getNameFromBarcode(self.barcode.text.strip())} and Barcode: {self.barcode.text.strip()}",
                    buttons=[MDRaisedButton(text="Delete",on_press =self.deleteConfirm ,font_size = fontsize['button'])],
            )
            self.dialog.open()

    def deleteConfirm(self, *args):
        self.closeDialog()
        if not self.sv is None:
            self.layout.remove_widget(self.sv)
            self.sv = None 
        self.sv = MDRelativeLayout(pos_hint={"x":0.45,"y":0.15},size_hint=[0.4,0.7])
        if self.barcode.text.strip() != "" and inv.isBarcode(self.barcode.text.strip()):
            inv.deleteItemFromBarcode(self.barcode.text.strip())
            self.sv.add_widget(MDLabel(
                text="[b]Item was successfully deleted[/b]",font_style="H6",pos_hint={"x":0.2,"y":0.2},markup=True))
        else:
            self.sv.add_widget(MDLabel(
                text="[b]Error while deleting: No item found associated with given barcode[/b]",font_style="H6",pos_hint={"x":0.2,"y":0.2},markup=True))
        self.layout.add_widget(self.sv )


    # Product Look-up Code
    def lookUpProduct(self, *args):
        self.removeButtons()
        self.chnageBack()
        self.layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.15},size_hint=[1,0.6],)
        self.layout.add_widget(
            MDLabel(text="Enter Product BARCODE ; ",pos_hint= {"x":0.03,"y":0.97},size_hint=[0.35,0.05])
        )
        self.layout.add_widget(
            MDLabel(text="[b] OR [/b]",pos_hint= {"x":0.03,"y":0.6},size_hint=[0.35,0.05],markup=True)
        )
        self.layout.add_widget(
            MDLabel(text="Enter Product NAME ; ",pos_hint= {"x":0.03,"y":0.42},size_hint=[0.35,0.05])
        )
        self.barcode = MDTextField(hint_text="Enter or Scan Barcode Here... ",mode="fill",size_hint=[0.35,0.05],
            pos_hint= {"x":0.03,"y":0.75},on_text_validate=self.lookup )
        self.nameField = MDTextField(hint_text="Enter name of the PRODUCT... ",mode="fill",size_hint=[0.35,0.05],
            pos_hint= {"x":0.03,"y":0.2},on_text_validate=self.lookup )
        self.layout.add_widget(self.barcode)
        self.layout.add_widget(self.nameField)
        self.add_widget(self.layout)
        self.getLabel(y="look")
    
    def lookup(self, *args):
        if not self.sv is None:
            self.layout.remove_widget(self.sv)
            self.sv = None 
        self.sv = ScrollView(size_hint=[0.53,None],pos_hint={'x':0.45,'y':0.035},scroll_type=['bars','content'],
                    do_scroll_x = False,size=(Window.width/2, Window.height/1.5),bar_width="10dp")
        stack = MDStackLayout(size_hint=(1,None))
        stack.bind(minimum_height=stack.setter('height'))
        
        if self.barcode.text.strip() != "" and inv.isBarcode(self.barcode.text.strip()):
            stack.add_widget( MDLabel(text=f"[b]Barcode : {self.barcode.text.strip()}[/b]",markup=True,size_hint_y = None, halign= "center") )
            stack.add_widget(self.productDisplay(inv.getItemFromBarcode(self.barcode.text.strip())))
        elif self.nameField.text.strip() != "" :
            stack.add_widget( MDLabel(text=f"[b]Name : {self.nameField.text.strip()}[/b]",markup=True ,size_hint_y = None, halign= "center") )
            for i in inv.getItemsFromName(self.nameField.text.strip()):
                stack.add_widget(
                    MDExpansionPanel(
                    content= self.productDisplay(i),
                    icon = "./images/computer-science-1331580_640.png",
                    panel_cls=MDExpansionPanelTwoLine(
                        text=str(i[0]),
                        secondary_text=str(i[1])),
                    ))
        else:
            stack.add_widget(MDLabel(
                text="[b]No Product Found[/b]",font_style="H5",markup=True, halign= "center",valign='middle'
            ))

        self.sv.add_widget(stack)
        self.barcode.text = ""
        self.nameField.text = ""
        self.layout.add_widget(self.sv)
    
    def productDisplay(self,plist):
        columns = ["Name","Barcode","Department","Purchase Price","Selling Price","Quantity","Tax Category","Deposit Category"]
        layout = MDGridLayout(cols = 2, adaptive_height= True,row_force_default =True,row_default_height=100,padding=[80,25,5,35])
        for i in zip(columns,plist):
            layout.add_widget(MDLabel(text = f"[b]{i[0]} : [/b]",markup=True))
            layout.add_widget(MDLabel(text = f"{i[1]}"))
        return layout
    #Window.bind(on_keyboard = self.deleteEnter)


    # Category Code for Department, Tax and Deposit
    def department(self, *args):
        self.removeButtons()
        self.chnageBack()
        self.layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.125},size_hint=[1,0.7],)
        if not self.sv is None:
            self.layout.remove_widget(self.sv)
            self.sv = None 
        self.sv = ScrollView(size_hint=[1,None],pos_hint={'x':0,'y':0.1},scroll_type=['bars','content'],
                    do_scroll_x = False,size=(Window.width-100, Window.height/1.5),bar_width="10dp")
        stack = MDGridLayout(size_hint=(1,None),cols = 3, adaptive_height= True,row_force_default =True,row_default_height=Window.height/5,
                    col_force_default =True,col_default_width=Window.width/3.25,padding = [50,50,50,50],spacing=[20,20])
        stack.bind(minimum_height=stack.setter('height'))
        for i in inv.getCategory("Department_Category") :
            if i[3] in ["Default","Miscellaneous/General","Deli/General"]:
                stack.add_widget(
                MDRaisedButton(size_hint=[0.9,0.9],padding=[75,100,75,100],anchor_x='left',text= f"{i[2]}\n{i[3]}", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,0.25] ),
                )
            else:
                stack.add_widget(
                MDRaisedButton(on_press=self.updateCategory,size_hint=[0.9,0.9],padding=[75,100,75,100],anchor_x='left',
                        text= f"{i[2]}\n{i[3]}", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,0.25] ),
                )
        stack.add_widget(
            MDRaisedButton(on_press=self.addCategory,size_hint=[0.9,0.9],padding=[75,100,75,100],
                    text= "Add Department", font_style="Subtitle1", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        self.sv.add_widget(stack)
        self.layout.add_widget(self.sv)
        self.add_widget(self.layout)
        self.getLabel(y="department")

    def taxandDeposit(self, *args):
        self.removeButtons()
        self.chnageBack()
        self.layout = MDRelativeLayout(pos_hint = {"x":0,"y":0.07},size_hint=[1,0.75],)
        if not self.sv is None:
            self.layout.remove_widget(self.sv)
            self.sv = None 
        self.sv = MDRelativeLayout(pos_hint = {"x":0,"y":0},size_hint=[1,1],)
        
        taxgrid = MDGridLayout(pos_hint={'x':0,'y':0.26},size_hint=[0.6,0.78],cols = 3,row_force_default =True,row_default_height=Window.height/10,
                    col_force_default =True,col_default_width=Window.width/5.75,padding = [50,50,50,50],spacing=[20,20])
        for i in inv.getCategory("Tax_Category"):
            txt = '\n'.join(i[2:])
            if i[-1] == "N/A":
                taxgrid.add_widget(
                MDRaisedButton(size_hint=[0.9,0.9],anchor_x='left',padding = [30,50,30,50], text= f"{txt}", font_style="Subtitle1",md_bg_color= [0.159,0.226,0.191,1] ),)
            else:
                taxgrid.add_widget(
                MDRaisedButton(size_hint=[0.9,0.9],anchor_x='left',padding = [30,50,30,50],on_press=self.updateCategory ,
                        text= f"{txt}", font_style="Subtitle1",md_bg_color= [0.159,0.226,0.191,1] ),
                )
        if inv.nextCategoryId('Tax_Category') <=15:
            taxgrid.add_widget(MDRaisedButton(size_hint=[0.9,0.9],anchor_x='left',padding = [30,50,30,50],on_press=self.addCategory,
                    text= "Add\nTax Category",md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        
        depgrid = MDGridLayout(pos_hint={'x':0.58,'y':0.26},cols = 2, size_hint=[0.4,0.78],row_force_default =True,row_default_height=Window.height/10,
                    col_force_default =True,col_default_width=Window.width/5.75,padding = [50,50,50,50],spacing=[20,20])
        for i in inv.getCategory("Deposit_Category"):
            txt = '\n'.join(i[2:])
            if i[-1] == "N/A":
                depgrid.add_widget(
                MDRaisedButton(size_hint=[0.9,0.9],anchor_x='center',padding = [30,50,30,50],text= f"{txt}", font_style="Subtitle1", md_bg_color= [0.159,0.226,0.251,1] ),)
            else:
                depgrid.add_widget(
                MDRaisedButton(size_hint=[0.9,0.9],anchor_x='center',padding = [30,50,30,50],on_press=self.updateCategory  ,
                        text= f"{txt}", font_style="Subtitle1", md_bg_color= [0.159,0.226,0.251,1] ),
                )
        if inv.nextCategoryId('Tax_Category') <=15:
            depgrid.add_widget(
            MDRaisedButton(size_hint=[0.9,0.9],anchor_x='center',padding = [30,50,30,50],on_press=self.addCategory,
                    text= "Add\nDeposit Category", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        self.sv.add_widget(
            MDLabel(text="[b][u]TAX CATEGORIES[/u][/b]",
                size_hint=[0.5,0.1],pos_hint={'x':0.025,'y':0.97},halign="center",markup=True,)
        )
        self.sv.add_widget(
            MDLabel(text="[b][u]DEPOSIT CATEGORIES[/u][/b]",
                size_hint=[0.4,0.1],pos_hint={'x':0.6,'y':0.97},halign="center",markup=True,)
        )
        self.sv.add_widget(
            MDLabel(text="**There is limit in creating Tax and Deposit categories. Maximum Tax-Category allowed is 15, and \n    Deposit-Category allowed is 10. Once Category is created you won't be able to delete it in future as \n    Inventory and Transactions are connected to it, unless you RESET the whole System",
                size_hint=[0.95,0.3],pos_hint={'x':0.025,'y':0},markup=True,)
        )
        self.sv.add_widget(taxgrid)
        self.sv.add_widget(depgrid)
        self.layout.add_widget(self.sv)
        self.add_widget(self.layout)
        self.getLabel(y="tax_deposit")

    def addCategory(self,widget,*args):
        self.layout.remove_widget(self.sv)
        if 'Department' in widget.text:
            self.main.on_press = self.department
            self.layout.add_widget(
                MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.65},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                    MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.4},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] )
                )
            self.layout.add_widget(
                MDLabel(text=f"[b]Deapartment_{inv.nextCategoryId('Department_Category')}[/b]",pos_hint={"x":0.45,"y":0.65},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            self.nameField= MDTextField(font_size=fontsize['button'],on_text_validate=self.addCategorySubmit,helper_text="Department_"+str(inv.nextCategoryId('Department_Category')),hint_text="Enter Department Name..",pos_hint={"x":0.45,"y":0.4},size_hint=[0.4,0.15])
            
            self.layout.add_widget(self.nameField
                )
            self.layout.add_widget(
            MDRaisedButton(on_press=self.addCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.1},padding=[25,25,25,25],
                    text= "Add Department", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        elif 'Tax' in widget.text:
            self.main.on_press = self.taxandDeposit
            self.layout.add_widget(
                MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.8},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                MDLabel(text=f"[b]Tax_{inv.nextCategoryId('Tax_Category')}[/b]",pos_hint={"x":0.45,"y":0.8},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                    MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.6},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] )
                )
            self.nameField= MDTextField(font_size=fontsize['button'],helper_text="Tax_"+str(inv.nextCategoryId('Tax_Category')),hint_text="Enter Tax Category Name..",required= True,pos_hint={"x":0.45,"y":0.6},size_hint=[0.4,0.15])
            self.layout.add_widget(self.nameField
                )
            
            self.layout.add_widget(
                    MDLabel(text="[b]Tax Value ;[/b]\nAdd '%' sign at end to act as percentage value, like 8.625%",pos_hint={"x":0.1,"y":0.4},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] )
                )
            
            self.barcode= MDTextField(on_text_validate=self.validateValue,font_size=fontsize['button'],helper_text="Tax_"+str(inv.nextCategoryId('Tax_Category')),required= True,hint_text="Enter Tax Value",pos_hint={"x":0.45,"y":0.4},size_hint=[0.4,0.15])
            self.layout.add_widget(self.barcode
                )
            
            self.layout.add_widget(
            MDRaisedButton(on_press=self.addCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.1},padding=[25,25,25,25],
                    text= "Add Tax Category", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        elif 'Deposit' in widget.text:
            self.main.on_press = self.taxandDeposit
            self.layout.add_widget(
                MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.8},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                MDLabel(text=f"[b]Deposit_{inv.nextCategoryId('Deposit_Category')}[/b]",pos_hint={"x":0.45,"y":0.8},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                    MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.6},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] )
                )
            self.nameField= MDTextField(font_size=fontsize['button'],helper_text="Deposit_"+str(inv.nextCategoryId('Deposit_Category')),hint_text="Enter Deposit Category Name..",required= True,pos_hint={"x":0.45,"y":0.6},size_hint=[0.4,0.15])
            self.layout.add_widget(self.nameField
                )
            
            self.layout.add_widget(
                    MDLabel(text="[b]Deposit Value ;[/b]\nJust sumbit decimal amount\nlike 0.05 or 0.25",pos_hint={"x":0.1,"y":0.4},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] )
                )
            
            self.barcode= MDTextField(on_text_validate=self.validateValue,font_size=fontsize['button'],helper_text="Deposit_"+str(inv.nextCategoryId('Deposit_Category')),required= True,hint_text="Enter Deposit Value",pos_hint={"x":0.45,"y":0.4},size_hint=[0.4,0.15])
            self.layout.add_widget(self.barcode
                )
            
            self.layout.add_widget(
            MDRaisedButton(on_press=self.addCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.1},padding=[25,25,25,25],
                    text= "Add Deposit Category", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )

    def addCategorySubmit(self,widget,*args):
        if self.nameField.text.strip()=="":
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Oops, Invalid Input !!",
                )
            self.dialog.open()
        elif ('Department' in widget.text) or ('Department' in self.nameField.helper_text) :
            inv.addCategoryData(datetime.now(),'Department_Category',self.nameField.helper_text,self.nameField.text.strip(),None)
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="Department has been successfully added!!",
                )
            self.dialog.open()
            self.department()
        elif ('Tax' in widget.text) or ('Tax' in self.nameField.helper_text) :
            if self.validateValue():
                inv.addCategoryData(datetime.now(),'Tax_Category',self.nameField.helper_text,self.nameField.text.strip(),self.barcode.text.strip())
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="Tax Category has been successfully added!!",
                )
                self.dialog.open()
                self.taxandDeposit()
        elif ('Deposit' in widget.text) or ('Deposit' in self.nameField.helper_text) :
            if self.validateValue():
                inv.addCategoryData(datetime.now(),'Deposit_Category',self.nameField.helper_text,self.nameField.text.strip(),self.barcode.text.strip())
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="Deposit Category has been successfully added!!",
                )
                self.dialog.open()
                self.taxandDeposit()

    def updateCategory(self,widget, *args):
        self.layout.remove_widget(self.sv)
        
        if 'Department' in widget.text:
            self.main.on_press = self.department

            self.layout.add_widget( MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.75},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label']) )
            self.layout.add_widget( MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.58},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.layout.add_widget( MDLabel(text="[b]Update Category Name ;[/b]",pos_hint={"x":0.1,"y":0.4},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[0],pos_hint={"x":0.45,"y":0.75},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[1],pos_hint={"x":0.45,"y":0.58},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            self.nameField= MDTextField(font_size=fontsize['button'],on_text_validate=self.updateCategorySubmit,helper_text=widget.text.split("\n")[0],hint_text="Enter New Department Name..",pos_hint={"x":0.45,"y":0.4},size_hint=[0.4,0.15])
            self.layout.add_widget(self.nameField)
            self.layout.add_widget(
            MDRaisedButton(on_press=self.updateCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.125},padding=[25,25,25,25],
                    text= "Update Department", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        elif 'Tax' in widget.text:
            self.main.on_press = self.taxandDeposit

            self.layout.add_widget( MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.8},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label']) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[0],pos_hint={"x":0.45,"y":0.8},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            
            self.layout.add_widget( MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.7},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[1],pos_hint={"x":0.45,"y":0.7},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )

            self.layout.add_widget( MDLabel(text="[b]Tax Percentage ;[/b]",pos_hint={"x":0.1,"y":0.60},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[2],pos_hint={"x":0.45,"y":0.60},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            
            self.layout.add_widget( MDLabel(text="[b]Update Category Name ;[/b]",pos_hint={"x":0.1,"y":0.45},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.nameField= MDTextField(font_size=fontsize['button'],helper_text=widget.text.split("\n")[0],hint_text="Enter New Department Name..",pos_hint={"x":0.45,"y":0.45},size_hint=[0.4,0.15])
            self.layout.add_widget(self.nameField)
            
            self.layout.add_widget( MDLabel(text="[b]Update Tax Percentage ;[/b]",pos_hint={"x":0.1,"y":0.315},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.barcode= MDTextField(font_size=fontsize['button'],helper_text=widget.text.split("\n")[0],hint_text="Enter New Tax Value",pos_hint={"x":0.45,"y":0.315},size_hint=[0.4,0.15])
            self.layout.add_widget(self.barcode
                )
            self.layout.add_widget(
            MDRaisedButton(on_press=self.updateCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.075},padding=[25,25,25,25],
                    text= "Update Tax Category", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        elif 'Deposit' in widget.text:
            self.main.on_press = self.taxandDeposit

            self.layout.add_widget( MDLabel(text="[b]Category ID Number ;[/b]",pos_hint={"x":0.1,"y":0.8},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label']) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[0],pos_hint={"x":0.45,"y":0.8},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            
            self.layout.add_widget( MDLabel(text="[b]Category Name ;[/b]",pos_hint={"x":0.1,"y":0.7},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[1],pos_hint={"x":0.45,"y":0.7},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )

            self.layout.add_widget( MDLabel(text="[b]Deposit Amount ;[/b]",pos_hint={"x":0.1,"y":0.60},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.layout.add_widget(
                MDLabel(text=widget.text.split("\n")[2],pos_hint={"x":0.45,"y":0.60},size_hint=[0.4,0.15],markup=True,font_size= fontsize['label'])
            )
            
            self.layout.add_widget( MDLabel(text="[b]Update Category Name ;[/b]",pos_hint={"x":0.1,"y":0.45},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.nameField= MDTextField(font_size=fontsize['button'],helper_text=widget.text.split("\n")[0],hint_text="Enter New Department Name..",pos_hint={"x":0.45,"y":0.45},size_hint=[0.4,0.15])
            self.layout.add_widget(self.nameField)
            
            self.layout.add_widget( MDLabel(text="[b]Update Deposit Amount ;[/b]",pos_hint={"x":0.1,"y":0.315},size_hint=[0.35,0.15],markup=True,font_size= fontsize['label'] ) )
            self.barcode= MDTextField(font_size=fontsize['button'],helper_text=widget.text.split("\n")[0],hint_text="Enter New Deposit Value",pos_hint={"x":0.45,"y":0.315},size_hint=[0.4,0.15])
            self.layout.add_widget(self.barcode
                )
            self.layout.add_widget(
            MDRaisedButton(on_press=self.updateCategorySubmit,size_hint=[0.3,0.2],pos_hint={"x":0.45,"y":0.075},padding=[25,25,25,25],
                    text= "Update Deposit Category", font_style="H6", md_bg_color= [0.120,0.220,0.220,0.55] ),
            )
        
    def updateCategorySubmit(self,widget,*args):
        if ('Department' in widget.text) or ('Department' in self.nameField.helper_text) :
            if self.nameField.text.strip()=="":
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="!! Oops, Invalid Input !!",
                    )
                self.dialog.open()
            inv.updateNameFromId(self.nameField.text.strip(),self.nameField.helper_text)
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="Department name has been successfully updated !!",
                )
            self.dialog.open()
            self.department()
        if ('Tax' in widget.text):
            if self.nameField.text.strip()=="" and self.barcode.text.strip()=="" :
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="!! Oops, Invalid Input !!",
                    )
                self.dialog.open()
            else:
                if self.nameField.text.strip():
                    inv.updateNameFromId(self.nameField.text.strip(),self.nameField.helper_text)
                    if self.dialog: self.remove_widget(self.dialog)
                    self.dialog = MDDialog(
                        title="Tax Category Name has been successfully updated !!",
                        )
                    self.dialog.open()
                if self.barcode.text.strip() and self.validateValue():
                    inv.updateValueFromId(self.barcode.text.strip(),self.barcode.helper_text)
                    if self.dialog: 
                        self.closeDialog()
                        self.remove_widget(self.dialog)
                    self.dialog = MDDialog(
                        title="Tax Category has been successfully updated !!",
                        )
                    self.dialog.open()
                self.taxandDeposit()
        if ('Deposit' in widget.text):
            if self.nameField.text.strip()=="" and self.barcode.text.strip()=="" :
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="!! Oops, Invalid Input !!",
                    )
                self.dialog.open()
            else:
                if self.nameField.text.strip():
                    inv.updateNameFromId(self.nameField.text.strip(),self.nameField.helper_text)
                    if self.dialog: self.remove_widget(self.dialog)
                    self.dialog = MDDialog(
                        title="Deposit Category Name has been successfully updated !!",
                        )
                    self.dialog.open()
                if self.barcode.text.strip() and self.validateValue():
                    inv.updateValueFromId(self.barcode.text.strip(),self.barcode.helper_text)
                    if self.dialog: 
                        self.closeDialog()
                        self.remove_widget(self.dialog)
                    self.dialog = MDDialog(
                        title="Deposit Category has been successfully updated !!",
                        )
                    self.dialog.open()
                self.taxandDeposit()

    def validateValue(self,*args):
        if self.barcode.text.strip()=="" or not re.search(r"(^\d*%$|^\d*$)",self.barcode.text.replace(".","")):
            if self.dialog: self.remove_widget(self.dialog)
            self.dialog = MDDialog(
                title="!! Oops, Invalid Input !!",
                )
            self.dialog.open()
        elif "Tax" in self.barcode.helper_text:
            if "%" not in self.barcode.text.strip()[-1]:
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="!! It seems it doesn't have '%' at end for Tax Value. It will not act as Tax Percentage, Please update value as Percentage !!",
                    )
                self.dialog.open()
            else: return True
        elif "Deposit" in self.barcode.helper_text:
            if "%" in self.barcode.text.strip():
                if self.dialog: self.remove_widget(self.dialog)
                self.dialog = MDDialog(
                    title="!! Please be sure that Deposit Category is being add as Percentage Value, Please update value as Amount Value without Percentage !!",
                    )
                self.dialog.open()
            else: return True
        return False
