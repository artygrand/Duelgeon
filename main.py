#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import os

# Panda3D
from panda3d.core import AntialiasAttrib, Filename, loadPrcFile
from direct.showbase.ShowBase import ShowBase

# Game
from Utils import win
from App.Managers import GameManager
from App.Options import Options
from App.Gui import Loading


class App(ShowBase):
    company = 'Lone Tentacle'
    name = 'Duelgeon'
    version = '0.1.0'

    def __init__(self):
        ShowBase.__init__(self)

        udir = self.get_user_dir()
        Options.load(udir + '/config.ini')
        Options.apply()

        self.disableMouse()
        self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.render.setShaderAuto()

        self.enableParticles()

        self.accept('Exit', self.userExit)
        self.accept('alt-enter', win.toggle_fullscreen)
        self.accept('f12', self.screenshot, [str(Filename.fromOsSpecific(udir + '/screenshots/scr'))])

        base.buttonThrowers[0].node().setButtonDownEvent('Any-key-pressed')

        manager = GameManager()
        loading = Loading()
        loading.show()

        def start(task):
            manager.request('Menu')
        self.taskMgr.doMethodLater(.1, start, 'Show menu')

    def get_user_dir(self):
        udir = os.path.join(os.path.expanduser('~'), self.company, self.name)

        if not os.path.exists(udir):
            os.makedirs(udir)
            os.makedirs(os.path.join(udir, 'screenshots'))

        return udir


if __name__ == '__main__':
    loadPrcFile('local.prc')
    app = App()
    app.run()
