#!/usr/bin/env python3

from direct.showbase.DirectObject import DirectObject

import App
from Utils import win


class BaseScene(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)

        self.accept('Pause-game', self.pause)
        self.accept('Resume-game', self.resume)

    def pause(self):
        App.paused = True
        win.show_cursor()

    def resume(self):
        App.paused = False
        win.hide_cursor()

    def destroy(self):
        self.ignoreAll()
