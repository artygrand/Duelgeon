#!/usr/bin/env python3

from direct.fsm.FSM import FSM

from Scenes import *
from Utils import win


class GM(FSM):
    def __init__(self, app):
        FSM.__init__(self, "GM")
        self.app = app
        self.accept('Menu', self.request, ['Menu'])

    def enterMenu(self):
        self.accept('Play-Arcade', self.request, ['Game', 'Arcade'])
        self.accept('Play-Hardcore', self.request, ['Game', 'Hardcore'])
        self.accept('Play-Coop', self.request, ['Game', 'Coop'])
        self.accept('Play-Versus', self.request, ['Game', 'Versus'])

        self.accept('Menu-Training', self.request, ['Training'])
        self.accept('Menu-Heroes', self.request, ['HeroEditor'])

        self.app.scene = Menu.Menu(self.app.sceneNode.attachNewNode('Current'))
        self.app.scene.show('main')

    def exitMenu(self):
        for e in ['Play-Arcade', 'Play-Hardcore', 'Play-Coop', 'Play-Versus',
                  'Menu-Training', 'Menu-Heroes']:
            self.ignore(e)

        self.app.scene.destroy()

    def enterGame(self, mode):
        win.hide_cursor()
        self.app.scene = Game.Game(self.app.sceneNode.attachNewNode('Current'), mode)

    def exitGame(self):
        win.show_cursor()
        self.app.scene.destroy()

    def enterTraining(self):
        win.hide_cursor()
        self.app.scene = Practice.Practice(self.app.sceneNode.attachNewNode('Current'))

    def exitTraining(self):
        self.app.scene.destroy()
        win.show_cursor()

    def enterHeroEditor(self):
        self.app.scene = HeroEditor.HeroEditor(self.app.sceneNode.attachNewNode('Current'))

    def exitHeroEditor(self):
        self.app.scene.destroy()
