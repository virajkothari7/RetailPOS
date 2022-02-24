from kivy.metrics import dp, sp
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, BaseButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.picker import MDDatePicker

from kivyScripts.screenManager import sm, fontsize, Window
import databaseScripts.allTransactions as at
import databaseScripts.transactions as ts
import databaseScripts.inventory as inv
import databaseScripts.shifts as shifts
import pandas as pd
from datetime import datetime
from functools import partial
from copy import deepcopy
from mainFunc import endShift, shift, printer

class labelgrid(MDRelativeLayout):
    def __init__(self, **kw):
        super().__init__(**kw)

class ReportsScreen(MDScreen):
    layout = None
    data_T = None
    end_date = datetime.now().date()
    start_date = datetime(2000, 1, 1, 0, 0).date()
    data = None
    Col_Names = ['date_time','date','transaction_id','shift_id','barcode','name','department','purchase_price', 'sales_price','qty','deposit','deposit_value','tax','tax_value','discount_value','payment_type']

    def on_pre_enter(self, *args):
        self.data_T = ts.getData()
        self.data = pd.DataFrame(at.getData(),columns = self.Col_Names)
        self.data["date_time"] = pd.to_datetime(self.data['date_time'])
        self.data["date"] = pd.to_datetime(self.data['date']).dt.date
        self.data["DATE-RANGE"] = pd.to_datetime(self.data['date'])
        self.data['sales_price'] = self.data['qty'] * self.data['sales_price']

    def onPreLeave(self, *args):
        if self.layout:
            self.remove_widget(self.layout)
            self.layout = None

    def main_layout(self,*args,**kwargs):
        self.layout.add_widget(MDRaisedButton(text="Clear Dates",md_bg_color= [1,0,0,0.5],font_style="H6" ,pos_hint={"x":0.1,"y":0.85},size_hint=[0.125,0.1],on_press=partial(self.transactionslayoutRange,"Clear",None,layoutName=kwargs['layoutName'])))
        self.layout.add_widget(MDLabel(text="Select Starting Date :",font_style="H6",halign="right", pos_hint={"x":0.235,"y":0.85},size_hint=[0.2,0.1]))
        date_dialog = MDDatePicker(title="Start Date")
        date_dialog.bind(on_save=partial(self.transactionslayoutRange,"start_date",layoutName=kwargs['layoutName'],))
        self.layout.add_widget(MDRaisedButton(text=f"{self.start_date}",md_bg_color= [0.128,0.128,0.128,0.15],font_style="H6" ,pos_hint={"x":0.45,"y":0.85},size_hint=[0.15,0.1],on_press=date_dialog.open))
        self.layout.add_widget(MDLabel(text="Select Ending Date :",font_style="H6",halign="right",pos_hint={"x":0.625,"y":0.85},size_hint=[0.2,0.1]))
        date_dialog1 = MDDatePicker(title="End Date")
        date_dialog1.bind(on_save=partial(self.transactionslayoutRange,"end_date",layoutName=kwargs['layoutName']))
        self.layout.add_widget(MDRaisedButton(text=f"{self.end_date}",md_bg_color= [0.128,0.128,0.128,0.15],font_style="H6",pos_hint={"x":0.835,"y":0.85},size_hint=[0.15,0.1],on_press=date_dialog1.open))
        self.add_widget(self.layout)
        self.ids.spinner.active = False

    def chnageLabelColor(self,id,*args):
        self.ids.spinner.active = True
        for i in ["shiftReports","dateReports","departmentReports","productReports","allTransactions"]:
            self.ids[i].md_bg_color = [0.128,0.128,0.128,1]
            self.ids[i].text_color = [1,1,1,1]
        self.ids[id].md_bg_color = [0.128,0.128,0.128,0.35]
        self.ids[id].text_color = [0,0,0,1]
        self.onPreLeave()

    def shiftlayout(self,*args,**kwargs):
        self.chnageLabelColor("shiftReports")
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.125},size_hint=[1,0.74])

        data = self.data.copy() 
        data = data.rename(columns={"shift_id":"SHIFT ID","department":"DEPARTMENT",'sales_price':'Net_Sales','qty':"Net_QTY",'tax_value':"Net_Tax", 'deposit_value':"Net_Deposit",'discount_value':"Net_Discount"})
        try:
            #Printing Report
            group = data.groupby("SHIFT ID")
            try:j = int(kwargs['shiftId'].text.strip())
            except: j = shift["Shift No"]
            shiftDetails = shifts.getDataFromShiftID(j)
            shiftReport = "SHIFT Report".center(32)+"\n"+str(datetime.now()).center(32)+"\n"
            shiftReport += f"{'*'*32}\n\nSHIFT ID : {j}\nStart_DT : {shiftDetails[0][:-7]}\nEnd_DT : {shiftDetails[1][:-7]}\n{shiftDetails[2]}\n\nDEPARTMENT DETAILS"
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
            
            noSale = 0 
            cashOut = []
            cashOutTotal = 0
            for a in [[b[2],b[4]] for b in shifts.get_data_C() if b[1] == j ]:
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

            shiftDepartment = group.get_group(j).groupby("DEPARTMENT")[["Net_QTY","Net_Sales","Net_Tax","Net_Deposit","Net_Discount"]].sum().round(2)
            self.layout.add_widget(MDLabel(text="Department Details ; ",font_style= "H6", pos_hint={"x":0.015,"y":0.665}, size_hint=[0.25,0.1], ))
            self.layout.add_widget(MDLabel(text=f"SHIFT ID : {j}",font_style= "H6",md_bg_color=[0.128,0.128,0.128,0.5],halign="center", pos_hint={"x":0.35,"y":0.675}, size_hint=[0.3,0.115], ))
            
            svData = ScrollView(size_hint=[None,None],size=(Window.width*0.65, Window.height*0.5) ,pos_hint={'x':0.01,'y':0},bar_width='15px',scroll_type = ["bars", "content"])
            datastack = MDGridLayout(cols = 6, adaptive_height= True,size_hint=[1,None],spacing=[1,3],row_force_default =True,row_default_height=70,)
            datastack.bind(minimum_height=datastack.setter('height'))
            datastack.add_widget(MDLabel(text= "", size_hint=[1,1] ))
            for j in ["Net_QTY","Net_Sales","Net_Tax","Net_Dep.","Net_Disc."]:
                datastack.add_widget(MDLabel(text= f"[b]{j}[/b]",halign="center", markup=True,size_hint=[1,1] ))
            for i in shiftDepartment.index:
                datastack.add_widget(MDLabel(text=f"[b]{i}[/b]",markup=True,size_hint=[1.55,1],padding_x=5))
                for j in shiftDepartment.loc[i]:
                    datastack.add_widget(MDLabel(text= str(j),halign="center"))
               
            displayReport = shiftReport.split("\n\n")
            displayReport = "\n\n".join(displayReport[0:2])+"\n\n"+"\n".join(displayReport[2].split("\n")[-3:])+"\n\n"+"\n\n".join(displayReport[3:5])
            self.layout.add_widget(MDLabel(text=displayReport, pos_hint={"x":0.7,"y":0.02}, size_hint=[0.25,1], ))
            self.layout.add_widget(MDRaisedButton(text="Print\nReport",font_style="H6",anchor_x="center" ,pos_hint={"x":0,"y":0.815},size_hint=[0.09,0.185],on_press=partial(printer.printReciept,shiftReport)))
            svData.add_widget(datastack)
            self.layout.add_widget(svData)

        except Exception as e:
            MDDialog(title= "<<<< NO DATA FOUND >>>>>").open()
        
        textFld = MDTextField(hint_text ="Search by SHIFT ID",helper_text="Enter To Submit", helper_text_mode= "persistent",mode="fill", pos_hint={"x":0.29,"y":0.815}, size_hint=[0.2,0.1], )
        textFld.on_text_validate = partial(self.shiftlayout, shiftId=textFld )
        self.layout.add_widget(textFld)
        self.layout.add_widget(MDRaisedButton(text="REFRESH",font_style="H6",anchor_x="center" ,md_bg_color=[0,0.235,0,1],pos_hint={"x":0.115,"y":0.815},size_hint=[0.15,0.15], on_press= self.shiftlayout))
        self.layout.add_widget(MDRaisedButton(text="END SHIFT",font_style="H6",anchor_x="center" ,md_bg_color=[0.235,0,0,1],pos_hint={"x":0.515,"y":0.815},size_hint=[0.15,0.15],on_press = endShift ))
        self.add_widget(self.layout)
        self.ids.spinner.active = False

    def daylayout(self,*args,**kwargs):
        self.chnageLabelColor("dateReports")
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.125},size_hint=[1,0.74])
        try: kwargs['dates']
        except: 
            self.end_date = datetime.now().date()
            self.start_date = datetime.now().date()
        data = self.data[self.data['date']==self.start_date].copy()
        data = data.rename(columns={"shift_id":"SHIFT ID","department":"DEPARTMENT",'sales_price':'Net_Sales','qty':"Net_QTY",'tax_value':"Net_Tax", 'deposit_value':"Net_Deposit",'discount_value':"Net_Discount"})
        dataValues = data.groupby([data["DATE-RANGE"].dt.to_period('D'),"SHIFT ID","DEPARTMENT"])[["Net_QTY","Net_Sales","Net_Tax","Net_Deposit","Net_Discount"]].sum().round(2).reset_index()
        cols = dataValues.columns.values.tolist()
        
        #Building Printable Report 
        report = "DAY Report".center(32)+"\n"+str(datetime.now()).center(32)+"\n"
        group_df = data.groupby([data["DATE-RANGE"].dt.to_period('D')])
        for i in group_df.groups.keys():
            dayReport = f"\n{'#'*32}\n"+f"Date : {i}".center(32)
            dayReport += "\n\n" + group_df.get_group(i)[["Net_QTY","Net_Sales","Net_Tax","Net_Deposit","Net_Discount"]].sum().round(2).to_string() +"\n\n" # 
            for j in group_df.get_group(i).groupby("payment_type").groups.keys():
                dayReport+=  "    {:<12} {:>8}\n".format(j,group_df.get_group(i).groupby("payment_type").get_group(j).apply(lambda i: i['Net_Sales'] + i["Net_Tax"] + i["Net_Deposit"] ,axis=1).sum().round(2))
            group = group_df.get_group(i).groupby("SHIFT ID")
            for j in group.groups.keys():
                shiftDetails = shifts.getDataFromShiftID(j)
                shiftReport = f"{'*'*32}\n\nSHIFT ID : {j}\nStart_DT : {shiftDetails[0][:-7]}\nEnd_DT : {shiftDetails[1][:-7]}\n{shiftDetails[2]}\n"
                shiftReport += "DEPARTMENT DETAILS"
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
                
                noSale = 0 
                cashOut = []
                cashOutTotal = 0
                for a in [[b[2],b[4]] for b in shifts.get_data_C() if b[1] == j ]:
                    if a[0] == "NO SALE":
                        noSale += 1
                    else:
                        cashOut.append(f"  {a[0][:20]}   {a[1]}")
                        cashOutTotal += a[1]
                if cashOutTotal: 
                    shiftReport += "\nCASH-OUT DETAILS\n"+ '\n'.join(cashOut) + "\n" + f"TOTAL AMOUNT   {cashOutTotal}".rjust(24) + "\n"
                if noSale : shiftReport += f"\nNO SALE DRAWER OPEN   {noSale}\n"
            
                dayReport += "\n"+ shiftReport
            report += dayReport 
        report += "\n"+"#"*32+"\n"+"END OF REPORT".center(32)
        # print(report)
        self.layout.add_widget(MDRaisedButton(text="Print\nReport",font_style="H6",anchor_x="center" ,pos_hint={"x":0,"y":0.815},size_hint=[0.09,0.185],on_press=partial(printer.printReciept,report)))
                
        svData = ScrollView(size_hint=[None,None],size=(Window.width*1, Window.height*0.55) ,pos_hint={'x':0,'y':0},bar_width='15px',scroll_type = ["bars", "content"])
        datastack = MDGridLayout( cols = len(cols),adaptive_height= True,size_hint=[1.5,None],spacing=[1,3],row_force_default =True,row_default_height=80,  )
        datastack.bind(minimum_height=datastack.setter('height'))
        for i in cols: datastack.add_widget(MDLabel(text=i,font_style="H6",halign="center"))
        
        for i in dataValues.values.tolist():
            for j in i[:3]:
                datastack.add_widget(MDLabel(text=f"[b]{j}[/b]",markup=True,md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
            for j in i[3:]:
                datastack.add_widget(MDLabel(text=f"{j}",md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
        svData.add_widget(datastack)
        self.layout.add_widget(svData)
        self.layout.add_widget(MDLabel(text="*NOTE: Please only select Starting-Date for Day-Report.",pos_hint={"x":0.485,"y":0.74},size_hint=[0.515,0.1]))
        self.main_layout(layoutName='day')

    
    def departmentlayout(self,*args):
        self.chnageLabelColor("departmentReports")
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.125},size_hint=[1,0.74])
        
        data = self.data[self.data['date'].between(self.start_date,self.end_date)].copy()
        departmentgroup = data.rename(columns={"department":"DEPARTMENT"}).groupby(['DEPARTMENT',data["DATE-RANGE"].dt.to_period('Q')])
        departmentgroup = departmentgroup[['qty','sales_price','tax_value','discount_value']].sum().round(2).rename(columns={'sales_price':'Sales','qty':"QTY",'tax_value':"Tax", 'deposit_value':"Deposit",'discount_value':"Discount"})
        datavalue = departmentgroup.reset_index()
        
        cols = datavalue.columns.values.tolist()
        heading_grid = MDGridLayout(cols=len(cols),pos_hint={"x":0,"y":0.725},size_hint=[1,0.1],row_force_default= True,row_default_height=Window.height*0.11)
        heading_grid.add_widget(MDLabel(text=cols[0],font_style="H6",size_hint_x = None,width=Window.width*0.3,halign="center"))
        for i in cols[1:]: heading_grid.add_widget(MDLabel(text=i,font_style="H6",halign="center"))
        self.layout.add_widget(heading_grid)
        
        svData = ScrollView(size_hint=[None,None],size=(Window.width*1, Window.height*0.5) ,pos_hint={'x':0,'y':0},bar_width='15px',scroll_type = ["bars", "content"])
        datastack = MDGridLayout( cols = len(cols),adaptive_height= True,size_hint=[1,None],spacing=[1,3],row_force_default =True,row_default_height=80,  )
        datastack.bind(minimum_height=datastack.setter('height'))
        for i in datavalue.values.tolist():
            datastack.add_widget(MDLabel(text=f"[b]{i[0]}[/b]",markup=True,size_hint_x = None,width=Window.width*0.3,md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
            for j in i[1:]:
                datastack.add_widget(MDLabel(text=f"{j}",md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
        
        self.layout.add_widget(MDRaisedButton(text="Print\nReport",font_style="H6",anchor_x="center" ,pos_hint={"x":0,"y":0.815},size_hint=[0.09,0.185],on_press=partial(self.printDepartmentReport,data,datavalue)))
        svData.add_widget(datastack)
        self.layout.add_widget(svData)
        self.main_layout(layoutName = "department")

    def printDepartmentReport(self,data,*args):
        reportPrint = "Department Report".center(32)+"\n"+str(datetime.now()).center(32) +f"\n\n{'*'*32}"
        reportDict = {}
        group_df = data.rename(columns={"department":"DEPARTMENT"}).groupby(["DEPARTMENT",data["DATE-RANGE"].dt.to_period('Q')])
        for i in group_df.groups.keys(): #facet_row="variable")9
            x = group_df.get_group(i).rename(columns={'payment_type':'Payment Type','sales_price':'Sales','qty':'QTY','tax_value':'Tax', 'deposit_value':'Deposit','discount_value':'Discount'}).groupby(['Payment Type'])
            x = x[["QTY","Sales","Tax","Deposit","Discount"]].sum().round(2)
            z = x.sum(numeric_only=True, axis=0).rename(index={'QTY':'Q-Total_Qty','Sales':'Q-Total_Sales','Tax':'Q-Total_Tax','Deposit':'Q-Total_Deposit','Discount':'Q-Total_Discount'})
            x = x.unstack().to_string(header=False)
            try : reportDict[i[0]] += f"{i[0]}  {i[1]}\n\n{x}\n\n{z.to_string()}\n\n\n"
            except : reportDict[i[0]] = f"{i[0]}  {i[1]}\n\n{x}\n\n{z.to_string()}\n\n\n"
        for i in data.groupby(["department"])[['qty','sales_price','tax_value','deposit_value',"discount_value"]].sum().rename(columns={'qty':'Dept. Total Qty : ','sales_price':'Dept. Total Sales : ','tax_value':'Dept. Total Tax : ','deposit_value':'Dept. Total Deposit : ','discount_value':'Dept. Total Discount : '}).iterrows():
            try: name = " : " + inv.getNameFromId(i[0])
            except: name = ""
            reportPrint += f"\n\n{(i[0]+name).center(32)}\n\n{i[1].to_string()}\n\n\n{reportDict[i[0]]}{'*'*32}"
        # print(reportPrint)
        printer.printReciept(reportPrint+"\n*This are Net Calculation"+"END OF REPORT".center(32)  )

    def productlayout(self,*args,**kwargs):
        self.chnageLabelColor("productReports")
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.125},size_hint=[1,0.74])
        
        data = self.data[self.data['date'].between(self.start_date,self.end_date)].copy()
                
        try:
            if kwargs['refreshed']:
                d = pd.Series(["D","M","Q","Y"])
                groupedProduct = data.rename(columns={"barcode":"BARCODE"}).groupby(["BARCODE"]).get_group(kwargs['productName']).groupby([data["DATE-RANGE"].dt.to_period(d[kwargs['date']].values[0])])
                groupedProduct = groupedProduct[['qty','sales_price','discount_value']].sum().round(2).rename(columns={'qty':"Net_QTY",'discount_value':"Net_Discount",'sales_price':"Net_Sales"})
                total = groupedProduct.sum(numeric_only=True, axis=0).rename(index={"Net_QTY":"Total Net_Qty","Net_Sales": "Total Net_Sales",'Net_Discount':"Total Net_Discount",}).to_string()
                productReport = "Product Report".center(32)+"\n"+str(datetime.now()).center(32) +f"\n\nBarcode : {kwargs['productName']}\nNAME : {at.getNameFromBarcode(kwargs['productName'])}\n\n"
                productReport += groupedProduct.to_string()  +"\n\n"+total+"\n\n"+"END OF REPORT".center(32)
                # print(productReport)
                self.layout.add_widget(MDRaisedButton(text="Print\nReport",font_style="H6",anchor_x="center" ,pos_hint={"x":0,"y":0.815},size_hint=[0.09,0.185],on_press=partial(printer.printReciept,productReport)))
                self.layout.add_widget(MDLabel(text=f"[b]Barcode : \n{kwargs['productName']}\n\nNAME : \n{at.getNameFromBarcode(kwargs['productName'])}\n\n\n{total}[/b]",markup=True,halign="left", pos_hint={"x":0.015,"y":0.025},size_hint=[0.155,0.75]))
                groupedProduct[kwargs['graphCol']].plot.barh(title = kwargs['graphCol'] ).figure.savefig("./images/productGraph.png",bbox_inches = "tight")
                im = Image(source="./images/productGraph.png",keep_ratio=False,allow_stretch=True,pos_hint={"x":0.175,"y":0.025},size_hint=[0.47,0.7])
                im.reload()
                self.layout.add_widget(im)
        except Exception as e:
            pass
        self.layout.add_widget(MDLabel(text="Enter Item's Barcode : ",font_style="H6",halign="left", pos_hint={"x":0.65,"y":0.6},size_hint=[0.3,0.1]))
        txtfld = MDTextField(hint_text="Enter or Scan Barcode.",halign="right",mode="fill", pos_hint={"x":0.65,"y":0.445},size_hint=[0.3,0.1])
        self.layout.add_widget(txtfld)
        date =[MDCheckbox( pos_hint={'x':0.65,'y':0.26},group= "date", active= False, size_hint= [None, None], size= [sp(32), sp(32)] ),
                MDCheckbox( pos_hint={'x':0.75,'y':0.26},group= "date", active= False, size_hint= [None, None], size= [sp(32), sp(32)] ),
                MDCheckbox( pos_hint={'x':0.85,'y':0.26},group= "date", active= False, size_hint= [None, None], size= [sp(32), sp(32)] ) 
            ]
        dateLabel = [MDLabel(text="[b]Day[/b]",markup=True,halign="left", pos_hint={"x":0.685,"y":0.27},size_hint=[0.075,0.05]),
                    MDLabel(text="[b]Month[/b]",markup=True,halign="left", pos_hint={"x":0.785,"y":0.27},size_hint=[0.075,0.05]),
                    MDLabel(text="[b]Quarterly[/b]",markup=True,halign="left", pos_hint={"x":0.885,"y":0.27},size_hint=[0.075,0.05]),
                ]
        for i in date + dateLabel:
            self.layout.add_widget(i)
        date.append(MDCheckbox( group= "date", active= True, size_hint= [None, None], size= [sp(32), sp(32)] ))
        self.layout.add_widget(MDLabel(text="Sub-Group Dates : ",font_style="H6",halign="left", pos_hint={"x":0.65,"y":0.335},size_hint=[0.3,0.1]))
        self.layout.add_widget(MDLabel(text="Show Graph : ",font_style="H6",halign="left", pos_hint={"x":0.65,"y":0.15},size_hint=[0.15,0.1]))
        self.layout.add_widget(MDRaisedButton(text="QTY",font_style="H6",halign="left",on_press=partial(self.checkItem,txtfld,date,"Net_QTY") ,pos_hint={"x":0.685,"y":0.035},size_hint=[0.125,0.115]))
        self.layout.add_widget(MDRaisedButton(text="Sales",font_style="H6",halign="left",on_press=partial(self.checkItem,txtfld,date,"Net_Sales"), pos_hint={"x":0.85,"y":0.035},size_hint=[0.125,0.115]))
        self.layout.add_widget(MDRaisedButton(text="Look Up All Inventory Data",font_style="H6",anchor_x="center" ,md_bg_color=[0,0.235,0,1],pos_hint={"x":0.65,"y":0.7},size_hint=[0.3,0.125],on_press = self.currentInvScreen ))
        self.main_layout(layoutName='products')
    
    def checkItem(self,txtfld,date,colName,*args):
        if at.isBarcode(txtfld.text.strip()):
            date = [i.active for i in date  ]
            self.productlayout(productName=txtfld.text.strip(),graphCol = colName,date = date,refreshed=True)
        elif txtfld.text.strip():
            MDDialog(title="NO ITEM TRANSACTIONS FOUND").open()
        else:
            MDDialog(title="PLEASE SCAN OR ENTER ITEM BARCODE TO PROCEED").open()
              
    def transactionslayout(self,*args,**kwargs):
        self.chnageLabelColor("allTransactions")
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.125},size_hint=[1,0.74])
        
        svData = ScrollView(size_hint=[None,None], do_scroll_x = False,size=(Window.width*1, Window.height*0.525) ,pos_hint={'x':0,'y':0},bar_width='15px',scroll_type = ["bars", "content"])
        datastack = MDStackLayout(spacing =15 ,size_hint=[1,None],padding=[25,25])
        datastack.bind(minimum_height=datastack.setter('height'))
        
        heading_grid = MDGridLayout(cols=5,padding = [50,0],pos_hint={"x":0,"y":0.725},size_hint=[1,0.1],row_force_default= True,row_default_height=Window.height*0.11)
        heading_grid.add_widget(MDLabel(text="Date & Time",font_style="H6",halign="center"))
        heading_grid.add_widget(MDLabel(text="Shift ID",font_style="H6",halign="center"))
        heading_grid.add_widget(MDLabel(text="Transaction ID",font_style="H6",halign="center"))
        heading_grid.add_widget(MDLabel(text="Total Sale",font_style="H6",halign="center"))
        heading_grid.add_widget(MDLabel(text="Payment Type",font_style="H6",halign="center"))
        self.layout.add_widget(heading_grid)
        
        for i in self.data_T:
            if datetime.strptime(i[0].split(" ")[0],"%Y-%m-%d").date() <= self.end_date and datetime.strptime(i[0].split(" ")[0],"%Y-%m-%d").date() >= self.start_date:
                button= BaseButton(md_bg_color=[0,0,0,0.35],font_style="H4",size_hint=[1,None],on_press=partial(self.transactionPopup,i[-2],i[-1]))
                grid = MDGridLayout(cols=5,padding = [35,0],row_force_default= True,row_default_height=Window.height*0.11)
                grid.add_widget(MDLabel(text=f"{i[0]}",halign="center"))
                grid.add_widget(MDLabel(text=f"{i[1]}",halign="center"))
                grid.add_widget(MDLabel(text=f"{i[2]}",halign="center"))
                grid.add_widget(MDLabel(text=f"{i[3]}",halign="center"))
                grid.add_widget(MDLabel(text=f"{i[-3]}",halign="center"))
                button.add_widget(grid)
                datastack.add_widget(button)

        svData.add_widget(datastack)
        self.layout.add_widget(svData)
        self.main_layout(layoutName='transaction')
        
    def transactionPopup(self,receipt,products,*args):
        sm.current = "receipt_transactions"
        sm.get_screen("receipt_transactions").ids.recieptScreen.text = receipt
        prod = "#"*25 +"\n\n"
        for i in eval(products):
            for j in i.keys():
                prod += j.upper() + " : " + str(i[j]) +"\n"
            prod += "\n"+"#"*25 +"\n\n"
        sm.get_screen("receipt_transactions").ids.recieptScreenProd.text = prod

    def transactionslayoutRange(self,dateType,widget,date,*args,**kwargs):
        if dateType == 'end_date': self.end_date = date
        elif dateType == 'start_date': self.start_date = date
        else:
            self.end_date = datetime.now().date()
            self.start_date = datetime(2000, 1, 1, 0, 0).date()
        
        if kwargs["layoutName"]=="transaction":
            self.transactionslayout()
        elif kwargs["layoutName"]=="department":
            self.departmentlayout()
        elif kwargs["layoutName"]=="products":
            self.productlayout()
        elif kwargs["layoutName"]=="day":
            self.daylayout(dates=True)
    
    def currentInvScreen(self,*args):
        sm.current = "current_inventory"


class receiptScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.ids.printRButton.on_press = partial(printer.printReciept, self.ids.recieptScreen.text)
        self.ids.printRDButton.on_press = partial(printer.printReciept , self.ids.recieptScreen.text+"\n\n\n"+ self.ids.recieptScreenProd.text)
    

class currentInventoryScreen(MDScreen):
    layout = None

    def on_pre_enter(self, *args):
        self.layout = MDRelativeLayout(pos_hint={"x":0,"y":0.0075},size_hint=[1,0.85])
        cols = ["Name","Barcode","Department CategoryID","Purchase Price","Sales Price","Inventory Qty","Tax CategoryID","Deposit CategoryID"]
        df = pd.DataFrame( inv.getInventoryData(), columns=cols)
            
        svData = ScrollView(size_hint=[None,None],size=(Window.width*1, Window.height*0.85) ,pos_hint={'x':0,'y':0},bar_width='15px',scroll_type = ["bars", "content"])
        datastack = MDGridLayout( cols = len(cols),adaptive_height= True,size_hint=[1.7,None],spacing=[1,3],row_force_default =True,row_default_height=100, padding = [10,10,10,50] )
        datastack.bind(minimum_height=datastack.setter('height'))
        
        datastack.add_widget(MDLabel(text=cols[0],font_style="H6",size_hint_x = None,width=Window.width*0.3,halign="center"))
        for i in cols[1:]: datastack.add_widget(MDLabel(text=i,font_style="H6",halign="center"))
        
        for i in df.values.tolist():
            datastack.add_widget(MDLabel(text=f"[b]{i[0]}[/b]",markup=True,size_hint_x = None,width=Window.width*0.3,md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
            for j in i[1:]:
                datastack.add_widget(MDLabel(text=f"{j}",md_bg_color=[0.128,0.128,0.128,0.05],halign="center"))
        
        svData.add_widget(datastack)
        self.layout.add_widget(svData)
        self.add_widget(self.layout)

    def on_pre_leave(self, *args):
        self.remove_widget(self.layout)
