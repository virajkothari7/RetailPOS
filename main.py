######################    Import Kivy Libraries  ###################
import os 
from kivy.config import Config
Config.set('kivy', 'log_dir', f"{os.getcwd()}/logsKivy")
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'log_maxfiles', 50)
Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'window_icon', './images/cash-register-g87e120a86_640.png')
# Config.set('graphics','borderless',0)# 1 for making this app only visible
# Config.set('graphics','fullscreen','auto') # Will us this if running in Main or Second full-screen
# Config.set('graphics', 'position', 'custom')
# Config.set('graphics', 'left', 0)
# Config.set('graphics', 'top',  0)
# Config.set('graphics', 'width', 960)
# Config.set('graphics', 'height', 540)
# Config.set('graphics', 'resizable', 0)

Config.set('input', 'mouse', 'mouse,disable_multitouch')


from datetime import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, RiseInTransition, NoTransition
from kivy.uix.button import Button

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel

from kivyScripts.inventoryScreen import InventoryScreen
from kivyScripts.storeScreen import StoreInformation
from kivyScripts.reportsScreen import ReportsScreen, receiptScreen, currentInventoryScreen
from kivyScripts.retailAdditonalScreens import CashOutScreen, buttonSettings
from kivyScripts.retailScreen import RetailScreen,  retailTransactions
from kivyScripts.settingsScreen import SettingsScreen
from kivyScripts.screenManager import sm

import databaseScripts.shifts as sf
from mainFunc import updateStoreInformation, endShift, shift, printerSettings, printer


def update_time(self):
    sm.get_screen("retail").update_time()


class MainScreen(Screen):
    printButton = None
    shiftLabel = None

    def on_pre_enter(self, *args):
        self.shiftLabel = MDLabel(text=f"Shift No: {shift['Shift No']}",md_bg_color=[0.128,0.128,0.128,0.2],halign="center",font_style="H6",size_hint=[0.195,0.13],pos_hint={"x":0.1375,"y":0.715} )
        self.printButton = Button(text= "[b]Print Recipt : ON[/b]" if printerSettings["Print_Reciept"] else "[b]Print Recipt : OFF[/b]", pos_hint = {"x":0.1375,"y":0.5375},markup=True,halign="center",background_color="lime" if printerSettings["Print_Reciept"] else "red", size_hint=[0.195,0.135],on_press= self.printOnOff )
        self.cashDrawer = Button(text= "[b]Cash Drawer\n\nCONNECTED[/b]" if printerSettings["Cash_Drawer"] else "[b]Cash Drawer\n\nNOT-CONNECTED[/b]", pos_hint = {"x":0.1375,"y":0.35},markup=True,halign="center",background_color="lime" if printerSettings["Cash_Drawer"] else "red", size_hint=[0.195,0.15])
        self.add_widget(self.printButton)
        self.add_widget(self.shiftLabel)
        self.add_widget(self.cashDrawer)

    def on_leave(self, *args):
        self.remove_widget(self.printButton)
        self.remove_widget(self.shiftLabel)
        self.remove_widget(self.cashDrawer)

    def update(self):
        self.on_leave()
        self.on_pre_enter()

    def printOnOff(self,*args):
        printerSettings["Print_Reciept"] = not printerSettings["Print_Reciept"]
        self.update()


class loginShift(Screen):
    def startShift(self,*args):
        shift["Shift Names"] = self.ids.shiftNames.text.strip()
        shift["Shift StartTime"] = str(datetime.now())
        shift["Shift No"] = sf.nextShiftId()
        sf.addData(shift["Shift StartTime"],"",shift["Shift No"],shift["Shift Names"],"")
        updateStoreInformation()
        sm.current = "main"


class posApp(MDApp):
    def build(self):
        self.title = "Retail-POS System"

        sm.transition = RiseInTransition()
        sm.add_widget(loginShift(name="login_shift"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(InventoryScreen(name="inventory"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(RetailScreen(name="retail"))
        sm.add_widget(CashOutScreen(name="cashout"))
        sm.add_widget(StoreInformation(name="storeinformation"))
        sm.add_widget(buttonSettings(name="buttons"))
        sm.add_widget(retailTransactions(name="retail_transactions"))
        sm.add_widget(receiptScreen(name="receipt_transactions"))
        sm.add_widget(currentInventoryScreen(name="current_inventory"))
        sm.add_widget(SettingsScreen(name="settings"))

        Clock.schedule_interval(update_time,1)
        printer.connectPrinter()

        if shift["Shift StartTime"] != "":
            endShift()
        else:
            sm.current="login_shift"

        return sm


if __name__ == '__main__':
    posApp().run()

