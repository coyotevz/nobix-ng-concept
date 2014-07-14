# -*- coding: utf-8 -*-

class MetaSignals(type):
    """
    Register the list of signals in the class variable signals, including
    signals in superclasses.
    """
    def __init__(cls, name, bases, d):
        signals = d.get('signals', [])
        for superclass in cls.__bases__:
            signals.extend(getattr(superclass, 'signals', []))
        signals = tuple(set(signals))
        d['signals'] = signals
        _make_signals_support(cls, signals)
        super(MetaSignals, cls).__init__(name, bases, d)


def _make_signals_support(cls, signals):

    def connect(self, name, callback, data=None):
        if not name in self._registered_signals:
            raise NameError("No such signal {0} for object {1}".format(name, self))
        self._registered_signals[name].append((callback, data))

    def disconnect(self, name, callback, data=None):
        if name not in self._registered_signals:
            return
        if (callback, data) not in self._registered_signals[name]:
            return
        self._registered_signals[name].remove((callback, data))

    def emit(self, name, *args):
        result = False
        pre_call = []
        sname = 'do_{}'.format(name.replace('-', '_').lower())
        if hasattr(self, sname) and callable(getattr(self, sname)):
            pre_call = [(getattr(self, sname), None)]
        for callback, data in pre_call + self._registered_signals.get(name, []):
            args_copy = args
            if data is not None:
                args_copy = args + (data,)
            result |= bool(callback(*args_copy))
        return result

    cls._registered_signals = dict([(signame, []) for signame in signals])

    setattr(cls, 'connect', connect)
    setattr(cls, 'disconnect', disconnect)
    setattr(cls, 'emit', emit)
