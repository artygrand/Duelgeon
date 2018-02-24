#!/usr/bin/env python3

from Utils import win
from App.Gui import PauseMenu, OptionsMenu


class BaseScene:
    paused = False

    def __init__(self):
        self.pause_menu = PauseMenu()  # self.esc_handler
        base.accept('Options', OptionsMenu)

    def esc_handler(self):
        if self.paused:
            self.pause_menu.hide()
            win.hide_cursor()
            win.center_cursor()
            self.resume()
        else:
            self.pause()
            win.show_cursor()
            self.pause_menu.show()

        self.paused = not self.paused

    def pause(self):
        pass

    def resume(self):
        pass
