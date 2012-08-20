# -*- coding: utf-8 -*-

import urwid

class Password(urwid.Edit):
    """
    Edit box wich doesn't show what is entered (show '*' or other car intead)
    """

    def __init__(self, *args, **kwargs):
        """
        Same args than Edit.__init__ with an additional keyword arg 'hidden_char'
        @param hidden_char: char to show intead of what is actually entered: default '*'
        """
        self.hidden_char = kwargs.pop('hidden_char', '*')
        self.__real_text = ''
        self.__super.__init__(*args, **kwargs)

    def set_edit_text(self, text):
        self.__real_text = text
        hidden_text = len(text) * self.hidden_char
        self.__super.set_edit_text(hidden_text)

    def get_edit_text(self):
        return self.__real_text

    def insert_text(self, text):
        self._edit_text = self.__real_text
        self.__super.insert_text(text)
