import random
import math

from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, BaseButton
from kivymd.uix.selectioncontrol import MDSwitch

from kivyScripts.screenManager import sm, fontsize, Window

import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.inventory as inv
import databaseScripts.shifts as shifts

import pandas as pd
from datetime import datetime
from functools import partial
from copy import deepcopy

from mainFunc import * 


class Tab(MDGridLayout,MDTabsBase):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color=[0.128,0.128,0,0.25]


transactions = []
class RetailScreen(MDScreen):

    layout= None
    dialog = None
    label= None
    quickAdd = None
    clock= None
    sv = None
    recallLayout = None
    cart = pd.DataFrame(columns=['barcode','name',"department","purchase_price",'sell_price','qty','deposit','deposit_value','tax','tax_value','discount','discount_v','discountPromo','line_total'])
    scancode = []

    def on_pre_enter(self, *args):
        self.layout =MDRelativeLayout(pos_hint = {"x":0,"y":0},size_hint=[1,1],)
        buttons = [
            Button(text="[b]Recall\nTransaction[/b]"  , pos_hint = {"x":0.45,"y":0.9},markup=True,halign="center",background_color="#0096FF", size_hint = [0.14, 0.1], on_press = self.mainButton),
            Button(text= "[b]Suspend\nTransaction[/b]",pos_hint = {"x":0.59,"y":0.9},markup=True,halign="center",background_color="#0096FF", size_hint = [0.14, 0.1], on_press = self.mainButton),
            Button(text= "[b]Transactions[/b]" , pos_hint = {"x":0.305,"y":0.9},markup=True,halign="center",background_color=[0,0,1,0.75], size_hint = [0.145, 0.1], on_press = self.mainButton),
            Button(text= "[b] Cash/Pay Out [/b]" , pos_hint = {"x":0.73,"y":0.9},markup=True,halign="center", background_color="#39dfe8",size_hint = [0.135, 0.1],on_press=self.mainButton, ),
            Button(text= "[b]Quick-Add\nSettings[/b]" , pos_hint = {"x":0.865,"y":0.9},markup=True,halign="center",background_color="blue", size_hint = [0.135, 0.1], on_press = self.mainButton),
            
            Button(text= "[b]Delete\nTransaction[/b]", pos_hint = {"x":0,"y":0.875},markup=True,halign="center", background_color="red",size_hint = [0.125, 0.125], on_press = self.mainButton),
            Button(text= "[b]Price\nLookup[/b]",  pos_hint = {"x":0,"y":0.75},markup=True,halign="center",background_color="#FFFF00", size_hint = [0.125, 0.125], on_press = self.mainButton),
            Button(text= "[b]Misc.[/b]" , pos_hint = {"x":0,"y":0.615},markup=True,halign="center", background_color="orange",size_hint = [0.125, 0.135],on_press=partial(self.keyBarcode,"MISC_GENERAL") ),
            Button(text= "[b]Deli[/b]" , pos_hint = {"x":0,"y":0.48},markup=True,halign="center", background_color="purple",size_hint = [0.125, 0.135],on_press=partial(self.keyBarcode,"DELI_GENERAL") ),
            Button(text= "[b] (-)\nReturns [/b]" , pos_hint = {"x":0,"y":0.36},markup=True,halign="center", background_color="#54d4fc",size_hint = [0.125, 0.12], on_press = self.mainButton),
            Button(text= "[b]Re-Print\nReciept[/b]" , pos_hint = {"x":0,"y":0.2425},markup=True,halign="center", background_color="black",size_hint = [0.125, 0.1175], on_press = self.mainButton),
            Button(text= "[b] NO\nSALE [/b]" , pos_hint = {"x":0,"y":0.125},markup=True,halign="center", background_color="yellow",size_hint = [0.125, 0.1175], on_press = self.mainButton),
            
            Button(text= "[b]Credit/Debit[/b]",pos_hint = {"x":0.875,"y":0},markup=True,halign="center", background_color="darkgreen",size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,"Credit/Debit")),
            Button(text= "[b]EBT[/b]",  pos_hint = {"x":0.875,"y":0.1125},markup=True,halign="center",background_color="darkgreen", size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,"EBT")),
            Button(text= "[b]100[/b]",pos_hint = {"x":0.75,"y":0},markup=True,halign="center", background_color="lime",size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,100)),
            Button(text= "[b]50[/b]",  pos_hint = {"x":0.75,"y":0.1125},markup=True,halign="center",background_color="lime", size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,50)),
            Button(text= "[b]20[/b]",pos_hint = {"x":0.625,"y":0},markup=True,halign="center", background_color="lime",size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,20)),
            Button(text= "[b]10[/b]",  pos_hint = {"x":0.625,"y":0.1125},markup=True,halign="center",background_color="lime", size_hint = [0.125, 0.1125],on_press=partial(self.endTransaction,10)),
            Button(text= "[b]NEXT\nDOLLAR[/b]",  pos_hint = {"x":0.525,"y":0},markup=True,halign="center",background_color="lime", size_hint = [0.1, 0.225],on_press=partial(self.endTransaction,"Next")),
            Button(text= "[b]CASH[/b]",  pos_hint = {"x":0.425,"y":0},markup=True,halign="center",background_color="grey", size_hint = [0.1, 0.225],on_press=self.calculateCash),
        ]
        for i in buttons:
            self.layout.add_widget(i)
        
        colors=["orange","whitesmoke","brown","lightblue","yellow","green","violet","purple","maroon","blue","white","lightgreen"]
        random.seed(22)
        quickAdd = MDRelativeLayout(pos_hint = {"x":0.625,"y":0.225},md_bg_color=[0.128,0.128,0,0.25],size_hint=[0.375,0.675],)
        tabPanel = MDTabs(background_color=[0.128,0.128,0,0.75],tab_bar_height=Window.height*0.1,size_hint=[1,1],md_bg_color=[0.128,0.128,0,0.25])
        for num,i in enumerate(tabs):
            titleName = i[0] if i[0] else f"Tab {num+1}"
            i[1] = Tab(title=titleName,cols = 3,padding = 15,spacing=[7,3],pos_hint={"x":0,"y":0},size_hint=[1,1],)
            for n,j in  enumerate(at.getTab(f"Tab{num+1}")):
                # if n<12:
                if j[2] == "Add Item":
                    i[1].add_widget(
                            MDLabel(halign='center',valign='center',text= f"{j[2]}", text_size=(Window.width*0.1,Window.height*0.1), size_hint=[1,1]),
                        )
                else:
                    i[1].add_widget(
                            Button(halign='center',valign='center',background_color=random.choice(colors),text= f"{j[2]}", text_size=(Window.width*0.1,Window.height*0.1), size_hint=[1,1],on_press=partial(self.keyBarcode,j[3])),
                        )
            tabPanel.add_widget(i[1])
        quickAdd.add_widget(tabPanel)
        self.layout.add_widget(quickAdd)

        self.label = MDLabel(text= "", pos_hint = {"x":0.125,"y":0},size_hint = [0.3 , 0.225],markup=True,font_size=fontsize['heading'],halign="left",text_color=[0,0,0,1],theme_text_color= "Custom",md_bg_color=[0.128,0.128,0.128,0.1])
        self.layout.add_widget(self.label)

    def on_enter(self, *args):    
        self.add_widget(self.layout)
        self.update_table()

    def on_leave(self, *args):
        self.remove_widget(self.layout)
        for i in tabs:
            i[1] = None
        Window.unbind(on_keyboard = self.barcode_enter)

    def clear_working(self,*args):
        if self.sv:
            self.layout.remove_widget(self.sv)
            self.sv = None

    def update_time(self):
        self.ids.clock.text = datetime.now().strftime("[b]%Y/%m/%d[/b]\n%H:%M:%S")
    
    def update_label(self,st,tx,ttl):
        if all([st,ttl]):
            self.label.text = f"  Sub-Total  :      {st}\n{' '*11} Tax  :      {tx}\n{'-'*int(Window.width*0.0335)}\n[b]{' '*5}TOTAL   :      {ttl}[/b]"
        else:
            self.label.text = f"  Sub-Total  :  \n{' '*11} Tax  :  \n{'-'*int(Window.width*0.0335)}\n[b]{' '*5}TOTAL   :  [/b]"
    
    def barcode_enter(self,a,b,c,d,*args):
        if d is None:
            barcode= "".join(self.scancode)
            self.scancode.clear()
            self.add_cart(barcode,None)
        else:
            self.scancode.append(d) 
    
    def add_cart(self,barcode,priceValue,*args,**kwargs):
        if priceValue:
            item = deepcopy(variableButtons[barcode])
            item["discount_v"] = ""
            item["sell_price"] = kwargs["price"]
            self.cart = self.cart.append(item,ignore_index = True)
            # self.cart = pd.concat([self.cart,pd.Series(item).to_frame().T])
            self.update_table()
        elif inv.isBarcode(barcode):
            if  barcode in self.cart["barcode"].to_list():
                index = self.cart[self.cart["barcode"]==barcode].index
                self.cart.loc[index,"qty"] += 1
            else:
                item = dict(zip(["Name","Barcode","Department","Purchase Price","Selling Price","Quantity","Tax Category","Deposit Category"], inv.getItemFromBarcode(barcode.strip())))
                self.cart = self.cart.append({'barcode':item["Barcode"],'name':item["Name"],"department":item["Department"].split("\n")[0],"purchase_price":item["Purchase Price"],'sell_price':item["Selling Price"],
                        'qty':1,'deposit':item["Deposit Category"].split("\n")[0],'deposit_value':0,'tax':item["Tax Category"].split("\n")[0],'tax_value':0,'discount':"",'discount_v':"",'discountPromo':"",'line_total':0},ignore_index = True)
            self.update_table()
        else:
            if self.dialog: 
                self.dialog.dismiss(force=True)
                self.remove_widget(self.dialog)
                self.dialog = None
            self.dialog = MDDialog( title="NO ITEM FOUND",size_hint=[0.4,0.2],pos_hint={"x":0.175,"y":0.4})
            self.dialog.open()
        

    def get_rows(self):
        for i in self.cart.index:
            try:
                lineSubTotal = float(self.cart.loc[i,'qty'])*float(self.cart.loc[i,'sell_price'])
                lineTotal = lineSubTotal
            except: pass #need to add dialog box
            
            try:
                if inv.getValueFromId(self.cart.loc[i,'tax']) != "N\A":
                    tax_p =float(inv.getValueFromId(self.cart.loc[i,'tax']).strip("%"))/100
                    self.cart.loc[i,'tax_value'] = round(tax_p*lineSubTotal,2)
                    lineTotal += self.cart.loc[i,'tax_value'] 
            except: self.cart.loc[i,'tax_value'] = 0

            try:
                discTotal = ""
                taxadjust = ""
                # Qty doesn't affect discount, amount discount wil subtract value from linetotal and percentage discount uses qty and price as it makes difference
                if '%T' in self.cart.loc[i,'discount_v']:
                    disc_p =float(self.cart.loc[i,'discount_v'].strip("%T"))/100
                    discTotal = lineSubTotal*disc_p
                elif '%' in self.cart.loc[i,'discount_v']:
                    disc_p =float(self.cart.loc[i,'discount_v'].strip("%"))/100
                    discTotal = lineTotal*disc_p
                    taxadjust = self.cart.loc[i,'tax_value']*disc_p
                elif 'T' in self.cart.loc[i,'discount_v']:
                    disc =float(self.cart.loc[i,'discount_v'].strip("T"))
                    discTotal = disc
                elif self.cart.loc[i,'discount_v']:
                    disc =float(self.cart.loc[i,'discount_v'])
                    discTotal = disc + (tax_p*disc)
                    taxadjust = tax_p*disc
                
                if isinstance(discTotal,float):
                    if discTotal <= lineTotal:
                        lineTotal -= discTotal
                        self.cart.loc[i,'discount'] = discTotal 
                        if isinstance(taxadjust,float):
                            self.cart.loc[i,'tax_value'] = round(self.cart.loc[i,'tax_value'] -taxadjust,2)
                            self.cart.loc[i,'discount'] = round(discTotal -taxadjust,2)
                    elif float(self.cart.loc[i,'qty']) < 0 and lineTotal<0 and (discTotal <= lineTotal*-1):
                        discTotal = discTotal * -1
                        lineTotal -= discTotal
                        self.cart.loc[i,'discount'] = discTotal 
                        if isinstance(taxadjust,float):
                            taxadjust = taxadjust * -1
                            self.cart.loc[i,'tax_value'] = round(self.cart.loc[i,'tax_value'] -taxadjust,2)
                            self.cart.loc[i,'discount'] = round(discTotal -taxadjust,2)
                    else:
                        self.cart.loc[i,'discount_v']="" 
                        self.cart.loc[i,'discount'] = ""
                        MDDialog( title= "Discount Value can not exceed Total Sale of the Product").open()
            except: pass
            
            try:
                if inv.getValueFromId(self.cart.loc[i,'deposit']) != "N\A":
                    self.cart.loc[i,'deposit_value'] = round(float(inv.getValueFromId(self.cart.loc[i,'deposit']))*float(self.cart.loc[i,'qty']) ,2)
                    lineTotal += self.cart.loc[i,'deposit_value']
            except: self.cart.loc[i,'deposit_value'] = 0
            
            self.cart.loc[i,'line_total'] = round(lineTotal,2)
        
        rows = []
        for i in self.cart.to_dict('records'):
            rows.append((
                f" {i['barcode']}\n {i['name'][:50]}",
                str(i['qty']),
                str(i['sell_price']),
                str(i['discount']),
                str(i['tax_value']) if i['tax_value'] != 0 else "",
                str(i['deposit_value']) if i['deposit_value'] !=0 else "" ,
                str(i['line_total'])
            ))
        
        tax=round(self.cart["tax_value"].sum(),2)
        total = round(self.cart["line_total"].sum(),2)
        self.update_label(round(total-tax,2),tax,total)
        
        return rows 

    def update_table(self,*args):
        self.clear_working()
        if self.dialog: 
            self.dialog.dismiss(force=True)
            self.remove_widget(self.dialog)
            self.dialog = None
        Window.bind(on_keyboard = self.barcode_enter)
        self.sv = ScrollView(size_hint=[None,None], size=(Window.width*0.5, Window.height*0.665) ,pos_hint={'x':0.125,'y':0.235},bar_width='8px',scroll_type = ["bars", "content"],scroll_distance=25)
        datatable = MDGridLayout( cols = 8,adaptive_height= True,size_hint=[2.15,None],spacing=[1,3],row_force_default =True,row_default_height=130,  )
        datatable.bind(minimum_height=datatable.setter('height'))
        columns = ["Description","Qty","Price","Disc./Coupon\nAmount","Tax\nAmount","Deposit\nAmount","Line Total"]
        datatable.add_widget(MDLabel(text= f"[b]{columns[0]}[/b]",size_hint_x = None,width=Window.width*0.27,markup= True,halign="center",md_bg_color = [0.204,0.204,0.204,0]))
        for i in columns[1:-1]:
            datatable.add_widget( MDLabel(text= f"[b] {i} [/b]",markup= True,halign="center",md_bg_color = [0.204,0.204,0.204,0]))
        datatable.add_widget(MDLabel(text= f"[b]{columns[-1]}[/b]",size_hint_x = None,width=Window.width*0.15,markup= True,halign="center",md_bg_color = [0.204,0.204,0.204,0]))
        datatable.add_widget(MDLabel(text= ""))
        for row_num, i in enumerate(self.get_rows()):
            datatable.add_widget(MDLabel(text= f"{i[0]}",size_hint_x = None,width=Window.width*0.27,markup= True,halign="left",md_bg_color = [0.204,0.204,0.204,0.15]))    
            for col_num, j in enumerate(i[1:-1]):
                datatable.add_widget(BaseButton(text= str(j),anchor_x="center",size_hint=[1,1],font_size=sp(24),md_bg_color= [0.204,0.204,0.204,0.15],on_press = partial(self.on_row_press,row_num,columns[col_num+1])))    
            datatable.add_widget(MDLabel(text= f"{i[-1]}",size_hint_x = None,width=Window.width*0.15,markup= True,halign="center",md_bg_color = [0.204,0.204,0.204,0.15]))    
            datatable.add_widget(MDRaisedButton(text="Delete",md_bg_color=[0.256,0,0,0.5],on_press=partial(self.del_row,row_num),size_hint=[1,1]))
        self.sv.add_widget(datatable)
        self.layout.add_widget(self.sv)      
        
    def on_row_press(self,row_num,col,widget,*args):
        columns = {'Qty':'qty','Price':'sell_price'}#,"Tax\nAmount":'tax_value',"Deposit\nAmount":'deposit_value'}
        if col in "Disc./Coupon\nAmount":
            Window.unbind(on_keyboard = self.barcode_enter)
            self.clear_working()
            row = self.cart.iloc[row_num]
            self.sv = MDGridLayout(cols=2,size_hint=[0.5,0.665],pos_hint={'x':0.125,'y':0.235},padding = [35,50],spacing=[30,30],row_force_default =True,row_default_height=Window.height*0.125,
                        col_force_default =True,col_default_width=Window.width*0.225,)
            self.sv.add_widget(MDLabel(text=f"{col}",font_style="H6"))
            textInput = MDTextField(hint_text="Amount or Percentage Disc.",text=f"{row['discount']}",font_size='18sp',size_hint=[1,1],mode="fill")
            self.sv.add_widget(textInput)
            self.sv.add_widget(MDLabel(text="Is this Discount\nTaxable ? ",font_style="H6"))
            switch = MDSwitch(active = False, width= 200, size_hint=[1,1])
            self.sv.add_widget(switch)
            self.sv.add_widget(MDLabel(text="For Percentage discount add % at end, like 2.5% or add amount as it in text field\n * Unverified Calculations"))
            self.sv.add_widget(MDLabel(text="Slider on right means Taxable.\nWeather discount is Taxable or not, see proper guidlines."))
            self.sv.add_widget(MDRaisedButton(text="Back",font_style="H5",on_press = self.update_table, md_bg_color=[0.200,0.200,0.200,0.5]))
            self.sv.add_widget(MDRaisedButton(text="Add Discount",size_hint=[1,1],font_style="H6", on_press=partial(self.discountAdd,row_num,'discount_v',textInput,switch)))
            self.layout.add_widget(self.sv)
        elif col in columns.keys():
            if self.dialog:
                self.remove_widget(self.dialog)
                self.dialog = None
            self.dialog = MDDialog( title=f"Enter updated {col} below...",type="custom", content_cls= NumPad(),size_hint=[0.4,0.95],
                    buttons=[MDRaisedButton(text="ENTER",on_press=partial(self.dialogRowText,row_num,columns[col]),font_size = fontsize['button'])] )
            self.dialog.open()
    
    def dialogRowText(self,row_num,column,*args):
        self.dialog.dismiss(force=True)
        if self.dialog.content_cls.ids.textField.text:
            try: value = float(self.dialog.content_cls.ids.textField.text)
            except: value = None
            if value: 
                self.cart.iloc[row_num,self.cart.columns.get_loc(column)] = value
            self.update_table()
    
    def discountAdd(self,row_num,column,textInput,switch,widget):
        text = textInput.text.strip()
        x = ""
        try: 
            x = float(text)
        except:
            try:
                x = float(text.strip("%"))
            except: 
                if self.dialog:
                    self.remove_widget(self.dialog)
                    self.dialog = None
                self.dialog = MDDialog( title=f"Error adding discount",md_bg_color=[1,0,0,0.5],)
                self.dialog.open()
        if isinstance(x,float):
            text = text+"T" if switch.active else text
            self.cart.iloc[row_num,self.cart.columns.get_loc(column)] = text
            self.update_table()




    def del_row(self,row_num,*args):
        self.cart = self.cart.drop(self.cart.index[row_num])
        self.cart = self.cart.reset_index(drop=True)
        self.update_table()

    def mainButton(self,widget,*args):
        button = widget.text
        if button == "[b]Delete\nTransaction[/b]":
            self.cart.drop(self.cart.index,inplace=True)
            self.update_table()
        elif button == "[b]Suspend\nTransaction[/b]" and len(self.cart):
            transactions.append(self.cart.copy(deep=True))
            self.cart.drop(self.cart.index,inplace=True)
            self.update_table()
        elif button == "[b]Recall\nTransaction[/b]":
            current = False
            if len(self.cart): 
                transactions.append(self.cart.copy(deep=True))
                self.cart.drop(self.cart.index,inplace=True)
                current = True
                self.update_table()
            if len(transactions): 
                self.clear_working()
                self.sv = ScrollView(size_hint=[None,None],size=(Window.width*0.5, Window.height*0.665) ,pos_hint={'x':0.125,'y':0.235},scroll_type=['bars','content'], do_scroll_x = False,bar_width="10dp")
                layout = MDGridLayout(cols=2,size_hint_x=1,size_hint_y=None,row_force_default =True,row_default_height=Window.height*0.125,col_force_default =True,col_default_width=Window.width*0.23, padding=[15,10], spacing=20)
                layout.bind(minimum_height=layout.setter('height'))
                layout.add_widget(MDRaisedButton(text="Back",font_style="H6",on_press = self.update_table, md_bg_color=[0.200,0.200,0.200,0.5]))
                layout.add_widget(MDLabel(text="[b]Suspended Transactions[/b]",font_style="H6",markup=True,size_hint=[1,1]))
                for i in range(len(transactions)):
                    if current and (i+1 == len(transactions)):  
                        layout.add_widget( Button(text=f"Current\nTransaction", background_color="#0096FF",on_press=partial(self.recallTransaction,i) ))
                    else:
                        layout.add_widget( Button(text=f"Suspended\nTransaction #{i+1}", background_color="#0096FF",on_press=partial(self.recallTransaction,i) ))
                if len(transactions)%2: layout.add_widget(MDLabel(text="",font_style="H5",markup=True,size_hint=[1,1]))
                layout.add_widget( MDRaisedButton(text="Clear All\nTransactions",font_style="Subtitle1",on_press = self.cleartransactions ))
                self.sv.add_widget(layout)    
                self.layout.add_widget(self.sv)
        elif button == "[b]Price\nLookup[/b]":
            Window.unbind(on_keyboard = self.barcode_enter)
            self.clear_working()
            self.sv = MDRelativeLayout(size_hint=[0.5,0.665],pos_hint={'x':0.125,'y':0.235},)
            textInput = MDTextField(hint_text=f"Enter Barcode...",mode="fill",pos_hint={'x':0.05,'y':0.7},size_hint=[0.6,0.2],on_text_validate = self.lookUpEnter )
            self.sv.add_widget(textInput)
            self.sv.add_widget(MDRaisedButton(text="Back",font_style="H6",on_press = self.update_table,pos_hint={'x':0.05,'y':0.06}, md_bg_color=[0.200,0.200,0.200,0.5]))
            self.layout.add_widget(self.sv)
        elif button == "[b] (-)\nReturns [/b]" and len(self.cart):
            self.cart["qty"] = self.cart["qty"]*(-1)
            self.update_table()
            MDDialog( title= f"Qty of scanned items has been converted to Negative(-), please process returns as usual transaction\n\n\nNote: This button needs to be only pressed at end, after scanning all items. Make sure all items qty are Negative if you processing this whole transaction as Return-Transaction").open()
        elif button == "[b]Re-Print\nReciept[/b]":
            if printer.printer is None: printer.connectPrinter() 
            if printer.printer:
                try: printer.printReciept(ts.getLastRecipt()[0])
                except: pass
            if printer.printer is None: MDDialog( title= "Printer Error: Printer might not be attached to the system.\n\nPlease Check...").open()
        elif button == "[b] Cash/Pay Out [/b]" :
            Window.unbind(on_keyboard = self.barcode_enter)
            self.clear_working()
            self.sv = MDGridLayout(cols=2, size_hint=[0.5,0.664],pos_hint={'x':0.125,'y':0.235},padding=50,spacing= 30,row_force_default =True, row_default_height=Window.height*0.125,
                            col_force_default =True,col_default_width=Window.width*0.22,)
            self.sv.add_widget(MDLabel(text="Enter Name : "))
            name = MDTextField(hint_text="Enter Name...",font_size= 42,mode="fill",required=True)
            self.sv.add_widget(name)
            self.sv.add_widget(MDLabel(text="Enter Invoice No : "))
            InvNo = MDTextField(hint_text="Enter Invoice No...",font_size= 42,mode="fill")
            self.sv.add_widget(InvNo)
            self.sv.add_widget(MDLabel(text="Enter Amount : "))
            amount = MDTextField(hint_text="Enter Amount...",font_size= 42,mode="fill",required=True,input_filter = "float")
            self.sv.add_widget(amount)
            self.sv.add_widget(MDRaisedButton(text="Back",font_style="H5",on_press = self.update_table, md_bg_color=[0.200,0.200,0.200,0.5]))
            self.sv.add_widget(Button(text="Cash/Pay Out",background_color="#39dfe8",font_size=50,on_press = partial(self.cashOut,name,InvNo,amount)))
            self.layout.add_widget(self.sv)
        elif button == "[b]Transactions[/b]":
            sm.current = "retail_transactions"
        elif button == "[b]Quick-Add\nSettings[/b]":
            sm.current = "buttons"
        elif button == "[b] NO\nSALE [/b]":
            shifts.add_data_C(datetime.now(),shift["Shift No"],"NO SALE","NO SALE",0)
            if printer.printer and printerSettings["Cash_Drawer"]: 
                try: printer.printer.cashdraw(2)
                except: pass

    def recallTransaction(self,num,*args):
        self.cart = transactions[num].copy(deep=True)
        transactions.pop(num)
        self.update_table()

    def cleartransactions(self,*args):
        transactions.clear()
        self.update_table()

    def lookUpEnter(self,widget,*args):
        barcode = widget.text.strip()
        if inv.isBarcode(barcode):
            self.sv.add_widget( MDLabel(text = f"{barcode}\n{inv.getNameFromBarcode(barcode)}\n\nPrice : {inv.getSellPriceFromBarcode(barcode)}",halign = "center",
                            pos_hint={'x':0.05,'y':0.175},size_hint=[0.9,0.6], font_style = "H6" ) )
            self.sv.add_widget(MDRaisedButton(text="Add\nItem",font_style="H6",on_press = partial(self.add_cart,barcode,None),pos_hint={'x':0.7,'y':0.7},size_hint=[0.265,0.25]))
        elif barcode == "stop_current_app_quit()":
            quit()

    def cashOut(self,name,invNo,amount,*args):
        name = name.text.strip()
        invNo = invNo.text.strip()
        amount = amount.text.strip()
        if name and amount:
            shifts.add_data_C(datetime.now(),shift["Shift No"],name,invNo,amount)
            if printer.printer and printerSettings["Cash_Drawer"]: 
                try: printer.printer.cashdraw(2)
                except: pass
            self.update_table() 
        else:
            MDDialog( title="!!!!!   ERROR  !!!!",text="Please Type in Name and Amount as they are required",md_bg_color=[1,0,0,0.3]).open()
            

    def keyBarcode(self,obj,*args):
        barcode = obj
        if barcode in variableButtons.keys():
            if variableButtons[barcode]['tax']!= "":
                if self.dialog: 
                        self.remove_widget(self.dialog)
                        self.dialog = None
                self.dialog = MDDialog( title="Enter amount below...",type="custom", content_cls= NumPad(),size_hint=[0.4,0.95],
                        buttons=[MDRaisedButton(text="ENTER",on_press=partial(self.dialogText,barcode),font_size = fontsize['button'])] )
                self.dialog.open()
            else:
                if self.dialog: 
                        self.remove_widget(self.dialog)
                        self.dialog = None
                self.dialog = MDDialog( title="Please add Tax category\n\n\nNeed to add tax category using [Qucik-Add Settings] until then it won't work")
                self.dialog.open()
        else: self.add_cart(barcode,None)

    def dialogText(self,barcode,*args):
        self.dialog.dismiss(force=True)
        if self.dialog.content_cls.ids.textField.text:
            try: value = float(self.dialog.content_cls.ids.textField.text)
            except: value = None
            if value: self.add_cart(barcode,True,price=value)
    
    def calculateCash(self,*args):
        if round(self.cart["line_total"].sum(),2)>0:
            if self.dialog: 
                    self.remove_widget(self.dialog)
                    self.dialog = None
            self.dialog = MDDialog( title="Enter Cash Given...",type="custom", content_cls= NumPad(),size_hint=[0.4,0.95],
                    buttons=[MDRaisedButton(text="ENTER",on_press=partial(self.endTransaction,"Cash"),font_size = fontsize['button'])] )
            self.dialog.open()
        elif round(self.cart["line_total"].sum(),2)<=0 :
            self.endTransaction(round(self.cart["line_total"].sum(),2))


    def endTransaction(self,value,*args,**kwargs):
        tax=round(self.cart["tax_value"].sum(),2)
        total = round(self.cart["line_total"].sum(),2)
        if len(self.cart):
            if value=="EBT" or value=="Credit/Debit":
                self.saveTransactions(total,tax,self.cart.copy(deep=True),value)
                self.cart.drop(self.cart.index,inplace=True)
                self.update_table()
                if self.dialog:
                        self.remove_widget(self.dialog)
                        self.dialog = None
                self.dialog = MDDialog( title=f"""Software is not attached to a Card-Reader Machine\n\nPlease Make Sure to finish Transaction on Card Reader and Charge on Card\n\n\nThis transaction is saved as Card-Transaction in Transactions\n\nAmount : \n{' '*25}{round(total,2)}""",
                                    size=[Window.width*0.5,Window.height*0.6],size_hint=[None,None],)
                self.dialog.open()
            elif value=="Cash":
                self.dialog.dismiss(force=True)
                if self.dialog.content_cls.ids.textField.text:
                    try: value = float(self.dialog.content_cls.ids.textField.text)
                    except: value = None
            elif value=="Next": value  = math.ceil(total)
            
            if isinstance(value,int) or isinstance(value,float):
                if value >= total:
                    self.saveTransactions(total,tax,self.cart.copy(deep=True),"CASH")
                    self.cart.drop(self.cart.index,inplace=True)
                    self.update_table()
                    if total>0:
                        if self.dialog:
                            self.remove_widget(self.dialog)
                            self.dialog = None
                        self.dialog = MDDialog( title=f"""\n Sub-Total  :      {round(total-tax,2)}\n{' '*11} Tax  :      {tax}\n{'-'*int(Window.width*0.0265)}\n[b]{' '*5}TOTAL   :      {total}\n\n{' '*7}CASH   :      {value}\n\n\nCHANGE : \n\n{' '*25}{round(value-total,2)}[/b]""",
                                            size=[Window.width*0.4,Window.height*0.7],size_hint=[None,None],)
                        self.dialog.open()
                    else:
                        if self.dialog:
                            self.remove_widget(self.dialog)
                            self.dialog = None
                        self.dialog = MDDialog( title=f"""\n Sub-Total  :      {round(total-tax,2)}\n{' '*11} Tax  :      {tax}\n{'-'*int(Window.width*0.0265)}\n[b]{' '*5}TOTAL   :      {total}\n\n\n\nCASH : \n\n{' '*25}{total}[/b]""",
                                            size=[Window.width*0.4,Window.height*0.7],size_hint=[None,None],)
                        self.dialog.open()
                else:
                    if self.dialog:
                            self.remove_widget(self.dialog)
                            self.dialog = None
                    self.dialog = MDDialog( title="ERROR\n\nCash Amount given is less than total please accept Total Cash-Amount",md_bg_color=[1,0,0,0.5],
                                        size=[Window.width*0.4,Window.height*0.7],size_hint=[None,None],)
                    self.dialog.open()
                
        

    def saveTransactions(self,total,tax,trans,payment):
        detailDict = {}
        detailDict['date_time'] = datetime.now()
        detailDict['shift_id'] = shift["Shift No"]
        detailDict['transaction_id'] = detailDict['date_time'].strftime('%Y%m%d%H%M%S%f')[:-5]
        detailDict['total_sale'] = total
        detailDict['total_amount'] = round(total-tax,2)
        detailDict['tax_amount'] = tax
        detailDict['payment_type'] = payment
        detailDict['products'] = trans.to_dict('records')
        detailDict['receipt'] = generateReceipt(detailDict['transaction_id'],detailDict['products'],detailDict['total_amount'] ,round(self.cart["deposit_value"].sum(),2),detailDict['tax_amount'],detailDict['total_sale'])
        ts.addData(detailDict)
        
        if printer.printer is None: printer.connectPrinter() 
        # Printing Receipt Here if on printeer Connected and Auto Print True
        if printer.printer and printerSettings["Print_Reciept"]: printer.printReciept(detailDict['receipt'])
        if printer.printer and printerSettings["Cash_Drawer"]: 
            try: printer.printer.cashdraw(2)
            except: pass
            


class retailTransactions(MDScreen):
    svData = None
    
    def on_pre_enter(self, *args):
        self.ids.printReciept.on_press = self.printReciept 
        
        label = MDLabel( text= "",size_hint=[0.425,0.1],markup=True,pos_hint = {'x':0.05,'y':0.78})
        self.add_widget(label)
        self.ids["recieptHead"]=label

        data_T = ts.getTransactionView()
        self.svData = ScrollView(size_hint=[None,None], do_scroll_x = False,size=(Window.width*0.5, Window.height*0.88) ,pos_hint={'x':0.5,'y':0.01},bar_width='8px',scroll_type = ["bars", "content"])
        datastack = MDStackLayout(spacing =25 ,size_hint=[0.98,None],padding=[25,25],md_bg_color=[0.128,0.128,0.128,0.5],)
        datastack.bind(minimum_height=datastack.setter('height'))
        for i in data_T:
            datastack.add_widget(MDRaisedButton(text = f"Date&Time :  {i[0][:-7]}\nTran. ID       :  {i[1]}   \n[b]Amount      :  {i[2]}[/b]",padding=[50,0],md_bg_color=[0,0,1,0.25],font_size=36,height = 150,size_hint=[1,None],on_press=partial(self.dataClick,i)))
        self.svData.add_widget(datastack)
        self.add_widget(self.svData)
        
        try: self.dataClick(data_T[0])
        except : pass
        
    def on_leave(self, *args):
        self.remove_widget(self.svData)
        self.remove_widget(self.ids.recieptHead)
        
    
    def dataClick(self,tran, *args):
        self.ids.reciept.text = tran[-1] 
        self.ids.recieptHead.text = f"[b]Date&Time :  {tran[0]}\nTran. ID    :  {tran[1]}\nAmount    :  {tran[2]}[/b]"
        
    def printReciept(self,**kwargs):
        if printer.printer is None: printer.connectPrinter() 
        if printer.printer: printer.printReciept(self.ids.reciept.text)
        if printer.printer is None: MDDialog( title= "Printer Error: Printer might not be attached to the system.\n\nPlease Check...").open()
   

        
class NumPad(MDStackLayout,MDBoxLayout):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.spacing = "15dp"
        self.size_hint_y = None
        self.height = Window.height*0.675
        layout = MDGridLayout(cols=3,orientation="rl-tb", size_hint_x=1,row_force_default =True,row_default_height=Window.height*0.0875,spacing=10)
        layout.add_widget(Button(text="<",background_color="maroon",font_size=50,on_press=self.addDigit))
        layout.add_widget(MDLabel(text=""))
        layout.add_widget(Button(text="Clear",background_color="red",font_size=50,on_press=self.addDigit))
        for i in range(9,0,-1):
            layout.add_widget(Button(text=str(i),font_size=50,on_press=self.addDigit))
        layout.add_widget(Button(text=".",font_size=50,on_press=self.addDigit))
        layout.add_widget(Button(text="0",font_size=50,on_press=self.addDigit))
        layout.add_widget(Button(text="( - )",background_color="slategrey",font_size=50,on_press=self.addDigit))
        self.add_widget(layout)

    def addDigit(self,widget,*args):
        if widget.text == "Clear":
            self.ids.textField.text = ""
        elif widget.text == "( - )":
            self.ids.textField.text = "-"+self.ids.textField.text
        elif widget.text == "<":
            self.ids.textField.text = self.ids.textField.text[:-1]
        else: self.ids.textField.text += widget.text

