import os,sys
from kivymd.app import MDApp
from kivymd.uix.card import MDCard,BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.screen import Screen

sys.path.append(r'../core')
print(sys.version)
from core.core import GModule,GModuleVN

class ResultGUI(BoxLayout):
    pass

class PopupWindow(BoxLayout):
    label = ObjectProperty(None)

class ChooserGUI(BoxLayout):
    layout = ObjectProperty(None)
    filechooser = ObjectProperty(None)
    inf = None

    def on_selected(self,filename):
        try:
            name = filename[0]
            extension = os.path.basename(name)[-3:]
            show = PopupWindow()
            
            if  extension != 'mp3' and extension != 'wav' and extension != 'mp4':
                show = PopupWindow()
                show.label.text = "Invalid file type"
                alert =  Popup(title = "Invalid", content = show, size_hint = (None,None), size = (400,400))
                alert.open()
                return
            if not os.path.isdir(name):
                self.inf.communicate(name,os.path.basename(name),[220,22,100])
                
        except:
            pass

class Interface:
    def __init__(self, MDcontainer) :
        self.MDcontainer = MDcontainer
        self.path = None
        self.music = None

    def communicate(self,path,name,color):
        self.MDcontainer.path_name_label.text = name
        self.MDcontainer.path_name_label.color = color
        self.path = path
        self.music = SoundLoader.load(path)

class MDLayout(Widget):
    file_chooser_button = ObjectProperty(None)
    path_name_label = ObjectProperty(None)
    predict_button = ObjectProperty(None)
    audio_player_button = ObjectProperty(None)
    playing = False
    module = GModule()
    module_vn = GModuleVN();
    def __init__(self):
        super(MDLayout,self).__init__()
        self._interface = Interface(self)
        
    def play_audio(self):
        if not self._interface.path:
            return

        if self._interface.music:
            if self.playing:
                self._interface.music.stop()
                self.playing = False
            else:
                self._interface.music.play()
                self.playing = True

    def press(self):
        show = ChooserGUI()
        show.inf = self._interface
        popup_window = Popup(title = "Browse", content = show, size_hint = (None,None), size = (600,600))
        popup_window.open()

    def predict(self):
        if not self._interface.path:
            return

        screen = Screen()
        show = ResultGUI()
        self.module.get(self._interface.path)
        re = self.module.predict()
        data = list(zip([ele[0][0] for ele in re],[ele[1] for ele in re]))
        data.sort(reverse = True,key = lambda x:x[1])
        print(data)
        table = MDDataTable(
            pos_hint = {'center_x':0.5, 'center_y':0.5},
            column_data = [("Genre", dp(30)),("Similarity", dp(30))],
            row_data = data
        )
        show.add_widget(table)

        popup_window = Popup(title = 'result',content = show, size_hint = (None,None), size = (400,400))
        popup_window.open()
    
    def predict_2(self):
        if not self._interface.path:
            return

        screen = Screen()
        show = ResultGUI()
        self.module_vn.get(self._interface.path)
        re = self.module_vn.predict()
        data = list(zip([ele[0] for ele in re],[ele[1] for ele in re]))
        data.sort(reverse = True,key = lambda x:x[1])
        table = MDDataTable(
            pos_hint = {'center_x':0.5, 'center_y':0.5},
            column_data = [("Genre", dp(30)),("Similarity", dp(30))],
            row_data = data
        )
        show.add_widget(table)

        popup_window = Popup(title = 'result',content = show, size_hint = (None,None), size = (400,400))
        popup_window.open()

class MDguiApp(MDApp):
    def build(self):
        
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        return MDLayout()

if __name__ == '__main__':
    MDguiApp().run()