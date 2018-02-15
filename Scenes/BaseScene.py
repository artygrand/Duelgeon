#!/usr/bin/env python3

from Utils import win


class BaseScene:
    paused = False

    def esc_handler(self):
        # TODO show mini-menu
        if self.paused:
            print('Pause menu close')
            win.hide_cursor()
            self.resume()
        else:
            self.pause()
            win.show_cursor()
            print('Pause menu open')

        self.paused = not self.paused

    def pause(self):
        pass

    def resume(self):
        pass
