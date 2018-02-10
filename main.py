#!/usr/bin/env python3

import os

# Panda3D
from panda3d.core import AntialiasAttrib, Filename, loadPrcFileData, loadPrcFile
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DGG

# Game
from Utils import win
from Managers.Game import GM


class App(ShowBase):
    company = "Lone Tentacle"
    name = "Duelgeon"
    version = "0.1.0"

    scene = None
    sceneNode = None

    def __init__(self):
        self.load_config()
        DGG.getDefaultFont().setPixelsPerUnit(100)

        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.render.setShaderAuto()

        self.enableParticles()

        self.accept('escape', self.quit)
        self.accept('alt-enter', win.toggle_fullscreen)

        self.sceneNode = render.attachNewNode('Scene node')

        self.manager = GM(self)
        self.manager.request('Menu')

    def load_config(self):
        loadPrcFile('local.prc')
        loadPrcFileData('', 'window-title {}'.format(self.name))

        basedir = os.path.join(os.path.expanduser('~'), self.company, self.name)
        file = os.path.join(basedir, 'config-{}.prc'.format(self.version))

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        if os.path.exists(file):
            loadPrcFile(Filename.fromOsSpecific(file))

    def quit(self):
        self.scene.esc_handler()


if __name__ == '__main__':
    app = App()
    app.run()
