# -*- coding: utf-8 -*-

import time

from urwid import (
    WidgetWrap, Columns, Pile, Edit, Filler, Divider, Overlay,
    LineBox, Frame, Text
)

from nobix.ui import Password


class LoginWindow(WidgetWrap):

    signals = ['login', 'logout']

    def __init__(self, app, extra=None, get_user=None, max_time=30):
        self.app = app

        self.extra = extra
        self.get_user = get_user
        self.max_time = max_time
        self._create_widgets()

        self._out_count = 0
        self._evt_time = 0
        self._parent = None
        self._key_sig_id = None
        self._timeout_sig_id = None

        self.__super.__init__(self.login_widget)

    def _create_widgets(self):
        self._create_login_widget()

        if self.extra:
            widget = Frame(LineBox(self.login_widget), footer=self.extra)
        else:
            widget = LineBox(self.login_widget)

        self.overlay = Overlay(
            widget, None,
            'center', ('relative', 100),
            'middle', ('relative', 100),
        )

    def _create_login_widget(self):
        self.username_entry = Edit(align='right')
        self.username_entry.keypress = self._username_keypress
        self.password_entry = Password(align='right')
        self.password_entry.keypress = self._password_keypress

        username_row = Columns([
            ('fixed', 10, Text("Usuario:", align='right')),
            ('fixed', 10, self.username_entry),
        ])

        password_row = Columns([
            ('fixed', 10, Text("Clave:", align='right')),
            ('fixed', 10, self.password_entry),
        ])

        self.pile = Pile([
            username_row,
            Divider(),
            password_row,
        ], focus_item=0)

        self.login_widget = Filler(Columns([Divider(), self.pile, Divider()]))

    def show(self):
        """Show login window"""
        #self.pile.set_focus(0)
        self.clear()
        loop = self.app.loop
        self.overlay.bottom_w = loop.widget
        loop.widget = self.overlay
        if loop.screen.started:
            loop.draw_screen()

    def hide(self):
        """Hide login window"""
        loop = self.app.loop
        loop.widget = self.overlay.bottom_w
        if loop.screen.started:
            loop.draw_screen()

    def login(self, user):
        """
        Login the session, showing all content and hidding login window.
        """
        # connect esc-esc signal to logout
        widget = self.overlay.bottom_w
        widget.orig_keypress = widget.keypress
        widget.keypress = self._wrapped_keypress

        self._last_key_time = time.time()
        self._timeout_sig_id = self.app.loop.set_alarm_in(self.max_time+1,
                                                          self._check_logout)

        if hasattr(widget, 'set_user') and callable(widget.set_user):
            widget.set_user(user)
        self.hide()
        self._emit("login")

    def logout(self):
        """Logout the session, hidding all content and showing login window
        again.
        """
        # disconnect esc-esc signal
        self.app.loop.widget.keypress = self.app.loop.widget.orig_keypress

        self.app.loop.remove_alarm(self._timeout_sig_id)
        self.show()
        self._emit("logout")

    def clear(self):
        self.username_entry.set_edit_text("")
        self.password_entry.set_edit_text("")
        self.pile.set_focus(0)

    def _wrapped_keypress(self, size, key):
        self._last_key_time = time.time()
        if key == 'esc':
            if self._out_count == 1 and (time.time() - self._evt_time) < 1:
                self._out_count = 0
                self._evt_time = 0
                self.logout()
            else:
                self._out_count = 1
                self._evt_time = time.time()
            return None
        else:
            return self.app.loop.widget.orig_keypress(size, key)

    def _username_keypress(self, size, key):
        if key == 'enter':
            key = 'down'
        return self.username_entry.__class__.keypress(self.username_entry, size, key)

    def _password_keypress(self, size, key):
        if key == 'enter':
            password = self.password_entry.get_edit_text()
            username = self.username_entry.get_edit_text()
            self.password_entry.set_edit_text("")
            if password and username:
                user = self.get_user(username, password)
                if user:
                    #self.username_entry.set_edit_text("")
                    self.login(user)
            return
        return self.password_entry.__class__.keypress(self.password_entry, size, key)

    def _check_logout(self, main_loop, user_data=None):
        etime = int(time.time() - self._last_key_time)
        if etime >= self.max_time:
            self.logout()
        else:
            main_loop.remove_alarm(self._timeout_sig_id)
            self._timeout_sig_id = main_loop.set_alarm_in(self.max_time-etime, self._check_logout)
        return False
