from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton

import os

from kivyScripts.screenManager import sm, fontsize, Window

from mainFunc import data, updateStoreInformation

# Kivy's bundled default font (Roboto) has no Arabic glyphs, so any field
# meant to hold Arabic text needs an explicit font that does - otherwise
# the manager can type it in fine (the character data is stored correctly
# either way) but can't actually read back what they typed on this screen,
# and it would show as empty boxes here even though it still prints
# correctly on receipts (the printer renders Arabic in its own firmware,
# independent of this on-screen font).
#
# Path is relative to the current working directory, not derived from
# __file__ - matching how every other asset path in this app works (e.g.
# "./images/..." in main.py/posapp.kv). __file__ can't be trusted to sit
# next to a real "fonts/" folder once this module is running from inside a
# PyInstaller-frozen bundle (its .py/.pyc may be packed into an archive
# rather than existing as a loose file on disk), whereas main.py already
# os.chdir()s to the app's own install folder before anything else runs,
# so a plain relative path here always resolves correctly in both dev and
# packaged builds.
_ARABIC_FONT = os.path.join("fonts", "NotoSansArabic-Regular.ttf")



class StoreInformation(MDScreen):
    storeDict = {}
    label = {}
    dialog = None
    layout = None
    
    def on_pre_enter(self):
        self.add_widget(Button(pos_hint = {"x":0,"y":0},size_hint=[ 0.15,  0.125], text= "[b]Back[/b]", markup = True, font_size = fontsize['button'],
        on_press = self.on_leave))
        self.add_widget(MDLabel( text = "[b][u]Previous Changes[/u][/b]",size_hint= [0.25,0.1],pos_hint = {"x":0.35,"y":0.758},font_size=fontsize['label'], markup =True ))
        self.add_widget(MDLabel( text = "[b][u]New Changes[/u][/b]",size_hint=[0.25,0.1],pos_hint = {"x":0.70,"y":0.758},font_style="Subtitle1", markup =True ))
        self.add_widget(MDToolbar(title=" Store Information ",md_bg_color= [0.128,0.128,0.128,1],anchor_title= "center",size_hint_x=  1,size_hint_y= 0.135 ,pos_hint = {"x":0,"y":0.865}))
        self.add_widget(MDRaisedButton(text=" Submit Changes ",on_press = self.submit,font_style="H5", font_size=fontsize['button'],pos_hint = {"x":0.45,"y":0.035}))
        self.add_widget(MDRaisedButton(text=" RESET ",on_press = self.reset,pos_hint = {"x":0,"y":0.805},md_bg_color=[0.255,0,0,1]))
        self.buildLayout()

    def on_leave(self,*args):
        self.clear_widgets()
        sm.current = "main"
        
    def buildLayout(self):
        layout = MDGridLayout(cols=3, row_force_default =True, row_default_height=Window.height*0.09, size_hint_x=0.8,size_hint_y=0.6 ,pos_hint = {"x":0.1,"y":0.165 })
        for i in data.keys():
            isArabicField = "arabic" in i.lower()
            layout.add_widget(MDLabel( text = i+" : " ,font_size = fontsize['text']))
            self.label[i] = MDLabel( text = f"{data[i]}",font_size = fontsize['text'])
            self.storeDict[i] = MDTextField(max_text_length= 32,multiline=True,helper_text= "Must be less than 32 characters",font_size = fontsize['text'])
            if isArabicField:
                # Must be set AFTER construction, not as a constructor kwarg:
                # MDLabel's own __init__ binds font_style -> update_font_style,
                # which runs during init and unconditionally overwrites
                # font_name with the current theme's font for font_style
                # ("Body1" by default here) - silently undoing a font_name
                # passed in the constructor. Setting it here, after that
                # already ran, is what actually sticks.
                self.label[i].font_name = _ARABIC_FONT
                self.storeDict[i].font_name = _ARABIC_FONT
            layout.add_widget(self.label[i])
            layout.add_widget(self.storeDict[i])
        self.layout = layout
        self.add_widget(layout)
        
    
    def refreshScreen(self,*args):
        self.remove_widget(self.layout)
        self.storeDict = {}
        self.label = {}
        self.layout = None
        self.buildLayout()

    def submit(self,*args):
        if all([i.text.strip() == "" for i in self.storeDict.values()]):
            pass
        else:
            self.dialog = MDDialog(
                size_hint = [0.5, 0.2],
                pos_hint = {"x":0.25,"y":0.4},
                title="Proceed with saving the changes ?",
                buttons=[MDRaisedButton(text="Yes",on_press =self.submitConfirm ,font_size = fontsize['button'])],
            )
            self.dialog.open()
    
    def closeDialog(self,*args):
        self.dialog.dismiss(force=True)

    def submitConfirm(self,*args):
        self.closeDialog()
        for key,value in self.storeDict.items():
            if value.text.strip() == "":
                continue
            data[key] = value.text.strip()[:32]
            
        updateStoreInformation()
        self.refreshScreen()
    
    def reset(self,*args):
        if not self.dialog is None:
            self.remove_widget(self.dialog)
            self.dialog =None
        self.dialog = MDDialog( size_hint = [0.5, 0.2], pos_hint = {"x":0.25,"y":0.4}, 
            title="Reset Store Information ?",
            buttons=[MDFlatButton(text="No",on_press =self.closeDialog ),
                MDRaisedButton(text="Yes",on_press =self.resetConfirm ) ],)
        self.dialog.open()
        
    def resetConfirm(self,*args):
        self.closeDialog()
        for i in data.keys():
            data[i] = ""
        updateStoreInformation()
        self.refreshScreen()
  