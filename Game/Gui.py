#!/usr/bin/env python3

from panda3d.core import Point2, Point3


class CharMarks:
    chars = {}
    marks = {}
    heights = {}

    def __init__(self):
        base.taskMgr.add(self.update, 'update char marks', 10)

    def add(self, name, char, mark, height):
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
        p2 = Point2()
        pos = (0, 0, 2)
        if base.camLens.project(p3, p2):
            r2d = Point3(p2[0], 0, p2[1])
            pos = pixel2d.getRelativePoint(render2d, r2d)

            pos[0] = (pos[0] / base.win.getXSize() - .5) * 2 * base.a2dRight
            pos[2] = ((-pos[2] / base.win.getYSize() - .5) * -2) + height * 4 / p3[1]

        return pos[0], pos[2]
