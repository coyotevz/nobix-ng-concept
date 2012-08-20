# -*- coding: utf-8 -*-

import urwid

class MainWindow(urwid.Frame):

    def __init__(self, app):
        self.app = app
        self.__super.__init__(urwid.Filler(urwid.Text("<Text Widget>")))
