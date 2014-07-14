# -*- coding: utf-8 -*-
# Urwid common display code, and raw display module
#    Copyright (C) 2004-2011  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/


from attr import AttrSpec, DEFAULT
from signals import MetaSignals
import ulib


# priority for redraw
PRIORITY_REDRAW = ulib.PRIORITY_HIGH_IDLE + 20


class ScreenError(Exception):
    pass


class BaseScreen(object):
    """
    Base class for Screen classes (raw_display.Screen, .. etc)
    """
    __metaclass__ = MetaSignals
    signals = ['start', 'stop', 'udpate-palette-entry', 'clear', 'draw-screen',
               'input-descriptors-changed']

    def __init__(self):
        super(BaseScreen, self).__init__()
        self._palette = {}
        self._started = False
        self._update_idle = None
        self._toplevels = []

    started = property(lambda self: self._started)

    def start(self):
        """
        Initialize the screen and input mode.
        """
        if self._started:
            return
        self.emit('start')
        if not self._started:
            raise ScreenError("Not properly started")

    def stop(self):
        """
        Restore the screen
        """
        if not self._started:
            return
        self.emit("stop")
        if self._started:
            raise ScreenError("Not properly stopped")

    def register_palette(self, palette):
        """Register a set of palette entries.

        palette -- a list of (name, like_other_name) or
        (name, foreground, background, mono, foreground_high,
        background_high) tuples

            The (name, like_other_name) format will copy the settings
            from the palette entry like_other_name, which must appear
            before this tuple in the list.

            The mono and foreground/background_high values are
            optional ie. the second tuple format may have 3, 4 or 6
            values.  See register_palette_entry() for a description
            of the tuple values.
        """
        for item in palette:
            if len(item) in (3, 4, 6):
                self.register_palette_entry(*item)
                continue
            if len(item) != 2:
                raise ScreenError("Invalid register_palette entry: %s" %
                    repr(item))
            name, like_name = item
            if not self._palette.has_key(like_name):
                raise ScreenError("palette entry '%s' doesn't exist"%like_name)
            self._palette[name] = self._palette[like_name]

    def register_palette_entry(self, name, foreground, background,
        mono=None, foreground_high=None, background_high=None):
        """Register a single palette entry.

        name -- new entry/attribute name

        foreground -- a string containing a comma-separated foreground
        color and settings

            Color values:
            'default' (use the terminal's default foreground),
            'black', 'dark red', 'dark green', 'brown', 'dark blue',
            'dark magenta', 'dark cyan', 'light gray', 'dark gray',
            'light red', 'light green', 'yellow', 'light blue',
            'light magenta', 'light cyan', 'white'

            Settings:
            'bold', 'underline', 'blink', 'standout'

            Some terminals use 'bold' for bright colors.  Most terminals
            ignore the 'blink' setting.  If the color is not given then
            'default' will be assumed.

        background -- a string containing the background color

            Background color values:
            'default' (use the terminal's default background),
            'black', 'dark red', 'dark green', 'brown', 'dark blue',
            'dark magenta', 'dark cyan', 'light gray'

        mono -- a comma-separated string containing monochrome terminal
        settings (see "Settings" above.)

            None = no terminal settings (same as 'default')

        foreground_high -- a string containing a comma-separated
        foreground color and settings, standard foreground
        colors (see "Color values" above) or high-colors may
        be used

            High-color example values:
            '#009' (0% red, 0% green, 60% red, like HTML colors)
            '#fcc' (100% red, 80% green, 80% blue)
            'g40' (40% gray, decimal), 'g#cc' (80% gray, hex),
            '#000', 'g0', 'g#00' (black),
            '#fff', 'g100', 'g#ff' (white)
            'h8' (color number 8), 'h255' (color number 255)

            None = use foreground parameter value

        background_high -- a string containing the background color,
        standard background colors (see "Background colors" above)
        or high-colors (see "High-color example values" above)
        may be used

            None = use background parameter value
        """
        basic = AttrSpec(foreground, background, 16)

        if isinstance(mono, tuple):
            mono = ",".join(mono)
        if mono is None:
            mono = DEFAULT
        mono = AttrSpec(mono, DEFAULT, 1)

        if foreground_high is None:
            foreground_high = foreground
        if background_high is None:
            background_high = background
        high_88 = AttrSpec(foreground_high, background_high, 88)
        high_256 = AttrSpec(foreground_high, background_high, 256)

        self.emit('update-palette-entry', name, basic, mono, high_88, high_256)
        self._palette[name] = (basic, mono, high_88, high_256)

    def clear(self):
        """
        Force the screen to be completely repainted on the next call to
        :meth:`draw_screen`
        """
        self.emit("clear")

    def get_cols_rows(self):
        """
        Return the terminal dimensions (num columns, num rows)
        """
        raise NotImplementedError("you must implement this method")

    def draw_screen(self):
        """
        Paint screen with rendered canvas.
        """
        self.emit("draw-screen")

    def draw_screen_idle(self):
        """
        Call :meth:`draw_screen` in idle update
        """
        self.draw_screen()
        self._update_idle = None
        return False

    def queue_draw(self):
        """
        Signal this Screen to redraw in the next idle update
        """
        if not self._update_idle:
            self._update_idle = ulib.idle_add(self.draw_screen_idle,
                                              priority=PRIORITY_REDRAW)

    def add_toplevel(self, widget):
        if widget not in self._toplevels:
            self._toplevels.append(widget)
            self.queue_draw()

    def remove_toplevel(self, widget):
        if widget in self._toplevels:
            self._toplevels.remove(widget)
            self.queue_draw()

    def raise_toplevel(self, widget):
        if widget in self._toplevels:
            self._toplevels.remove(widget)
            self._toplevels.append(widget)
            self.queue_draw()


_default_screen = None

def get_default_screen():
    global _default_screen
    if _default_screen is None:
        from raw_screen import Screen
        _default_screen = Screen()
    return _default_screen
