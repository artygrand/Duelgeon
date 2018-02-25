#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from code import InteractiveInterpreter

from panda3d.core import TextNode, TextProperties, TextPropertiesManager
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectFrame, DirectEntry
from direct.gui.OnscreenText import OnscreenText

TEXT_MARGIN = (0.03, -0.06)


class PseudoFile:
    def __init__(self, write):
        self.write = write

    def readline(self):
        pass

    def writelines(self, l):
        map(self.append, l)

    def flush(self):
        pass

    def isatty(self):
        return 1


class DeveloperConsole(InteractiveInterpreter, DirectObject):
    def __init__(self):
        sys.stdout = PseudoFile(self.write_out)
        sys.stderr = PseudoFile(self.write_err)
        tp_err = TextProperties()
        tp_err.setTextColor(1, 0.5, 0.5, 1)
        TextPropertiesManager.getGlobalPtr().setProperties('err', tp_err)
        font = loader.loadFont('cmss12')
        self.frame = DirectFrame(parent=base.a2dTopCenter, text_align=TextNode.ALeft,
                                 text_pos=(base.a2dLeft + TEXT_MARGIN[0], TEXT_MARGIN[1]), text_scale=0.05,
                                 text_fg=(1, 1, 1, 1), frameSize=(-2.0, 2.0, -1, 0.0), frameColor=(0, 0, 0, 0.5),
                                 text='', text_font=font, sortOrder=4)
        self.entry = DirectEntry(parent=base.a2dTopLeft, command=self.command, scale=0.05, width=1000.0,
                                 pos=(-0.02, 0, -0.98), relief=None, text_pos=(1.5, 0, 0), text_fg=(1, 1, 0.5, 1),
                                 rolloverSound=None, clickSound=None, text_font=font)
        self.otext = OnscreenText(parent=self.entry, scale=1, align=TextNode.ALeft, pos=(1, 0, 0), fg=(1, 1, 0.5, 1),
                                  text=':', font=font)
        self.lines = [''] * 19
        self.commands = []  # All previously sent commands
        self.cscroll = None  # Index of currently navigated command, None if current
        self.command = ''  # Currently entered command
        self.block = ''  # Temporarily stores a block of commands
        self.hide()
        self.initialized = False

    def prev_command(self):
        if self.hidden:
            return
        if len(self.commands) == 0:
            return
        if self.cscroll is None:
            self.cscroll = len(self.commands)
            self.command = self.entry.get()
        elif self.cscroll <= 0:
            return
        else:
            self.commands[self.cscroll] = self.entry.get()
        self.cscroll -= 1
        self.entry.set(self.commands[self.cscroll])
        self.entry.setCursorPosition(len(self.commands[self.cscroll]))

    def next_command(self):
        if self.hidden:
            return
        if len(self.commands) == 0:
            return
        if self.cscroll is None:
            return
        self.commands[self.cscroll] = self.entry.get()
        self.cscroll += 1
        if self.cscroll >= len(self.commands):
            self.cscroll = None
            self.entry.set(self.command)
            self.entry.setCursorPosition(len(self.command))
        else:
            self.entry.set(self.commands[self.cscroll])
            self.entry.setCursorPosition(len(self.commands[self.cscroll]))

    def write_out(self, line, copy=True):
        if copy:
            sys.__stdout__.write(line)
        lines = line.split('\n')
        firstline = lines.pop(0)
        self.lines[-1] += firstline
        self.lines += lines
        self.frame['text'] = '\n'.join(self.lines[-19:])

    def write_err(self, line, copy=True):
        if copy:
            sys.__stderr__.write(line)
        line = '\1err\1%s\2' % line
        lines = line.split('\n')
        firstline = lines.pop(0)
        self.lines[-1] += firstline
        self.lines += lines
        self.frame['text'] = '\n'.join(self.lines[-19:])

    def command(self, text):
        if self.hidden:
            return

        self.cscroll = None
        self.command = ''
        self.entry.set('')
        self.entry['focus'] = True
        self.write_out(self.otext['text'] + ' ' + text + '\n', False)
        if text != '' and (len(self.commands) == 0 or self.commands[-1] != text):
            self.commands.append(text)

        if not self.initialized:
            InteractiveInterpreter.__init__(self)
            self.initialized = True
        try:
            if self.runsource(self.block + '\n' + text) and text != '':
                self.otext['text'] = '.'
                self.block += '\n' + text
            else:
                self.otext['text'] = ':'
                self.block = ''
        except Exception:
            self.write_err(traceback.format_exc())

    def toggle(self):
        if self.hidden:
            self.show()
        else:
            self.hide()

    def show(self):
        self.accept('arrow_up', self.prev_command)
        self.accept('arrow_up-repeat', self.prev_command)
        self.accept('arrow_down', self.next_command)
        self.accept('arrow_down-repeat', self.next_command)
        self.hidden = False
        self.entry['focus'] = True
        self.frame.show()
        self.entry.show()
        self.otext.show()

    def hide(self):
        self.ignoreAll()
        self.hidden = True
        self.entry['focus'] = False
        self.entry.set(self.entry.get()[:-1])
        self.frame.hide()
        self.entry.hide()
        self.otext.hide()

    def destroy(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.ignoreAll()
        self.frame.destroy()
        self.entry.destroy()
        self.otext.destroy()
