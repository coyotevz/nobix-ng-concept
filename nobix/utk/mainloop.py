# -*- coding: utf-8 -*-

import select
import time
import heapq


PIPE_BUFFER_READ_SIZE = 4096


class MainLoop(object):
    """
    This is the standard main loop implementation fro a single interactive
    session.
    """

    def __init__(self):
        self.screen = None
        self.handle_mouse = False
        self.screen_size = None
        self.event_loop = SelectEventLoop()
        self._input_timeout = None

    def set_alarm_in(self, sec, callback, user_data=None):
        """
        Schedule an alarm in *sec* seconds that will call *callback* from the
        within the :meth:`run` method.

        sec -- seconds until alarm
        callback -- function to call with two parameters: this main loop object
                    and *user_data*
        """
        def cb():
            callback(self, user_data)
        return self.event_loop.alarm(sec, cb)

    def set_alarm_at(self, tm, callback, user_data=None):
        """
        Schedule an alarm at *tm* time that will call *callback* from the
        within the :meth:`run` method.

        Returns a handle that may be passed to :meth:`remove_alarm`.

        tm -- time to call callback e.g. ``time.time() + 5``
        callback -- function to call with two parameters: this main loop object
                    and *user_data*
        """
        def cb():
            callback(self, user_data)
        return self.event_loop.alarm(tm-time.time(), cb)

    def remove_alarm(self, handle):
        """
        Remove an alarm.

        Returns ``True`` if *handle* was found, ``False`` otherwise.
        """
        return self.event_loop.remove_alarm(handle)

    def watch_pipe(self, callback):
        pass

    def entering_idle(self):
        """
        This method is called whenever the eventloop is about to enter the idle
        state. :meth:`draw_screen` is called here to update the screen when
        anything has changed.
        """
        if self.screen.started:
            #self.draw_screen()
            pass

    def draw_screen(self):
        if not self.screen_size:
            self.screen_size = self.screen.get_cols_rows()

        canvas = self._topmost_widget.render(self.screen_size, focus=True)
        self.screen.draw_screen(self.screen_size, canvas)

    def process_input(self, keys):
        """
        This method will pass keyboard input and mouse events to
        :attr:`widget`.  This method is called automatically from the
        :meth:`run` method when there is input, but may also be called to
        simulate input from the user.

        *keys* is a list of input returned from :attr:`screen`'s get_input() or
        get_input_nonblocking() methods.

        Returns ``True`` if any key was handled by a widget or the
        :meth:`unhandled_input` method.
        """
        # TODO: implement
        pass

    def input_filter(self, keys, raw):
        """
        This function is passed each all the input events and raw keystroke
        values. These values are passed to the *input_filter* function passed
        to the constructor. That function must return a list of keys to be
        passed to the widgets to handle. If no *input_filter* was defined this
        implementation will return all the input events.
        """
        return keys

    def run(self):
        """
        Start the main loop handling input events and updating the screen. The
        loop will continue until :meth:`.quit` method is called.
        """
        if not self.screen:
            import screen
            self.screen = screen.Screen()

        if self.screen.started:
            self._run()
        else:
            self.screen.run_wrapper(self._run)

    def _run(self):
        if self.handle_mouse:
            self.screen.set_mouse_tracking()

        if not hasattr(self.screen, 'get_input_descriptors'):
            return self._run_screen_event_loop()

        #self.draw_screen()

        fd_handles = []
        def reset_input_descriptors(only_remove=False):
            for handle in fd_handles:
                self.event_loop.remove_watch_file(handle)
            if only_remove:
                return
            fd_handles[:] = [self.event_loop.watch_file(fd, self._update)
                             for fd in self.screen.get_input_descriptors()]

        try:
            signals.connect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED,
                                   reset_input_descriptors)
        except NameError:
            pass

        # watch our input descriptors
        reset_input_descriptors()
        idle_handle = self.event_loop.enter_idle(self.entering_idle)

        # go ..
        self.event_loop.run()

        # tidy up
        self.event_loop.remove_enter_idle(idle_handle)
        reset_input_descriptors(True)
        try:
            signals.disconnect_signal(self.screen, INPUT_DESCRIPTORS_CHANGED,
                                      reset_input_descriptors)
        except NameError:
            pass

    def _update(self, timeout=False):
        if self._input_timeout is not None and not timeout:
            # cancel the timeout, something else triggered the update
            self.event_loop.remove_alarm(self._input_timeout)
        self._input_timeout = None

        max_wait, keys, raw = self.screen.get_input_nonblocking()

        if max_wait is not None:
            # if get_input_nonblocking wants to be called back
            # make sure it happens with an alarm
            self._input_timeout = self.event_loop.alarm(max_wait,
                    lambda: self._update(timeout=True))

        keys = self.input_filter(keys, raw)

        if keys:
            self.process_input(keys)
            if 'window resize' in keys:
                self.screen_size = None

    def quit(self):
        self.event_loop.quit()


class SelectEventLoop(object):
    """
    Event loop based on :func:`select.select`
    """

    def __init__(self):
        self._alarms = []
        self._watch_files = {}
        self._idle_handle = 0
        self._idle_callbacks = {}
        self._stopped = False

    def alarm(self, seconds, callback):
        """
        Call callback() given time from now. No parameters are passed to
        callback.

        Returns a handle that may be passed to :meth:`remove_alarm`.

        seconds -- floating point time to wait before calling callback
        callback -- function to call from event loop
        """
        tm = time.time() + seconds
        heapq.heappush(self._alarms, (tm, callback))
        return (tm, callback)

    def remove_alarm(self, handle):
        """
        Remove an alarm.

        Returns True if the alarm exists, False otherwise
        """
        try:
            self._alarms.remove(handle)
            heapq.heapify(self._alarms)
            return True
        except ValueError:
            return False

    def watch_file(self, fd, callback):
        """
        Call callback() when fd has some data to read. No parameters are passed
        to callback.

        Returns a handle that may be passed to :meth:`remove_watch_file`

        fd -- file descriptor to watch for input
        callback -- function to call when input is available
        """
        self._watch_files[fd] = callback
        return fd

    def remove_watch_file(self, handle):
        """
        Remove an input file.

        Returns ``True`` if the input file exists, ``False`` otherwise.
        """
        if handle in self._watch_files:
            del self._watch_files[handle]
            return True
        return False

    def enter_idle(self, callback):
        """
        Add a callback for entering idle.

        Returns a handle that may be passed to remove_idle()
        """
        self._idle_handle += 1
        self._idle_callbacks[self._idle_handle] = callback
        return self._idle_handle

    def remove_enter_idle(self, handle):
        """
        Remove an idle callback.

        Returns True if the handle was removed.
        """
        if handle in self._idle_callbacks:
            del self._idle_callbacks[handle]
            return True
        return False

    def _entering_idle(self):
        """
        Call all the registered idle callbacks.
        """
        for callback in self._idle_callbacks.values():
            callback()

    def run(self):
        """
        Start the event loop. Exit the loop when any callback call
        :meth:`quit`.
        """
        self._did_something = True
        while not self._stopped:
            try:
                self.iteration()
            except select.error, e:
                if e.args[0] != 4:
                    raise

    def quit(self):
        self._stopped = True

    def is_running(self):
        return not self._stopped

    def iteration(self):
        """
        A single iteration of the event loop
        """
        fds = self._watch_files.keys()
        if self._alarms or self._did_something:
            if self._alarms:
                tm = self._alarms[0][0]
                timeout = max(0, tm-time.time())
            if self._did_something and (not self._alarms or timeout > 0):
                timeout = 0
                tm = 'idle'
            ready, w, err = select.select(fds, [], fds, timeout)
        else:
            tm = None
            ready, w, err = select.select(fds, [], fds)

        if not ready:
            if tm == 'idle':
                self._entering_idle()
                self._did_something = False
            elif tm is not None:
                # must have been a timeout
                tm, alarm_callback = self._alarms.pop(0)
                alarm_callback()
                self._did_something = True

        for fd in ready:
            self._watch_files[fd]()
            self._did_something = True

    def events_pending(self):
        fds = self._watch_files.keys()
        timeout = -1
        if self._alarms:
            tm = self._alarms[0][0]
            timeout = max(0, tm-time.time())
        ready, w, err = select.select(fds, [], fds, 0)
        return bool(ready or timeout) or self._did_something
