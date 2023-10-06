import npyscreen
import os
from utils import utils
import main


class MainForm(npyscreen.FormBaseNew):


    def create(self):

        # self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = self.exit_application

        self.option = self.add(utils.TitleSelectOne, max_height=4, name="Select method",
                   values=["1. Load from config", "2. Login manually"], scroll_exit=True, kasher=self.option_selected)

    def option_selected(self):

        if "Login manually" in self.option.get_selected_objects()[0]:
            self.parentApp.switchForm("CredsForm")
        else:

            self.parentApp.switchForm("mainForm")


class CredsForm(npyscreen.ActionFormMinimal):
    def create(self):
        # self.parent_option = None
        # self.add(npyscreen.FixedText, value="You selected Option 2. Please enter your credentials:")
        self.username = self.add(npyscreen.TitleText, name="Apple ID:")
        self.password = self.add(utils.TitlePassword, name="Password:")

    def on_ok(self):
        username = utils.username_legit(self.username.value)
        password = utils.password_legit(self.password.value)

        if username and password:
            self.parentApp.switchForm("authForm")
        elif username and not password:
            npyscreen.notify_wait("Please enter a valid password.", title="Invalid Input")
        elif password and not username:
            npyscreen.notify_wait("Please enter a valid username.", title="Invalid Input")
        else:
            npyscreen.notify_wait("Please enter valid credentials.", title="Invalid Input")


class AuthForm(npyscreen.ActionFormMinimal):
    def create(self):
        # self.parent_option = None
        # self.add(npyscreen.FixedText, value="You selected Option 2. Please enter your credentials:")
        self.username = self.add(npyscreen.TitleText, name="2fa code:")

    def on_ok(self):
        username = self.username.value

        if len(username) == 6:
            self.parentApp.switchForm("mainForm")
        else:
            r = npyscreen.notify_yes_no("You did not enter an auth code with 6 digits.\n\nDo you still want to use it?", title="Invalid Input")
            if not r:
                return
            else:
                self.parentApp.switchForm("mainForm")


class PypushForm(utils.FormWithMenus):
    def create(self):

        # MultiLineAction: https://npyscreen.readthedocs.io/widgets-multiline.html
        self.option = self.add(utils.SelectOne, max_height=4,
            values=["1. Send iMessage", "2. Check for incoming messages"], scroll_exit=True, kasher=self.option_selected)

        #-----------

        self.initialize_menus()

        self.m1 = self.add_menu(name="Program Control")
        self.m1.addItemsFromList([
            ("Back to Main Screen", self.dummy_function),
            ("Exit Application", quit),
        ])

        self.m2 = self.add_menu(name="iMessage Handles")
        self.m2.addItemsFromList([
            ("Set Default Handle", self.dummy_function),
            ("Get all Handles", self.dummy_function),
        ])


        # self.m3 = self.m2.addNewSubmenu("A sub menu")
        # self.m3.addItemsFromList([
        #     ("Just Beep", self.dummy_function),
        # ])

    def dummy_function(self):

        pass

    def option_selected(self):

        pass

        # if "Login manually" in self.option.get_selected_objects()[0]:
        #     self.parentApp.switchForm("CredsForm")
        # else:
        #     self.parentApp.switchForm("mainForm")


class MyApplication(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Pypush CLI - not connected")
        self.addForm("CredsForm", CredsForm, name="Pypush CLI - login")
        self.addForm("authForm", AuthForm, name="Pypush CLI - login")
        self.addForm("mainForm", PypushForm, name="Pypush CLI - connected - Keagan.a.peterson@icloud.com")


if __name__ == "__main__":

    client = main.Client()

    app = MyApplication()
    app.run()
