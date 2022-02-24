from kivy.uix.button import Button

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton

from kivyScripts.screenManager import sm, fontsize, Window

from mainFunc import data, updateStoreInformation



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
            layout.add_widget(MDLabel( text = i+" : " ,font_size = fontsize['text']))
            self.label[i] = MDLabel( text = f"{data[i]}",font_size = fontsize['text']) 
            layout.add_widget(self.label[i])
            self.storeDict[i] = MDTextField(max_text_length= 32,multiline=True,helper_text= "Must be less than 32 characters",font_size = fontsize['text'])
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
  