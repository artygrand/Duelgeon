#!/usr/bin/env python3

from panda3d.core import Point2, Point3, VBase4
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText


class HasFrame:
    def __init__(self, z):
        self.frame = DirectFrame()
        self.frame.setBin('onscreen', z)

    def show(self):
        self.frame.show()

    def hide(self):
        self.frame.hide()

    def destroy(self):
        self.frame.removeNode()


class CharMarks(HasFrame):
    chars = {}
    marks = {}
    heights = {}

    def __init__(self):
        HasFrame.__init__(self, 1)

        base.taskMgr.add(self.update, 'update char marks', 10)

    def add(self, name, char, mark, height):
        mark.reparentTo(self.frame)
        self.chars[name] = char
        self.marks[name] = mark
        self.heights[name] = height

    def remove(self, name):
        del self.chars[name]
        del self.marks[name]
        del self.heights[name]

    def update(self, task):
        for name, char in self.chars.items():
            self.marks[name].setPos(*self.get_pos(char, self.heights[name]))

        return task.cont

    def get_pos(self, node, height):
        p3 = base.cam.getRelativePoint(render, node.getPos(render))
        full = base.camLens.getProjectionMat().xform(VBase4(p3[0], p3[1], p3[2], 1.0))
        p2 = 10.0, 10.0

        if full[3] > 0:
            full3 = 1.0 / full[3]
            p2 = full[0] * full3, full[1] * full3

        pos = aspect2d.getRelativePoint(render2d, Point3(p2[0], 0, p2[1]))
        pos[2] = pos[2] + height * 4 / p3[1]

        return pos[0], pos[2]


class HUD(HasFrame):
    def __init__(self):
        HasFrame.__init__(self, 2)

        self.crosshair = OnscreenImage('gui/crosshair.png', pos=(0, 0, 0), scale=0.03, parent=self.frame)
        self.crosshair.setTransparency(1)
        self.crosshair.setColor(1, 1, 1, 0.7)


class PauseMenu(HasFrame):
    def __init__(self, resume):
        HasFrame.__init__(self, 3)

        button = loader.loadModel('gui/pause-button')

        self.frame['text'] = 'Pause'
        self.frame['text_pos'] = 0, 0.38
        self.frame['text_fg'] = 1, 1, 1, 1
        self.frame['text_scale'] = 0.1
        self.frame['frameColor'] = 0, 0, 0, 0.6
        self.frame['frameSize'] = -.33, .33, 0.5, -0.5
        self.frame.setPos(0, 0, 0)
        self.frame.hide()

        pos = .25
        for text, cmd in {
                'Resume': (resume, []),
                'Options': (resume, []),
                'Leave game': (base.messenger.send, ['Menu']),
                'Exit to desktop': (base.messenger.send, ['exit'])}.items():
            DirectButton(
                parent=self.frame,
                text=text,
                pos=(0, 0, pos),
                relief=DGG.FLAT,
                geom=(button.find('**/button'), button.find('**/button-click'),
                      button.find('**/button-hover'), button.find('**/button-disabled')),
                frameSize=(-0.5, 0.5, .15, -.15),
                text_fg=(1, 1, 1, 1),
                text_scale=0.1,
                text_pos=(0, -0.02),
                scale=0.5,
                rolloverSound=None,
                clickSound=None,
                command=cmd[0],
                extraArgs=cmd[1],
            )
            pos -= .20
