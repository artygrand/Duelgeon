#!/usr/bin/env python3

from direct.fsm.FSM import FSM

from Scenes import *
from Utils import win
import App
from App.Gui import PauseMenu, OptionsMenu, MainMenu, GameModesMenu
from App.Console import DeveloperConsole


class GameManager(FSM):
    def __init__(self):
        FSM.__init__(self, 'GM')

        self.console = ConsoleManager()
        self.mgr = None
        self.scene = None
        self.scene_holder = render.attachNewNode('Scene holder')

        self.accept('Menu', self.request, ['Menu'])
        for mode in ['Arcade', 'Hardcore', 'Coop', 'Versus']:
            self.accept('Play-' + mode, self.request, ['Game', mode])
        self.accept('Menu-Training', self.request, ['Training'])
        self.accept('Menu-Heroes', self.request, ['HeroEditor'])

    def destroy(self):
        self.ignoreAll()

    def enterMenu(self):
        self.scene = Menu.Menu(self.scene_holder)
        self.mgr = MenuManager()
        self.mgr.request('Main')

        base.messenger.send('Loaded')

    def exitMenu(self):
        base.messenger.send('Loading')

        self.scene.destroy()
        self.mgr.destroy()
        self.mgr = None

    def enterGame(self, mode):
        win.hide_cursor()

        self.scene = Game.Game(self.scene_holder, mode)
        self.mgr = OverlayManager()
        self.mgr.request('None')

        base.messenger.send('Loaded')

    def exitGame(self):
        base.messenger.send('Loading')

        self.scene.destroy()
        self.mgr.destroy()
        self.mgr = None

        win.show_cursor()

    def enterTraining(self):
        win.hide_cursor()

        self.scene = Practice.Practice(self.scene_holder)
        self.mgr = OverlayManager()
        self.mgr.request('None')

        base.messenger.send('Loaded')

    def exitTraining(self):
        base.messenger.send('Loading')

        self.scene.destroy()
        self.mgr.destroy()
        self.mgr = None

        win.show_cursor()

    def enterHeroEditor(self):
        self.scene = HeroEditor.HeroEditor(self.scene_holder)

        self.accept('escape', self.request, ['Menu'])

        base.messenger.send('Loaded')

    def exitHeroEditor(self):
        base.messenger.send('Loading')

        self.scene.destroy()

        self.ignore('escape')


class MenuManager(FSM):
    def __init__(self):
        FSM.__init__(self, 'MM')

        self.main = MainMenu()
        self.modes = GameModesMenu()
        self.options = OptionsMenu()

        self.accept('Menu-Play', self.request, ['ModeSelection'])
        self.accept('Menu-Back', self.request, ['Main'])
        self.accept('Menu-Options', self.request, ['Options'])
        self.accept('Options-Back', self.request, ['Main'])
        self.accept('escape', self.on_esc)

    def destroy(self):
        self.main.destroy()
        self.modes.destroy()
        self.options.destroy()

        self.ignoreAll()

    def enterMain(self):
        self.main.show()

    def exitMain(self):
        self.main.hide()

    def enterModeSelection(self):
        self.modes.show()

    def exitModeSelection(self):
        self.modes.hide()

    def enterOptions(self):
        self.options.show()

    def exitOptions(self):
        self.options.hide()

    def on_esc(self):
        if self.state != 'Main':
            self.request('Main')


class OverlayManager(FSM):
    def __init__(self):
        FSM.__init__(self, 'OM')

        self.pause = PauseMenu()
        self.options = OptionsMenu()

        self.accept('Overlay-None', self.request, ['None'])
        self.accept('Overlay-Pause', self.request, ['Pause'])
        self.accept('Overlay-Options', self.request, ['Options'])
        self.accept('Options-Back', self.request, ['Pause'])
        self.accept('escape', self.on_esc)

    def destroy(self):
        self.pause.destroy()
        self.options.destroy()

        self.ignoreAll()

    def enterNone(self, hide=True):
        App.paused = False
        base.messenger.send('Resume-game')
        if hide:  # TODO reformat
            win.hide_cursor()

    def exitNone(self):
        App.paused = True
        base.messenger.send('Pause-game')
        win.show_cursor()

    def enterPause(self):
        self.pause.show()

    def exitPause(self):
        self.pause.hide()

    def enterOptions(self):
        self.options.show()

    def exitOptions(self):
        self.options.hide()

    def on_esc(self):
        if self.state == 'Pause':
            self.request('None')
        else:
            self.request('Pause')


class ConsoleManager(FSM):
    def __init__(self):
        FSM.__init__(self, 'CM')

        self.console = DeveloperConsole()

        self.acceptOnce('`', self.request, ['Show'])

    def enterShow(self):
        base.messenger.send('Pause-game')
        self.console.show()
        self.acceptOnce('`', self.request, ['Hide'])

    def enterHide(self):
        base.messenger.send('Resume-game')
        self.console.hide()
        self.acceptOnce('`', self.request, ['Show'])
