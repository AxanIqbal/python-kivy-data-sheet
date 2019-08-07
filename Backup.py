import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text="username: "))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)

        self.add_widget(Label(text="password: "))
        self.password = TextInput(multiline=False, password=True)
        self.add_widget(self.password)

        self.login = Button(text="Login")
        self.login.bind(on_press=self.pressed)
        self.add_widget(self.login)

        self.forgot = Button(text="forgot")
        self.add_widget(self.forgot)

    def pressed(self, instance):
        username = self.username.text
        password = self.password.text
        print(f"username = {username}\npassword = {password}")
        self.username.text = ''
        self.password.text = ''


class MainApp(App):
    def build(self):
        return MyGrid()


if __name__ == "__main__":
    MainApp().run()
