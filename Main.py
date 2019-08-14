from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition

from kivymd.theming import ThemeManager
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.ripplebehavior import CircularRippleBehavior
from kivymd.utils.cropimage import crop_image

url = "https://project-001-af863.firebaseio.com/"


class Test(Screen):
    def asd(self, a, s):
        print(f"a = {a} b = {s} root = {self.width}")

    pass


class LogIn(Screen):
    def test(self):
        print("at login")

    pass


class MainFrame(Screen):
    pass


gui = Builder.load_file("main.kv")


class MyApp(App):
    theme_cls = ThemeManager()

    def build(self):
        self.title = "Project 001"
        return gui

    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.transition = NoTransition()
        screen_manager.current = screen_name

    def test(self):
        print("at myapp")


if __name__ == "__main__":
    MyApp().run()
