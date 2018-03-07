#!/usr/bin/env python3


class Events:
    def __init__(self):
        self.events = {}

    def on(self, event, callback, *args, **kwargs):
        self.__add(event, (callback, args, kwargs), 0)

    def once(self, event, callback, *args, **kwargs):
        self.__add(event, (callback, args, kwargs), 1)

    def __add(self, event, params, once=0):
        """Add callback to event
           If once = 1, callback will be deleted after call
        """
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(params + (once,))

    def trigger(self, event):
        """Trigger event and call callbacks with args"""
        try:
            for data in self.events[event]:
                data[0](*data[1], **data[2])
                if data[3]:
                    self.events[event].remove(data)
        except KeyError:
            pass
