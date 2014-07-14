# -*- coding: utf-8 -*-

from urwid import Filler, Text
from screen import get_default_screen
import ulib

class UtkText(Text):

    def set_text(self, markup):
        super(UtkText, self).set_text(markup)
        s.queue_draw()

s = get_default_screen()
label = UtkText("<Hello World!>", 'center')
w = Filler(label)
s.add_toplevel(w)

def app_quit():
    loop.quit()

def change_text():
    label.set_text("<Bye World!>")

ulib.timeout_add_seconds(3, change_text)
ulib.timeout_add_seconds(6, app_quit)

s.start()
loop = ulib.MainLoop()
loop.run()
s.stop()
