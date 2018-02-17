#!/usr/bin/env python3

import os

# Panda3D
from panda3d.core import AntialiasAttrib, Filename, loadPrcFileData, loadPrcFile, CullBinManager
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
        udir = self.get_user_dir()
        self.load_config(udir)

        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0)
        self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.render.setShaderAuto()

        self.enableParticles()

        self.accept('escape', self.quit)
        self.accept('exit', self.userExit)
        self.accept('alt-enter', win.toggle_fullscreen)
        self.accept('f12', self.screenshot, [str(Filename.fromOsSpecific(udir + '/screenshots/scr'))])

        self.sceneNode = self.render.attachNewNode('Scene node')

        self.manager = GM(self)
        self.manager.request('Menu')

        cull_manager = CullBinManager.getGlobalPtr()
        cull_manager.addBin('onscreen', cull_manager.BTFixed, 60)

    def get_user_dir(self):
        udir = os.path.join(os.path.expanduser('~'), self.company, self.name)

        if not os.path.exists(udir):
            os.makedirs(udir)
            os.makedirs(os.path.join(udir, 'screenshots'))

        return udir

    def load_config(self, udir):
        loadPrcFile('local.prc')
        loadPrcFileData('', 'window-title {}'.format(self.name))

        file = os.path.join(udir, 'config-{}.prc'.format(self.version))

        if os.path.exists(file):
            loadPrcFile(Filename.fromOsSpecific(file))

    def quit(self):
        self.scene.esc_handler()


if __name__ == '__main__':
    app = App()
    app.run()
