from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

sm = ScreenManager()

### font sizes
fontsize= {
            'button' : ((Window.width**2 + Window.height**2) / 16.5**4),
            'label'  : ((Window.width**2 + Window.height**2) / 16.25**4),
            'text'   : ((Window.width**2 + Window.height**2) / 18**4),
            'heading': ((Window.width**2 + Window.height**2) / 16**4),
        }

"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput

from kivymd.uix import dialog
from kivymd.uix import boxlayout

from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp

from functools import partial
from kivy.uix.dropdown import DropDown


from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRectangleFlatButton
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, RiseInTransition, NoTransition
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine


"""