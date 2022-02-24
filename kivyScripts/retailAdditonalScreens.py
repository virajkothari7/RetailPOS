from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton

from kivyScripts.screenManager import sm, fontsize, Window
import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.inventory as inv

from mainFunc import * 
from functools import partial

class buttonSettings(MDScreen):
    sv = None
    popup = None 

    def on_pre_enter(self, *args):
        
        self.sv = ScrollView(size_hint=[1,None],pos_hint={'x':0,'y':0.125},scroll_type=['bars','content'],
                    do_scroll_x = False,size=(Window.width, Window.height*0.875),bar_width="10dp")
        stack = MDStackLayout(size_hint=(0.99,None))
        stack.bind(minimum_height=stack.setter('height'))
        
        stack.add_widget(MDLabel(text="Misc. and Deli Tax Settings",md_bg_color=[0.100,0,0.10,0.6],halign="center",size = [Window.width,200],size_hint=[1,None],font_style="H4"))
        grid = MDGridLayout(cols=4,size_hint=(1,None),md_bg_color=[0.100,0,0.10,0.35], adaptive_height= True,row_force_default =True,row_default_height=130,spacing=30,padding=[50,50,50,50])
        grid.add_widget(MDLabel(text="MISC_GENERAL",size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDLabel(text=variableButtons["MISC_GENERAL"]['tax'],size_hint=[1,1],halign="center",font_style="Subtitle1"))
        dropdown1 = DropDown()
        for idx in inv.getCategory("Tax_Category"):
            btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
            btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
            dropdown1.add_widget(btn)
        mainbutton1 = Button(text='Select Category', size_hint=[1,1] )
        mainbutton1.bind(on_release=dropdown1.open)
        dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
        tax1 = mainbutton1
        grid.add_widget(tax1)
        grid.add_widget(MDRaisedButton(text="UPDATE",size_hint=[1,1], on_press = partial(self.update_Misc_Deli,"MISC_GENERAL",tax1)))
        grid.add_widget(MDLabel(text="DELI_GENERAL",size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDLabel(text=variableButtons["DELI_GENERAL"]['tax'],size_hint=[1,1],halign="center",font_style="Subtitle1"))
        dropdown2 = DropDown()
        for idx in inv.getCategory("Tax_Category"):
            btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
            btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
            dropdown2.add_widget(btn)
        mainbutton2 = Button(text='Select Category', size_hint=[1,1] )
        mainbutton2.bind(on_release=dropdown2.open)
        dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
        tax2 = mainbutton2
        grid.add_widget(tax2)
        grid.add_widget(MDRaisedButton(text="UPDATE",size_hint=[1,1], on_press = partial(self.update_Misc_Deli,"DELI_GENERAL",tax2)))
        stack.add_widget(grid)
        
        stack.add_widget(MDLabel(text="",size = [Window.width,50],halign="center",size_hint=[1,None],font_style="H4"))
        stack.add_widget(MDLabel(text="Quick Add Tab and Tab Items Setting",md_bg_color=[0.10,0.200,0.200,0.5], size = [Window.width,200],halign="center",size_hint=[1,None],font_style="H4"))
        grid = None
        for num,i in enumerate(tabs):
            titleName = i[0] if i[0] else f"Tab {num+1}"
            grid = MDGridLayout(cols=5,size_hint=(1,None),md_bg_color=[0.10,0.200,0.200,0.15], adaptive_height= True,row_force_default =True,row_default_height=150,spacing=10,padding=[20,55,20,55])
            grid.add_widget(MDLabel(text="",size_hint=[1,1]))
            grid.add_widget(MDLabel(text=titleName,size_hint=[1,1],font_style="H4"))
            grid.add_widget(MDLabel(text="",size_hint=[1,1]))
            grid.add_widget(MDTextField(hint_text="Write New Tab Name Here and\nPress Enter to chnage it.....",font_size= fontsize["label"],helper_text= f"{num}",on_text_validate=self.changeTabName,size_hint=[1,1]))
            grid.add_widget(MDLabel(text="",size_hint=[1,1]))
            for j in  at.getTab(f"Tab{num+1}"):
                grid.add_widget(  MDFillRoundFlatButton(anchor_x='center',text= f"{j[0]}\n{j[2]}\n{j[3]}",size_hint=[1,1],on_press = self.addItem))
            stack.add_widget(grid)
        
        self.sv.add_widget(stack)
        self.add_widget(self.sv)

    def on_leave(self,*args):
        if self.popup: self.remove_widget(self.popup)
        if self.sv: self.remove_widget(self.sv)
        self.sv= None 
        self.popup =None
        
    
    def innerBack(self,*args):
        self.on_leave()
        self.on_pre_enter()

    def update_Misc_Deli(self,barcode,tax_id,*args):
        tax_id = tax_id.text.strip().split("\n")[0]
        barcode = barcode
        if tax_id == "" or tax_id in [i[2] for i in inv.getCategory("Tax_Category")]:
            variableButtons[barcode]['tax']=tax_id
            updateStoreInformation()
            self.innerBack()
        else:
            pass
    
    def changeTabName(self,widget,*args):
        num = int(widget.helper_text.strip())
        text = widget.text.strip()
        if text != "":
            tabs[num][0] = text
            updateStoreInformation()
            MDDialog( title= f"Tab Name Successfully Changed").open()
            self.innerBack()
    
    def addItem(self,widget,*args):
        if self.popup:
                self.remove_widget(self.popup)
                self.popup = None
        text = widget.text.strip()
        if text.split("\n")[1] == "Add Item":
            self.popup = MDDialog( title= "What type of Item you would like to associate with this Entry",size_hint=[0.4,None],
                text = "\nBarcode Entry means fixed price Items.\n\nVariable Entry means variable price for given Item.\n",
                buttons = [MDRaisedButton(text= "Barcode Entry",font_size= 40,on_press = partial(self.addBarcode,text.split("\n")[0] )),
                        MDRaisedButton(text="Variable Entry",md_bg_color=[0.10,0.200,0.200,0.5],font_size= 40,on_press = partial(self.addVariableItem,text.split("\n")[0]) ) ] 
            )
            self.popup.open()
        else:
            self.popup = MDDialog( title= "Clear or Delete this button space", text= "\nThis will reset the button to default...[Add Item]\n",size_hint=[0.25,None],
                buttons= [MDRaisedButton(text= "CLEAR/RESET",font_size= 48,md_bg_color= [0.255,0,0,1],on_press = partial(self.delItem,text.split("\n")[0]))] )
            self.popup.open()
    
    def delItem(self,btnId,*args):
        self.popup.dismiss(force= True)
        barcode = at.getButtonBarcode(btnId)
        if barcode in variableButtons.keys():
            del variableButtons[barcode]
            updateStoreInformation()
        at.updateTabId(btnId,"Add Item","")
        MDDialog( title= f"Tab ID: {btnId}\n\nReset Successful").open()
        self.innerBack()
    
    def addVariableItem(self,btnId,*args):
        self.popup.dismiss(force= True)
        self.on_leave()
        columnData = {}
        self.sv = ScrollView(size_hint=[1,None],pos_hint={'x':0,'y':0.2},scroll_type=['bars','content'],
                    do_scroll_x = False,size=(Window.width, Window.height*0.8),bar_width="10dp")
        grid = MDGridLayout(cols=2,pos_hint={"x":0,"y":0},size_hint=(0.8,None),adaptive_height= True,row_force_default =True,row_default_height=Window.height*0.12,spacing=[50,20],padding=[50,20,50,50])
        grid.bind(minimum_height=grid.setter('height'))
        grid.add_widget(MDFillRoundFlatButton(text= "Close/Go back",md_bg_color=[0.128,0.128,0.128,1],on_press = self.innerBack ))
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDLabel(text="Tab Button ID : ",size_hint=[1,1],halign="right",font_style="H6"))
        columnData['btnId']= MDLabel(text=btnId,size_hint=[1,1],halign="left",font_style="H6")
        grid.add_widget(columnData['btnId'])
        grid.add_widget(MDLabel(text="Display Name : ",size_hint=[1,1],halign="right",font_style="H6"))
        columnData["displayName"] = MDTextField(helper_text="Must be Only 16 Characters", helper_text_mode="on_error", required=True, max_text_length= 16, hint_text="Enter Item Display Name here...",font_size= fontsize['text'],size_hint=[1,1], )
        grid.add_widget(columnData["displayName"])
        grid.add_widget(MDLabel(text="Enter Barcode : ",size_hint=[1,1],halign="right",font_style="H6"))
        columnData["barcode"] = MDTextField(hint_text="Enter or Scan Barcode here...",required=True,font_size= fontsize['text'],size_hint=[1,1], )
        grid.add_widget(columnData["barcode"])
        grid.add_widget(MDLabel(text="Enter Name : ",size_hint=[1,1],halign="right",font_style="H6"))
        columnData["name"] = MDTextField(hint_text="Enter or Scan Barcode here...",required=True,font_size= fontsize['text'],size_hint=[1,1], )
        grid.add_widget(columnData["name"])
        for i in ["Department Category","Tax Category","Deposit Category"]:
            if i == "Department Category":
                dropdown1 = DropDown()
                for idx in inv.getCategory("Department_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown1.select(btn.text))
                    dropdown1.add_widget(btn)
                mainbutton1 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton1.bind(on_release=dropdown1.open)
                dropdown1.bind(on_select=lambda instance, x: setattr(mainbutton1, 'text', x))
                grid.add_widget(MDLabel(text=f"[b]{i} : [/b]",halign="right" ,font_style="H6",markup=True))
                columnData["department"] = mainbutton1
                grid.add_widget(columnData["department"])
            elif i == "Tax Category":
                dropdown2 = DropDown()
                for idx in inv.getCategory("Tax_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None],halign="left" ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
                    dropdown2.add_widget(btn)
                mainbutton2 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton2.bind(on_release=dropdown2.open)
                dropdown2.bind(on_select=lambda instance, x: setattr(mainbutton2, 'text', x))
                grid.add_widget(MDLabel(text=f"[b]{i} : [/b]",halign= "right",font_style="H6",markup=True))
                columnData["tax"] = mainbutton2
                grid.add_widget(columnData["tax"])
            elif i == "Deposit Category":
                dropdown3 = DropDown()
                for idx in inv.getCategory("Deposit_Category"):
                    btn = Button(text=f"{idx[2]}\n{idx[3]}", size_hint=[1,None] ,background_color=[0.150, 0.60, 1.0, 1.0])
                    btn.bind(on_release=lambda btn: dropdown3.select(btn.text))
                    dropdown3.add_widget(btn)
                
                mainbutton3 = Button(text='Select Category', size_hint=[1,1] )
                mainbutton3.bind(on_release=dropdown3.open)
                dropdown3.bind(on_select=lambda instance, x: setattr(mainbutton3, 'text', x))
                grid.add_widget(MDLabel(text=f"[b]{i} : [/b]",halign="right" ,font_style="H6",markup=True))
                columnData["deposit"] = mainbutton3
                grid.add_widget(columnData["deposit"] )
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDRaisedButton(text= "Add Shortcut",md_bg_color=[0.10,0.200,0.200,0.5],size_hint=[1,1],on_press = partial(self.addVariableItemConfirm,columnData )))
        self.sv.add_widget(grid)
        self.add_widget(self.sv)

    def addVariableItemConfirm(self,columnD,*args):
        columnData = {}
        for i in columnD.keys():
            columnData[i] = columnD[i].text.strip()
            if columnData[i] == 'Select Category': columnData[i] = ""
        if all([i!="" for i in columnData.values()]):
            variableButtons[columnData['barcode']] = {'barcode': columnData['barcode'], 
                        'name': columnData['name'], 'department': columnData['department'].split("\n")[0],
                        'purchase_price': 0, 'qty': 1, 'deposit': columnData['deposit'].split("\n")[0], 'deposit_value': 0,
                        'tax': columnData['tax'].split("\n")[0], 'tax_value': 0, 'discount': '', 'discountPromo': '', 'line_total': 0}
            updateStoreInformation()
            self.addItemConfirm(False,columnData['btnId'],columnData['displayName'],columnData['barcode'])
        else:
            MDDialog( title= "!!!  ERORR  !!!",text="Please check, all fields are required").open()


    def addBarcode(self,btnId,*args):
        self.popup.dismiss(force= True)
        self.on_leave()
        grid = MDGridLayout(cols=2,pos_hint={"x":0,"y":0.2},size_hint=(0.8,0.8), adaptive_height= True,row_force_default =True,row_default_height=100,spacing=[50,20],padding=[50,20,50,0])
        grid.add_widget(MDFillRoundFlatButton(text= "Close/Go back",on_press = self.innerBack,md_bg_color=[0.128,0.128,0.128,1]))
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDLabel(text="Tab Button ID : ",size_hint=[1,1],halign="right",font_style="H6"))
        grid.add_widget(MDLabel(text=btnId,size_hint=[1,1],halign="left",font_style="H6"))
        grid.add_widget(MDLabel(text="Item Display Name : ",size_hint=[1,1],halign="right",font_style="H6"))
        displayName = MDTextField(helper_text="Must be Only 16 Characters", helper_text_mode="on_error", required=True, max_text_length= 16, hint_text="Enter Item Display Name here...",font_size= fontsize['text'],size_hint=[1,1], )
        grid.add_widget(displayName)
        grid.add_widget(MDLabel(text="Enter Barcode : ",size_hint=[1,1],halign="right",font_style="H6"))
        barcode = MDTextField(hint_text="Enter or Scan Barcode here...",required=True,font_size= fontsize['text'],size_hint=[1,1], )
        grid.add_widget(barcode)
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="right",font_style="H6"))
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="right",font_style="H6"))
        grid.add_widget(MDLabel(text="",size_hint=[1,1],halign="right",font_style="H6"))
        grid.add_widget(MDRaisedButton(text= "Add Shortcut ",size_hint=[1,1],on_press = partial(self.addItemConfirm,True,btnId,displayName, barcode )))
        self.sv = grid
        self.add_widget(self.sv)

    def addItemConfirm(self,barcodeItem,btnId,displayName,barcode, *args,**kwargs):
        if barcodeItem:
            displayName = displayName.text.strip()
            barcode = barcode.text.strip()
            if inv.isBarcode(barcode) and displayName!="":
                at.updateTabId(btnId,displayName[:16],barcode)
                MDDialog( title= "Successfully Added").open()
                self.innerBack()
            else:
                MDDialog( title= "!!!  ERORR  !!!",text="It may be because Barcode was not found or Name Error\n\nPlease add Item from Inventory.\nAdd Item in inventory before adding it here.").open()
        else:
            at.updateTabId(btnId,displayName[:16],barcode[:13])
            MDDialog( title= "Successfully Added").open()
            self.innerBack()



class CashOutScreen(MDScreen):
    pass


