import time
from os.path import join

from kivy.app import App
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen


class LogIn(Screen):
    def __init__(self, **kw):

        super().__init__(**kw)
        print(self.ids)
        for key, val in self.ids.items():
            print("key={0}, val={1}".format(key, val))
        self.username = ''
        self.password = ''

    def log_in(self):
        self.username = self.ids.login_username.text
        self.password = self.ids.login_password.text

        data_dir = App().user_data_dir
        store = JsonStore(join(data_dir, 'storage.json'))
        try:
            store.get('credentials')['username']
        except KeyError:
            self.username = ""
        else:
            self.ids.login_username.text = store.get('credentials')['username']

        try:
            store.get('credentials')['password']
        except KeyError:
            self.password = ""
        else:
            self.ids.login_password.text = store.get('credentials')['password']

    def test(self):
        AppScreen.store.put('credentials', username=self.username, password=self.password)


class LoadingScreen(Screen):
    pass


class WindowManager(ScreenManager):
    pass


app = Builder.load_file("main.kv")


# class LogIn(FloatLayout):
#     data_dir = App().user_data_dir
#     store = JsonStore(join(data_dir, 'storage.json'))
#
#     def loading_screen(self):
#         self.parent.current = 'LoadingScreen'
#
#     def test(self):
#         print("pressed")
#
#     pass


# class LoadingScreen(FloatLayout):
#     def __init__(self):
#         print("on loading")
#
#     def show_popup(self):
#         print("on loading")
#         self.pop_up = Factory.PopupBox()
#         self.pop_up.update_pop_up_text('Running some task...')
#         self.pop_up.open()


class AppScreen(ScreenManager):
    data_dir = App().user_data_dir
    store = JsonStore(join(data_dir, 'storage.json'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def login(self):
        username = self.login_username.text
        password = self.login_password.text
        AppScreen.store.put('credentials', username=username, password=password)


class MainApp(App):
    def build(self):
        return app


if __name__ == "__main__":
    MainApp().run()
