# -*- coding: utf-8 -*-

from urwid import MainLoop, ExitMainLoop
from nobix.ui import MainWindow, LoginWindow

class Application(object):

    def __init__(self):
        pass

    def run(self):
        """Run commander"""
        self.parse_args()
        self.init_logger()

        self.create_ui()
        self.create_remote_api()

        self._run()

        self.finalize()

    def parse_args(self):
        print("Parsing args...")

    def init_logger(self):
        print("Initiating logger...")

    def create_ui(self):
        print("Creating user interface...")
        self.main_window = MainWindow(self)
        self.login_window = LoginWindow(self, get_user=self.get_user)

    def create_remote_api(self):
        print("Creating remote api ...")

    def _run(self):
        self.loop = MainLoop(self.main_window, input_filter=self.input_filter)
        self.login_window.show()

        self.loop.run()

    def exit(self):
        raise ExitMainLoop()

    def finalize(self):
        print("Finalizing")

    def get_user(self, username, password):
        if username == "18" and password == "123":
            return True
        return False

    def input_filter(self, keys, raw):
        if 'f10' in keys:
            self.exit()
        return keys
