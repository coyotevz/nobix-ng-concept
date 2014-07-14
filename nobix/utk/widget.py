# -*- coding: utf-8 -*-

class Widget(object):
    """
    Base class for all Utk widgets.
    """
    __metaclass__ = MetaSignals

    signals = ('show', 'hide', 'map', 'unmap')

    _toplevel = False

    def __init__(self):
        self._state = STATE_NORMAL
        self._saved_state = STATE_NORMAL
        self._name = None
        self._requisition = None
        self._allocation = None
        self._parent = None

        # flags
        self._visible = False
        self._mapped = False
        self._realized = False

        # private flags
        self._child_visible = True
        self._redraw_on_alloc = True
        self._request_needed = True
        self._alloc_needed = True

        super(Widget, self).__init__()

    def show(self):
        if not self.is_visible:
            if self.is_toplevel:
                self.queue_resize()
            self.emit("show")
            self.notify("visible")

    def do_show(self):
        if not self.is_visible:
            self._visible = True
            if (self.parent and
                self.parent.is_mapped and
                self._child_visible and
                not self.is_mapped):
                    self.map()
