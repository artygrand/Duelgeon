#!/usr/bin/env python3

from direct.fsm.FSM import FSM


class MM(FSM):
    def __init__(self, menu):
        FSM.__init__(self, "MM")
        self.menu = menu

        self.accept('Menu-Play', self.request, ['ModeSelection'])
        self.accept('Menu-Options', self.request, ['Options'])
        self.accept('Menu-Back', self.request, ['Main'])

    def enterMain(self):
        self.menu.show('main')

    def exitMain(self):
        self.menu.hide('main')

    def enterModeSelection(self):
        self.menu.show('modes')

    def exitModeSelection(self):
        self.menu.hide('modes')

    def enterOptions(self):
        self.menu.show('options')

    def exitOptions(self):
        self.menu.hide('options')
