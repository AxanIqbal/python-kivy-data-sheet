import os.path
from json import dumps
from os.path import join
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen, NoTransition
import progressspinner
from kivymd.theming import ThemeManager
from kivy.storage.jsonstore import JsonStore

url = "https://project-001-af863.firebaseio.com/"
folder = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(folder + "/Kv/loadingpopup.kv")


class Test(Screen):
    def asd(self, a, s):
        print(f"a = {a} b = {s} root = {self.width}")

    pass


class LogIn(Screen, EventDispatcher):
    web_api_key = StringProperty()  # From Settings tab in Firebase project

    # Firebase Authentication Credentials - what developers want to retrieve
    refresh_token = ""
    localId = ""
    idToken = ""
    # Properties used to send events to update some parts of the UI
    login_success = BooleanProperty(False)  # Called upon successful sign in
    sign_up_msg = StringProperty()
    sign_in_msg = StringProperty()
    email_exists = BooleanProperty(False)
    email_not_found = BooleanProperty(False)

    debug = True
    popup = Factory.LoadingPopup()
    popup.background = folder + "/Image/transparent_image.png"

    data_dir = App().user_data_dir
    store = JsonStore(join(data_dir, 'storage.json'))

    check_box = False

    def on_pre_enter(self, *args):
        try:
            self.store.get('credentials')['remember_password']
        except KeyError:
            if self.debug:
                print("Key Error Store")
            self.check_box = False
        else:
            self.check_box = self.store.get('credentials')['remember_password']

    def on_login_success(self, *args):
        """Overwrite this method to switch to your app's home screen.
        """
        print("Logged in successfully", args)
        if self.ids['rempass'].active:
            print("activated")
        self.check_box = self.ids['rempass'].active
        self.store.put('credentials', remember_password=self.check_box)
        print(self.store.get('credentials'))
        screen_manager = self.parent
        screen_manager.transition = NoTransition()
        screen_manager.current = "MainFrame"

    def on_web_api_key(self, *args):
        """When the web api key is set, look for an existing account in local
        memory.
        """
        # Try to load the users info if they've already created an account
        self.refresh_token_file = App.get_running_app().user_data_dir + "/refresh_token.txt"
        if self.debug:
            print("Looking for a refresh token in:", self.refresh_token_file)
        if os.path.exists(self.refresh_token_file):
            self.load_saved_account()

    def sign_up(self, email, password):
        """If you don't want to use Firebase, just overwrite this method and
        do whatever you need to do to sign the user up with their email and
        password.
        """
        if self.debug:
            print("Attempting to create a new account: ", email, password)
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.web_api_key
        signup_payload = dumps(
            {"email": email, "password": password, "returnSecureToken": "true"})

        UrlRequest(signup_url, req_body=signup_payload,
                   on_success=self.successful_login,
                   on_failure=self.sign_up_failure,
                   on_error=self.sign_up_error)

    def successful_login(self, urlrequest, log_in_data):
        """Collects info from Firebase upon successfully registering a new user.
        """
        self.hide_loading_screen()
        self.refresh_token = log_in_data['refreshToken']
        self.localId = log_in_data['localId']
        self.idToken = log_in_data['idToken']
        self.save_refresh_token(self.refresh_token)
        self.login_success = True
        if self.debug:
            print("Successfully logged in a user: ", log_in_data)

    def sign_up_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to log in was
        invalid.
        """
        self.hide_loading_screen()
        self.email_exists = False  # Triggers hiding the sign in button
        print(failure_data)
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        # Check if the error msg is the same as the last one
        if msg == self.sign_up_msg:
            # Need to modify it somehow to make the error popup display
            msg = " " + msg + " "
        self.sign_up_msg = msg
        if msg == "Email exists":
            self.email_exists = True
        if self.debug:
            print("Couldn't sign the user up: ", failure_data)

    def sign_up_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign up Error: ", args)

    def sign_in(self, email, password):
        """Called when the "Log in" button is pressed.

        Sends the user's email and password in an HTTP request to the Firebase
        Authentication service.
        """
        if self.debug:
            print("Attempting to sign user in: ", email, password)
        sign_in_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.web_api_key
        sign_in_payload = dumps(
            {"email": email, "password": password, "returnSecureToken": True})

        UrlRequest(sign_in_url, req_body=sign_in_payload,
                   on_success=self.successful_login,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error)

    def sign_in_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to create an
        account was invalid.
        """
        self.hide_loading_screen()
        self.email_not_found = False  # Triggers hiding the sign in button
        print(failure_data)
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        # Check if the error msg is the same as the last one
        if msg == self.sign_in_msg:
            # Need to modify it somehow to make the error popup display
            msg = " " + msg + " "
        self.sign_in_msg = msg
        if msg == "Email not found":
            self.email_not_found = True
        if self.debug:
            print("Couldn't sign the user in: ", failure_data)

    def sign_in_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign in error", args)

    def reset_password(self, email):
        """Called when the "Reset password" button is pressed.

        Sends an automated email on behalf of your Firebase project to the user
        with a link to reset the password. This email can be customized to say
        whatever you want. Simply change the content of the template by going to
        Authentication (in your Firebase project) -> Templates -> Password reset
        """
        if self.debug:
            print("Attempting to send a password reset email to: ", email)
        reset_pw_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key=" + self.web_api_key
        reset_pw_data = dumps({"email": email, "requestType": "PASSWORD_RESET"})

        UrlRequest(reset_pw_url, req_body=reset_pw_data,
                   on_success=self.successful_reset,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error)

    def successful_reset(self, urlrequest, reset_data):
        """Notifies the user that a password reset email has been sent to them.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully sent a password reset email", reset_data)
        self.sign_in_msg = "Reset password instructions sent to your email."

    def save_refresh_token(self, refresh_token):
        """Saves the refresh token in a local file to enable automatic sign in
        next time the app is opened.
        """
        if self.debug:
            print("Saving the refresh token to file: ", self.refresh_token_file)
        with open(self.refresh_token_file, "w") as f:
            f.write(refresh_token)

    def load_refresh_token(self):
        """Reads the refresh token from local storage.
        """
        if self.debug:
            print("Loading refresh token from file: ", self.refresh_token_file)
        with open(self.refresh_token_file, "r") as f:
            self.refresh_token = f.read()

    def load_saved_account(self):
        """Uses the refresh token to get the user's idToken and localId by
        sending it as a request to Google/Firebase's REST API.

        Called immediately when a web_api_key is set and if the refresh token
        file exists.
        """

        print(self.parent.parent)

        if not self.check_box:
            if self.debug:
                print("Save Password is Unchecked Going Back")
            return

        if self.debug:
            print("Attempting to log in a user automatically using a refresh token.")
        self.load_refresh_token()
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.web_api_key
        refresh_payload = dumps({"grant_type": "refresh_token", "refresh_token": self.refresh_token})
        UrlRequest(refresh_url, req_body=refresh_payload,
                   on_success=self.successful_account_load,
                   on_failure=self.failed_account_load,
                   on_error=self.failed_account_load)

    def successful_account_load(self, urlrequest, loaded_data):
        """Sets the idToken and localId variables upon successfully loading an
        account using the refresh token.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully logged a user in automatically using the refresh token")
        self.idToken = loaded_data['id_token']
        self.localId = loaded_data['user_id']
        self.login_success = True

    def failed_account_load(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Failed to load an account.", args)

    def display_loading_screen(self, *args):
        self.popup.color = self.tertiary_color
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()

    def show_password(self, field, button):
        """
        Called when you press the right button in the password field
        for the screen TextFields.

        instance_field: kivy.uix.textinput.TextInput;
        instance_button: kivymd.button.MDIconButton;

        """

        # Show or hide text of password, set focus field
        # and set icon of right button.
        field.password = not field.password
        field.focus = True
        button.icon = "eye" if button.icon == "eye-off" else "eye-off"


class MainFrame(Screen):
    pass


class MyApp(App):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Blue'
    title = "Data Entry"

    def build(self):
        return Builder.load_file("main.kv")

    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.transition = NoTransition()
        screen_manager.current = screen_name


MyApp().run()
