# -*- coding: utf-8 -*-

from misc import Misc


class Label(Misc):

    def __init__(self, text=""):
        super(Label, self).__init__()
        self._text = text

    def set_text(self, text):
        if text != self._text:
            self._text = text
            self.notify("text")
            self.queue_draw()
